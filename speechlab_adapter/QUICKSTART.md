# SpeechLab TTS Adapter - Quick Start Guide

## Overview

This adapter bridges KhmerDubStudio with SpeechLab's VoxCPM2 Khmer TTS engine.

## Quick Installation (3 Steps)

### 1. Start SpeechLab (Terminal 1)

```powershell
# Navigate to SpeechLab directory
cd <your-speechlab-path>

# Install Khmer engine (first time only)
python studio.py install-nanovllm

# Start SpeechLab
python studio.py start
```

Wait until you see the UI at http://localhost:8880

### 2. Start the Adapter (Terminal 2)

```powershell
cd C:\Users\songh\OneDrive\Desktop\KhmerDubStudio\speechlab_adapter

# Create .env file
Copy-Item .env.example .env

# Install dependencies
pip install fastapi uvicorn httpx pydantic python-multipart

# Start adapter
python adapter.py
```

The adapter will start at http://localhost:8881

### 3. Start KhmerDubStudio (Terminal 3)

```powershell
cd C:\Users\songh\OneDrive\Desktop\KhmerDubStudio
python main.py
```

## Testing the Integration

### Test 1: Check adapter health
```powershell
curl http://localhost:8881/health
# Expected: {"status":"ok","service":"SpeechLab Adapter","version":"1.0.0"}
```

### Test 2: Check SpeechLab status
```powershell
curl http://localhost:8881/status
# Expected: ready=true, engine=nanovllm_km
```

### Test 3: Synthesize Khmer text
```powershell
curl -X POST http://localhost:8881/synthesize `
  -H "Content-Type: application/json" `
  -d "{\"text\":\"សួស្តី\",\"voice\":\"khmer-female\",\"language\":\"km\",\"format\":\"wav\",\"sample_rate\":24000}" `
  --output test.wav

# Play test.wav to verify
```

## Voice Options

- `khmer-female` - Female voice with calm style
- `khmer-male` - Male voice

## Configuration

Edit `.env` if you need to change ports:

```bash
SPEECHLAB_BASE_URL=http://localhost:8880
ADAPTER_PORT=8881
REQUEST_TIMEOUT=300.0
```

## Troubleshooting

### "Cannot connect to SpeechLab"
- Verify SpeechLab is running at http://localhost:8880/api/health
- Check if another process is using port 8880

### "Khmer engine not available"
- Make sure you installed nanovllm: `python studio.py install-nanovllm`
- In SpeechLab UI, select "nanovllm_km" engine from dropdown

### Slow synthesis
- First synthesis loads the model (30-60s)
- Check if SpeechLab is using GPU (much faster than CPU)
- GPU info visible in SpeechLab UI system monitor

### Port already in use
- Change `ADAPTER_PORT` in `.env` to a different port (e.g., 8882)
- Update KhmerDubStudio's `TTS_BASE_URL` to match

## Complete! 

Your KhmerDubStudio now uses high-quality local Khmer TTS via SpeechLab.

- No internet required after initial model download
- Male and female Khmer voices
- Handles long text automatically
- Audio synced to video timing

## Support

For issues:
- SpeechLab: https://github.com/im4tta/speechlab
- KhmerDubStudio adapter: See main project repository
