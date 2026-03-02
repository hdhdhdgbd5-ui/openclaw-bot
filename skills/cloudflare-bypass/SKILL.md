---
name: cloudflare-bypass
description: Bypass Cloudflare protection using stealth browser techniques. Uses puppeteer-extra-plugin-stealth, undetected-chromedriver, and custom headers to bypass anti-bot protection.
homepage: https://cloudflare.com
metadata: {"clawdbot":{"emoji":"🛡️","requires":{"bins":["node","npm","python"],"packages":["puppeteer-extra","puppeteer-extra-plugin-stealth","undetected-chromedriver"]},"noApiKey":true}}
---

# Cloudflare Bypass

Bypass Cloudflare protection using stealth browser techniques. Access Cloudflare-protected sites automatically!

## Install Dependencies

```bash
cd {baseDir}
npm install puppeteer-extra puppeteer-extra-plugin-stealth puppeteer
pip install undetected-chromedriver
```

## Usage

### Launch stealth browser with Cloudflare bypass

```bash
node {baseDir}/scripts/launcher.mjs "https://groq.com"
node {baseDir}/scripts/launcher.mjs "https://cloudflare-protected-site.com" --headless
```

### Python version (uses undetected-chromedriver)

```bash
python {baseDir}/scripts/launcher.py "https://groq.com"
```

### Programmatic usage (JavaScript)

```javascript
const { getStealthBrowser } = require('./scripts/stealth.mjs');

async function example() {
  const browser = await getStealthBrowser({ headless: false });
  const page = await browser.newPage();
  
  // Navigate to Cloudflare-protected site
  await page.goto('https://groq.com', { waitUntil: 'networkidle2' });
  
  // Wait for Cloudflare challenge to complete
  await waitForCloudflare(page);
  
  // Now you're past the challenge!
  const content = await page.content();
  console.log('Page loaded:', content.substring(0, 500));
  
  await browser.close();
}
```

## Options

- `--headless`: Run in headless mode (default: visible mode for Cloudflare)
- `--timeout <seconds>`: Max wait time for challenge (default: 30)
- `--user-agent <ua>`: Custom user agent string
- `--proxy <proxy>`: Use proxy server

## How it works

1. **puppeteer-extra-plugin-stealth**: Removes 90+ detection vectors
2. **undetected-chromedriver**: Python fallback using modified ChromeDriver
3. **User agent rotation**: Random real browser user agents
4. **Custom headers**: Adds proper headers Cloudflare expects
5. **Challenge detection**: Waits for Cloudflare challenge completion
6. **Retry logic**: Automatic retry on failure

## Techniques Used

- ✅ WebGL vendor/renderer spoofing
- ✅ Canvas fingerprint randomization  
- ✅ Chrome runtime detection bypass
- ✅ Navigator properties spoofing
- ✅ Proxy detection bypass
- ✅ Automation detection removal
- ✅ Proper headers (DNT, Accept-Language)
- ✅ JavaScript challenge waiting

## Troubleshooting

**Still getting blocked?**
- Try visible mode (no --headless)
- Increase timeout
- Use a residential proxy
- Try the Python version

**"Chrome not found" error?**
- Install Google Chrome browser
- Or use: `PUPPETEER_EXECUTABLE_PATH=/path/to/chrome`
