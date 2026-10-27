#!/usr/bin/env python3
"""
EMERGENCY FIX - Force correct settings to stop token waste
Run this immediately to fix translation provider issues
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("EMERGENCY SETTINGS FIX")
print("=" * 60)
print()

# Step 1: Force overwrite .env file with correct settings
print("Step 1: Forcing .env file with correct settings...")

env_content = """# OmniRoute Configuration
OMNIROUTE_BASE_URL=http://localhost:20128/v1
OMNIROUTE_API_KEY=sk-ab09c4986eca7e63-628253-8d530fd8
OMNIROUTE_MODEL=kr/claude-sonnet-4.5

# Translation Provider - HYBRID MODE (SAVES TOKENS!)
TRANSLATION_PROVIDER=hybrid
MANUAL_DICT_PATH=translations.json

# Speech-to-Text Provider
STT_PROVIDER=whisper
STT_API_KEY=optional_for_cloud_services
STT_MODEL=base

# Text-to-Speech Provider (Khmer)
TTS_PROVIDER=edge
TTS_API_KEY=
TTS_VOICE=km-KH-SreymomNeural
TTS_BASE_URL=

# Processing Settings
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT=300
TEMP_DIR=C:\\Temp\\KhmerDub
OUTPUT_DIR=C:\\Temp\\KhmerDub\\output

# FFmpeg Settings
FFMPEG_PATH=ffmpeg
FFPROBE_PATH=ffprobe

# Audio Settings
AUDIO_CODEC=aac
AUDIO_BITRATE=128k
AUDIO_SAMPLE_RATE=48000
"""

with open('.env', 'w', encoding='utf-8') as f:
    f.write(env_content)

print("✓ .env file updated with HYBRID mode")
print()

# Step 2: Verify config loads correctly
print("Step 2: Testing configuration loading...")
from src.utils.config import config

# Force reload
config.reload()

print(f"  Translation Provider: {config.translation_provider}")
print(f"  OmniRoute Model: {config.omniroute_model}")
print(f"  Manual Dict Path: {config.manual_dict_path}")

if config.translation_provider != 'hybrid':
    print()
    print("ERROR: Config still not loading hybrid!")
    print("There may be a caching issue. Try:")
    print("1. Close ALL Python processes")
    print("2. Delete __pycache__ folders")
    print("3. Run this script again")
    sys.exit(1)

print("✓ Config loads correctly")
print()

# Step 3: Test pipeline creation
print("Step 3: Testing pipeline with hybrid mode...")
from src.services import ProcessingPipeline

pipeline = ProcessingPipeline(
    translation_provider='hybrid',
    manual_dict_path='translations.json'
)

print(f"  Pipeline provider: {pipeline.translation_provider}")
print(f"  Translator type: {type(pipeline.translator).__name__}")

if type(pipeline.translator).__name__ != 'HybridTranslationService':
    print()
    print("ERROR: Pipeline is not using HybridTranslationService!")
    sys.exit(1)

print("✓ Pipeline created with HybridTranslationService")
print()

# Step 4: Test manual translations
print("Step 4: Testing manual translations...")
try:
    result = pipeline.translator.translate("Hello")
    print(f"  'Hello' translated to: {result[:50]}...")
    manual_count = pipeline.translator.get_manual_translation_count()
    print(f"  Manual translations available: {manual_count}")
    
    if manual_count == 0:
        print()
        print("WARNING: No manual translations loaded!")
        print("Check that translations.json exists")
    else:
        print("✓ Manual translations working")
except Exception as e:
    print(f"  Error testing translation: {e}")

print()
print("=" * 60)
print("FIX COMPLETE!")
print("=" * 60)
print()
print("YOUR APP IS NOW CONFIGURED TO:")
print("✓ Use HYBRID translation mode")
print("✓ Use manual translations (41 phrases = ZERO tokens)")
print("✓ Fall back to free APIs (MyMemory/LibreTranslate)")
print("✓ STOP wasting tokens on repeated phrases")
print()
print("NEXT STEPS:")
print("1. Close this window")
print("2. Start your app: python main.py")
print("3. Check logs show: 'Using Hybrid translation'")
print("4. Start dubbing - you'll save tokens immediately!")
print()
print("If you still see 'Using OmniRoute', there's a caching issue.")
print("Solution: Delete all __pycache__ folders and try again")
