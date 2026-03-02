---
name: captcha-solver
description: Solve numeric CAPTCHAs (pinmx.com and similar) using AI vision
metadata: {"clawdbot":{"emoji":"🔢","noApiKey":true,"requires":{}}}
---

# 🔢 Numeric CAPTCHA Solver Skill

Solves numeric CAPTCHAs (like pinmx.com) using AI vision to extract numbers from images and automatically enter them.

## ✨ Features

- **Auto-detect CAPTCHA** - Detects numeric CAPTCHA dialogs automatically
- **AI Vision OCR** - Uses AI to read numbers from CAPTCHA images
- **Retry Logic** - Automatically retries on failure (up to 3 attempts)
- **Universal Integration** - Can be integrated into any automation flow

## 📖 How It Works

1. **Detect CAPTCHA** - Waits for CAPTCHA dialog to appear
2. **Screenshot** - Captures the CAPTCHA image
3. **AI Analysis** - Uses AI vision to extract the 6-digit number
4. **Auto-enter** - Types the numbers into the input field
5. **Verify** - Clicks the verify button
6. **Validate** - Checks if CAPTCHA was solved correctly

## 🚀 Usage

### As Agent Tools (Recommended)

The captcha-solver is designed to work with OpenClaw's agent tools (browser and image). Use the `agent-solver.mjs` module:

```javascript
// In your agent workflow
import { solvePinmxCaptcha } from './scripts/agent-solver.mjs';

// Solve CAPTCHA
const code = await solvePinmxCaptcha(tools, targetId, 'openclaw');
console.log('Solved:', code);
```

### Manual Step-by-Step

1. **Detect CAPTCHA** - Check if the verification dialog is visible
2. **Screenshot** - Take a screenshot of the page
3. **Analyze** - Use the image tool with this prompt:
   ```
   Look very carefully at this CAPTCHA image. It shows a 6-digit number made 
   of individual colored digits. Tell me EXACTLY what each digit is, from left 
   to right. List them one by one as a single string of 6 digits.
   ```
4. **Enter Code** - Type the extracted numbers into the input field
5. **Verify** - Click the verify button
6. **Retry if needed** - The AI may misread sometimes, so implement retry logic

### Integration with pinmx-automation

The pinmx-automation skill has been updated to detect and handle numeric CAPTCHAs.

## ⚙️ Configuration

```javascript
{
  page: page,           // Playwright page object (REQUIRED)
  maxRetries: 3,        // Maximum retry attempts
  timeout: 30000,       // Timeout for CAPTCHA to appear
  retryDelay: 1000,     // Delay between retries
  verifySelector: 'button:has-text("verifizieren")',  // Verify button selector
  inputSelector: 'input[type="text"], input[placeholder=""]', // Input selector
  dialogSelector: 'dialog, [role="dialog"], .modal' // Dialog selector
}
```

## 🎯 Use Cases

- **pinmx.com** - Solve numeric CAPTCHA when creating temp email
- **Similar numeric CAPTCHAs** - Works with any 6-digit numeric CAPTCHA
- **Automation** - Integrate into any browser automation flow

## 🔧 API

### `solve()`

Solves the CAPTCHA and returns the entered code.

**Returns:** `string` - The CAPTCHA code that was entered

**Throws:** `Error` if CAPTCHA cannot be solved after max retries

### `detectCaptcha()`

Checks if a CAPTCHA dialog is visible.

**Returns:** `boolean` - True if CAPTCHA is detected

### `extractCodeFromImage(imagePath)`

Extracts the numeric code from a CAPTCHA image using AI vision.

**Parameters:**
- `imagePath` - Path to the CAPTCHA screenshot

**Returns:** `string` - The extracted numeric code

## ⚠️ Notes

- Requires AI vision capability for image analysis
- Works best with clear numeric CAPTCHAs
- May need multiple attempts for complex images
- Supports 6-digit numeric CAPTCHAs (extendable)

## License

MIT
