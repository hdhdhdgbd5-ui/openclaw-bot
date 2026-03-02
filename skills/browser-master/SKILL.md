---
name: browser-master
description: ULTIMATE browser automation with human-like interactions, CAPTCHA solving, auto-signup, and stealth capabilities. Works like a REAL HUMAN!
metadata: {"clawdbot":{"emoji":"🤖","noApiKey":true,"requires":{"bins":["node","npm","python","playwright"]}}}
---

# 🤖 Browser Master - ULTIMATE Human-Like Browser Automation

The most advanced browser automation skill that mimics real human behavior for undetectable web automation!

## ✨ Features

### 🖱️ Human-Like Interactions
- Realistic mouse movements (bezier curves, not instant jumps)
- Natural typing with random delays and typos
- Smooth scrolling with human-like patterns
- Precise clicks with micro-movements
- Random wait times between actions

### 🔐 CAPTCHA Solving
- Automatic CAPTCHA detection (reCAPTCHA, hCaptcha, image captchas)
- AI-powered visual CAPTCHA solving
- Integration with 2Captcha API for backup
- Audio captcha support
- Challenge detection and handling

### 📧 Auto-Signup System
- Temporary email creation (Guerrilla Mail, Mailinator, etc.)
- Automatic email verification handling
- Phone number verification bypass (SMS APIs)
- Complete form filling with human-like patterns
- Account creation flows for major platforms

### 🛡️ Advanced Interactions
- Cloudflare protection bypass
- Dropdown and modal handling
- Iframe automation
- Dynamic content waiting
- Anti-detection stealth mode

## 🚀 Quick Start

```bash
cd skills/browser-master
npm install
```

### Start the API Server

```bash
npm start
```

The API runs on `http://localhost:3001`

## 📖 Usage Examples

### JavaScript/Node.js

```javascript
import { BrowserMaster } from './scripts/index.mjs';

// Create browser master instance
const browser = new BrowserMaster({
  headless: false,
  stealth: true,
  humanLike: true
});

// Start browser
await browser.start();

// Navigate like a human
await browser.navigateHuman('https://example.com');

// Type like a human
await browser.typeHuman('input[name="email"]', 'test@example.com', {
  typingSpeed: 50,  // ms between chars
  makeTypos: true   // occasionally make mistakes
});

// Click like a human
await browser.clickHuman('#submit-button');

// Scroll like a human
await browser.scrollHuman();  // natural scroll
await browser.scrollToBottomHuman();  // page bottom

// Solve CAPTCHA automatically
const solved = await browser.solveCaptcha();
if (solved) {
  console.log('CAPTCHA solved!');
}

// Auto-signup for a service
const account = await browser.autoSignup('https://example.com/signup', {
  email: 'auto',        // generate temp email
  username: 'auto',     // generate random username
  password: 'auto'      // generate strong password
});
console.log('Created account:', account);

// Save session for later
await browser.saveSession('my-session');

// Close browser
await browser.close();
```

### HTTP API

```bash
# Start browser
curl -X POST http://localhost:3001/api/browser/start

# Navigate like human
curl -X POST http://localhost:3001/api/navigate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Click element
curl -X POST http://localhost:3001/api/click \
  -H "Content-Type: application/json" \
  -d '{"selector": "#button"}'

# Type like human
curl -X POST http://localhost:3001/api/type \
  -H "Content-Type: application/json" \
  -d '{"selector": "input[name=email]", "text": "test@example.com"}'

# Solve captcha
curl -X POST http://localhost:3001/api/captcha/solve

# Auto-signup
curl -X POST http://localhost:3001/api/signup \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/signup"}'

# Save session
curl -X POST http://localhost:3001/api/session/save \
  -H "Content-Type: application/json" \
  -d '{"name": "my-session"}'
```

## 🎯 Human-Like Behavior

### Mouse Movements

```javascript
// Move mouse naturally to element
await browser.moveToHuman('#button');

// Move with custom path
await browser.moveToHuman('#button', {
  curve: true,          // use bezier curve
  overshoot: true,     // overshoot slightly then return
  microMovements: true // add tiny random movements
});
```

### Typing

