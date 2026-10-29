@echo off
REM Setup SpeechLab with Python 3.11
echo ========================================
echo SpeechLab Setup for KhmerDubStudio
echo ========================================
echo.

echo This will set up SpeechLab TTS engine with Python 3.11
echo.
echo The setup will:
echo 1. Create a virtual environment
echo 2. Install PyTorch (CPU version)
echo 3. Install SpeechLab dependencies
echo 4. Download Khmer TTS models (optional)
echo.
pause

cd D:\speechlab

echo.
echo Starting SpeechLab setup...
echo Answer 'Y' to install PyTorch CPU version
echo Answer 'Y' to install nanovllm_km (Khmer voice model)
echo.
py -3.11 studio.py setup

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Start SpeechLab: py -3.11 studio.py start
echo 2. Start Adapter: (in D:\KhmerDubStudio) .\START_SPEECHLAB_ADAPTER.bat
echo 3. Start KhmerDub Studio: .\START_FRESH.bat
echo.
pause
