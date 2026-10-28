"""Download NLLB-200 model for offline use."""
import os
import sys
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def download_nllb_model():
    """Download and cache NLLB-200 model locally."""
    print("=" * 60)
    print("NLLB-200 Model Downloader")
    print("=" * 60)
    print()
    print("This will download approximately 2.5 GB of model files.")
    print("Files will be cached in: %USERPROFILE%\\.cache\\huggingface\\hub\\")
    print()
    print("Starting download...")
    print()
    
    model_name = "facebook/nllb-200-distilled-600M"
    
    try:
        # Download tokenizer
        print("[1/2] Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        print("[OK] Tokenizer downloaded successfully!")
        print()
        
        # Download model
        print("[2/2] Downloading model (this may take several minutes)...")
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        print("[OK] Model downloaded successfully!")
        print()
        
        # Test the model
        print("Testing model...")
        tokenizer.src_lang = "eng_Latn"
        inputs = tokenizer("Hello", return_tensors="pt")
        forced_bos_token_id = tokenizer.convert_tokens_to_ids("khm_Khmr")
        outputs = model.generate(**inputs, forced_bos_token_id=forced_bos_token_id, max_length=50)
        result = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
        print(f"[OK] Test translation: 'Hello' -> '{result}'")
        print()
        
        print("=" * 60)
        print("SUCCESS! NLLB-200 model is ready for offline use.")
        print("=" * 60)
        print()
        print("You can now use TRANSLATION_PROVIDER=nllb-local in your .env file")
        
    except Exception as e:
        print()
        print("=" * 60)
        print("ERROR: Failed to download model")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        print("Make sure you have:")
        print("1. Active internet connection")
        print("2. At least 3 GB free disk space")
        print("3. transformers library installed: pip install transformers torch")
        return False
    
    return True

if __name__ == "__main__":
    download_nllb_model()
