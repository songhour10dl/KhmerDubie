# Hybrid Translation System - Quick Start Guide

## What You Now Have

Your KhmerDubStudio now has a **hybrid translation system** that:
- Uses manual translations first (instant, no tokens)
- Falls back to free APIs for unknown phrases
- Never wastes tokens on phrases you've already translated

## 4 Translation Providers Available

### 1. **Hybrid (RECOMMENDED)** ⭐
Best for cost-effective, high-quality translations
- **Speed**: Manual translations are instant
- **Cost**: Zero tokens for known phrases
- **Quality**: High for manual translations, good for fallback
- **Setup**: Point to `translations.json`

### 2. **Alternative (Free APIs)**
Good when you want no setup needed
- **Providers**: Google Translate, MyMemory, LibreTranslate
- **Cost**: Completely free, no tokens
- **Speed**: 2-3 seconds per phrase
- **Setup**: None needed - works out of the box

### 3. **OmniRoute (Premium)**
Use only when you need highest quality
- **Cost**: Uses your tokens
- **Quality**: Highest quality
- **Speed**: 3-5 seconds per phrase
- **Setup**: Configure API key and model

### 4. **Google Only**
Lightweight option with just Google Translate
- **Cost**: Free
- **Quality**: Good
- **Speed**: 2 seconds per phrase
- **Setup**: None needed

---

## How to Use Hybrid Mode (Recommended)

### Step 1: Add Your Translations
Edit `translations.json` and add English→Khmer pairs:

```json
{
  "Hello": "សូស្តី",
  "How are you?": "សុខសប្បាយដែរឬ",
  "Good morning": "ថ្ងៃព្រឹក",
  "Thank you": "សូមអរគុណ",
  "Goodbye": "លាហើយ"
}
```

**Format**: `"English phrase": "Khmer translation"`

### Step 2: Configure Settings
1. Open your app and go to **Settings**
2. Under "Translation Provider", select **"hybrid"**
3. Set "Manual Dictionary" path to: `translations.json`
4. Click "Test Connection" (should show 41+ manual translations)
5. Click "Save"

### Step 3: Run Your Project
When you process a video:
- Phrases in `translations.json` → Used instantly (no API call)
- Unknown phrases → Auto-translated via free API (MyMemory)
- Result → Perfect translations with zero wasted tokens!

---

## Adding More Translations

### Method 1: Edit translations.json Manually
```json
{
  "existing translation": "khmer",
  "new phrase": "khmer translation"
}
```

### Method 2: Load from CSV File
Create a CSV file with columns: `english`, `khmer`

```csv
english,khmer
Hello,សូស្តី
Thank you,សូមអរគុណ
```

Then in settings, point to your CSV file.

### Method 3: Export After Processing
After translating a video:
1. Go to project folder
2. Find `segments.json`
3. Extract the English→Khmer pairs
4. Add to `translations.json`
5. Next video will reuse those translations!

---

## Troubleshooting

### "Manual translations not loading"
- Check file path is correct in Settings
- Verify `translations.json` exists in project root
- Check file is valid JSON (use online JSON validator)

### "Alternative services unavailable"
- Google Translate often rate-limits (HTTP 429)
- Use MyMemory or LibreTranslate instead
- Or use Hybrid mode with manual translations

### "Test connection failed"
- For Hybrid: Make sure `translations.json` exists
- For Alternative: Check internet connection
- For OmniRoute: Verify API key and base URL

### "Still running out of tokens?"
- Make sure "hybrid" provider is selected
- Add more phrases to `translations.json`
- Use alternative providers for new phrases

---

## Sample translations.json (41 common phrases)

Already included in your project! Contains:
- Greetings (Hello, Good morning, Good evening, etc.)
- Polite phrases (Thank you, Sorry, Excuse me, etc.)
- Common questions (How are you?, What is your name?, etc.)
- Emergency phrases (Help, Emergency, Police, Doctor, etc.)
- Travel phrases (Hotel, Taxi, Bathroom, Money, etc.)

---

## Code Examples

### Use Hybrid Mode Programmatically
```python
from src.services import HybridTranslationService

# Initialize
translator = HybridTranslationService(manual_dict_path="translations.json")

# Translate (will use manual first, then fallback)
result = translator.translate("Hello")

# Add translations dynamically
translator.add_manual_translation("New phrase", "khmer")

# Save for next time
translator.save_manual_translations("translations.json")

# Check how many are manual
print(f"Manual translations: {translator.get_manual_translation_count()}")
```

### Use in ProcessingPipeline
```python
from src.services import ProcessingPipeline

# Create pipeline with hybrid provider
pipeline = ProcessingPipeline(
    translation_provider="hybrid",
    manual_dict_path="translations.json"
)

# Use normally - hybrid will handle translations
segments = pipeline.extract_and_transcribe()
segments = pipeline.translate_segments()  # Uses hybrid!
pipeline.generate_speech(segments)
```

### Switch Providers
```python
# Alternative (free APIs)
pipeline = ProcessingPipeline(translation_provider="alternative")

# Google only
pipeline = ProcessingPipeline(translation_provider="google")

# OmniRoute (premium)
pipeline = ProcessingPipeline(translation_provider="omniroute")

# Hybrid (recommended)
pipeline = ProcessingPipeline(translation_provider="hybrid")
```

---

## Cost Comparison

| Provider | Manual Phrases | Unknown Phrases | Total Cost |
|----------|---|---|---|
| **Hybrid** | Instant, 0 tokens | Free API | ~0.1¢ |
| **Alternative** | N/A | Free API | 0¢ |
| **OmniRoute** | Full tokens | Full tokens | $$$$ |
| **Google** | N/A | Free | 0¢ |

---

## Pro Tips

1. **Build Your Dictionary Gradually**
   - Start with 50 common phrases
   - After each project, add new phrases to dictionary
   - Over time, you'll use almost zero tokens

2. **Export and Save**
   - After processing, export all translations
   - Add to `translations.json`
   - Future projects reuse them instantly

3. **Test Translation**
   - Use Settings dialog "Test Connection" button
   - Shows how many manual translations are loaded
   - Helps debug if phrases aren't being found

4. **Combine with TTS**
   - Hybrid translations + ElevenLabs TTS = Perfect dubbing
   - No token waste, professional audio quality

5. **Backup Your Dictionary**
   - Keep copies of `translations.json`
   - Git commit it so you don't lose phrases
   - Share across team members

---

## Files You Now Have

- `src/services/alternative_translation.py` - All translation services (HybridTranslationService, etc.)
- `src/services/processing_pipeline.py` - Updated to support all providers
- `src/ui/settings_dialog.py` - Updated with translation provider UI
- `src/services/__init__.py` - Updated exports
- `translations.json` - 41 sample Khmer translations
- `test_hybrid_translation.py` - Test script to verify everything works

---

## Next Steps

1. ✓ Hybrid system is installed
2. Run `test_hybrid_translation.py` to verify
3. Edit `translations.json` to add your phrases
4. Open Settings and select "hybrid" provider
5. Set manual dictionary path to `translations.json`
6. Start dubbing - watch tokens stay at zero!

---

## Questions?

Check the code:
- `src/services/alternative_translation.py` - Full source code
- `test_hybrid_translation.py` - Working examples
- `src/services/processing_pipeline.py` - How it's integrated

Everything is documented inline in the source!
