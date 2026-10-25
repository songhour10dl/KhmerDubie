@echo off
REM KhmerDub Studio Launch Script for Windows

echo ========================================
echo KhmerDub Studio - AI Video Dubbing
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found!
    echo Please run setup first:
    echo   python -m venv venv
    echo   .\venv\Scripts\Activate.ps1
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist ".env" (
    echo Warning: .env file not found!
    echo Please copy .env.example to .env and configure your API keys.
    echo.
    pause
)

REM Launch application
echo Starting KhmerDub Studio...
echo.
python main.py

REM Deactivate on exit
deactivate

echo.
echo Application closed.
pause
