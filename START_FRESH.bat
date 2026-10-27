@echo off
REM KhmerDub Studio Launcher with Cache Clear
REM This ensures app always uses latest code

echo ========================================
echo KhmerDub Studio - Starting Fresh
echo ========================================
echo.

REM Clear Python cache to ensure latest code is used
echo Clearing Python cache...
for /d /r %%i in (__pycache__) do @if exist "%%i" rd /s /q "%%i"
del /s /q *.pyc 2>nul
echo Cache cleared!
echo.

REM Show current settings
echo Current Settings:
echo - Translation Provider: HYBRID (saves tokens!)
echo - Manual Translations: 41 phrases
echo - OmniRoute Model: kr/claude-sonnet-4.5 (backup only)
echo.

REM Start the app
echo Starting KhmerDub Studio...
echo.
python main.py

pause
