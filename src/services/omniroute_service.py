"""Enhanced OmniRoute service with better translation prompts."""
import requests
from typing import List, Optional, Dict, Any
from ..utils.logger import setup_logger
from ..utils.config import config


logger = setup_logger(__name__)


class OmniRouteService:
    """OmniRoute API adapter for high-quality translation."""
    
    def __init__(self, base_url: str = None, api_key: str = None, model: str = None):
        self.base_url = (base_url or config.omniroute_base_url).rstrip('/')
        self.api_key = api_key or config.omniroute_api_key
        self.model = model or config.omniroute_model
        self.timeout = config.request_timeout
    
    def test_connection(self) -> tuple[bool, str]:
        """Test connection to OmniRoute endpoint."""
        try:
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
                  target_lang: str = "Khmer", context: str = None) -> str:
        """Translate text with enhanced context and quality."""
        try:
            # Enhanced system prompt for better Khmer translation
            system_prompt = f"""You are a professional translator specializing in {source_lang} to {target_lang} for video dubbing and subtitles.

Your translation must:
1. Sound natural when spoken aloud in {target_lang}
2. Match the tone and emotion of the original dialogue
3. Preserve names, places, and technical terms accurately
4. Keep the same speaking pace and length as the original
5. Use conversational {target_lang}, not formal or literary language
6. Maintain character personality and speaking style

Only return the translated text without explanations, notes, or formatting."""

            # Build enhanced user prompt
            user_prompt = self._build_enhanced_prompt(text, source_lang, target_lang, context)
            
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers=self._get_headers(),
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": user_prompt
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
            
            # Clean up common translation artifacts
            translated = self._clean_translation(translated)
            
            logger.info(f"Translated: {text[:50]}... -> {translated[:50]}...")
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
                       target_lang: str = "Khmer", contexts: List[str] = None) -> List[str]:
        """Translate multiple texts in batch with optional context for each."""
        results = []
        contexts = contexts or [None] * len(texts)
        
        for text, context in zip(texts, contexts):
            try:
                translated = self.translate(text, source_lang, target_lang, context)
                results.append(translated)
            except Exception as e:
                logger.error(f"Batch translation failed for text: {text[:50]}... - {e}")
                results.append(text)  # Fallback to original text
        
        return results
    
    def _build_enhanced_prompt(self, text: str, source_lang: str, 
                              target_lang: str, context: str = None) -> str:
        """Build enhanced translation prompt with context."""
        prompt = f"Translate this {source_lang} dialogue to natural spoken {target_lang}:\n\n\"{text}\""
        
        if context:
            prompt += f"\n\nContext: {context}"
        
        return prompt
    
    def _clean_translation(self, text: str) -> str:
        """Clean common translation artifacts."""
        # Remove quotes if AI added them
        text = text.strip()
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        if text.startswith("'") and text.endswith("'"):
            text = text[1:-1]
        
        # Remove common prefixes
        prefixes_to_remove = [
            "Translation: ",
            "Khmer: ",
            "កម្ពុជា: ",
        ]
        for prefix in prefixes_to_remove:
            if text.startswith(prefix):
                text = text[len(prefix):]
        
        return text.strip()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with API key."""
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
