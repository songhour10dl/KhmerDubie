@echo off
REM Fix SpeechLab Python 3.13 to 3.11 Migration
echo ========================================
echo SpeechLab - Fix Python Version
echo ========================================
echo.

echo This will remove the old Python 3.13 venv and create a new one with Python 3.11
echo.

echo Step 1: Close all Python/SpeechLab processes
echo Please close any running SpeechLab or Python windows now!
echo.
pause

echo.
echo Step 2: Killing any remaining Python processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Step 3: Removing old venv...
cd D:\speechlab
rd /s /q backend\venv 2>nul
timeout /t 2 /nobreak >nul
rd /s /q backend\venv 2>nul
timeout /t 2 /nobreak >nul

if exist backend\venv (
    echo WARNING: Could not fully remove venv. Some files may be locked.
    echo Try manually deleting D:\speechlab\backend\venv and run this script again.
    pause
    exit /b 1
)

echo Done!
echo.

echo Step 4: Creating fresh venv with Python 3.11...
py -3.11 -m venv backend\venv

if not exist backend\venv\Scripts\python.exe (
    echo ERROR: Failed to create venv!
    pause
    exit /b 1
)

echo Done!
echo.

echo Step 5: Verifying Python version...
backend\venv\Scripts\python.exe --version

echo.
echo ========================================
echo Cleanup Complete!
echo ========================================
echo.
echo Now run the setup:
echo   cd D:\speechlab
echo   py -3.11 studio.py setup
echo.
pause
