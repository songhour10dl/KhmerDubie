"""Speech-to-Text service using Whisper."""
import whisper
from pathlib import Path
from typing import List, Optional
from ..utils.logger import setup_logger
from ..utils.config import config
from ..models.dialogue_segment import DialogueSegment


logger = setup_logger(__name__)


class STTService:
    """Speech-to-Text service using OpenAI Whisper."""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or config.stt_model
        self.model = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load Whisper model."""
        try:
            logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise RuntimeError(f"Failed to load Whisper model: {e}") from e
    
    def transcribe(self, audio_path: str, language: str = "en") -> List[DialogueSegment]:
        """Transcribe audio file and return dialogue segments with timestamps."""
        try:
            logger.info(f"Transcribing audio: {audio_path}")
            
            result = self.model.transcribe(
                audio_path,
                language=language,
                task="transcribe",
                word_timestamps=False,
                verbose=False
            )
            
            segments = []
            for seg in result['segments']:
                dialogue_seg = DialogueSegment(
                    start_time=seg['start'],
                    end_time=seg['end'],
                    english_text=seg['text'].strip()
                )
                segments.append(dialogue_seg)
            
            logger.info(f"Transcribed {len(segments)} segments")
            return segments
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise RuntimeError(f"Transcription failed: {e}") from e
    
    def transcribe_segment(self, audio_path: str, start_time: float, 
                          end_time: float, language: str = "en") -> str:
        """Transcribe a specific time segment of audio."""
        try:
            # For now, transcribe the whole file and extract the relevant segment
            # A more efficient implementation would extract the audio segment first
            result = self.model.transcribe(
                audio_path,
                language=language,
                task="transcribe",
                verbose=False
            )
            
            # Find segments that overlap with the requested time range
            text_parts = []
            for seg in result['segments']:
                if seg['start'] >= start_time and seg['end'] <= end_time:
                    text_parts.append(seg['text'].strip())
            
            return ' '.join(text_parts)
            
        except Exception as e:
            logger.error(f"Segment transcription failed: {e}")
            raise RuntimeError(f"Segment transcription failed: {e}") from e
