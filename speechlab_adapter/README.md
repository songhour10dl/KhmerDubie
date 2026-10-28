# SpeechLab TTS Adapter for KhmerDubStudio

This adapter provides a compatibility layer between KhmerDubStudio and the SpeechLab local TTS engine, specifically for Khmer voice synthesis using the VoxCPM2/nanovllm_km engine.

## Overview

The adapter translates KhmerDubStudio's expected TTS API format into SpeechLab's actual API format, handles voice mapping, text chunking, and audio resampling.

## Features

- ✅ **Status endpoint** - Reports SpeechLab readiness and Khmer engine availability
- ✅ **Synthesize endpoint** - Converts text to speech with male/female Khmer voices
- ✅ **Voice mapping** - Maps `khmer-female` and `khmer-male` to VoxCPM2 style instructions
- ✅ **Text splitting** - Safely splits long Khmer text at sentence boundaries
- ✅ **Audio resampling** - Resamples output to requested sample rate (48kHz by default)
- ✅ **Segment joining** - Joins multiple audio segments seamlessly

## Architecture

```
KhmerDubStudio Application
    ↓ (HTTP requests)
SpeechLab Adapter :8881
    ↓ (translates format)
SpeechLab Service :8880
    ↓ (nanovllm_km engine)
VoxCPM2 Model (Khmer TTS)
```

## Installation

### Prerequisites

1. **SpeechLab** must be installed and running
2. **Python 3.10+**
3. **Windows PowerShell** (for Windows users)

### Step 1: Clone or navigate to the speechlab_adapter directory

The adapter is located in your KhmerDubStudio project:

```powershell
cd C:\Users\songh\OneDrive\Desktop\KhmerDubStudio\speechlab_adapter
```

### Step 2: Create and activate virtual environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

### Step 3: Install dependencies

```powershell
pip install -r requirements.txt
```

### Step 4: Configure environment

```powershell
# Copy example config
Copy-Item .env.example .env

# Edit .env if needed (default settings should work)
notepad .env
```

## Running the Services

### Start SpeechLab First

In a **separate terminal**, start SpeechLab:

```powershell
cd <path-to-speechlab>
python studio.py start
```

Wait for SpeechLab to fully load (check http://localhost:8880/api/health shows `"status": "ok"`).

### Start the Adapter

In your adapter terminal:

```powershell
cd C:\Users\songh\OneDrive\Desktop\KhmerDubStudio\speechlab_adapter
.\venv\Scripts\Activate.ps1
python adapter.py
```

The adapter will start on http://localhost:8881

### Start KhmerDubStudio

In a **third terminal**:

```powershell
cd C:\Users\songh\OneDrive\Desktop\KhmerDubStudio
python main.py
```

## API Endpoints

### GET /status

Check adapter and SpeechLab readiness.

**Response:**
```json
{
  "status": "ok",
  "engine": "nanovllm_km",
  "ready": true,
  "message": "SpeechLab ready for Khmer synthesis",
  "khmer_support": true,
  "supported_voices": ["khmer-female", "khmer-male"]
}
```

### POST /synthesize

Synthesize Khmer text to speech.

**Request:**
```json
{
  "text": "សួស្តី អ្នកទាំងអស់គ្នា",
  "voice": "khmer-female",
  "language": "km",
  "format": "wav",
  "sample_rate": 48000
}
```

**Response:**
- Content-Type: `audio/wav`
- Headers:
  - `X-Sample-Rate`: Output sample rate
  - `X-Voice`: Voice used
  - `X-Chunks`: Number of text chunks processed

### GET /health

Simple health check for the adapter itself.

**Response:**
```json
{
  "status": "ok",
  "service": "SpeechLab Adapter",
  "version": "1.0.0"
}
```

## Voice Mapping

The adapter maps KhmerDubStudio voice IDs to SpeechLab VoxCPM2 style instructions:

| Voice ID | Style Instruction | Gender |
|----------|------------------|--------|
| `khmer-female` | `(សំឡេងស្ត្រី ស្ងប់ស្ងាត់)` | Female, calm |
| `khmer-male` | `(សំឡេងបុរស)` | Male |

These styles are prepended to the input text and processed by the nanovllm_km engine.

## Configuration

Edit `.env` to customize:

```bash
# SpeechLab service base URL
SPEECHLAB_BASE_URL=http://localhost:8880

# Adapter listening configuration
ADAPTER_HOST=0.0.0.0
ADAPTER_PORT=8881

# Request timeout in seconds (for long synthesis)
REQUEST_TIMEOUT=300.0
```

## Testing

Run the test suite:

```powershell
.\venv\Scripts\Activate.ps1
pip install pytest pytest-asyncio
pytest test_adapter.py -v
```

## Troubleshooting

### "Cannot connect to SpeechLab"

**Problem:** Adapter cannot reach SpeechLab at http://localhost:8880

**Solutions:**
1. Verify SpeechLab is running: `curl http://localhost:8880/api/health`
2. Check `SPEECHLAB_BASE_URL` in `.env`
3. Ensure no firewall blocking port 8880

### "Khmer engine not available"

**Problem:** SpeechLab doesn't have nanovllm_km engine

**Solutions:**
1. Install the Khmer engine in SpeechLab:
   ```powershell
   python studio.py install-nanovllm
   ```
2. Activate the engine in SpeechLab UI or via API:
   ```powershell
   curl -X POST http://localhost:8880/api/engines/activate -H "Content-Type: application/json" -d "{\"name\":\"nanovllm_km\"}"
   ```

### "Synthesis timed out"

**Problem:** Long text takes too long to synthesize

**Solutions:**
1. Increase `REQUEST_TIMEOUT` in `.env` (default 300s)
2. Reduce text length - the adapter auto-splits but very long texts still take time
3. Check if SpeechLab is using CPU instead of GPU (much slower)

### Audio quality issues

**Problem:** Audio sounds distorted or wrong pitch

**Solutions:**
1. Verify sample rate resampling: adapter resamples from SpeechLab's native rate (typically 24kHz) to your requested rate (48kHz)
2. Check original SpeechLab output quality first (test directly at http://localhost:8880)
3. Try reducing text chunk size in `split_khmer_text()` if joins are audible

## Integration with KhmerDubStudio

Update your KhmerDubStudio `.env` file:

```bash
# Text-to-Speech Provider
TTS_PROVIDER=speechlab
TTS_BASE_URL=http://localhost:8881
TTS_VOICE=khmer-female
```

The adapter is now set as the TTS provider, and KhmerDubStudio will use:
- `GET http://localhost:8881/status` for connection testing
- `POST http://localhost:8881/synthesize` for audio generation

## Performance Notes

- **First synthesis:** May take longer as SpeechLab loads the model
- **Subsequent synthesis:** Faster due to model caching
- **Long text:** Automatically split into chunks (max 500 chars) and joined
- **GPU vs CPU:** GPU synthesis is 10-100x faster; ensure SpeechLab uses GPU
- **Concurrent requests:** Adapter handles one request at a time (serialized through SpeechLab's GPU gate)

## License

MIT - Same as KhmerDubStudio main application

## Credits

- **SpeechLab:** im4tta/speechlab (https://github.com/im4tta/speechlab)
- **VoxCPM2:** Tsinghua NLP Lab
- **nanovllm-voxcpm:** a710128 (concurrent batching runtime)
