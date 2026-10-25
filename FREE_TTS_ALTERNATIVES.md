# Free Khmer TTS Alternatives

Since Kiri TTS is returning errors, I've added **three FREE alternatives** that work without API keys:

---

## 🎯 **Best FREE Options (Recommended)**

### 1. **Edge TTS** ⭐ RECOMMENDED
- **Quality**: High quality, neural voices
- **Cost**: Completely FREE
- **API Key**: Not required
- **Offline**: No (requires internet)
- **Khmer Voices**: 
  - `km-KH-SreymomNeural` (Female)
  - `km-KH-PisethNeural` (Male)

**Installation:**
```powershell
pip install edge-tts
```

**Configuration in Settings:**
- Provider: `edge`
- Voice: `km-KH-SreymomNeural` or `km-KH-PisethNeural`
- API Key: (leave empty)

---

### 2. **gTTS (Google Text-to-Speech)** 
- **Quality**: Good, standard voices
- **Cost**: Completely FREE
- **API Key**: Not required
- **Offline**: No (requires internet)
- **Khmer**: Supported as `km`

**Installation:**
```powershell
pip install gtts
```

**Configuration in Settings:**
- Provider: `gtts`
- Voice: `km` (automatic)
- API Key: (leave empty)

---

### 3. **eSpeak-ng** (Local/Offline)
- **Quality**: Basic/robotic (lower quality)
- **Cost**: Completely FREE
- **API Key**: Not required
- **Offline**: Yes (fully local)
- **Khmer**: Basic support

**Installation:**
1. Download from: https://github.com/espeak-ng/espeak-ng/releases
2. Install the Windows installer
3. Add to PATH if needed

**Configuration in Settings:**
- Provider: `local`
- Voice: `km` (automatic)
- API Key: (leave empty)

---

## 📋 **Quick Setup Steps**

### Option 1: Use Edge TTS (Recommended)

```powershell
# 1. Install Edge TTS
pip install edge-tts

# 2. Update your .env file
notepad .env
```

Change these lines:
```
TTS_PROVIDER=edge
TTS_VOICE=km-KH-SreymomNeural
TTS_API_KEY=
```

### Option 2: Use gTTS (Simplest)

```powershell
# 1. Install gTTS
pip install gtts

# 2. Update your .env file
notepad .env
```

Change these lines:
```
TTS_PROVIDER=gtts
TTS_VOICE=km
TTS_API_KEY=
```

---

## 🎛️ **Comparison Table**

| Provider | Quality | Speed | Cost | API Key | Internet | Installation |
|----------|---------|-------|------|---------|----------|--------------|
| **Edge TTS** ⭐ | Excellent | Fast | FREE | No | Yes | `pip install edge-tts` |
| **gTTS** | Good | Medium | FREE | No | Yes | `pip install gtts` |
| **eSpeak-ng** | Basic | Very Fast | FREE | No | No | Download installer |
| Kiri | Unknown | N/A | Paid | Yes | Yes | Currently failing |
| Google Cloud | Excellent | Fast | $$ | Yes | Yes | `pip install google-cloud-texttospeech` |

---

## 🚀 **How to Switch Providers in the App**

1. Open KhmerDub Studio
2. Click **Settings** button
3. In the "Text-to-Speech" section:
   - **Provider**: Select `edge` (recommended) or `gtts`
   - **API Key**: Leave empty for free providers
   - **Voice**: 
     - For Edge: `km-KH-SreymomNeural` (female) or `km-KH-PisethNeural` (male)
     - For gTTS: `km` (automatic)
4. Click **Test Connection** to verify it works
5. Click **Save**

---

## 💡 **Which One Should You Choose?**

### Choose **Edge TTS** if you want:
- ✅ Best quality
- ✅ Neural, natural-sounding voices
- ✅ Multiple voice options (male/female)
- ✅ FREE forever
- ✅ No API key hassle

### Choose **gTTS** if you want:
- ✅ Simplest setup
- ✅ Reliable and stable
- ✅ Good enough quality
- ✅ FREE forever
- ✅ No API key hassle

### Choose **eSpeak-ng** if you want:
- ✅ Completely offline
- ✅ No internet required
- ✅ Privacy (no data sent to cloud)
- ⚠️ Lower quality (robotic voice)

---

## ✅ **Quick Install & Test**

Install the recommended Edge TTS and test it:

```powershell
# Install
pip install edge-tts

# Test from command line
edge-tts --voice km-KH-SreymomNeural --text "សួស្តី" --write-media test_khmer.mp3

# If successful, you'll get test_khmer.mp3 file
```

---

## 🔧 **Updated Configuration**

Your updated `.env` file should look like this:

```env
# OmniRoute Configuration
OMNIROUTE_BASE_URL=http://localhost:8000
OMNIROUTE_API_KEY=your_api_key_here
OMNIROUTE_MODEL=gpt-4

# Speech-to-Text Provider
STT_PROVIDER=whisper
STT_API_KEY=
STT_MODEL=base

# Text-to-Speech Provider (Khmer)
TTS_PROVIDER=edge
TTS_API_KEY=
TTS_VOICE=km-KH-SreymomNeural
TTS_BASE_URL=

# Processing Settings
MAX_CONCURRENT_REQUESTS=3
REQUEST_TIMEOUT=300
TEMP_DIR=./temp
OUTPUT_DIR=./output

# FFmpeg Settings
FFMPEG_PATH=ffmpeg
FFPROBE_PATH=ffprobe

# Audio Settings
AUDIO_CODEC=aac
AUDIO_BITRATE=128k
AUDIO_SAMPLE_RATE=48000
```

---

## 📝 **What Changed in the Code**

I've updated KhmerDub Studio to support all these providers:

1. **Enhanced TTS Service** (`src/services/tts_service.py`):
   - Added Edge TTS support (FREE)
   - Added gTTS support (FREE)
   - Added eSpeak-ng support (FREE, offline)
   - Kept Google Cloud TTS (paid)
   - Kept original Kiri support

2. **Updated Settings Dialog** (`src/ui/settings_dialog.py`):
   - Dropdown now shows: edge, gtts, google, local, kiri
   - Auto-disables API key field for free providers
   - Shows helpful installation hints
   - Smart defaults for each provider

3. **Updated Requirements** (`requirements.txt`):
   - Added `edge-tts>=6.1.0`
   - Added `gTTS>=2.5.0`
   - Clear comments about FREE vs PAID options

---

## 🎉 **Ready to Use!**

Simply run:

```powershell
pip install edge-tts
python main.py
```

Then go to Settings → TTS Provider → Select "edge" → Save

Your video dubbing should now work perfectly with FREE, high-quality Khmer voices!
