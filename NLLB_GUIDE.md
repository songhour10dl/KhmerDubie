# NLLB-200 Translation Guide

## What is NLLB-200?

NLLB-200 (No Language Left Behind) is a state-of-the-art translation model by Meta AI specifically designed for low-resource languages like Khmer. It provides high-quality translations and works great for English to Khmer.

## Why Use NLLB for Khmer?

- ✅ **Designed for Khmer**: Unlike generic translators, NLLB was trained on Khmer data
- ✅ **Higher Quality**: Better context understanding and natural translations
- ✅ **100% Free**: No API keys, no token costs
- ✅ **Open Source**: Transparent and community-driven
- ✅ **Offline Option**: Can run locally on your computer

## Available NLLB Options

### 1. **NLLB-Hybrid** (RECOMMENDED) ⭐

**Best for:** Most users who want high quality + speed

Combines:
- Manual translations (instant)
- NLLB-200 via Hugging Face API (free)

**How to use:**
1. Settings → Translation Provider → "nllb-hybrid"
2. Click Save
3. Done!

### 2. **NLLB** (Pure NLLB via API)

**Best for:** Those who want pure NLLB translations

Uses:
- NLLB-200 via Hugging Face API (free)
- No manual translations

**How to use:**
1. Settings → Translation Provider → "nllb"
2. Click Save
3. Done!

### 3. **NLLB-Local** (Advanced - On-Device)

**Best for:** Advanced users who want offline translation

Requires:
- `pip install transformers torch` (large download)
- 2GB+ disk space for model
- Good CPU/GPU for speed

**How to use:**
1. Install dependencies: `pip install transformers torch`
2. Change .env: `TRANSLATION_PROVIDER=nllb-local`
3. Restart app
4. First run downloads model (takes time)

## Comparison with Other Options

| Provider | Quality | Speed | Cost | Offline | API Key |
|----------|---------|-------|------|---------|---------|
| **NLLB-Hybrid** ⭐ | ★★★★★ | Fast | Free | No | No |
| **NLLB** | ★★★★★ | Medium | Free | No | No |
| **NLLB-Local** | ★★★★★ | Slow* | Free | Yes | No |
| Hybrid (MyMemory) | ★★★☆☆ | Fast | Free | No | No |
| Alternative | ★★★☆☆ | Fast | Free | No | No |

*Depends on your hardware

## Installation

### Option 1: API-Based (No Installation)

NLLB and NLLB-Hybrid work out of the box - no installation needed!

### Option 2: Local Model (Advanced)

For offline use, install transformers:

```bash
pip install transformers torch
```

**Note:** First run downloads ~600MB model from Hugging Face.

## Usage Examples

### Quick Start

1. **Open Settings**
2. **Change Translation Provider** to one of:
   - `nllb-hybrid` (recommended)
   - `nllb` (pure NLLB)
   - `nllb-local` (offline)
3. **Click Save**
4. **Start dubbing!**

### Test Connection

1. Open Settings
2. Select NLLB provider
3. Click "Test Connection"
4. Should see: "Connection successful via Hugging Face API"

## Troubleshooting

### "Model is loading" message

**Problem:** Hugging Face API needs to load model
**Solution:** Wait 20 seconds and try again (automatic retry built-in)

### Connection timeout

**Problem:** API is slow or unavailable
**Solution:** 
- Wait a few minutes
- Switch to `nllb-hybrid` which has fallback
- Use local model (`nllb-local`)

### Local model fails to load

**Problem:** transformers or torch not installed
**Solution:** 
```bash
pip install transformers torch
```

### Translation quality issues

**Problem:** NLLB result doesn't sound natural
**Solution:**
- Use `nllb-hybrid` to add manual translations for common phrases
- Edit `translations.json` to add better translations
- Manual translations always used first

## Performance Tips

### For Best Speed:
- Use `nllb-hybrid` (manual translations are instant)
- Add frequently used phrases to `translations.json`

### For Best Quality:
- Use `nllb` or `nllb-hybrid`
- NLLB quality is significantly better than MyMemory/LibreTranslate

### For Offline Use:
- Install `transformers torch`
- Use `nllb-local`
- First run takes time (downloads model)
- Subsequent runs work offline

## Configuration

### .env Settings

```ini
# For NLLB Hybrid (recommended)
TRANSLATION_PROVIDER=nllb-hybrid
MANUAL_DICT_PATH=translations.json

# For Pure NLLB API
TRANSLATION_PROVIDER=nllb

# For Local NLLB (offline)
TRANSLATION_PROVIDER=nllb-local
```

### Optional: Hugging Face API Key

NLLB works without an API key (free tier), but you can add one for higher rate limits:

1. Create free account: https://huggingface.co/
2. Get API token: https://huggingface.co/settings/tokens
3. Not required - skip this step!

## Technical Details

### Model Information

- **Model:** facebook/nllb-200-distilled-600M
- **Size:** ~600MB
- **Languages:** 200+ including Khmer
- **Architecture:** Transformer-based seq2seq
- **License:** CC-BY-NC (research & education)

### Language Codes

- English: `eng_Latn`
- Khmer: `khm_Khmr`

### API Endpoint

```
https://api-inference.huggingface.co/models/facebook/nllb-200-distilled-600M
```

## Advantages of NLLB for Khmer

1. **Trained on Khmer Data**: Unlike generic models
2. **Context Awareness**: Better understanding of sentence structure
3. **Natural Output**: More fluent Khmer translations
4. **Open Source**: Transparent and auditable
5. **Academic Backing**: Meta AI research quality

## Cost Comparison

| Solution | Monthly Cost | Limitations |
|----------|-------------|-------------|
| NLLB (API) | $0 | Rate limits (generous) |
| NLLB-Hybrid | $0 | Manual + API |
| NLLB-Local | $0 | Hardware dependent |
| OmniRoute | $$$ | Token limits |
| Google Translate | $0 | Strict rate limits |

## Support

- **Hugging Face Docs**: https://huggingface.co/facebook/nllb-200-distilled-600M
- **Meta AI Paper**: https://ai.meta.com/research/no-language-left-behind/
- **Issues**: Create issue in KhmerDub Studio repo

## Future Enhancements

Coming soon:
- NLLB-1.3B (larger, better quality)
- NLLB-3.3B (production quality)
- Fine-tuned Khmer models
- Batch processing optimization
- GPU acceleration for local model

## Conclusion

NLLB-200 provides the best free translation quality for English to Khmer. Use `nllb-hybrid` for optimal speed and quality with manual translations as a first layer.
