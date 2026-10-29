@echo off
REM Script to reinstall KhmerDubStudio with Python 3.11
echo ========================================
echo KhmerDubStudio - Python 3.11 Reinstall
echo ========================================
echo.

echo STEP 1: Please download Python 3.11.9 if not installed:
echo https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
echo.
echo Run the installer and CHECK "Add Python 3.11 to PATH"
echo.
pause

echo.
echo STEP 2: Checking for Python 3.11...
python --version
echo.

echo If you see Python 3.11.x above, press any key to continue.
echo If you see Python 3.13.x, you need to uninstall Python 3.13 first.
echo.
pause

echo.
echo STEP 3: Removing old virtual environment...
echo Please CLOSE any terminals that have (venv) active!
echo.
pause

REM Force delete venv (run multiple times to handle locked files)
rd /s /q venv 2>nul
timeout /t 2 /nobreak >nul
rd /s /q venv 2>nul
timeout /t 2 /nobreak >nul
rd /s /q venv 2>nul

echo.
echo STEP 4: Creating new virtual environment with Python 3.11...
python -m venv venv

if not exist venv\Scripts\activate.bat (
    echo ERROR: Failed to create virtual environment!
    echo Make sure Python 3.11 is installed correctly.
    pause
    exit /b 1
)

echo.
echo STEP 5: Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo STEP 6: Upgrading pip...
python -m pip install --upgrade pip

echo.
echo STEP 7: Installing dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo You can now run: START_FRESH.bat
echo.
pause
