"""OmniRoute translation service."""
import requests
from typing import List, Optional, Dict, Any
from ..utils.logger import setup_logger
from ..utils.config import config


logger = setup_logger(__name__)


class OmniRouteService:
    """OmniRoute API adapter for translation."""
    
    def __init__(self, base_url: str = None, api_key: str = None, model: str = None):
        self.base_url = (base_url or config.omniroute_base_url).rstrip('/')
        self.api_key = api_key or config.omniroute_api_key
        self.model = model or config.omniroute_model
        self.timeout = config.request_timeout
    
    def test_connection(self) -> tuple[bool, str]:
        """Test connection to OmniRoute endpoint."""
        try:
            # Try to list models or make a simple request
            response = requests.get(
                f"{self.base_url}/v1/models",
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("OmniRoute connection successful")
                return True, "Connection successful"
            else:
                msg = f"Connection failed: HTTP {response.status_code}"
                logger.warning(msg)
                return False, msg
                
        except requests.exceptions.ConnectionError:
            msg = f"Cannot connect to {self.base_url}"
            logger.error(msg)
            return False, msg
        except requests.exceptions.Timeout:
            msg = "Connection timeout"
            logger.error(msg)
            return False, msg
        except Exception as e:
            msg = f"Connection error: {str(e)}"
            logger.error(msg)
            return False, msg
    
    def get_available_models(self) -> List[str]:
        """Get list of available models from OmniRoute."""
        try:
            response = requests.get(
                f"{self.base_url}/v1/models",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            models = [model['id'] for model in data.get('data', [])]
            logger.info(f"Retrieved {len(models)} models from OmniRoute")
            return models
            
        except Exception as e:
            logger.warning(f"Failed to retrieve models: {e}")
            return []
    
    def translate(self, text: str, source_lang: str = "English", 
                  target_lang: str = "Khmer") -> str:
        """Translate text from source to target language."""
        try:
            prompt = self._build_translation_prompt(text, source_lang, target_lang)
            
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers=self._get_headers(),
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": f"You are a professional translator specializing in {source_lang} to {target_lang} translation. Provide natural, contextually appropriate translations. Preserve names and proper nouns. Only return the translated text without explanations."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2000
                },
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            translated = data['choices'][0]['message']['content'].strip()
            logger.info(f"Translated text: {text[:50]}... -> {translated[:50]}...")
            return translated
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Translation HTTP error: {e.response.status_code} - {e.response.text}")
            raise RuntimeError(f"Translation failed: {e.response.text}") from e
        except requests.exceptions.Timeout:
            logger.error("Translation request timeout")
            raise RuntimeError("Translation request timeout")
        except Exception as e:
            logger.error(f"Translation error: {e}")
            raise RuntimeError(f"Translation failed: {str(e)}") from e
    
    def translate_batch(self, texts: List[str], source_lang: str = "English",
                       target_lang: str = "Khmer") -> List[str]:
        """Translate multiple texts in batch."""
        results = []
        for text in texts:
            try:
                translated = self.translate(text, source_lang, target_lang)
                results.append(translated)
            except Exception as e:
                logger.error(f"Batch translation failed for text: {text[:50]}... - {e}")
                results.append(text)  # Fallback to original text
        return results
    
    def _build_translation_prompt(self, text: str, source_lang: str, 
                                 target_lang: str) -> str:
        """Build translation prompt."""
        return f"Translate the following {source_lang} text to {target_lang}:\n\n{text}"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with API key."""
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
