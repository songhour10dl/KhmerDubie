# Quick SpeechLab Setup Guide

## Current Issue
You're getting "could not connect to speechlab localhost:8881" because the SpeechLab adapter isn't running.

## How to Fix - Start Both Services

You need **3 separate terminal windows**:

### Terminal 1: Start SpeechLab (Main TTS Engine)

```powershell
cd D:\speechlab
python studio.py start
```

Wait until you see the web interface at: http://localhost:8880

### Terminal 2: Start SpeechLab Adapter (Bridge)

```powershell
cd D:\KhmerDubStudio
.\START_SPEECHLAB_ADAPTER.bat
```

Or manually:
```powershell
cd D:\KhmerDubStudio\speechlab_adapter
py -3.11 adapter.py
```

The adapter will start at: http://localhost:8881

### Terminal 3: Start KhmerDub Studio

```powershell
cd D:\KhmerDubStudio
.\START_FRESH.bat
```

## Verify Setup

Once all three are running, test the connection:

**1. Check SpeechLab health:**
```powershell
curl http://localhost:8880/api/health
```
Should return: `{"status":"ok"}`

**2. Check adapter health:**
```powershell
curl http://localhost:8881/health
```
Should return: `{"status":"ok","service":"SpeechLab Adapter",...}`

**3. Test TTS connection in KhmerDub Studio:**
- Go to Settings > TTS Provider
- Click "Test Connection"
- Should show: ✅ Connection successful

## Architecture

```
KhmerDub Studio (GUI)
    ↓ Port 8881
SpeechLab Adapter (Bridge)
    ↓ Port 8880
SpeechLab (TTS Engine)
```

## Troubleshooting

### "SpeechLab not found at D:\speechlab"
- Make sure you have SpeechLab installed
- Clone it from: https://github.com/im4tta/speechlab
- Or adjust the path to where you installed it

### "Port 8881 already in use"
- Kill any existing adapter process
- Change ADAPTER_PORT in `speechlab_adapter/.env`

### "Adapter can't connect to SpeechLab"
- Make sure SpeechLab (Terminal 1) is running first
- Check: http://localhost:8880/api/health
- Verify `SPEECHLAB_BASE_URL=http://localhost:8880` in `speechlab_adapter/.env`

## Alternative: Use Different TTS Provider

If you don't want to use SpeechLab right now, change your `.env`:

```bash
# Use Edge TTS instead (works without setup)
TTS_PROVIDER=edge
TTS_BASE_URL=
TTS_VOICE=km-KH-PisethNeural
```

Then restart KhmerDub Studio.
