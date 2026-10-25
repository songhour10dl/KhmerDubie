# KhmerDub Studio

**AI-Powered Video Dubbing Desktop Application for Cambodian Khmer**

KhmerDub Studio is a complete Windows desktop application that automatically dubs English videos into natural Cambodian Khmer speech while preserving original video quality without watermarks.

---

## Features

- **Video Import**: Support for MP4, MKV, MOV, AVI formats
- **Video Inspection**: Display duration, resolution, frame rate, codecs, and audio tracks
- **Speech Transcription**: Automatic English speech-to-text with timestamps using Whisper
- **AI Translation**: Context-aware English-to-Khmer translation via OmniRoute
- **Khmer Text-to-Speech**: Generate natural Khmer speech (Kiri TTS support)
- **Transcript Editing**: Review and edit English transcripts
- **Translation Editing**: Review and edit Khmer translations
- **Timeline Management**: Dialogue segments with precise timestamps
- **Video Export**: High-quality output with original video stream preserved (no re-encoding)
- **Subtitle Generation**: Optional Khmer SRT subtitles
- **No Watermarks**: Clean professional output
- **Background Processing**: Responsive UI with threaded operations
- **Project State**: Save and resume work

---

## Requirements

### System Requirements
- **OS**: Windows 11 (tested) or Windows 10
- **Python**: 3.11 or newer (tested with 3.13)
- **FFmpeg**: Required for video/audio processing
- **RAM**: 8GB minimum, 16GB recommended
- **Disk**: 5GB+ free space for processing

### API Requirements
- **OmniRoute**: Translation service endpoint and API key
- **Khmer TTS Provider**: Kiri TTS or compatible Khmer TTS API key

---

## Installation

