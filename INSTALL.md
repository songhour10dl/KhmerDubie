# Installation Guide for KhmerDub Studio

## Windows Long Path Issue Fix

If you encounter the error:
```
ERROR: Could not install packages due to an OSError: [Errno 2] No such file or directory
HINT: This error might have occurred since this system does not have Windows Long Path support enabled.
```

### Solution 1: Enable Long Path Support (Recommended)

1. **Run the provided script as Administrator:**
   - Right-click on PowerShell
   - Select "Run as Administrator"
   - Navigate to the project directory:
     ```powershell
     cd D:\KhmerDubStudio
     ```
   - Run the script:
     ```powershell
     .\enable_long_paths.ps1
     ```
   - **Restart your computer** after running the script
   - After restart, install dependencies:
     ```powershell
     pip install -r requirements.txt
     ```

### Solution 2: Manual Registry Edit (Alternative)

1. Press `Win + R`, type `regedit`, and press Enter
2. Navigate to: `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem`
3. Find or create a DWORD value named `LongPathsEnabled`
4. Set its value to `1`
5. **Restart your computer**
6. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

### Solution 3: Use Virtual Environment in Shorter Path (Workaround)

If you cannot enable Long Path support:

1. Create a virtual environment in a shorter path:
   ```powershell
   python -m venv C:\venv\khmer
   ```

2. Activate the virtual environment:
   ```powershell
   C:\venv\khmer\Scripts\Activate.ps1
   ```

3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

 4. Run the application from the project directory:
    ```powershell
    cd D:\KhmerDubStudio
    python run.py
    ```

## Normal Installation (After Long Path is Enabled)

1. **Install Python 3.10 or higher**

2. **Install FFmpeg**
   - Download from: https://ffmpeg.org/download.html
   - Add FFmpeg to your PATH

3. **Clone or download the repository**

4. **Install Python dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

5. **Configure environment variables:**
   - Copy `.env.example` to `.env`
   - Update the settings in `.env` with your configuration

6. **Run the application:**
   ```powershell
   python run.py
   ```

## Troubleshooting

### Error: "FFmpeg not found"
- Make sure FFmpeg is installed and added to your PATH
- Or specify the path in `.env`:
  ```
  FFMPEG_PATH=C:\path\to\ffmpeg.exe
  FFPROBE_PATH=C:\path\to\ffprobe.exe
  ```

### Error: "Module not found"
- Make sure all dependencies are installed: `pip install -r requirements.txt`

### Application crashes on "Generate Khmer Speech"
- Make sure `TTS_PROVIDER=custom` in your `.env` file
- The custom provider works offline without external dependencies

### Audio sync issues
- Re-export the video after generating Khmer speech
- The latest version uses timeline-based composition for perfect sync

## System Requirements

- **OS:** Windows 10/11 (with Long Path support enabled)
- **Python:** 3.10 or higher
- **RAM:** 8GB minimum, 16GB recommended
- **Disk Space:** 5GB free space for models and temporary files
- **FFmpeg:** Required for video/audio processing
