# 🦙 Ollama on Kaggle - Complete Setup Guide

## QUICK START (3 Steps)

### Step 1: Open Kaggle Notebook
- Go to: https://www.kaggle.com/code/slash021/notebook441b59526b/edit

### Step 2: Replace All Code with This:

```python
# CELL 1: Install Ollama
!curl -fsSL https://ollama.com/install.sh | sh
```

```python
# CELL 2: Start Server
import subprocess, time, os
os.environ['OLLAMA_HOST'] = '0.0.0.0:11434'
process = subprocess.Popen(['ollama', 'serve'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
time.sleep(15)
print("✅ Ollama server started!")
```

```python
# CELL 3: Pull Model
!ollama pull qwen2.5:0.5b
```

```python
# CELL 4: Install ngrok for public URL
!pip install pyngrok -q
from pyngrok import ngrok
ngrok.kill()  # Clear old tunnels
public_url = ngrok.connect(11434, "http")
print(f"🌐 PUBLIC URL: {public_url}")
print("⚠️  COPY THIS URL AND PASTE IT IN TELEGRAM!")
```

```python
# CELL 5: Keep Alive (run this last)
import time
from datetime import datetime
while True:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Ollama running...")
    time.sleep(300)
```

### Step 3: Run & Share URL
1. Run all cells
2. Copy the ngrok URL from Cell 4
3. Paste it here in Telegram
4. I'll configure OpenClaw to use it!

---

## 🔗 OpenClaw Configuration

Once you give me the ngrok URL, I'll add this to your OpenClaw config:

```json
{
  "id": "ollama-kaggle-fallback",
  "name": "Ollama Kaggle Fallback",
  "provider": "ollama",
  "baseUrl": "https://xxxx.ngrok.io/v1",
  "apiKey": "ollama-kaggle",
  "models": ["qwen2.5:0.5b"]
}
```

---

## ⚠️ IMPORTANT WARNINGS

1. **URL Changes:** ngrok URL changes every restart
2. **Session Timeout:** Kaggle times out after ~9 hours without activity
3. **Keep Running:** Cell 5 keeps the session alive
4. **Free Tier:** Ngrok free tier has limits but works for fallback

---

## 🔄 For 24/7 Operation

**Option A: Always-On Notebook**
- Just keep Cell 5 running indefinitely
- Check occasionally that it's still alive

**Option B: Scheduled Runs**
- Use Kaggle's "Schedule" feature
- Runs automatically every X hours

**Option C: Multiple Backups**
- Create 2-3 notebooks on different accounts
- Rotate between them for redundancy

---

## ✅ TESTING

Once connected, test with:
```
ollama run qwen2.5:0.5b "Hello, are you working?"
```

Expected output: Confirmation message from the model.

---

**Tez — go to your Kaggle notebook now and run these cells!**
**Then paste the ngrok URL here and I'll connect it!**
