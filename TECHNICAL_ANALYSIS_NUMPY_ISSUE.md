# Technical Analysis: NumPy MINGW-W64 Runtime Errors with Python 3.13

## Executive Summary

Your KhmerDub Studio application is experiencing **critical compatibility issues** between Python 3.13.14 and NumPy 1.26.4 built with the experimental MINGW-W64 compiler. This results in floating-point computation errors and **application crashes** (exit code -1073741819 = ACCESS VIOLATION). This configuration is **unsuitable for production**.

---

## 1. Source and Implications of MINGW-W64 Warning

### Root Cause
```
Warning: Numpy built with MINGW-W64 on Windows 64 bits is experimental, 
and only available for testing. You are advised not to use it for production.
CRASHES ARE TO BE EXPECTED
```

**What is MINGW-W64?**
- MINGW-W64 is a Windows port of the GCC (GNU Compiler Collection) compiler
- NumPy wheels built with MINGW-W64 are **experimental** and not production-ready
- Official NumPy Windows builds should use MSVC (Microsoft Visual C++)

**Why This Warning Appears:**
- Python 3.13 was released in **October 2024** (very recent)
- Pre-compiled NumPy wheels for Python 3.13 may not be available from official sources
- pip falls back to building NumPy from source using MINGW-W64
- MINGW-W64 builds have known stability issues on Windows

**Production Implications:**
- ❌ **Crashes expected** - The warning explicitly states this
- ❌ **Floating-point precision errors** - Invalid mathematical operations
- ❌ **Access violations** - Your application exits with code -1073741819 (0xC0000005)
- ❌ **Unpredictable behavior** - Scientific computations may produce incorrect results
- ❌ **No vendor support** - NumPy developers explicitly discourage production use

---

## 2. Analysis of RuntimeWarning Errors

### Error Details
```python
# File: numpy/core/getlimits.py

Line 225: RuntimeWarning: invalid value encountered in exp2
  epsneg_f128 = exp2(ld(-113))

Line 226: RuntimeWarning: invalid value encountered in exp2
  tiny_f128 = exp2(ld(-16382))

Line 240: RuntimeWarning: invalid value encountered in exp2
  eps=exp2(ld(-112))

Line 41: RuntimeWarning: invalid value encountered in nextafter
  self._smallest_subnormal = nextafter(...)

Line 52: RuntimeWarning: invalid value encountered in log10
  self.precision = int(-log10(self.eps))
```

### Technical Explanation

**What is `getlimits.py` doing?**
- This module determines floating-point precision limits for the system
- It calculates machine epsilon, smallest/largest representable numbers
- These values are fundamental for all NumPy numerical operations

**Why are these operations failing?**
1. **IEEE 754 float128 (f128) not properly supported**
   - `exp2(ld(-113))` and `exp2(ld(-16382))` calculate float128 precision bounds
   - MINGW-W64's GCC compiler has incomplete float128 support on Windows
   - These operations return `NaN` (Not a Number) instead of valid values

2. **nextafter() function failure**
   - `nextafter()` finds the next representable floating-point number
   - MINGW-W64's math library implementation is incomplete
   - Critical for determining subnormal number ranges

3. **Cascading failures**
   - When epsilon values are NaN, `log10(self.eps)` fails
   - This corrupts NumPy's entire floating-point type system
   - All subsequent numerical operations become unreliable

---

## 3. Root Cause: Python 3.13 + NumPy Compatibility

### Is this a Python 3.13 issue or MINGW-W64 issue?

**Answer: BOTH - They compound each other**

**Python 3.13 Factors:**
- ✅ Python 3.13.0 released: October 7, 2024
- ❌ NumPy 1.26.4 released: February 2024 (pre-dates Python 3.13 stable release)
- ❌ No official MSVC-compiled NumPy wheels for Python 3.13 on Windows yet
- ❌ pip attempts source compilation with available compiler (MINGW-W64)

**MINGW-W64 Factors:**
- ❌ Experimental on Windows 64-bit
- ❌ Incomplete C99/IEEE 754 math library support
- ❌ ABI incompatibilities with Windows system libraries
- ❌ Known issues with long double (float128) types

**Why Python 3.10/3.11 work fine:**
- Official NumPy wheels compiled with MSVC are available
- Mature ecosystem with tested compatibility
- No fallback to source compilation needed

### Evidence from Your System
```
Exit code: -1073741819 (0xC0000005)
```
This is **STATUS_ACCESS_VIOLATION** - a memory access error indicating:
- Corrupted floating-point state
- Invalid memory operations from math library
- Hard crash before application window can open

---

## 4. Step-by-Step Resolution Guide

### ✅ RECOMMENDED SOLUTION: Downgrade to Python 3.11

