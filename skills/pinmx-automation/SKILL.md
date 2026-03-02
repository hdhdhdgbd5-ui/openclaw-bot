---
name: pinmx-automation
description: Automate pinmx.com temp email creation with CAPTCHA solving
metadata: {"clawdbot":{"emoji":"📧","noApiKey":true,"requires":{"bins":["node","npm","playwright"]}}}
---

# 📧 pinmx.com Automation Skill

Automates the complete pinmx.com temp email creation process including:
- Generate random email prefix
- Create email postfach (inbox)
- Solve CAPTCHA
- Enter the inbox
- Handle popup notifications

## ✨ Features

- **Random Email Prefix** - Click "zufälliges präfix" to generate random email
- **Postfach Creation** - Create temp email inbox with one click
- **CAPTCHA Solving** - Automatic CAPTCHA detection and solving
- **Inbox Access** - Enter the created postfach
- **Popup Handling** - Auto-dismiss "wichtiger Hinweis" popup

## 🚀 Quick Start

```bash
cd skills/pinmx-automation
npm install
```

## 📖 Usage

### CLI

```bash
# Run the automation
node scripts/main.mjs

# Run with custom options
node scripts/main.mjs --headless false
```

### JavaScript API

```javascript
import { PinmxAutomation } from './scripts/index.mjs';

const pinmx = new PinmxAutomation({
  headless: false,
  stealth: true
});

await pinmx.start();

// Execute the full automation flow
const result = await pinmx.runFullAutomation();

console.log('Email:', result.email);
console.log('Inbox URL:', result.inboxUrl);

// Access inbox
await pinmx.enterInbox();

// Handle the "wichtiger Hinweis" popup
await pinmx.dismissPopup();

// Close browser
await pinmx.close();
```

## 🔧 Configuration

```javascript
{
  headless: false,        // Run in headless mode
  stealth: true,          // Enable stealth mode
  timeout: 30000,         // Default timeout in ms
  slowMo: 50              // Slow down actions for human-like behavior
}
```

## 📋 Automation Steps

1. **Navigate to pinmx.com** - Open the main page
2. **Click "zufälliges präfix"** - Yellow button to generate random prefix
3. **Wait for email** - Wait until email address is visible
4. **Click "Postfach erstellen"** - Blue button to create inbox
5. **Solve CAPTCHA** - Detect and solve any CAPTCHA challenge
6. **Click "betrete Sie das Postfach"** - Blue button to enter inbox
7. **Dismiss popup** - Click X on "wichtiger Hinweis" popup

## 🎯 Use Cases

- **Auto-signup** - Use for creating accounts on services requiring email verification
- **Testing** - Test email-based workflows
- **Privacy** - Use disposable email for signups

## ⚠️ Notes

- Requires CAPTCHA solving (may need 2Captcha API key for complex CAPTCHAs)
- Some websites may block disposable emails
- Rate limiting may apply

## License

MIT