```javascript
// Type with human-like delays
await browser.typeHuman('input[name="text"]', 'Hello World', {
  minDelay: 30,        // minimum ms between chars
  maxDelay: 120,      // maximum ms between chars
  makeTypos: true,    // occasionally make typos
  typoRate: 0.05,     // 5% chance of typo
  correctTypos: true   // automatically correct typos
});

// Type with varying speed
await browser.typeHuman('input', 'Text', {
  variableSpeed: true // speed varies naturally
});
```

### Scrolling

```javascript
// Natural scroll
await browser.scrollHuman();

// Scroll to element
await browser.scrollToHuman('#footer');

// Scroll to bottom (like human)
await browser.scrollToBottomHuman({
  pauses: true,       // pause occasionally while scrolling
  speed: 'medium'     // slow, medium, or fast
});

// Scroll with momentum
await browser.scrollWithMomentum(500);
```

### Clicking

```javascript
// Human-like click
await browser.clickHuman('#button');

// Click with micro-movement (jitter)
await browser.clickHuman('#button', {
  jitter: true,       // add tiny random movement
  doubleClick: false, // optionally double-click
  rightClick: false   // optionally right-click
});
```

## 🔐 CAPTCHA Solving

### Automatic Detection

```javascript
// Detect any CAPTCHA on page
const captcha = await browser.detectCaptcha();
if (captcha) {
  console.log('Found:', captcha.type); // recaptcha, hcaptcha, image, etc.
}
```

### Solve reCAPTCHA

```javascript
// Solve reCAPTCHA v2
await browser.solveRecaptcha();

// Solve reCAPTCHA v3
await browser.solveRecaptchaV3({
  siteKey: 'SITE_KEY',  // optional, auto-detect
  action: 'login'       // action name for v3
});
```

### Solve hCaptcha

```javascript
await browser.solveHCaptcha();
```

### Solve Image CAPTCHA

```javascript
// Solve image captcha (select images)
await browser.solveImageCaptcha({
  instruction: 'Select all images with traffic lights',
  images: ['img1.png', 'img2.png', ...]
});
```

### Solve Text CAPTCHA

```javascript
// Solve text captcha
const solution = await browser.solveTextCaptcha();
console.log('Solution:', solution);
```

## 📧 Auto-Signup System

### Basic Auto-Signup

```javascript
// Create account with temp email
const account = await browser.autoSignup('https://example.com/signup', {
  email: 'auto',        // generates temp email
  username: 'auto',     // generates random username
  password: 'auto',     // generates strong password
  fillProfile: true,    // fill additional profile fields
  verifyEmail: true     // wait for email verification
});

console.log('Account created:', account);
// { email, username, password, verified }
```

### Custom Email Service

```javascript
// Use specific temp email service
const account = await browser.autoSignup(url, {
  email: {
    service: 'guerrilla', // guerrilla, mailinator, temp-mail
    domain: 'grr.la'
  },
  username: 'custom_user',
  password: 'MyPassword123!'
});
```

### Phone Verification Bypass

```javascript
// Handle phone verification
const account = await browser.autoSignup(url, {
  phone: 'auto',  // use temp phone number
  phoneService: 'sms-activate'  // SMS receiving service
});
```

### Fill Forms

```javascript
// Fill signup form with human-like typing
await browser.fillFormHuman({
  'input[name="email"]': 'test@example.com',
  'input[name="password"]': 'Password123!',
  'input[name="name"]': 'John Doe',
  'select[name="country"]': 'US',
  'textarea[name="bio"]': 'Hello world'
}, {
  typingSpeed: 50,
  makeTypos: true
});

// Submit form
await browser.clickHuman('button[type="submit"]');
```

## 🛡️ Advanced Features

### Cloudflare Bypass

```javascript
// Navigate with Cloudflare bypass
await browser.navigateWithCloudflare('https://protected-site.com');

// Wait for Cloudflare challenge
await browser.waitForCloudflare();
```

### Handle Modals

```javascript
// Close modal
await browser.closeModal();

// Handle any modal
await browser.handleModal({
  accept: true,      // accept or dismiss
  fillIfNeeded: true // fill form in modal if present
});
```

### Iframe Automation

```javascript
// Switch to iframe
await browser.switchToIframe('iframe[name="content"]');

// Work in iframe
await browser.typeHuman('input[name="email"]', 'test@example.com');

// Switch back to main
await browser.switchToMain();
```

### Wait for Dynamic Content

```javascript
// Wait for element
await browser.waitForElement('#content', { state: 'visible' });

// Wait for text
await browser.waitForText('.status', 'Ready');

// Wait for network idle
await browser.waitForNetworkIdle();

// Wait for lazy loaded images
await browser.waitForLazyImages('.lazy-image');
```