### 1. Install Python
Download and install Python 3.11+ from [python.org](https://www.python.org/downloads/)

Ensure "Add Python to PATH" is checked during installation.

### 2. Install FFmpeg
FFmpeg is already detected in your system. If you need to install it elsewhere:

1. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add FFmpeg `bin` folder to system PATH

Verify installation:
```powershell
ffmpeg -version
```

### 3. Clone or Download Project
```powershell
cd C:\Users\songh\OneDrive\Desktop
cd KhmerDubStudio
```

### 4. Create Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 5. Install Dependencies
```powershell
pip install -r requirements.txt
```

**Note**: Installing `openai-whisper` will download the Whisper model on first use (several hundred MB depending on model size).

### 6. Configure API Keys
Copy the example environment file:
```powershell
Copy-Item .env.example .env
```

Edit `.env` with your actual API credentials:
```
OMNIROUTE_BASE_URL=http://your-omniroute-url:8000
OMNIROUTE_API_KEY=your_omniroute_api_key
OMNIROUTE_MODEL=gpt-4

TTS_PROVIDER=kiri
TTS_API_KEY=your_kiri_api_key
TTS_BASE_URL=https://api.kiri.ai/v1
TTS_VOICE=khmer_female_1
```

---

## Usage

### Launch Application

#### Using Python Directly
```powershell
.\venv\Scripts\Activate.ps1
python main.py
```

#### Using Launch Script
```powershell
.\launch.bat
```

### Workflow

1. **Import Video**
   - Click "Select Video File"
   - Choose your MP4, MKV, MOV, or AVI file
   - View video metadata

2. **Transcribe Audio**
   - Click "1. Transcribe Audio"
   - Wait for Whisper to process (first run downloads model)
   - Review English transcript in the Transcript tab

3. **Translate to Khmer**
   - Click "2. Translate to Khmer"
   - OmniRoute translates each segment
   - Review and edit translations in the Translation tab

4. **Generate Khmer Speech**
   - Click "3. Generate Khmer Speech"
   - TTS generates audio for each Khmer segment
   - Progress updates shown

5. **Export Video**
   - Go to Export tab
   - Click "Choose Output Location"
   - Select output filename and location
   - Click "Export Dubbed Video"
   - Wait for processing
   - Original video quality preserved (stream copy)
   - Khmer SRT subtitle file generated alongside video

---

## Configuration

### Settings Dialog
Access via the "Settings" button in the main window.

**OmniRoute Translation**
- Base URL: Your OmniRoute endpoint
- API Key: Your authentication key
- Model: Translation model name (e.g., gpt-4, claude-3-opus)
- Test Connection: Verify settings

**Text-to-Speech**
- Provider: Currently supports "kiri"
- Base URL: TTS API endpoint
- API Key: Your TTS authentication key
- Voice ID: Khmer voice identifier
- Test Connection: Verify Khmer TTS support

**Processing Settings**
- Max Concurrent Requests: Parallel API calls (1-10)
- Request Timeout: API timeout in seconds (10-600)

---

## Khmer TTS Provider Setup

### Kiri TTS (Recommended)

**Important**: The Kiri TTS implementation is a placeholder based on common TTS API patterns. You must verify the actual Kiri API specification.

1. Visit [Kiri AI](https://kiri.ai) (or your Khmer TTS provider)
2. Sign up for an account
3. Obtain API key
4. Check API documentation for:
   - Correct base URL endpoint
   - Request format (JSON structure)
   - Available Khmer voices
   - Audio format support
   - Authentication method

5. Update `src/services/tts_service.py` if the API format differs from the placeholder implementation

### Alternative Providers
If using a different Khmer TTS provider:
1. Implement a new provider adapter in `src/services/tts_service.py`
2. Follow the existing `TTSService` interface
3. Add provider name to Settings dialog
4. Update `.env.example` with provider-specific settings

---

## Video Quality & Export

KhmerDub Studio preserves original video quality:

- **No Re-encoding**: Video stream copied directly (`-c:v copy`)
- **No Watermarks**: Clean output
- **Configurable Audio**: AAC encoding at 128k by default
- **Original Metadata**: Preserved where possible
- **No Truncation**: `-shortest` flag used carefully to match durations

The original video file is never modified. All processing creates new output files.

---

## Project Structure

```
KhmerDubStudio/
├── src/
│   ├── models/          # Data models (Project, DialogueSegment, VideoMetadata)
│   ├── services/        # Core services (FFmpeg, STT, TTS, Translation, Pipeline)
│   ├── ui/              # PySide6 GUI components (MainWindow, SettingsDialog)
│   ├── utils/           # Configuration and logging
│   └── workers/         # Background thread workers
├── tests/               # Unit tests (pytest)
├── output/              # Exported videos (created automatically)
├── temp/                # Temporary processing files (created automatically)
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── .env.example         # Example configuration
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

---

## Testing

Run unit tests:
```powershell
.\venv\Scripts\Activate.ps1
pytest tests/ -v
```

Run specific test file:
```powershell
pytest tests/test_models.py -v
```

**Note**: Some tests require real video files and API access. Unit tests focus on logic without external dependencies.

---

## Troubleshooting

### FFmpeg Not Found
- Verify FFmpeg is installed: `ffmpeg -version`
- Check PATH environment variable includes FFmpeg bin directory
- Restart terminal after PATH changes

### Whisper Model Download
- First transcription downloads Whisper model (300MB-1.5GB depending on model)
- Requires internet connection
- Stored in user cache directory
- Subsequent runs use cached model

### API Connection Errors
- Verify API keys in `.env` file
- Test connections in Settings dialog
- Check base URLs are correct (no trailing slashes in .env, though code handles it)
- Verify firewall allows outbound connections
- Check OmniRoute service is running (if self-hosted)

### Translation Errors
- Verify OmniRoute model name is correct
- Check API quota/credits
- Review logs in `logs/khmerdub.log`

### TTS Errors
- Verify Khmer language support with provider
- Check voice ID exists for Khmer
- Verify API format matches provider documentation
- Test with simple Khmer text: "សួស្តី"

### Memory Issues
- Use smaller Whisper model (base, small, medium instead of large)
- Process shorter videos
- Close other applications
- Increase virtual memory

### Performance Optimization
- Use GPU-enabled Whisper if available
- Reduce max concurrent requests
- Use faster Whisper model (base, small)
- Process videos in segments

---

## Features Implemented

✅ Complete application structure
✅ FFmpeg video processing with stream copy
✅ Whisper speech-to-text transcription
✅ OmniRoute translation integration
✅ Khmer TTS adapter (Kiri placeholder)
✅ PySide6 dark-themed GUI
✅ Transcript and translation editors
✅ Background worker threads
✅ Settings dialog with connection testing
✅ SRT subtitle generation
✅ Project state management
✅ Video export without re-encoding
✅ Progress indicators and error handling
✅ Unit tests
✅ Configuration management
✅ Logging system

---

## Features Requiring API Credentials

The following features are implemented but require valid API credentials to function:

🔑 **OmniRoute Translation**: Requires valid OmniRoute endpoint and API key
🔑 **Khmer TTS**: Requires valid Kiri (or compatible) TTS API key and verified endpoint
🔑 **Cloud Whisper** (optional): Local Whisper works without credentials

---

## Known Limitations

1. **Kiri TTS API**: Implementation is a placeholder. Actual API format must be verified from official documentation.
2. **Audio Timing**: Long Khmer translations may not fit original English timing perfectly. Manual adjustment may be needed.
3. **Speaker Diarization**: Whisper base model doesn't include speaker labels. Use Whisper with diarization or upgrade model.
4. **Voice Selection**: Single voice per project. Multi-character voice assignment not yet implemented.
5. **Segment Regeneration**: Individual segment regeneration implemented in pipeline but not exposed in GUI yet.

---

## Development

### Adding Features
1. Create feature branch: `git checkout -b feature/new-feature`
2. Implement changes
3. Add unit tests in `tests/`
4. Update README if needed
5. Commit with descriptive message
6. Test thoroughly

### Code Style
- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Keep functions focused and modular

---

## License

This project is provided as-is for educational and commercial use.

---

## Support

For issues, questions, or contributions:
1. Check existing documentation
2. Review logs in `logs/khmerdub.log`
3. Test API connections in Settings dialog
4. Verify video file is valid with FFprobe

---

## Credits

**Technologies Used**:
- [PySide6](https://www.qt.io/qt-for-python) - Desktop GUI framework
- [FFmpeg](https://ffmpeg.org/) - Video/audio processing
- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition
- [Python](https://www.python.org/) - Core language

**AI Services**:
- OmniRoute - Translation routing
- Kiri TTS - Khmer text-to-speech

---

## Quick Start Checklist

- [ ] Python 3.11+ installed
- [ ] FFmpeg installed and in PATH
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created from `.env.example`
- [ ] OmniRoute API key configured
- [ ] Khmer TTS API key configured (Kiri or alternative)
- [ ] API connections tested in Settings dialog
- [ ] Application launches successfully
- [ ] Test video imported successfully
- [ ] Transcription works (downloads Whisper model on first run)
- [ ] Translation works (requires OmniRoute)
- [ ] TTS works (requires valid Khmer TTS provider)
- [ ] Export produces valid video

---

**KhmerDub Studio** - Built for professional Khmer video dubbing with AI.
