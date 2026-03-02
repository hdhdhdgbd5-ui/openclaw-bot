# 🚀 OPENCLAW 24/7 CLOUD DEPLOYMENT

## Quick Deploy to FREE Cloud Hosting

### OPTION 1: Hugging Face Spaces (EASIEST - 5 minutes!)

**Step 1: Create Account**
1. Go to https://huggingface.co/join
2. Sign up with email: `5ycofnljdy@pinmx.net`
3. Password: `OpenClaw2026!`
4. Verify email (check Pinmx inbox)

**Step 2: Create Space**
1. Click profile → New Space
2. Name: `openclaw-bot`
3. License: MIT
4. Visibility: Private
5. Click Create

**Step 3: Upload Files**
Upload these files to your Space:

**requirements.txt:**
```
openclaw
python-telegram-bot
requests
```

**run.py:**
```python
import os
import subprocess

# Set environment variables from secrets
os.environ['TELEGRAM_BOT_TOKEN'] = '8455353239:AAHMxK1y--esr3d_0I5UxBCHnhLy0xglo94'
os.environ['CEREBRAS_API_KEY'] = 'csk-826xjcryndx5pv344mrrf8khph68hr9mvyww5mhxdcnv365y'
os.environ['GROQ_API_KEY'] = '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'

# Start OpenClaw gateway
subprocess.run(['openclaw', 'gateway', '--port', '18789'])
```

**Step 4: Add Secrets**
In Space Settings → Repository secrets:
- TELEGRAM_BOT_TOKEN = `8455353239:AAHMxK1y--esr3d_0I5UxBCHnhLy0xglo94`
- CEREBRAS_API_KEY = `csk-826xjcryndx5pv344mrrf8khph68hr9mvyww5mhxdcnv365y`
- GROQ_API_KEY = `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`

**Step 5: Deploy**
- Space will automatically start
- Bot will be online 24/7!

---

### OPTION 2: Oracle Cloud Free Tier (BEST - 20 minutes!)

**Step 1: Sign Up**
1. Go to https://cloud.oracle.com
2. Click "Start for free"
3. Fill form with Pinmx email
4. Phone verification required
5. Create account

**Step 2: Create VM**
1. Go to Compute → Instances
2. Create Instance
3. Choose: VM.Standard.A1.Flex (FREE - 4 cores, 24GB RAM!)
4. Image: Ubuntu 22.04
5. SSH keys: Generate or upload

**Step 3: Connect & Install**
```bash
ssh -i your_key ubuntu@YOUR_VM_IP

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install OpenClaw
sudo npm install -g openclaw

# Upload config
# (Use SCP or SFTP to upload openclaw.json and secrets)

# Start gateway
openclaw gateway start
```

**Step 4: Keep Running**
```bash
# Install PM2
sudo npm install -g pm2

# Start OpenClaw with PM2
pm2 start openclaw --name "openclaw-gateway" -- gateway

# Save PM2 config
pm2 save

# Setup PM2 startup
pm2 startup
```

---

### OPTION 3: GitHub Actions (FREE - 10 minutes!)

**Step 1: Create Repo**
1. Go to github.com
2. Create new repo: `openclaw-cloud`
3. Make it Private

**Step 2: Add Secrets**
Settings → Secrets → New repository secret:
- TELEGRAM_BOT_TOKEN
- CEREBRAS_API_KEY
- GROQ_API_KEY

**Step 3: Create Workflow**
Create `.github/workflows/deploy.yml`:
```yaml
name: OpenClaw 24/7

on:
  push:
    branches: [main]
  schedule:
    - cron: '*/5 * * * *'  # Run every 5 minutes
  workflow_dispatch:

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      
      - name: Install OpenClaw
        run: npm install -g openclaw
      
      - name: Setup Config
        run: |
          mkdir -p ~/.openclaw
          echo '${{ secrets.OPENCLAW_CONFIG }}' > ~/.openclaw/openclaw.json
      
      - name: Start Gateway
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          CEREBRAS_API_KEY: ${{ secrets.CEREBRAS_API_KEY }}
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
        run: openclaw gateway start
```

---

## 📦 DEPLOYMENT PACKAGE

### Files to Upload:

**~/.openclaw/openclaw.json** - Your config
**~/.openclaw/workspace/secrets/** - All API keys
**~/.openclaw/workspace/memory/** - All session data
**~/.openclaw/workspace/*.md** - All documentation

### Environment Variables Needed:
```
TELEGRAM_BOT_TOKEN=8455353239:AAHMxK1y--esr3d_0I5UxBCHnhLy0xglo94
CEREBRAS_API_KEY=csk-826xjcryndx5pv344mrrf8khph68hr9mvyww5mhxdcnv365y
GROQ_API_KEY=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
```

---

## ✅ VERIFICATION

After deployment:
1. Send Telegram message to bot
2. Bot should respond
3. Check gateway status
4. Confirm memory intact

---

## 🎯 RECOMMENDED: Hugging Face Spaces

**Why:**
- No phone verification
- Email only signup
- Free forever
- Easy deployment
- 24/7 uptime
- Python support

**Start here:** https://huggingface.co/join
