@echo off
REM Start SpeechLab TTS Adapter for KhmerDubStudio
echo ========================================
echo Starting SpeechLab TTS Adapter
echo ========================================
echo.

echo IMPORTANT: Make sure SpeechLab is running first!
echo SpeechLab should be at: http://localhost:8880
echo.
echo Press Ctrl+C to cancel, or
pause

echo.
echo Starting adapter on http://localhost:8881...
echo.

cd speechlab_adapter
py -3.11 adapter.py

pause
