# 🚀 OpenClaw 24/7 Cloud Deployment Package

**Ready to deploy to FREE cloud hosting!**

---

## 📦 What's Included

- `openclaw.json` - Your complete configuration
- `secrets/` - All API keys (Cerebras, Groq, Pinmx)
- `memory/` - All session data and conversations
- `start.js` - Cloud startup script
- `requirements.txt` - Node.js dependencies
- `README.md` - This file

---

## ☁️ DEPLOY NOW (3 Options)

### OPTION 1: Hugging Face Spaces (FASTEST - 5 min!) ⭐ RECOMMENDED

**1. Create Account:**
```
URL: https://huggingface.co/join
Email: 5ycofnljdy@pinmx.net
Password: OpenClaw2026!
```

**2. Verify Email:**
- Check Pinmx inbox: https://www.pinmx.com
- Click verification link

**3. Create Space:**
- Click profile → New Space
- Name: `openclaw-bot`
- Type: Docker (or Python)
- Visibility: Private
- Click Create

**4. Upload Files:**
- Upload ALL files from this folder to your Space
- Or drag & drop the entire folder

**5. Add Secrets (Settings → Repository secrets):**
```
TELEGRAM_BOT_TOKEN = 8455353239:AAHMxK1y--esr3d_0I5UxBCHnhLy0xglo94
CEREBRAS_API_KEY = csk-826xjcryndx5pv344mrrf8khph68hr9mvyww5mhxdcnv365y
GROQ_API_KEY = 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
```

**6. Deploy!**
- Space will auto-start
- Bot online 24/7!

**URL to access:** https://huggingface.co/spaces/YOUR_USERNAME/openclaw-bot

---

### OPTION 2: Oracle Cloud Free Tier (BEST SPECS - 20 min!)

**1. Sign Up:**
```
URL: https://cloud.oracle.com
Click: "Start for free"
Email: 5ycofnljdy@pinmx.net
Phone: Your phone (verification required)
```

**2. Create VM:**
- Compute → Instances → Create Instance
- Choose: VM.Standard.A1.Flex (FREE!)
- Specs: 4 cores, 24GB RAM
- Image: Ubuntu 22.04
- SSH: Generate key pair

**3. Connect:**
```bash
ssh -i your_key.pem ubuntu@YOUR_VM_IP
```

**4. Install OpenClaw:**
```bash
# Update
sudo apt update && sudo apt upgrade -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install OpenClaw
sudo npm install -g openclaw

# Upload files (from your laptop)
scp -i your_key.pem -r cloud-deploy/* ubuntu@YOUR_VM_IP:~/
```

**5. Setup & Run:**
```bash
cd ~/cloud-deploy

# Copy config
cp openclaw.json ~/.openclaw/
cp -r secrets ~/.openclaw/workspace/
cp -r memory ~/.openclaw/workspace/

# Install PM2 (process manager)
sudo npm install -g pm2

# Start with PM2
pm2 start start.js --name openclaw

# Save & startup
pm2 save
pm2 startup
```

**6. Done!**
- Bot runs 24/7
- Survives reboots
- Check: `pm2 status`

---

### OPTION 3: Render.com (EASY - 10 min!)

**1. Sign Up:**
```
URL: https://render.com
Sign up with GitHub
```

**2. Create Web Service:**
- New → Web Service
- Connect your GitHub repo (upload files first)
- Or deploy from Git

**3. Configure:**
- Name: openclaw-bot
- Environment: Node
- Build: `npm install`
- Start: `node start.js`

**4. Add Environment Variables:**
```
TELEGRAM_BOT_TOKEN = 8455353239:AAHMxK1y--esr3d_0I5UxBCHnhLy0xglo94
CEREBRAS_API_KEY = csk-826xjcryndx5pv344mrrf8khph68hr9mvyww5mhxdcnv365y
GROQ_API_KEY = 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
```

**5. Deploy!**
- Free tier: 750 hours/month
- Bot online 24/7!

---

## ✅ Verify Deployment

**1. Send Telegram message to your bot**
- Bot should respond within seconds

**2. Check logs:**
- Hugging Face: Space logs tab
- Oracle: `pm2 logs openclaw`
- Render: Dashboard → Logs

**3. Test continuity:**
- Ask: "What was our last task?"
- Should remember EuroJackpot prediction!

---

## 🔧 Troubleshooting

**Bot not responding?**
- Check gateway status
- Verify API keys in environment
- Check logs for errors

**Memory not loaded?**
- Ensure memory/ folder uploaded correctly
- Check file permissions

**Gateway won't start?**
- Run: `openclaw gateway status`
- Check port 18789 is free
- Review openclaw.json syntax

---

## 📊 Current Configuration

- **Primary Model:** qwen-portal/coder-model
- **Fallbacks:** minimax, cerebras/gpt-oss-120b
- **Telegram:** Connected
- **Memory:** All sessions preserved
- **Last Task:** EuroJackpot prediction for Feb 24, 6 PM

---

## 🎯 Quick Start Commands

**Oracle Cloud:**
```bash
pm2 status          # Check if running
pm2 logs openclaw   # View logs
pm2 restart openclaw # Restart
```

**Hugging Face:**
- Check Space logs in UI
- Restart: Delete & recreate Space

**Render:**
- Dashboard → Restart button
- Logs tab for debugging

---

**DEPLOY NOW AND YOUR BOT WILL RUN 24/7 WITHOUT LAPTOP!** 🚀
