"""Enhanced TTS service with multiple professional provider options."""
import requests
from pathlib import Path
from typing import Optional, List
import subprocess
import tempfile
from ..utils.logger import setup_logger
from ..utils.config import config


logger = setup_logger(__name__)


class TTSService:
    """Text-to-Speech service adapter with multiple provider support."""
    
    SUPPORTED_PROVIDERS = ['custom', 'elevenlabs', 'kiri', 'google', 'edge', 'gtts', 'local', 'speechlab']
    
    def __init__(self, provider: str = None, api_key: str = None, 
                 base_url: str = None, voice: str = None):
        self.provider = provider or config.tts_provider
        self.api_key = api_key or config.tts_api_key
        self.base_url = (base_url or config.tts_base_url).rstrip('/')
        self.voice = voice or config.tts_voice
        self.timeout = config.request_timeout
    
    def test_connection(self) -> tuple[bool, str]:
        """Test TTS provider connection and Khmer support."""
        test_text = "សួស្តី"  # Hello in Khmer
        
        try:
            if self.provider == "custom":
                return self._test_custom_connection(test_text)
            elif self.provider == "elevenlabs":
                return self._test_elevenlabs_connection(test_text)
            elif self.provider == "kiri":
                return self._test_kiri_connection(test_text)
            elif self.provider == "google":
                return self._test_google_connection(test_text)
            elif self.provider == "edge":
                return self._test_edge_connection(test_text)
            elif self.provider == "gtts":
                return self._test_gtts_connection(test_text)
            elif self.provider == "local":
                return self._test_local_connection(test_text)
            elif self.provider == "speechlab":
                return self._test_speechlab_connection(test_text)
            else:
                return False, f"Unknown provider: {self.provider}"
                
        except Exception as e:
            msg = f"Connection test failed: {str(e)}"
            logger.error(msg)
            return False, msg
    
    def get_available_voices(self) -> list[str]:
        """Get available Khmer voices from the provider."""
        try:
            if self.provider == "elevenlabs":
                return self._get_elevenlabs_voices()
            elif self.provider == "edge":
                return self._get_edge_voices()
            elif self.provider == "google":
                return ["km-KH-Standard-A", "km-KH-Standard-B", "km-KH-Standard-C", "km-KH-Standard-D"]
            elif self.provider == "gtts":
                return ["km"]
            elif self.provider == "local":
                return ["espeak-km"]
            elif self.provider == "speechlab":
                return self._get_speechlab_voices()
            else:
                return [self.voice]
                
        except Exception as e:
            logger.error(f"Failed to retrieve voices: {e}")
            return [self.voice]
    
    def synthesize(self, text: str, output_path: str, voice: str = None) -> str:
        """Synthesize Khmer text to speech audio file."""
        voice = voice or self.voice
        
        try:
            logger.info(f"Synthesizing with {self.provider}: {text[:50]}...")
            
            if self.provider == "custom":
                return self._synthesize_custom(text, output_path, voice)
            elif self.provider == "elevenlabs":
                return self._synthesize_elevenlabs(text, output_path, voice)
            elif self.provider == "kiri":
                return self._synthesize_kiri(text, output_path, voice)
            elif self.provider == "google":
                return self._synthesize_google(text, output_path, voice)
            elif self.provider == "edge":
                return self._synthesize_edge(text, output_path, voice)
            elif self.provider == "gtts":
                return self._synthesize_gtts(text, output_path)
            elif self.provider == "local":
                return self._synthesize_local(text, output_path)
            elif self.provider == "speechlab":
                return self._synthesize_speechlab(text, output_path, voice)
            else:
                raise NotImplementedError(f"Provider '{self.provider}' not implemented")
                
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            raise RuntimeError(f"TTS synthesis failed: {e}") from e
    
    # ==================== ElevenLabs ====================
    
    def _get_elevenlabs_voices(self) -> list[str]:
        """Get available voices from ElevenLabs."""
        try:
            from elevenlabs import voices
            voice_list = voices()
            return [v.name for v in voice_list]
        except Exception as e:
            logger.warning(f"Could not fetch ElevenLabs voices: {e}")
            return ["default"]
    
    def _test_elevenlabs_connection(self, test_text: str) -> tuple[bool, str]:
        """Test ElevenLabs connection."""
        try:
            from elevenlabs import generate, set_api_key
            
            if self.api_key:
                set_api_key(self.api_key)
            
            # Determine male/female from voice name
            voice_type = "male" if "male" in voice.lower() or "piseth" in voice.lower() else "female"
            
            # Use multilingual model for Khmer
            audio = generate(
                text=test_text,
                model="eleven_multilingual_v2"
            )
            
            return True, f"ElevenLabs multilingual model ready (supports Khmer)"
            
        except ImportError:
            return False, "elevenlabs package not installed. Install with: pip install elevenlabs"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    
    def _synthesize_elevenlabs(self, text: str, output_path: str, voice: str) -> str:
        """Synthesize using ElevenLabs API."""
        try:
            from elevenlabs import generate, set_api_key
            
            if self.api_key:
                set_api_key(self.api_key)
            
            # Use multilingual model for Khmer
            audio = generate(
                text=text,
                voice=voice or "default",
                model="eleven_multilingual_v2"
            )
            
            output_path = str(Path(output_path).with_suffix('.mp3'))
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(audio)
            
            logger.info(f"ElevenLabs audio synthesized successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"ElevenLabs TTS error: {e}")
            raise RuntimeError(f"ElevenLabs TTS failed: {str(e)}") from e
    
    # ==================== Microsoft Edge TTS ====================
    
    def _get_edge_voices(self) -> list[str]:
        """Get Khmer voices from Edge TTS."""
        return ["km-KH-SreymomNeural", "km-KH-PisethNeural"]
    
    def _test_edge_connection(self, test_text: str) -> tuple[bool, str]:
        """Test Edge TTS connection."""
        try:
            import edge_tts
            return True, "Edge TTS available (free Khmer voices: Sreymom, Piseth)"
        except ImportError:
            return False, "edge-tts package not installed. Install with: pip install edge-tts"
    
    def _synthesize_edge(self, text: str, output_path: str, voice: str = None) -> str:
        """Synthesize using Microsoft Edge TTS (free, high quality)."""
        try:
            import edge_tts
            import asyncio
            
            voice = voice or "km-KH-SreymomNeural"
            output_path = str(Path(output_path).with_suffix('.mp3'))
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            async def _generate():
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(output_path)
            
            # Run async function
            asyncio.run(_generate())
            
            logger.info(f"Edge TTS audio synthesized successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Edge TTS error: {e}")
            raise RuntimeError(f"Edge TTS failed: {str(e)}") from e
    
    # ==================== gTTS (Google Text-to-Speech) ====================
    
    def _test_gtts_connection(self, test_text: str) -> tuple[bool, str]:
        """Test gTTS connection."""
        try:
            from gtts import gTTS
            return True, "gTTS available (free Google TTS for Khmer)"
        except ImportError:
            return False, "gtts package not installed. Install with: pip install gtts"
    
    def _synthesize_gtts(self, text: str, output_path: str) -> str:
        """Synthesize using Google Text-to-Speech (free, basic)."""
        try:
            from gtts import gTTS
            
            output_path = str(Path(output_path).with_suffix('.mp3'))
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            tts = gTTS(text=text, lang='km', slow=False)
            tts.save(output_path)
            
            logger.info(f"gTTS audio synthesized successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"gTTS error: {e}")
            raise RuntimeError(f"gTTS failed: {str(e)}") from e
    
    # ==================== Google Cloud TTS ====================
    
    def _test_google_connection(self, test_text: str) -> tuple[bool, str]:
        """Test Google Cloud TTS connection."""
        try:
            from google.cloud import texttospeech
            client = texttospeech.TextToSpeechClient()
            return True, "Google Cloud TTS connected (requires API key)"
        except ImportError:
            return False, "google-cloud-texttospeech package not installed"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    
    def _synthesize_google(self, text: str, output_path: str, voice: str) -> str:
        """Synthesize using Google Cloud TTS."""
        try:
            from google.cloud import texttospeech
            
            client = texttospeech.TextToSpeechClient()
            
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            voice_params = texttospeech.VoiceSelectionParams(
                language_code="km-KH",
                name=voice or "km-KH-Standard-A"
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                sample_rate_hertz=config.audio_sample_rate
            )
            
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice_params,
                audio_config=audio_config
            )
            
            output_path = str(Path(output_path).with_suffix('.wav'))
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(response.audio_content)
            
            logger.info(f"Google Cloud TTS audio synthesized: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Google Cloud TTS error: {e}")
            raise RuntimeError(f"Google Cloud TTS failed: {str(e)}") from e
    
    # ==================== Local eSpeak-ng ====================
    
    def _test_local_connection(self, test_text: str) -> tuple[bool, str]:
        """Test local eSpeak-ng installation."""
        try:
            result = subprocess.run(
                ['espeak-ng', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True, "eSpeak-ng available (free, offline Khmer TTS)"
            else:
                return False, "eSpeak-ng not working properly"
        except FileNotFoundError:
            return False, "eSpeak-ng not installed. Download from: https://github.com/espeak-ng/espeak-ng/releases"
        except Exception as e:
            return False, f"eSpeak-ng test failed: {str(e)}"
    
    def _synthesize_local(self, text: str, output_path: str) -> str:
        """Synthesize using local eSpeak-ng (offline, free)."""
        try:
            output_path = str(Path(output_path).with_suffix('.wav'))
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            subprocess.run(
                [
                    'espeak-ng',
                    '-v', 'km',  # Khmer voice
                    '-w', output_path,
                    text
                ],
                check=True,
                capture_output=True,
                timeout=30
            )
            
            logger.info(f"eSpeak-ng audio synthesized successfully: {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"eSpeak-ng failed: {e.stderr}")
            raise RuntimeError(f"eSpeak-ng failed: {e.stderr}") from e
        except Exception as e:
            logger.error(f"eSpeak-ng error: {e}")
            raise RuntimeError(f"eSpeak-ng failed: {str(e)}") from e
    
    # ==================== Custom API ====================
    
    def _test_custom_connection(self, test_text: str) -> tuple[bool, str]:
        """Test custom TTS API connection."""
        if not self.base_url:
            return False, "No base URL configured for custom provider"
        
        try:
            # Try to reach the API
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5
            )
            if response.status_code == 200:
                return True, f"Custom TTS API connected at {self.base_url}"
            else:
                return False, f"API returned status {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, f"Could not connect to {self.base_url}"
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"
    
    def _synthesize_custom(self, text: str, output_path: str, voice: str) -> str:
        """Synthesize using custom TTS API."""
        try:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            response = requests.post(
                f"{self.base_url}/synthesize",
                headers=headers,
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
            
            output_path = str(Path(output_path).with_suffix('.wav'))
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Custom TTS audio synthesized successfully: {output_path}")
            return output_path
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Custom TTS HTTP error: {e.response.status_code}")
            raise RuntimeError(f"Custom TTS failed: {e.response.text}") from e
        except Exception as e:
            logger.error(f"Custom TTS error: {e}")
            raise RuntimeError(f"Custom TTS failed: {str(e)}") from e
    
    # ==================== Kiri TTS ====================
    
    def _test_kiri_connection(self, test_text: str) -> tuple[bool, str]:
        """Test Kiri TTS API connection."""
        if not self.base_url:
            return False, "No base URL configured for Kiri provider"
        
        if not self.api_key:
            return False, "No API key configured for Kiri provider"
        
        try:
            response = requests.get(
                f"{self.base_url}/voices",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=5
            )
            if response.status_code == 200:
                return True, f"Kiri TTS API connected"
            else:
                return False, f"API returned status {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, f"Could not connect to {self.base_url}"
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"
    
    def _synthesize_kiri(self, text: str, output_path: str, voice: str) -> str:
        """Synthesize using Kiri TTS API."""
        try:
            if not self.base_url:
                raise ValueError("Kiri base URL not configured")
            
            if not self.api_key:
                raise ValueError("Kiri API key not configured")
            
            response = requests.post(
                f"{self.base_url}/synthesize",
                headers={"Authorization": f"Bearer {self.api_key}"},
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
            
            output_path = str(Path(output_path).with_suffix('.wav'))
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Kiri audio synthesized successfully: {output_path}")
            return output_path
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Kiri TTS HTTP error: {e.response.status_code} - {e.response.text}")
            raise RuntimeError(f"Kiri TTS failed: {e.response.text}") from e
        except requests.exceptions.Timeout:
            logger.error("Kiri TTS request timeout")
            raise RuntimeError("Kiri TTS request timeout")
        except Exception as e:
            logger.error(f"Kiri TTS error: {e}")
            raise RuntimeError(f"Kiri TTS failed: {str(e)}") from e
    
    # ==================== SpeechLab ====================
    
    def _get_speechlab_voices(self) -> list[str]:
        """Get available Khmer voices from SpeechLab."""
        # TODO: Update with actual SpeechLab voices once API documentation is available
        return ["khmer-male", "khmer-female"]
    
    def _test_speechlab_connection(self, test_text: str) -> tuple[bool, str]:
        """Test SpeechLab TTS API connection."""
        if not self.base_url:
            return False, "No base URL configured for SpeechLab provider. Set TTS_BASE_URL in .env"
        
        try:
            # Try to reach the API health/status endpoint
            # TODO: Update with actual SpeechLab endpoint once API documentation is available
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            response = requests.get(
                f"{self.base_url}/status",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                return True, f"SpeechLab TTS API connected"
            else:
                return False, f"SpeechLab API returned status {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return False, f"Could not connect to SpeechLab at {self.base_url}"
        except Exception as e:
            return False, f"SpeechLab connection test failed: {str(e)}"
    
    def _synthesize_speechlab(self, text: str, output_path: str, voice: str) -> str:
        """Synthesize using SpeechLab TTS API.
        
        NOTE: This is a template implementation. Update the endpoint and payload
        based on actual SpeechLab API documentation.
        """
        try:
            if not self.base_url:
                raise ValueError("SpeechLab base URL not configured. Set TTS_BASE_URL in .env")
            
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            # TODO: Update payload structure based on actual SpeechLab API
            payload = {
                "text": text,
                "voice": voice or "khmer-female",
                "language": "km",
                "format": "wav",
                "sample_rate": config.audio_sample_rate
            }
            
            response = requests.post(
                f"{self.base_url}/synthesize",  # TODO: Update with actual endpoint
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            output_path = str(Path(output_path).with_suffix('.wav'))
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save audio content
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"SpeechLab audio synthesized successfully: {output_path}")
            return output_path
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"SpeechLab TTS HTTP error: {e.response.status_code} - {e.response.text}")
            raise RuntimeError(f"SpeechLab TTS failed: {e.response.text}") from e
        except requests.exceptions.Timeout:
            logger.error("SpeechLab TTS request timeout")
            raise RuntimeError("SpeechLab TTS request timeout")
        except Exception as e:
            logger.error(f"SpeechLab TTS error: {e}")
            raise RuntimeError(f"SpeechLab TTS failed: {str(e)}") from e
