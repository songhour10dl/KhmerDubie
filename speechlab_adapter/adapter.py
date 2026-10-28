"""FastAPI adapter for SpeechLab TTS integration with KhmerDubStudio.

This adapter translates KhmerDubStudio's expected TTS API format into
SpeechLab's actual API format, handles voice mapping, and resamples audio
to the requested sample rate.
"""
import os
import io
import logging
import wave
from pathlib import Path
from typing import Optional

import httpx
import numpy as np
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseModel, Field
from scipy import signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SpeechLab Adapter for KhmerDubStudio",
    description="Compatibility layer between KhmerDubStudio and SpeechLab TTS",
    version="1.0.0"
)

# Configuration from environment variables
SPEECHLAB_BASE_URL = os.getenv("SPEECHLAB_BASE_URL", "http://localhost:8880")
ADAPTER_HOST = os.getenv("ADAPTER_HOST", "0.0.0.0")
ADAPTER_PORT = int(os.getenv("ADAPTER_PORT", "8881"))
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "300.0"))

# Voice mapping: KhmerDubStudio voice names -> SpeechLab voice configuration
# These map to actual voice IDs that should exist in SpeechLab's backend/voices/
# or use the default built-in voice with style instructions for nanovllm_km
VOICE_MAPPING = {
    "khmer-female": {
        "voice_id": "",  # Empty = use default nanovllm_km voice
        "style": "(សំឡេងស្ត្រី ស្ងប់ស្ងាត់)",  # Female, calm voice style
        "gender": "female"
    },
    "khmer-male": {
        "voice_id": "",  # Empty = use default nanovllm_km voice
        "style": "(សំឡេងបុរស)",  # Male voice style
        "gender": "male"
    }
}


class SynthesizeRequest(BaseModel):
    """Request model matching KhmerDubStudio's expected format."""
    text: str = Field(..., min_length=1, description="Khmer text to synthesize")
    voice: str = Field(..., description="Voice ID: khmer-female or khmer-male")
    language: str = Field(default="km", description="Language code")
    format: str = Field(default="wav", description="Audio format (only wav supported)")
    sample_rate: int = Field(default=48000, ge=8000, le=48000, description="Target sample rate in Hz")


class StatusResponse(BaseModel):
    """Status response model."""
    status: str = Field(..., description="Status: ok, loading, or error")
    engine: str = Field(..., description="Active TTS engine name")
    ready: bool = Field(..., description="Whether the service is ready to synthesize")
    message: str = Field(default="", description="Additional status information")
    khmer_support: bool = Field(default=True, description="Khmer language support available")
    supported_voices: list[str] = Field(default_factory=list, description="List of supported voice IDs")


def validate_voice(voice: str) -> dict:
    """Validate and map voice to SpeechLab configuration.
    
    Args:
        voice: Voice identifier from KhmerDubStudio (e.g., 'khmer-female')
        
    Returns:
        Voice configuration dictionary
        
    Raises:
        HTTPException: If voice is not supported
    """
    if voice not in VOICE_MAPPING:
        logger.error(f"Unsupported voice requested: {voice}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported voice '{voice}'. Supported voices: {list(VOICE_MAPPING.keys())}"
        )
    return VOICE_MAPPING[voice]


def split_khmer_text(text: str, max_chars: int = 500) -> list[str]:
    """Split Khmer text at natural sentence boundaries.
    
    Splits on Khmer sentence terminators (។ ៕ ! ? etc.) while respecting
    maximum character limits to avoid memory issues with long text.
    
    Args:
        text: Input Khmer text
        max_chars: Maximum characters per chunk
        
    Returns:
        List of text chunks
    """
    # Khmer sentence terminators
    terminators = ['។', '៕', '!', '?', '\n']
    
    chunks = []
    current_chunk = ""
    
    for char in text:
        current_chunk += char
        
        # Split on sentence boundary if we've exceeded max length
        if char in terminators and len(current_chunk) >= max_chars:
            chunks.append(current_chunk.strip())
            current_chunk = ""
    
    # Add remaining text
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    # If no terminators found and text is long, split by max_chars
    if len(chunks) == 1 and len(chunks[0]) > max_chars:
        single_chunk = chunks[0]
        chunks = []
        for i in range(0, len(single_chunk), max_chars):
            chunks.append(single_chunk[i:i + max_chars])
    
    return chunks if chunks else [text]


