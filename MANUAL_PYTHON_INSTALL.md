# Quick Manual Fix for Python Installation

## Current Situation
- Python 3.11 is NOT installed on your system
- You have Python 3.12 from msys64 (not suitable)
- The Microsoft Store Python shortcut is interfering

## Step-by-Step Manual Installation

### Step 1: Download Python 3.11.9

1. Open this link in your browser:
   ```
   https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
   ```

2. Save the installer to your Desktop or Downloads

### Step 2: Install Python 3.11.9

1. **Double-click** the downloaded `python-3.11.9-amd64.exe`

2. **IMPORTANT - On the first screen:**
   - ✅ **CHECK** "Add python.exe to PATH" (bottom checkbox)
   - ✅ **CHECK** "Install for all users" (if available)
   - Click **"Customize installation"** (not "Install Now")

3. **Optional Features screen:**
   - ✅ Keep all boxes checked
   - Click **Next**

4. **Advanced Options screen:**
   - ✅ CHECK "Install for all users"
   - ✅ CHECK "Add Python to environment variables"
   - Install location should be: `C:\Program Files\Python311\`
   - Click **Install**

5. Wait for installation to complete

6. Click **"Disable path length limit"** if prompted (important!)

7. Click **Close**

### Step 3: Verify Installation

1. **Close ALL PowerShell windows** (important - PATH updates won't apply otherwise)

2. Open a **NEW PowerShell window**

3. Type:
   ```powershell
   python --version
   ```

4. You should see: `Python 3.11.9`

### Step 4: Fix KhmerDubStudio

Once Python 3.11.9 is verified:

```powershell
cd D:\KhmerDubStudio

# Remove old venv
Remove-Item -Path venv -Recurse -Force

# Create new venv with Python 3.11
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Test the app
.\START_FRESH.bat
```

## Troubleshooting

### Problem: "python: command not found" after installation

**Solution:**
1. Close ALL PowerShell windows
2. Open Task Manager (Ctrl+Shift+Esc)
3. End any "python.exe" processes
4. Open NEW PowerShell window
5. Try `python --version` again

### Problem: Still shows Python 3.13 or wrong version

**Solution:**
```powershell
# Use the full path directly
"C:\Program Files\Python311\python.exe" --version

# If that works, use it to create venv:
cd D:\KhmerDubStudio
"C:\Program Files\Python311\python.exe" -m venv venv
```

### Problem: Permission denied during installation

**Solution:**
- Right-click the installer
- Select "Run as Administrator"
- Try again

## Quick Test After Setup

```powershell
# Should show Python 3.11.9
python --version

# Should show venv location
Get-Command python | Select-Object Source

# Should be: D:\KhmerDubStudio\venv\Scripts\python.exe
```

---

**Once Python 3.11.9 is installed and verified, come back and we'll recreate your venv!**
