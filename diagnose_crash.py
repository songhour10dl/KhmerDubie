"""
Quick diagnostic to test what's causing the crash
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing components one by one...")

# Test 1: Can we import everything?
print("\n1. Testing imports...")
try:
    from src.services.stt_service import STTService
    print("   [OK] STT Service imports")
except Exception as e:
    print(f"   [ERROR] STT import failed: {e}")
    sys.exit(1)

# Test 2: Can we load Whisper?
print("\n2. Testing Whisper model loading...")
try:
    import whisper
    print("   [OK] Whisper imports")
    print("   Loading 'base' model (this takes ~30 seconds)...")
    model = whisper.load_model("base")
    print("   [OK] Whisper model loaded")
except Exception as e:
    print(f"   [ERROR] Whisper loading failed: {e}")
    print("\n   Possible causes:")
    print("   - Not enough RAM (Whisper needs 1-2GB)")
    print("   - CPU too slow")
    print("   - Corrupted model files")
    sys.exit(1)

# Test 3: Can we transcribe a test file?
print("\n3. Testing transcription...")
test_file = Path("C:/Temp/KhmerDub/p19a205f7/extracted_audio.wav")
if test_file.exists():
    print(f"   Testing with: {test_file}")
    try:
        result = model.transcribe(str(test_file), language="en", verbose=False)
        print(f"   [OK] Transcription succeeded!")
        print(f"   Found {len(result.get('segments', []))} segments")
        if result.get('text'):
            print(f"   Sample text: {result['text'][:100]}...")
    except Exception as e:
        print(f"   [ERROR] Transcription failed: {e}")
        sys.exit(1)
else:
    print(f"   [SKIP] Test file not found: {test_file}")

print("\n" + "="*60)
print("All tests passed! The issue might be in the UI/threading.")
print("="*60)
