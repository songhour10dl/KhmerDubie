# Fix Python Version Issue

## Problem
You're using Python 3.13.14, which is too new and causes crashes with NumPy and PySide6.
Error: `Exit code: -1073741819` (ACCESS VIOLATION crash)

## Solution: Downgrade to Python 3.11

### Step 1: Install Python 3.11

1. Download Python 3.11.9 (latest stable 3.11):
   - Go to: https://www.python.org/downloads/
   - Download: **Python 3.11.9** (Windows installer 64-bit)

2. Run the installer:
   - ✅ Check "Add Python 3.11 to PATH"
   - Click "Install Now"

### Step 2: Recreate Virtual Environment

Open PowerShell in `D:\KhmerDubStudio`:

```powershell
# Remove old virtual environment
Remove-Item -Recurse -Force venv

# Create new venv with Python 3.11
py -3.11 -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Test the Application

```powershell
# Should work without crashes now
.\START_FRESH.bat
```

## Why This Happened

- Python 3.13 was released in October 2024 and is very new
- NumPy 1.26.4 was built with MINGW-W64 which is experimental on Python 3.13
- The warnings "CRASHES ARE TO BE EXPECTED" actually happened
- Python 3.11 is the recommended stable version for scientific Python packages

## Verification

After fixing, you should see:
```
Starting KhmerDub Studio...
```
And the GUI window will open without crashes.

## Alternative: Use Python 3.10

If Python 3.11 doesn't work, try Python 3.10.11:
```powershell
py -3.10 -m venv venv
```

Both Python 3.10 and 3.11 are fully stable with NumPy and PySide6.
