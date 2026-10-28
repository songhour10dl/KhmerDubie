"""Tests for SpeechLab adapter endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
import io
import wave
import numpy as np

from adapter import app, VOICE_MAPPING


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


@pytest.fixture
def mock_wav_audio():
    """Generate a mock WAV audio file."""
    sample_rate = 24000
    duration = 1.0  # 1 second
    frequency = 440  # A4 note
    
    # Generate sine wave
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio_data = (np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)
    
    # Write to WAV bytes
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(audio_data.tobytes())
    
    return wav_buffer.getvalue(), sample_rate


class TestStatusEndpoint:
    """Tests for GET /status endpoint."""
    
    @patch('adapter.httpx.AsyncClient')
    def test_status_success(self, mock_client_class, client):
        """Test successful status check."""
        # Mock health response
        mock_health_response = MagicMock()
        mock_health_response.status_code = 200
        mock_health_response.json.return_value = {
            "status": "ok",
            "model_loaded": True
        }
        
        # Mock config response
        mock_config_response = MagicMock()
        mock_config_response.status_code = 200
        mock_config_response.json.return_value = {
            "active_engine": "nanovllm_km",
            "engines": [
                {"name": "nanovllm_km", "display_name": "VoxCPM2 Khmer"}
            ]
        }
        
        # Setup async context manager
        mock_client = MagicMock()
        mock_client.get = AsyncMock(side_effect=[mock_health_response, mock_config_response])
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        response = client.get("/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["ready"] is True
        assert data["engine"] == "nanovllm_km"
        assert data["khmer_support"] is True
        assert "khmer-female" in data["supported_voices"]
        assert "khmer-male" in data["supported_voices"]
    
    @patch('adapter.httpx.AsyncClient')
    def test_status_speechlab_unreachable(self, mock_client_class, client):
        """Test status when SpeechLab is unreachable."""
        from httpx import RequestError
        
        mock_client = MagicMock()
        mock_client.get = AsyncMock(side_effect=RequestError("Connection refused"))
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        response = client.get("/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert data["ready"] is False
        assert "Cannot connect" in data["message"]
    
    @patch('adapter.httpx.AsyncClient')
    def test_status_loading(self, mock_client_class, client):
        """Test status when model is loading."""
        mock_health_response = MagicMock()
        mock_health_response.status_code = 200
        mock_health_response.json.return_value = {
            "status": "loading",
            "model_loaded": False
        }
        
        mock_config_response = MagicMock()
        mock_config_response.status_code = 200
        mock_config_response.json.return_value = {
            "active_engine": "nanovllm_km",
            "engines": [{"name": "nanovllm_km"}]
        }
        
        mock_client = MagicMock()
        mock_client.get = AsyncMock(side_effect=[mock_health_response, mock_config_response])
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        response = client.get("/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "loading"
        assert data["ready"] is False


class TestSynthesizeEndpoint:
    """Tests for POST /synthesize endpoint."""
    
    @patch('adapter.synthesize_with_speechlab')
    def test_synthesize_success(self, mock_synth, client, mock_wav_audio):
        """Test successful synthesis."""
        wav_bytes, sample_rate = mock_wav_audio
        mock_synth.return_value = AsyncMock(return_value=(wav_bytes, sample_rate))()
        
        response = client.post("/synthesize", json={
            "text": "សួស្តី",
            "voice": "khmer-female",
            "language": "km",
            "format": "wav",
            "sample_rate": 24000
        })
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"
        assert int(response.headers["x-sample-rate"]) == 24000
        assert len(response.content) > 0
    
    def test_synthesize_invalid_voice(self, client):
        """Test synthesis with invalid voice."""
        response = client.post("/synthesize", json={
            "text": "សួស្តី",
            "voice": "invalid-voice",
            "language": "km",
            "format": "wav",
            "sample_rate": 48000
        })
        
        assert response.status_code == 400
        assert "Unsupported voice" in response.json()["detail"]
    
    def test_synthesize_invalid_format(self, client):
        """Test synthesis with unsupported format."""
        with patch('adapter.synthesize_with_speechlab') as mock_synth:
            mock_synth.return_value = AsyncMock(return_value=(b"audio", 24000))()
            
            response = client.post("/synthesize", json={
                "text": "សួស្តី",
                "voice": "khmer-female",
                "language": "km",
                "format": "mp3",
                "sample_rate": 48000
            })
            
            assert response.status_code == 400
            assert "Unsupported format" in response.json()["detail"]
    
    def test_synthesize_empty_text(self, client):
        """Test synthesis with empty text."""
        response = client.post("/synthesize", json={
            "text": "",
            "voice": "khmer-female",
            "language": "km",
            "format": "wav",
            "sample_rate": 48000
        })
        
        assert response.status_code == 422  # Validation error
    
    @patch('adapter.synthesize_with_speechlab')
    def test_synthesize_both_voices(self, mock_synth, client, mock_wav_audio):
        """Test synthesis with both male and female voices."""
        wav_bytes, sample_rate = mock_wav_audio
        mock_synth.return_value = AsyncMock(return_value=(wav_bytes, sample_rate))()
        
        for voice in ["khmer-female", "khmer-male"]:
            response = client.post("/synthesize", json={
                "text": "សួស្តី",
                "voice": voice,
                "language": "km",
                "format": "wav",
                "sample_rate": 48000
            })
            
            assert response.status_code == 200
            assert response.headers["x-voice"] == voice


class TestVoiceMapping:
    """Tests for voice mapping functionality."""
    
    def test_voice_mapping_keys(self):
        """Test that required voices are mapped."""
        assert "khmer-female" in VOICE_MAPPING
        assert "khmer-male" in VOICE_MAPPING
    
    def test_voice_mapping_structure(self):
        """Test voice mapping structure."""
        for voice_id, config in VOICE_MAPPING.items():
            assert "voice_id" in config
            assert "style" in config
            assert "gender" in config
            assert config["gender"] in ["male", "female"]


class TestTextSplitting:
    """Tests for Khmer text splitting."""
    
    def test_split_short_text(self):
        """Test that short text is not split."""
        from adapter import split_khmer_text
        
        text = "សួស្តី"
        chunks = split_khmer_text(text, max_chars=500)
        assert len(chunks) == 1
        assert chunks[0] == text
    
    def test_split_at_sentence_boundary(self):
        """Test splitting at Khmer sentence terminator."""
        from adapter import split_khmer_text
        
        text = "សួស្តី។ អរុណសួស្តី។"
        chunks = split_khmer_text(text, max_chars=10)
        assert len(chunks) == 2
    
    def test_split_long_text(self):
        """Test splitting very long text."""
        from adapter import split_khmer_text
        
        text = "ក" * 1000  # 1000 characters
        chunks = split_khmer_text(text, max_chars=500)
        assert len(chunks) == 2


class TestAudioProcessing:
    """Tests for audio resampling and joining."""
    
    def test_resample_no_change(self, mock_wav_audio):
        """Test that resampling at same rate returns original."""
        from adapter import resample_audio
        
        wav_bytes, sample_rate = mock_wav_audio
        result = resample_audio(wav_bytes, sample_rate, sample_rate)
        assert result == wav_bytes
    
    def test_resample_to_higher_rate(self, mock_wav_audio):
        """Test resampling to higher rate."""
        from adapter import resample_audio
        
        wav_bytes, sample_rate = mock_wav_audio
        result = resample_audio(wav_bytes, sample_rate, 48000)
        
        # Verify output is valid WAV
        with io.BytesIO(result) as wav_buffer:
            with wave.open(wav_buffer, 'rb') as wav:
                assert wav.getframerate() == 48000
                assert wav.getnframes() > 0
    
    def test_join_single_segment(self, mock_wav_audio):
        """Test joining single audio segment."""
        from adapter import join_audio_segments
        
        wav_bytes, sample_rate = mock_wav_audio
        result = join_audio_segments([wav_bytes], sample_rate)
        assert result == wav_bytes
    
    def test_join_multiple_segments(self, mock_wav_audio):
        """Test joining multiple audio segments."""
        from adapter import join_audio_segments
        
        wav_bytes, sample_rate = mock_wav_audio
        result = join_audio_segments([wav_bytes, wav_bytes], sample_rate)
        
        # Verify output is valid WAV
        with io.BytesIO(result) as wav_buffer:
            with wave.open(wav_buffer, 'rb') as wav:
                assert wav.getframerate() == sample_rate
                # Should be roughly 2x length
                assert wav.getnframes() > 0


class TestHealthEndpoint:
    """Tests for GET /health endpoint."""
    
    def test_health(self, client):
        """Test adapter health check."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "SpeechLab Adapter"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
