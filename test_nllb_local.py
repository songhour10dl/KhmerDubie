"""
Test NLLB-200 Local Model Setup
This will download the model and test it works before using in the app.
"""
import sys
from pathlib import Path

print("=" * 60)
print("NLLB-200 Local Model Setup & Test")
print("=" * 60)
print()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

print("Step 1: Checking dependencies...")
try:
    import transformers
    import torch
    import sentencepiece
    print("[OK] All dependencies installed")
    print(f"  - transformers: {transformers.__version__}")
    print(f"  - torch: {torch.__version__}")
except ImportError as e:
    print(f"[ERROR] Missing dependency: {e}")
    print("Run: pip install transformers torch sentencepiece")
    sys.exit(1)

print()
print("Step 2: Loading NLLB-200 model (this will take 2-5 minutes on first run)...")
print("  Model size: ~600MB")
print("  Please wait... (downloads from Hugging Face)")
print()

try:
    from src.services.nllb_translation import NLLBTranslationService
    
    # Create service with local model
    nllb = NLLBTranslationService(use_local=True)
    
    print("[OK] NLLB-200 model loaded successfully!")
    print()
    
    # Test translation
    print("Step 3: Testing translation...")
    test_phrases = [
        "Hello",
        "How are you?",
        "Thank you very much",
        "Good morning"
    ]
    
    for phrase in test_phrases:
        try:
            result = nllb.translate(phrase, 'en', 'km')
            print(f"  '{phrase}' -> '{result}'")
        except Exception as e:
            print(f"  Error translating '{phrase}': {e}")
    
    print()
    print("=" * 60)
    print("SUCCESS! NLLB-200 Local is ready to use!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Your .env is already set to: TRANSLATION_PROVIDER=nllb-local")
    print("2. Start your app: START_FRESH.bat")
    print("3. Enjoy offline, high-quality Khmer translations!")
    print()
    print("Note: Future translations will be much faster since the")
    print("      model is now cached on your computer.")
    
except Exception as e:
    print(f"[ERROR] Failed to load NLLB model: {e}")
    print()
    print("Troubleshooting:")
    print("1. Check internet connection (needed for first download)")
    print("2. Check disk space (need ~2GB free)")
    print("3. Try again - downloads can sometimes timeout")
    sys.exit(1)
