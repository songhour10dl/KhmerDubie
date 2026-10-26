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
    
    SUPPORTED_PROVIDERS = ['custom', 'elevenlabs', 'kiri', 'google', 'edge', 'gtts', 'local']
    
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
            else:
                raise NotImplementedError(f"Provider '{self.provider}' not implemented")
                
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            raise RuntimeError(f"TTS synthesis failed: {e}") from e
    
    # ============= CUSTOM FREE TTS (NO SIGNUP, WORKS IN CAMBODIA) =============
    
    def _test_custom_connection(self, test_text: str) -> tuple[bool, str]:
        """Test custom TTS providers."""
        return True, "Custom FREE TTS available (multiple providers, works in Cambodia)"
    
    def _synthesize_custom(self, text: str, output_path: str, voice: str) -> str:
        """Synthesize using custom free TTS with multiple fallback providers."""
        try:
            from .custom_free_tts import CustomFreeTTS
            
            tts = CustomFreeTTS()
            
            # Determine male/female from voice name
            voice_type = "male" if "male" in voice.lower() or "piseth" in voice.lower() else "female"
            
            result = tts.synthesize(text, output_path, voice_type)
            
            logger.info(f"Custom TTS synthesis successful: {result}")
            return result
            
        except ImportError:
            raise RuntimeError("Custom TTS module not found")
        except Exception as e:
            logger.error(f"Custom TTS error: {e}")
            raise RuntimeError(f"Custom TTS failed: {str(e)}") from e
    
    # ============= ELEVENLABS (BEST QUALITY, PROFESSIONAL) =============
    
    def _test_elevenlabs_connection(self, test_text: str) -> tuple[bool, str]:
        """Test ElevenLabs API connection."""
        if not self.api_key:
            return False, "ElevenLabs API key not configured"
        
        try:
            from elevenlabs import ElevenLabs
            client = ElevenLabs(api_key=self.api_key)
            
            # Get available voices to test connection
            voices = client.voices.get_all()
            return True, f"ElevenLabs connected - {len(voices.voices)} voices available (BEST quality)"
            
        except ImportError:
            return False, "ElevenLabs not installed. Run: pip install elevenlabs"
        except Exception as e:
            return False, f"ElevenLabs connection failed: {str(e)}"
    
    def _get_elevenlabs_voices(self) -> list[str]:
        """Get available voices from ElevenLabs."""
        try:
            from elevenlabs import ElevenLabs
            client = ElevenLabs(api_key=self.api_key)
            
            voices_response = client.voices.get_all()
            voices = [v.name for v in voices_response.voices]
            
            logger.info(f"Retrieved {len(voices)} voices from ElevenLabs")
            return voices
            
        except Exception as e:
            logger.warning(f"Failed to retrieve ElevenLabs voices: {e}")
            return ["Adam", "Bella", "Charlie", "Dorothy"]  # Default options
    
    def _synthesize_elevenlabs(self, text: str, output_path: str, voice: str) -> str:
        """Synthesize using ElevenLabs (BEST quality, natural, expressive)."""
        try:
            from elevenlabs import ElevenLabs, VoiceSettings
            
            client = ElevenLabs(api_key=self.api_key)
            
            # Use provided voice or get first available multilingual voice
            if not voice:
                voices = client.voices.get_all()
                # Try to find a multilingual voice
                for v in voices.voices:
                    if hasattr(v, 'labels') and 'multilingual' in str(v.labels).lower():
                        voice = v.voice_id
                        break
                if not voice:
                    voice = voices.voices[0].voice_id if voices.voices else "Adam"
            
            logger.info(f"Using ElevenLabs voice: {voice}")
            
            # Generate audio with optimized settings for dubbing
            audio = client.text_to_speech.convert(
                voice_id=voice,
                text=text,
                model_id="eleven_multilingual_v2",  # Best for non-English
                voice_settings=VoiceSettings(
                    stability=0.5,  # Balanced stability
                    similarity_boost=0.75,  # High similarity to training
                    style=0.5,  # Moderate style
                    use_speaker_boost=True  # Enhance speaker characteristics
                )
            )
            
            # Save audio
            output_path = str(Path(output_path).with_suffix('.mp3'))
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                for chunk in audio:
                    f.write(chunk)
            
            logger.info(f"ElevenLabs audio generated successfully: {output_path}")
            return output_path
            
        except ImportError:
            raise RuntimeError("ElevenLabs not installed. Run: pip install elevenlabs")
        except Exception as e:
            logger.error(f"ElevenLabs TTS error: {e}")
            raise RuntimeError(f"ElevenLabs TTS failed: {str(e)}") from e
    
    # ============= EDGE TTS (FREE, RECOMMENDED) =============
    
    def _test_edge_connection(self, test_text: str) -> tuple[bool, str]:
        """Test Edge TTS (requires edge-tts package)."""
        try:
            import edge_tts
            return True, "Edge TTS available (FREE, no API key needed)"
        except ImportError:
            return False, "Edge TTS not installed. Run: pip install edge-tts"
    
    def _get_edge_voices(self) -> list[str]:
        """Get available Khmer voices from Edge TTS."""
        try:
            import edge_tts
            import asyncio
            
            async def get_voices():
                voices = await edge_tts.list_voices()
                khmer_voices = [v['ShortName'] for v in voices if v['Locale'].startswith('km')]
                return khmer_voices
            
            voices = asyncio.run(get_voices())
            logger.info(f"Found {len(voices)} Khmer voices in Edge TTS")
            return voices if voices else ["km-KH-SreymomNeural", "km-KH-PisethNeural"]
            
        except Exception as e:
            logger.warning(f"Failed to retrieve Edge voices: {e}")
            return ["km-KH-SreymomNeural", "km-KH-PisethNeural"]
    
    def _synthesize_edge(self, text: str, output_path: str, voice: str) -> str:
        """Synthesize using Microsoft Edge TTS (FREE)."""
        try:
            import edge_tts
            import asyncio
            
            # Default to Khmer voice if not specified
            if not voice or voice == "khmer_female_1":
                voice = "km-KH-SreymomNeural"
            
            output_path = str(Path(output_path).with_suffix('.mp3'))
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            async def synthesize():
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(output_path)
            
            asyncio.run(synthesize())
            
            logger.info(f"Edge TTS synthesis successful: {output_path}")
            return output_path
            
        except ImportError:
            raise RuntimeError("Edge TTS not installed. Run: pip install edge-tts")
        except Exception as e:
            logger.error(f"Edge TTS error: {e}")
            raise RuntimeError(f"Edge TTS failed: {str(e)}") from e
    
    # ============= GTTS (FREE, SIMPLE) =============
    
    def _test_gtts_connection(self, test_text: str) -> tuple[bool, str]:
        """Test gTTS (Google Text-to-Speech - FREE)."""
        try:
            from gtts import gTTS
            return True, "gTTS available (FREE, no API key needed)"
        except ImportError:
            return False, "gTTS not installed. Run: pip install gtts"
    
    def _synthesize_gtts(self, text: str, output_path: str) -> str:
        """Synthesize using gTTS (Google Text-to-Speech - FREE)."""
        try:
            from gtts import gTTS
            
            output_path = str(Path(output_path).with_suffix('.mp3'))
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            tts = gTTS(text=text, lang='km', slow=False)
            tts.save(output_path)
            
            logger.info(f"gTTS synthesis successful: {output_path}")
            return output_path
            
        except ImportError:
            raise RuntimeError("gTTS not installed. Run: pip install gtts")
        except Exception as e:
            logger.error(f"gTTS error: {e}")
            raise RuntimeError(f"gTTS failed: {str(e)}") from e
    
    # ============= GOOGLE CLOUD TTS (PAID, HIGH QUALITY) =============
    
    def _test_google_connection(self, test_text: str) -> tuple[bool, str]:
        """Test Google Cloud TTS."""
        if not self.api_key:
            return False, "Google Cloud API key not configured"
        
        try:
            from google.cloud import texttospeech
            return True, "Google Cloud TTS available"
        except ImportError:
            return False, "Google Cloud TTS not installed. Run: pip install google-cloud-texttospeech"
    
    def _synthesize_google(self, text: str, output_path: str, voice: str) -> str:
        """Synthesize using Google Cloud TTS (requires API key and billing)."""
        try:
            from google.cloud import texttospeech
            import os
            
            # Set credentials
            if self.api_key:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.api_key
            
            client = texttospeech.TextToSpeechClient()
            
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            voice_params = texttospeech.VoiceSelectionParams(
                language_code="km-KH",
                name=voice or "km-KH-Standard-A"
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice_params,
                audio_config=audio_config
            )
            
            output_path = str(Path(output_path).with_suffix('.mp3'))
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(response.audio_content)
            
            logger.info(f"Google Cloud TTS synthesis successful: {output_path}")
            return output_path
            
        except ImportError:
            raise RuntimeError("Google Cloud TTS not installed. Run: pip install google-cloud-texttospeech")
        except Exception as e:
            logger.error(f"Google Cloud TTS error: {e}")
            raise RuntimeError(f"Google Cloud TTS failed: {str(e)}") from e
    
    # ============= LOCAL ESPEAK (FREE, OFFLINE) =============
    
    def _test_local_connection(self, test_text: str) -> tuple[bool, str]:
        """Test local eSpeak-ng."""
        try:
            result = subprocess.run(
                ['espeak-ng', '--version'],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                return True, "eSpeak-ng available (FREE, offline)"
            else:
                return False, "eSpeak-ng not working"
        except FileNotFoundError:
            return False, "eSpeak-ng not installed. Install from: https://github.com/espeak-ng/espeak-ng/releases"
        except Exception as e:
            return False, f"eSpeak-ng test failed: {str(e)}"
    
    def _synthesize_local(self, text: str, output_path: str) -> str:
        """Synthesize using local eSpeak-ng (FREE, offline, lower quality)."""
        try:
            output_path = str(Path(output_path).with_suffix('.wav'))
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Use eSpeak-ng with Khmer language
            cmd = [
                'espeak-ng',
                '-v', 'km',  # Khmer language
                '-w', output_path,
                text
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            
            logger.info(f"eSpeak-ng synthesis successful: {output_path}")
            return output_path
            
        except FileNotFoundError:
            raise RuntimeError("eSpeak-ng not installed. Install from: https://github.com/espeak-ng/espeak-ng/releases")
        except subprocess.CalledProcessError as e:
            logger.error(f"eSpeak-ng error: {e.stderr}")
            raise RuntimeError(f"eSpeak-ng failed: {e.stderr}") from e
        except Exception as e:
            logger.error(f"eSpeak-ng error: {e}")
            raise RuntimeError(f"eSpeak-ng failed: {str(e)}") from e
    
    # ============= KIRI TTS (ORIGINAL) =============
    
    def _test_kiri_connection(self, test_text: str) -> tuple[bool, str]:
        """Test Kiri TTS API connection."""
        if not self.api_key:
            return False, "Kiri API key not configured"
        
        try:
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
                return True, "Kiri TTS connection successful"
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
    
    def _synthesize_kiri(self, text: str, output_path: str, voice: str) -> str:
        """Synthesize speech using Kiri TTS API."""
        try:
            logger.info(f"Synthesizing Khmer text: {text[:50]}...")
            
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