async def synthesize_with_speechlab(text: str, voice_config: dict) -> tuple[bytes, int]:
    """Call SpeechLab API to synthesize speech.
    
    Args:
        text: Text to synthesize (may include style prefix)
        voice_config: Voice configuration from VOICE_MAPPING
        
    Returns:
        Tuple of (audio_bytes, sample_rate)
        
    Raises:
        HTTPException: If synthesis fails
    """
    # Prepare text with style instruction if provided
    styled_text = text
    if voice_config.get("style"):
        # Only add style if not already present
        if not text.strip().startswith("("):
            styled_text = f"{voice_config['style']} {text}"
    
    # Prepare request for SpeechLab's /api/synthesize endpoint
    speechlab_request = {
        "text": styled_text,
        "speakers": [
            {
                "name": "Speaker 1",
                "voice": voice_config["voice_id"],  # Empty string uses default
                "voice_mode": None  # Use default mode for nanovllm_km
            }
        ],
        "engine": "nanovllm_km",  # Force Khmer engine
        "force_regenerate": False
    }
    
    logger.info(f"Synthesizing with SpeechLab: text='{text[:50]}...', engine=nanovllm_km")
    
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.post(
                f"{SPEECHLAB_BASE_URL}/api/synthesize",
                json=speechlab_request,
                headers={"Accept": "audio/wav"}
            )
            
            if response.status_code != 200:
                error_detail = response.text
                logger.error(f"SpeechLab synthesis failed: {response.status_code} - {error_detail}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"SpeechLab synthesis failed: {error_detail}"
                )
            
            # Extract sample rate from headers
            sample_rate = int(response.headers.get("X-Sample-Rate", "24000"))
            audio_bytes = response.content
            
            logger.info(f"Synthesis successful: {len(audio_bytes)} bytes, {sample_rate} Hz")
            return audio_bytes, sample_rate
            
    except httpx.TimeoutException:
        logger.error("SpeechLab request timed out")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Synthesis timed out after {REQUEST_TIMEOUT}s"
        )
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to SpeechLab: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Cannot connect to SpeechLab at {SPEECHLAB_BASE_URL}: {str(e)}"
        )


def resample_audio(audio_bytes: bytes, source_rate: int, target_rate: int) -> bytes:
    """Resample WAV audio to target sample rate.
    
    Args:
        audio_bytes: Input WAV audio bytes
        source_rate: Source sample rate
        target_rate: Target sample rate
        
    Returns:
        Resampled WAV audio bytes
    """
    if source_rate == target_rate:
        return audio_bytes
    
    logger.info(f"Resampling audio: {source_rate} Hz -> {target_rate} Hz")
    
    # Read WAV data
    with io.BytesIO(audio_bytes) as wav_in:
        with wave.open(wav_in, 'rb') as wav:
            n_channels = wav.getnchannels()
            sampwidth = wav.getsampwidth()
            frames = wav.readframes(wav.getnframes())
    
    # Convert to numpy array
    if sampwidth == 2:
        dtype = np.int16
    elif sampwidth == 4:
        dtype = np.int32
    else:
        dtype = np.int16  # fallback
    
    audio_data = np.frombuffer(frames, dtype=dtype)
    
    # Reshape for multi-channel
    if n_channels > 1:
        audio_data = audio_data.reshape(-1, n_channels)
    
    # Resample using scipy
    num_samples = int(len(audio_data) * target_rate / source_rate)
    
    if n_channels == 1:
        resampled = signal.resample(audio_data, num_samples)
    else:
        # Resample each channel separately
        resampled = np.zeros((num_samples, n_channels), dtype=audio_data.dtype)
        for ch in range(n_channels):
            resampled[:, ch] = signal.resample(audio_data[:, ch], num_samples)
    
    # Convert back to bytes
    resampled_int = resampled.astype(dtype)
    
    # Write to WAV
    with io.BytesIO() as wav_out:
        with wave.open(wav_out, 'wb') as wav:
            wav.setnchannels(n_channels)
            wav.setsampwidth(sampwidth)
            wav.setframerate(target_rate)
            wav.writeframes(resampled_int.tobytes())
        
        return wav_out.getvalue()


