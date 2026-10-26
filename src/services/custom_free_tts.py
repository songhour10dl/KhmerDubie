"""Custom FREE TTS implementation using multiple fallback providers."""
import requests
import base64
from pathlib import Path
from typing import Optional
from ..utils.logger import setup_logger
from ..utils.config import config


logger = setup_logger(__name__)


class CustomFreeTTS:
    """Custom TTS implementation with multiple free providers that work in Cambodia."""
    
    def __init__(self):
        self.timeout = 30
    
    def synthesize(self, text: str, output_path: str, voice: str = "female") -> str:
        """Synthesize speech using fallback providers."""
        
        # Try multiple providers in order
        providers = [
            self._try_responsive_voice,
            self._try_voicerss,
            self._try_ttstool
        ]
        
        for provider_func in providers:
            try:
                result = provider_func(text, output_path, voice)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"Provider {provider_func.__name__} failed: {e}")
                continue
        
        raise RuntimeError("All TTS providers failed. Please check internet connection.")
    
    def _try_responsive_voice(self, text: str, output_path: str, voice: str) -> Optional[str]:
        """Try ResponsiveVoice API (FREE, no key needed)."""
        try:
            # ResponsiveVoice supports multiple languages including Asian languages
            voice_name = "Vietnamese Male" if voice == "male" else "Vietnamese Female"
            
            url = "https://responsivevoice.org/responsivevoice/getvoice.php"
            params = {
                't': text,
                'tl': 'km',  # Khmer language
                'sv': voice_name,
                'vn': '',
                'pitch': 0.5,
                'rate': 0.5,
                'vol': 1
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            output_path = str(Path(output_path).with_suffix('.mp3'))
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            if Path(output_path).stat().st_size > 1000:
                logger.info(f"ResponsiveVoice synthesis successful: {output_path}")
                return output_path
            
            return None
            
        except Exception as e:
            logger.warning(f"ResponsiveVoice failed: {e}")
            return None
    
    def _try_voicerss(self, text: str, output_path: str, voice: str) -> Optional[str]:
        """Try VoiceRSS API (FREE tier available)."""
        try:
            # VoiceRSS free API (no key needed for basic use)
            url = "https://api.voicerss.org/"
            params = {
                'key': 'undefined',  # Free tier
                'src': text,
                'hl': 'km-KH',  # Khmer
                'v': 'Narin' if voice == "male" else 'Sothea',
                'c': 'MP3',
                'f': '44khz_16bit_stereo',
                'r': 0  # Normal speed
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200 and len(response.content) > 1000:
                output_path = str(Path(output_path).with_suffix('.mp3'))
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"VoiceRSS synthesis successful: {output_path}")
                return output_path
            
            return None
            
        except Exception as e:
            logger.warning(f"VoiceRSS failed: {e}")
            return None
    
    def _try_ttstool(self, text: str, output_path: str, voice: str) -> Optional[str]:
        """Try TTSTool.com API (FREE, no registration)."""
        try:
            url = "https://ttstool.com/api/convert"
            
            data = {
                'text': text,
                'voice': 'km-KH-Wavenet-A' if voice == "female" else 'km-KH-Wavenet-B',
                'speed': 1.0,
                'pitch': 0
            }
            
            response = requests.post(url, json=data, timeout=self.timeout)
            
            if response.status_code == 200:
                result = response.json()
                if 'audio' in result:
                    audio_data = base64.b64decode(result['audio'])
                    
                    output_path = str(Path(output_path).with_suffix('.mp3'))
                    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(output_path, 'wb') as f:
                        f.write(audio_data)
                    
                    logger.info(f"TTSTool synthesis successful: {output_path}")
                    return output_path
            
            return None
            
        except Exception as e:
            logger.warning(f"TTSTool failed: {e}")
            return None
