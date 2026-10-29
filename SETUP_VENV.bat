@echo off
REM Manual setup script for Python 3.11 environment
echo ========================================
echo KhmerDubStudio - Python 3.11 Setup
echo ========================================
echo.

echo Step 1: Removing old virtual environment...
rd /s /q venv 2>nul
timeout /t 2 /nobreak >nul
echo Done.
echo.

echo Step 2: Creating new virtual environment with Python 3.11...
py -3.11 -m venv venv --without-pip
if errorlevel 1 (
    echo ERROR: Failed to create venv. Make sure Python 3.11 is installed.
    pause
    exit /b 1
)
echo Done.
echo.

echo Step 3: Installing pip manually...
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
venv\Scripts\python.exe get-pip.py
del get-pip.py
echo Done.
echo.

echo Step 4: Verifying installation...
venv\Scripts\python.exe --version
venv\Scripts\pip.exe --version
echo.

echo Step 5: Installing dependencies...
venv\Scripts\pip.exe install -r requirements.txt
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo You can now run: START_FRESH.bat
echo.
pause
