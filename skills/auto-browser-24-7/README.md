# Auto Browser 24/7

Fully automated headless browser that runs 24/7 without any extensions or manual intervention!

## Features

- ✅ **Headless Browser** - Uses Playwright for reliable automation
- ✅ **Cloudflare Bypass** - Automatically handles Cloudflare challenges
- ✅ **CAPTCHA Solving** - Integrates with 2Captcha for automatic CAPTCHA solving
- ✅ **Session Management** - Save and restore cookies, localStorage, sessionStorage
- ✅ **Multi-tab Support** - Open, close, switch between tabs
- ✅ **Screenshots** - Take full page or element screenshots
- ✅ **Form Filling** - Automatically fill forms and submit
- ✅ **API Control** - HTTP API for remote control
- ✅ **24/7 Operation** - Runs continuously in the background

## Installation

```bash
cd skills/auto-browser-24-7
npm install
```

## Usage

### Start the API Server (24/7 mode)

```bash
npm start
```

This starts both the browser and API server. The API runs on `http://localhost:3000`.

### Browser Only Mode

```bash
npm run browser
```

Opens browser for interactive use.

### Run Tests

```bash
npm run test
```

## API Endpoints

### Browser Control

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/browser/start` | POST | Start browser |
| `/api/browser/stop` | POST | Stop browser |
| `/api/browser/status` | GET | Get browser status |

### Navigation

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/navigate` | POST | Navigate to URL |
| `/api/cloudflare/wait` | GET | Wait for Cloudflare bypass |

### Tabs

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/tabs` | GET | List all tabs |
| `/api/tabs/new` | POST | Open new tab |
| `/api/tabs/switch` | POST | Switch to tab |
| `/api/tabs/close` | POST | Close current tab |

### Page Operations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/screenshot` | POST | Take screenshot |
| `/api/content` | GET | Get page content |
| `/api/form/fill` | POST | Fill form |
| `/api/click` | POST | Click element |
| `/api/execute` | POST | Execute JavaScript |

### Session Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/session/save` | POST | Save session |
| `/api/session/load` | POST | Load session |
| `/api/session/list` | GET | List sessions |
| `/api/session/clear` | POST | Clear session |

### CAPTCHA

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/captcha/detect` | GET | Detect CAPTCHA |
| `/api/captcha/solve` | POST | Solve CAPTCHA |

## API Examples

### Start Browser
```bash
curl -X POST http://localhost:3000/api/browser/start \
  -H "Content-Type: application/json" \
  -d '{"headless": true, "stealth": true}'
```

### Navigate to URL
```bash
curl -X POST http://localhost:3000/api/navigate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "bypassCloudflare": true}'
```

### Take Screenshot
```bash
curl -X POST http://localhost:3000/api/screenshot \
  -H "Content-Type: application/json" \
  -d '{"filename": "screenshot.png", "fullPage": true}'
```

### Fill Form
```bash
curl -X POST http://localhost:3000/api/form/fill \
  -H "Content-Type: application/json" \
  -d '{
    "username": "myuser",
    "password": "mypass",
    "#email": "test@example.com"
  }'
```

### Save Session
```bash
curl -X POST http://localhost:3000/api/session/save \
  -H "Content-Type: application/json" \
  -d '{"name": "my-session"}'
```

### Load Session
```bash
curl -X POST http://localhost:3000/api/session/load \
  -H "Content-Type: application/json" \
  -d '{"name": "my-session"}'
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | API server port | `3000` |
| `HEADLESS` | Run browser headless | `true` |
| `TWOCAPTCHA_API_KEY` | 2Captcha API key | - |

## Configuration

Create `.auto-browser-config.json` in the skill directory:

```json
{
  "headless": true,
  "stealth": true,
  "apiPort": 3000,
  "startupUrls": [
    "https://example.com"
  ],
  "screenshotDir": "./screenshots",
  "sessionDir": "./sessions"
}
```

## Programmatic Usage

```javascript
import { 
  createBrowser, 
  navigateWithCloudflareBypass,
  screenshot,
  fillForm,
  saveSession,
  loadSession
} from './scripts/api.mjs';

// Create browser
const { browser, context } = await createBrowser({ headless: true });

// Create page
const page = await context.newPage();

// Navigate with Cloudflare bypass
await navigateWithCloudflareBypass(page, 'https://example.com');

// Take screenshot
await page.screenshot({ path: 'screenshot.png' });

// Fill form
await fillForm(page, {
  'input[name="email"]': 'test@example.com',
  'input[name="password"]': 'secret'
});

// Save session
await saveSession(context, 'my-session');

// Close browser
await browser.close();
```

## Requirements

- Node.js 18+
- Chrome/Chromium (installed by Playwright)

## License

MIT
