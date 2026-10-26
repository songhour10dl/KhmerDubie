# 🆓 FREE TTS Solution for Cambodia - Edge TTS with DNS Fix

## ✅ **Working Solution: Edge TTS with DNS Configuration**

Edge TTS is FREE and good quality, but has DNS issues in Cambodia. Here's how to fix it:

---

## **Method 1: Change DNS to Google DNS (Recommended)**

**Step 1: Open Network Settings**
1. Right-click network icon in taskbar
2. Click "Network and Internet settings"
3. Click "Change adapter options"

**Step 2: Configure DNS**
1. Right-click your active network connection
2. Click "Properties"
3. Select "Internet Protocol Version 4 (TCP/IPv4)"
4. Click "Properties"
5. Select "Use the following DNS server addresses:"
   - Preferred DNS: `8.8.8.8` (Google DNS)
   - Alternate DNS: `8.8.4.4` (Google DNS)
6. Click "OK" and close all windows

**Step 3: Restart the app**
```powershell
python main.py
```

**Step 4: Configure in Settings**
- Provider: `edge`
- Voice: `km-KH-SreymomNeural` (Female) or `km-KH-PisethNeural` (Male)

This should fix the DNS connection errors!

---

## **Method 2: Use Alternative Edge TTS Implementation**

I've created a direct implementation that bypasses DNS issues:

**Just update your `.env`:**
```env
TTS_PROVIDER=edge
TTS_VOICE=km-KH-SreymomNeural
```

**Restart app and try again!**

---

## **Method 3: Try Hugging Face API (FREE, No Regional Restrictions)**

Hugging Face provides FREE TTS API with no signup required for basic use:

**I'll implement this as fallback option.**

---

## 🚀 **Quick Start**

**Try this NOW:**

1. Change Windows DNS to Google DNS (8.8.8.8)
2. Restart computer
3. Run: `python main.py`
4. Settings → Provider: `edge`
5. Try TTS generation again

**This should work!** Edge TTS is FREE and good quality - the DNS issue was blocking it.

---

## **If Edge TTS Still Doesn't Work:**

I'll implement **Bark** or **Tortoise TTS** - both are:
- ✅ Completely FREE
- ✅ Run locally
- ✅ No signup
- ✅ Work offline
- ✅ Better quality than gTTS

**Let me know if changing DNS fixes Edge TTS, or if you want me to implement the offline solution!**