#### Step 1: Install Python 3.11.9 (Latest Stable 3.11)

**Download:**
```
https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
```

**Installation:**
1. Run the installer as Administrator
2. ✅ **CRITICAL:** Check "Add Python 3.11 to PATH"
3. ✅ Check "Install for all users" (optional but recommended)
4. Click "Customize installation"
5. Ensure "pip" is selected
6. Click "Install"

**Verification:**
```powershell
python --version
# Should show: Python 3.11.9
```

#### Step 2: Clean Environment Reset

**Option A: Use the automated script (RECOMMENDED)**
```powershell
cd D:\KhmerDubStudio

# Close ALL terminals with (venv) active
# Open a NEW PowerShell window

.\REINSTALL_PYTHON311.bat
```

**Option B: Manual cleanup**
```powershell
cd D:\KhmerDubStudio

# Deactivate venv if active
deactivate

# Force remove old venv (close all Python processes first)
Remove-Item -Path venv -Recurse -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Remove-Item -Path venv -Recurse -Force -ErrorAction SilentlyContinue

# Create fresh venv with Python 3.11
python -m venv venv

# Activate
.\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

#### Step 3: Verify NumPy Installation

```powershell
python -c "import numpy as np; print(f'NumPy {np.__version__}'); print(f'Location: {np.__file__}'); import sys; print(f'Python: {sys.version}')"
```

**Expected output:**
```
NumPy 1.26.4 (or newer)
Location: D:\KhmerDubStudio\venv\Lib\site-packages\numpy\...
Python: 3.11.9 (main, ...) [MSC v.XXXX 64 bit (AMD64)]
                              ^^^^^ Should show MSC (Microsoft Compiler)
```

**Key indicator:** `MSC v.XXXX` means NumPy was compiled with MSVC (good)

#### Step 4: Test Application

```powershell
.\START_FRESH.bat
```

**Expected result:**
- No NumPy warnings
- GUI window opens successfully
- Clean startup log

---

### 🔧 ALTERNATIVE SOLUTIONS (If Python 3.11 unavailable)

#### Option 1: Use Python 3.10.11
```powershell
# Download: https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
# Same process as Python 3.11
```

#### Option 2: Install Pre-Release NumPy for Python 3.13 (NOT RECOMMENDED)
```powershell
# Only if you must use Python 3.13
pip install --pre --upgrade numpy

# Or try nightly build
pip install -i https://pypi.anaconda.org/scientific-python-nightly-wheels/simple numpy
```
⚠️ **Warning:** Still experimental, no stability guarantees

#### Option 3: Use Conda Environment (Advanced)
```powershell
# Install Miniconda: https://docs.conda.io/en/latest/miniconda.html
conda create -n khmerdub python=3.11
conda activate khmerdub
conda install numpy scipy
pip install -r requirements.txt
```
Conda provides pre-compiled binaries with better Windows compatibility

---

## Verification Checklist

After following the resolution steps:

- [ ] Python version shows 3.11.x or 3.10.x
- [ ] `pip list | findstr numpy` shows NumPy installed in venv
- [ ] No MINGW-W64 warnings appear
- [ ] No RuntimeWarning errors in getlimits.py
- [ ] Application starts without crashes
- [ ] GUI window displays correctly
- [ ] Exit code is 0 (not -1073741819)

---

## Technical Background: Why This Matters

### Impact on KhmerDub Studio

Your application uses NumPy indirectly through:
1. **openai-whisper** (speech recognition) - Heavy NumPy usage for audio processing
2. **torch/PyTorch** (if used) - Depends on NumPy for tensor operations
3. **Audio processing** - FFT, resampling, signal processing

**Corrupted NumPy = Unreliable Results:**
- Audio transcription errors
- Incorrect timing calculations
- Potential data corruption
- Random crashes during processing

---

## Recommended Production Configuration

```plaintext
Operating System: Windows 10/11 64-bit
Python Version:   3.11.9 (or 3.10.11)
NumPy Source:     PyPI official wheels (MSVC compiled)
Virtual Env:      Yes (isolated dependencies)
Long Paths:       Enabled (via enable_long_paths.ps1)
```

---

## Summary

| Issue | Cause | Solution |
|-------|-------|----------|
| MINGW-W64 warning | Python 3.13 too new, no official wheels | Use Python 3.11.9 |
| exp2/nextafter errors | MINGW-W64 incomplete math lib | Official MSVC NumPy wheels |
| Access violation crash | Corrupted floating-point state | Downgrade Python version |
| Production instability | Experimental build chain | Stable Python + official wheels |

**Action Required:** Install Python 3.11.9 and run `REINSTALL_PYTHON311.bat`

---

*Last Updated: 2026-10-29*
*Python 3.13 Status: NumPy official wheels not yet available*
