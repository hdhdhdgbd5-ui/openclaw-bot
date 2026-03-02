# Coolify Setup Guide

## What is Coolify?
Coolify is an open-source, self-hostable PaaS (Platform as a Service) alternative to Heroku, Netlify, and Vercel. It lets you easily deploy static sites, databases, and full-stack applications on your own servers.

## Why Use Coolify for Backup?
- **Self-hosted** - You own your data
- **Free forever** - Open source with no paywall
- **Easy deployment** - One-click deployments
- **280+ one-click services** - Including databases, caches, and more

## Installation Options

### Option 1: Cloud Version (Paid)
- Visit: https://app.coolify.io
- Paid but with high-availability and support
- ~$4-5/month for a server

### Option 2: Self-Hosted (Free)
**Requirements:**
- A server (VPS, Bare Metal, Raspberry PI, or any Linux machine)
- SSH access to the server
- At least 1GB RAM (recommended 2GB+)

**Installation:**
```bash
# SSH into your server, then run:
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

**Post-Installation:**
1. After installation, you'll get a URL to access Coolify
2. Create an admin account
3. Add your first server
4. Start deploying!

## For Angel Army Backup

### Recommended Setup:
1. **Use a cheap VPS** (~$4-5/month from Hetzner, DigitalOcean, or similar)
2. **Install Coolify** on the VPS
3. **Set up automated backups** of the workspace folder
4. **Deploy applications** directly from Coolify

### Backup Strategy:
- Coolify can manage database backups
- Use Coolify's built-in scheduling for cron jobs
- Store backups on the same server or connect S3-compatible storage

## Resources
- **Docs:** https://coolify.io/docs
- **GitHub:** https://github.com/coollabsio/coolify
- **Community:** https://discord.gg/coolify

## Alternative: Kopia (Backup-Only)
If you only need backup (not full PaaS), consider **Kopia**:
- Free, open-source backup tool
- Encrypts data locally
- Supports cloud storage (S3, Google Cloud, Azure, etc.)
- Install: `winget install kopia` or download from https://kopia.io
