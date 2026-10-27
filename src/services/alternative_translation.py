"""Alternative translation services for English to Khmer when OmniRoute is unstable."""
import requests
from typing import Optional
from ..utils.logger import setup_logger


logger = setup_logger(__name__)


class GoogleTranslateService:
    """Google Translate API (Free tier available)."""
    
    def __init__(self):
        self.timeout = 30
    
    def translate(self, text: str, source_lang: str = 'en', target_lang: str = 'km') -> str:
        """Translate using Google Translate (free, no API key needed)."""
        try:
            url = f"https://translate.googleapis.com/translate_a/element.js?cb=GoogleTranslateElementInit"
            
            # Using the free Google Translate endpoint
            data = {
                'client': 'gtx',
                'sl': source_lang,
                'tl': target_lang,
                'dt': 't',
                'q': text
            }
            
            response = requests.get(
                "https://translate.google.com/translate_a/single",
                params=data,
                timeout=self.timeout,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            if response.status_code == 200:
                result = response.json()
                translation = result[0][0][0]
                logger.info(f"Google Translate: '{text[:50]}...' -> '{translation[:50]}...'")
                return translation
            else:
                raise Exception(f"Google Translate failed: HTTP {response.status_code}")
                
        except Exception as e:
            logger.error(f"Google Translate error: {e}")
            raise


class LibreTranslateService:
    """LibreTranslate (Free, open-source translation)."""
    
    def __init__(self, api_url: str = "https://libretranslate.de"):
        self.api_url = api_url
        self.timeout = 30
    
    def translate(self, text: str, source_lang: str = 'en', target_lang: str = 'km') -> str:
        """Translate using LibreTranslate."""
        try:
            response = requests.post(
                f"{self.api_url}/translate",
                json={
                    'q': text,
                    'source': source_lang,
                    'target': target_lang
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                translation = result.get('translatedText', '')
                logger.info(f"LibreTranslate: '{text[:50]}...' -> '{translation[:50]}...'")
                return translation
            else:
                raise Exception(f"LibreTranslate failed: HTTP {response.status_code}")
                
        except Exception as e:
            logger.error(f"LibreTranslate error: {e}")
            raise


class MyMemoryTranslateService:
    """MyMemory Translation API (Free, no authentication needed)."""
    
    def __init__(self):
        self.timeout = 30
    
    def translate(self, text: str, source_lang: str = 'en', target_lang: str = 'km') -> str:
        """Translate using MyMemory API."""
        try:
            url = "https://api.mymemory.translated.net/get"
            params = {
                'q': text,
                'langpair': f'{source_lang}|{target_lang}'
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('responseStatus') == 200:
                    translation = result['responseData']['translatedText']
                    logger.info(f"MyMemory: '{text[:50]}...' -> '{translation[:50]}...'")
                    return translation
                else:
                    raise Exception(f"MyMemory error: {result.get('responseStatus')}")
            else:
                raise Exception(f"MyMemory failed: HTTP {response.status_code}")
                
        except Exception as e:
            logger.error(f"MyMemory error: {e}")
            raise


class AltTranslationService:
    """Fallback translation service that tries multiple providers."""
    
    def __init__(self):
        self.providers = [
            GoogleTranslateService(),
            MyMemoryTranslateService(),
            LibreTranslateService(),
        ]
        self.current_provider = 0
    
    def translate(self, text: str) -> str:
        """Try to translate using available providers."""
        errors = []
        
        # Try each provider in order
        for i, provider in enumerate(self.providers):
            try:
                result = provider.translate(text, 'en', 'km')
                if result and len(result) > 0:
                    self.current_provider = i  # Remember which one worked
                    logger.info(f"Translation successful with {provider.__class__.__name__}")
                    return result
            except Exception as e:
                errors.append(f"{provider.__class__.__name__}: {str(e)}")
                logger.warning(f"Provider {provider.__class__.__name__} failed, trying next...")
                continue
        
        # All providers failed
        error_msg = "; ".join(errors)
        logger.error(f"All translation providers failed: {error_msg}")
        raise RuntimeError(f"Translation failed with all providers: {error_msg}")
    
    def test_connection(self) -> tuple[bool, str]:
        """Test if any translation provider is available."""
        for provider in self.providers:
            try:
                # Try translating a short test phrase
                result = provider.translate("Hello", 'en', 'km')
                if result:
                    logger.info(f"Translation provider available: {provider.__class__.__name__}")
                    return True, f"Translation available via {provider.__class__.__name__}"
            except Exception as e:
                logger.warning(f"{provider.__class__.__name__} unavailable: {e}")
                continue
        
        return False, "No translation providers available"


class ManualTranslationService:
    """Manual translation mode - allows user to manually enter Khmer text."""
    
    def __init__(self):
        self.manual_translations = {}
    
    def add_translation(self, english_text: str, khmer_text: str):
        """Add a manual translation."""
        self.manual_translations[english_text] = khmer_text
        logger.info(f"Added manual translation: '{english_text}' -> '{khmer_text}'")
    
    def translate(self, text: str) -> Optional[str]:
        """Get manual translation if available."""
        return self.manual_translations.get(text)
    
    def has_translation(self, text: str) -> bool:
        """Check if manual translation exists."""
        return text in self.manual_translations
    
    def load_from_file(self, filepath: str):
        """Load translations from a file (JSON or CSV format)."""
        import json
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                if filepath.endswith('.json'):
                    self.manual_translations = json.load(f)
                elif filepath.endswith('.csv'):
                    import csv
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.manual_translations[row['english']] = row['khmer']
            logger.info(f"Loaded {len(self.manual_translations)} translations from {filepath}")
        except Exception as e:
            logger.error(f"Failed to load translations from {filepath}: {e}")
            raise
    
    def save_to_file(self, filepath: str):
        """Save translations to a file."""
        import json
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.manual_translations, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(self.manual_translations)} translations to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save translations to {filepath}: {e}")
            raise
