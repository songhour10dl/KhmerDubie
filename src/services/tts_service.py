"""Text-to-Speech service for Khmer language."""
import requests
from pathlib import Path
from typing import Optional
from ..utils.logger import setup_logger
from ..utils.config import config


logger = setup_logger(__name__)


class TTSService:
    """Text-to-Speech service adapter."""
    
    def __init__(self, provider: str = None, api_key: str = None, 
                 base_url: str = None, voice: str = None):
        self.provider = provider or config.tts_provider
        self.api_key = api_key or config.tts_api_key
        self.base_url = (base_url or config.tts_base_url).rstrip('/')
        self.voice = voice or config.tts_voice
        self.timeout = config.request_timeout
    
    def test_connection(self) -> tuple[bool, str]:
        """Test TTS provider connection and Khmer support."""
        if not self.api_key:
            return False, "API key not configured"
        
        try:
            # Test with a simple Khmer phrase
            test_text = "សួស្តី"  # Hello in Khmer
            
            if self.provider == "kiri":
                return self._test_kiri_connection(test_text)
            else:
                return False, f"Provider '{self.provider}' not implemented"
                
        except Exception as e:
            msg = f"Connection test failed: {str(e)}"
            logger.error(msg)
            return False, msg
    
    def _test_kiri_connection(self, test_text: str) -> tuple[bool, str]:
        """Test Kiri TTS API connection."""
        try:
            # This is a placeholder - actual Kiri API endpoint needs verification
            response = requests.post(
                f"{self.base_url}/tts",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "text": test_text,
                    "voice": self.voice,
                    "language": "km"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Kiri TTS connection successful")
                return True, "Connection successful - Khmer TTS available"
            else:
                msg = f"Kiri TTS returned HTTP {response.status_code}: {response.text}"
                logger.warning(msg)
                return False, msg
                
        except requests.exceptions.ConnectionError:
            msg = f"Cannot connect to Kiri TTS at {self.base_url}"
            logger.error(msg)
            return False, msg
        except Exception as e:
            msg = f"Kiri TTS test failed: {str(e)}"
            logger.error(msg)
            return False, msg
    
    def get_available_voices(self) -> list[str]:
        """Get available Khmer voices from the provider."""
        try:
            if self.provider == "kiri":
                return self._get_kiri_voices()
            else:
                logger.warning(f"Voice listing not implemented for provider: {self.provider}")
                return [self.voice]
                
        except Exception as e:
            logger.error(f"Failed to retrieve voices: {e}")
            return [self.voice]
    
    def _get_kiri_voices(self) -> list[str]:
        """Get available voices from Kiri TTS API."""
        try:
            response = requests.get(
                f"{self.base_url}/voices",
                headers={"Authorization": f"Bearer {self.api_key}"},
                params={"language": "km"},
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            voices = [v['id'] for v in data.get('voices', [])]
            logger.info(f"Retrieved {len(voices)} Khmer voices from Kiri")
            return voices if voices else [self.voice]
            
        except Exception as e:
            logger.warning(f"Failed to retrieve Kiri voices: {e}")
            return [self.voice]
    
    def synthesize(self, text: str, output_path: str, voice: str = None) -> str:
        """Synthesize Khmer text to speech audio file."""
        voice = voice or self.voice
        
        try:
            if self.provider == "kiri":
                return self._synthesize_kiri(text, output_path, voice)
            else:
                raise NotImplementedError(f"Provider '{self.provider}' not implemented")
                
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            raise RuntimeError(f"TTS synthesis failed: {e}") from e
    
    def _synthesize_kiri(self, text: str, output_path: str, voice: str) -> str:
        """Synthesize speech using Kiri TTS API."""
        try:
            logger.info(f"Synthesizing Khmer text: {text[:50]}...")
            
            # This is a placeholder implementation - actual Kiri API format needs verification
            response = requests.post(
                f"{self.base_url}/tts",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "text": text,
                    "voice": voice,
                    "language": "km",
                    "format": "wav",
                    "sample_rate": config.audio_sample_rate
                },
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            # Save audio data
            output_path = str(Path(output_path).with_suffix('.wav'))
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Audio synthesized successfully: {output_path}")
            return output_path
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Kiri TTS HTTP error: {e.response.status_code} - {e.response.text}")
            raise RuntimeError(f"Kiri TTS failed: {e.response.text}") from e
        except requests.exceptions.Timeout:
            logger.error("TTS request timeout")
            raise RuntimeError("TTS request timeout")
        except Exception as e:
            logger.error(f"Kiri TTS error: {e}")
            raise RuntimeError(f"Kiri TTS failed: {str(e)}") from e


# Note: The Kiri TTS API implementation above is a placeholder based on common TTS API patterns.
# The actual Kiri API endpoint, request format, and authentication method need to be verified
# from official Kiri TTS documentation. Users will need to configure the correct base URL,
# API key, and adjust the request/response format based on the actual API specification.