def join_audio_segments(segments: list[bytes], sample_rate: int) -> bytes:
    """Join multiple WAV audio segments into a single WAV file.
    
    Args:
        segments: List of WAV audio bytes
        sample_rate: Sample rate (must be same for all segments)
        
    Returns:
        Combined WAV audio bytes
    """
    if not segments:
        raise ValueError("No audio segments to join")
    
    if len(segments) == 1:
        return segments[0]
    
    logger.info(f"Joining {len(segments)} audio segments")
    
    # Read all segments and extract audio data
    all_audio_data = []
    n_channels = None
    sampwidth = None
    
    for segment_bytes in segments:
        with io.BytesIO(segment_bytes) as wav_in:
            with wave.open(wav_in, 'rb') as wav:
                if n_channels is None:
                    n_channels = wav.getnchannels()
                    sampwidth = wav.getsampwidth()
                
                frames = wav.readframes(wav.getnframes())
                all_audio_data.append(frames)
    
    # Concatenate all audio data
    combined_audio = b''.join(all_audio_data)
    
    # Write to output WAV
    with io.BytesIO() as wav_out:
        with wave.open(wav_out, 'wb') as wav:
            wav.setnchannels(n_channels)
            wav.setsampwidth(sampwidth)
            wav.setframerate(sample_rate)
            wav.writeframes(combined_audio)
        
        return wav_out.getvalue()


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Check SpeechLab service status and Khmer TTS engine readiness.
    
    Returns status information including:
    - Whether SpeechLab is reachable
    - Active TTS engine
    - Readiness for synthesis
    - Supported voices
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Check SpeechLab health
            health_response = await client.get(f"{SPEECHLAB_BASE_URL}/api/health")
            
            if health_response.status_code != 200:
                return StatusResponse(
                    status="error",
                    engine="unknown",
                    ready=False,
                    message=f"SpeechLab health check failed: {health_response.status_code}",
                    khmer_support=False,
                    supported_voices=[]
                )
            
            health_data = health_response.json()
            
            # Check config for engine info
            config_response = await client.get(f"{SPEECHLAB_BASE_URL}/api/config")
            config_data = config_response.json() if config_response.status_code == 200 else {}
            
            active_engine = config_data.get("active_engine", "unknown")
            model_loaded = health_data.get("model_loaded", False)
            status_value = health_data.get("status", "error")
            
            # Check if Khmer engine (nanovllm_km) is available
            engines = config_data.get("engines", [])
            khmer_engine_available = any(
                e.get("name") == "nanovllm_km" for e in engines
            )
            
            ready = (
                status_value == "ok" and
                model_loaded and
                khmer_engine_available
            )
            
            message = "SpeechLab ready for Khmer synthesis" if ready else \
                     "SpeechLab loading..." if status_value == "loading" else \
                     "Khmer engine not available"
            
            return StatusResponse(
                status=status_value,
                engine=active_engine,
                ready=ready,
                message=message,
                khmer_support=khmer_engine_available,
                supported_voices=list(VOICE_MAPPING.keys())
            )
            
    except httpx.RequestError as e:
        logger.error(f"Cannot reach SpeechLab: {e}")
        return StatusResponse(
            status="error",
            engine="unknown",
            ready=False,
            message=f"Cannot connect to SpeechLab at {SPEECHLAB_BASE_URL}: {str(e)}",
            khmer_support=False,
            supported_voices=[]
        )


@app.post("/synthesize")
async def synthesize(request: SynthesizeRequest) -> Response:
    """Synthesize Khmer text to speech using SpeechLab.
    
    Accepts KhmerDubStudio's format and translates to SpeechLab's format.
    Handles long text by splitting at sentence boundaries, synthesizes each
    segment, and joins the results.
    
    Returns:
        WAV audio at the requested sample rate
    """
    # Validate voice
    voice_config = validate_voice(request.voice)
    
    logger.info(f"Synthesis request: voice={request.voice}, text_length={len(request.text)}, sample_rate={request.sample_rate}")
    
    # Validate format
    if request.format.lower() != "wav":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format '{request.format}'. Only 'wav' is supported."
        )
    
    # Split long text into manageable chunks
    text_chunks = split_khmer_text(request.text, max_chars=500)
    
    if len(text_chunks) > 1:
        logger.info(f"Split text into {len(text_chunks)} chunks")
    
    # Synthesize each chunk
    audio_segments = []
    source_sample_rate = None
    
    for i, chunk in enumerate(text_chunks):
        logger.info(f"Synthesizing chunk {i+1}/{len(text_chunks)}: '{chunk[:30]}...'")
        
        audio_bytes, chunk_sample_rate = await synthesize_with_speechlab(chunk, voice_config)
        
        if source_sample_rate is None:
            source_sample_rate = chunk_sample_rate
        
        audio_segments.append(audio_bytes)
    
    # Join segments if multiple
    if len(audio_segments) > 1:
        combined_audio = join_audio_segments(audio_segments, source_sample_rate)
    else:
        combined_audio = audio_segments[0]
    
    # Resample if needed
    if source_sample_rate != request.sample_rate:
        combined_audio = resample_audio(combined_audio, source_sample_rate, request.sample_rate)
        final_sample_rate = request.sample_rate
    else:
        final_sample_rate = source_sample_rate
    
    logger.info(f"Synthesis complete: {len(combined_audio)} bytes at {final_sample_rate} Hz")
    
    return Response(
        content=combined_audio,
        media_type="audio/wav",
        headers={
            "Content-Type": "audio/wav",
            "X-Sample-Rate": str(final_sample_rate),
            "X-Voice": request.voice,
            "X-Chunks": str(len(text_chunks))
        }
    )


@app.get("/health")
async def health():
    """Simple health check for the adapter itself."""
    return {"status": "ok", "service": "SpeechLab Adapter", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting SpeechLab Adapter")
    logger.info(f"SpeechLab URL: {SPEECHLAB_BASE_URL}")
    logger.info(f"Listening on: {ADAPTER_HOST}:{ADAPTER_PORT}")
    logger.info(f"Supported voices: {list(VOICE_MAPPING.keys())}")
    
    uvicorn.run(
        app,
        host=ADAPTER_HOST,
        port=ADAPTER_PORT,
        log_level="info"
    )