### Stealth Mode

```javascript
// Enable full stealth
await browser.enableStealth();

// Disable automation detection
await browser.disableAutomationDetection();

// Randomize fingerprint
await browser.randomizeFingerprint();
```

## 📡 API Reference

### Browser Control

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST /api/browser/start` | Start browser | Start browser with options |
| `POST /api/browser/stop` | Stop browser | Close browser |
| `GET /api/browser/status` | Get status | Get browser status |

### Navigation

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST /api/navigate` | Navigate | Navigate to URL |
| `POST /api/navigate/human` | Navigate human | Navigate with human-like delay |
| `GET /api/cloudflare/wait` | Wait bypass | Wait for Cloudflare |

### Interactions

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST /api/click` | Click | Click element |
| `POST /api/click/human` | Click human | Click with human-like movement |
| `POST /api/type` | Type | Type text |
| `POST /api/type/human` | Type human | Type with human delays |
| `POST /api/scroll` | Scroll | Scroll page |
| `POST /api/scroll/human` | Scroll human | Natural scroll |

### CAPTCHA

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET /api/captcha/detect` | Detect | Detect CAPTCHA on page |
| `POST /api/captcha/solve` | Solve | Solve detected CAPTCHA |

### Signup

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST /api/signup` | Auto-signup | Create account automatically |

### Session

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST /api/session/save` | Save | Save session |
| `POST /api/session/load` | Load | Load session |
| `GET /api/session/list` | List | List saved sessions |

## ⚙️ Configuration

### Environment Variables

```bash
PORT=3001                    # API port
HEADLESS=true               # Run headless
STEALTH=true                # Enable stealth
HUMAN_LIKE=true             # Human-like behavior
TWOCAPTCHA_KEY=your-key     # 2Captcha API key
TEMP_MAIL_API=your-api      # Temp mail API key
```

### Config File

Create `browser-master.config.json`:

```json
{
  "port": 3001,
  "headless": true,
  "stealth": true,
  "humanLike": true,
  "viewport": {
    "width": 1920,
    "height": 1080
  },
  "userAgent": "random",
  "timezone": "America/New_York",
  "language": "en-US",
  "captcha": {
    "autoSolve": true,
    "timeout": 120000
  },
  "signup": {
    "tempEmail": true,
    "verifyEmail": true
  }
}
```

## 🎭 Randomization Options

### Mouse Movement Randomization

```javascript
{
  curve: {
    enabled: true,
    controlPoints: 3     // bezier curve points
  },
  overshoot: {
    enabled: true,
    probability: 0.3,   // 30% chance
    distance: 20        // pixels to overshoot
  },
  microMovements: {
    enabled: true,
    count: 5,           // number of micro movements
    distance: 3         // max pixels per movement
  }
}
```

### Typing Randomization

```javascript
{
  delay: {
    min: 30,
    max: 150
  },
  typos: {
    enabled: true,
    rate: 0.05,         // 5% typo rate
    corrections: true   // auto-correct
  },
  speed: {
    variance: 0.3,       // 30% speed variation
    burst: {
      enabled: true,
      probability: 0.2,
      chars: 3
    }
  }
}
```

### Scrolling Randomization

```javascript
{
  speed: {
    min: 300,           // pixels per scroll
    max: 800
  },
  pauses: {
    enabled: true,
    probability: 0.3,
    duration: [500, 2000]
  },
  direction: {
    reverse: {
      probability: 0.1  // occasionally scroll up
    }
  }
}
```

## 🔧 Requirements

- Node.js 18+
- Python 3.8+ (for some CAPTCHA features)
- Playwright (`npx playwright install chromium`)

## 📦 Installation

```bash
# Install dependencies
npm install

# Install Playwright browsers
npx playwright install chromium

# Install Python dependencies (optional)
pip install requests pillow
```

## 🚨 Troubleshooting

**Detection by anti-bot:**
- Enable full stealth mode
- Use residential proxy
- Increase random delays

**CAPTCHA not solving:**
- Check 2Captcha API key
- Try manual solving fallback
- Increase timeout

**Cloudflare blocking:**
- Use visible mode (not headless)
- Increase wait time
- Try Python undetected-chromedriver

## 📝 License

MIT
