"""NLLB-200 Translation Service for English to Khmer.

NLLB-200 (No Language Left Behind) by Meta AI is specifically designed 
for low-resource languages like Khmer, providing high-quality translations.

This can run locally (free, no API) or via Hugging Face API (free tier available).
"""
import requests
import torch
from typing import Optional
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class NLLBTranslationService:
    """NLLB-200 translation service via Hugging Face API (free tier)."""
    
    def __init__(self, api_key: Optional[str] = None, use_local: bool = False):
        """Initialize NLLB translation service.
        
        Args:
            api_key: Optional Hugging Face API key (free tier available)
            use_local: If True, use local model (requires transformers installed)
        """
        self.api_key = api_key
        self.use_local = use_local
        self.timeout = 60  # NLLB can be slower than simple APIs
        
        # NLLB language codes
        self.lang_codes = {
            'en': 'eng_Latn',  # English
            'km': 'khm_Khmr'   # Khmer
        }
        
        # Hugging Face API endpoint
        self.api_url = "https://api-inference.huggingface.co/models/facebook/nllb-200-distilled-600M"
        
        if use_local:
            self._init_local_model()
    
    def _init_local_model(self):
        """Initialize local NLLB model (requires transformers library)."""
        try:
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
            
            logger.info("Loading NLLB-200 local model (this may take a moment)...")
            model_name = "facebook/nllb-200-distilled-600M"
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            
            logger.info("NLLB-200 local model loaded successfully")
        except ImportError:
            logger.error("transformers library not installed. Install with: pip install transformers torch")
            raise RuntimeError(
                "Local NLLB requires transformers library. "
                "Install with: pip install transformers torch"
            )
        except Exception as e:
            logger.error(f"Failed to load local NLLB model: {e}")
            raise
    
    def test_connection(self) -> tuple[bool, str]:
        """Test connection to NLLB service."""
        try:
            # Test the actual mode being used (local or API)
            if self.use_local:
                # Test local model
                result = self._translate_local("Hello", 'en', 'km')
            else:
                # Test API
                result = self._translate_api("Hello", 'en', 'km')
            
            if result:
                mode = "local model" if self.use_local else "Hugging Face API"
                logger.info(f"NLLB-200 connection successful ({mode})")
                return True, f"Connection successful via {mode}"
            else:
                return False, "Translation returned empty result"
        except Exception as e:
            mode = "local model" if self.use_local else "Hugging Face API"
            msg = f"Connection failed: {str(e)}"
            logger.error(f"NLLB-200 test failed ({mode}): {msg}")
            return False, f"{mode} failed: {msg}"
    
    def translate(self, text: str, source_lang: str = 'en', target_lang: str = 'km') -> str:
        """Translate using NLLB-200.
        
        Args:
            text: Text to translate
            source_lang: Source language code (en)
            target_lang: Target language code (km)
            
        Returns:
            Translated text
        """
        if self.use_local:
            return self._translate_local(text, source_lang, target_lang)
        else:
            return self._translate_api(text, source_lang, target_lang)
    
    def _translate_local(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate using local NLLB model."""
        try:
            # Get NLLB language codes
            src_code = self.lang_codes.get(source_lang, 'eng_Latn')
            tgt_code = self.lang_codes.get(target_lang, 'khm_Khmr')
            
            # Tokenize with source language
            self.tokenizer.src_lang = src_code
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            )
            
            # Generate translation with target language
            # Use convert_tokens_to_ids instead of lang_code_to_id
            forced_bos_token_id = self.tokenizer.convert_tokens_to_ids(tgt_code)
            
            generated_tokens = self.model.generate(
                **inputs,
                forced_bos_token_id=forced_bos_token_id,
                max_length=512,
                num_beams=5,
                early_stopping=True
            )
            
            # Decode
            translation = self.tokenizer.batch_decode(
                generated_tokens,
                skip_special_tokens=True
            )[0]
            
            logger.info(f"NLLB Local: '{text[:50]}...' -> '{translation[:50]}...'")
            return translation
            
        except Exception as e:
            logger.error(f"NLLB local translation error: {e}")
            raise
    
    def _translate_api(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate using Hugging Face API."""
        try:
            # Get NLLB language codes
            src_code = self.lang_codes.get(source_lang, 'eng_Latn')
            tgt_code = self.lang_codes.get(target_lang, 'khm_Khmr')
            
            # Prepare payload
            payload = {
                "inputs": text,
                "parameters": {
                    "src_lang": src_code,
                    "tgt_lang": tgt_code
                }
            }
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json"
            }
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            # Make request
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            # Handle rate limiting
            if response.status_code == 503:
                # Model is loading, retry after a moment
                import time
                logger.info("NLLB model is loading, waiting 20 seconds...")
                time.sleep(20)
                response = requests.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract translation
            if isinstance(result, list) and len(result) > 0:
                translation = result[0].get('translation_text', '')
            else:
                translation = result.get('translation_text', '')
            
            logger.info(f"NLLB API: '{text[:50]}...' -> '{translation[:50]}...'")
            return translation
            
        except requests.exceptions.Timeout:
            logger.error("NLLB API timeout")
            raise RuntimeError("NLLB API request timeout")
        except requests.exceptions.HTTPError as e:
            logger.error(f"NLLB API HTTP error: {e.response.status_code}")
            raise RuntimeError(f"NLLB API failed: {e.response.text}")
        except Exception as e:
            logger.error(f"NLLB API error: {e}")
            raise RuntimeError(f"NLLB translation failed: {str(e)}")


class NLLBHybridService:
    """Hybrid service using manual translations + NLLB fallback."""
    
    def __init__(self, manual_dict_path: str = None, use_local_nllb: bool = False):
        """Initialize hybrid NLLB service.
        
        Args:
            manual_dict_path: Path to manual translations JSON
            use_local_nllb: Use local NLLB model instead of API
        """
        from .alternative_translation import ManualTranslationService
        
        self.manual = ManualTranslationService()
        self.nllb = NLLBTranslationService(use_local=use_local_nllb)
        
        if manual_dict_path:
            try:
                self.manual.load_from_file(manual_dict_path)
                logger.info(f"Loaded manual translations from {manual_dict_path}")
            except Exception as e:
                logger.warning(f"Could not load manual translations: {e}")
    
    def translate(self, text: str) -> str:
        """Translate using manual dictionary first, fall back to NLLB."""
        # Try manual translation first
        if self.manual.has_translation(text):
            translation = self.manual.translate(text)
            logger.info(f"Manual translation found: '{text[:50]}...'")
            return translation
        
        # Fall back to NLLB
        logger.info(f"Using NLLB for: '{text[:50]}...'")
        return self.nllb.translate(text, 'en', 'km')
    
    def test_connection(self) -> tuple[bool, str]:
        """Test if NLLB service is available."""
        return self.nllb.test_connection()
    
    def get_manual_translation_count(self) -> int:
        """Get number of manual translations loaded."""
        return len(self.manual.manual_translations)
    
    def add_manual_translation(self, english_text: str, khmer_text: str):
        """Add a manual translation."""
        self.manual.add_translation(english_text, khmer_text)
    
    def save_manual_translations(self, filepath: str):
        """Save manual translations to file."""
        self.manual.save_to_file(filepath)
