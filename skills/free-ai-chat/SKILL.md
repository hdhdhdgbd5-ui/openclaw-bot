# Free AI Chat Skill

## Overview
This skill provides free AI chat capabilities using browser automation to connect to Bing Copilot (free, no API key required).

## Prerequisites
1. The OpenClaw browser must be running
2. Use profile "openclaw" for headless browser

## Usage via Browser Tool

### Step 1: Start Browser (if not running)
```bash
# Start the browser
browser action=start profile=openclaw
```

### Step 2: Navigate to Copilot
```bash
# Navigate to Bing Copilot
browser action=navigate profile=openclaw targetUrl=https://copilot.microsoft.com
```

### Step 3: Accept Cookies (if needed)
```bash
# Click accept button if cookie dialog appears
browser action=act profile=openclaw request={"kind": "click", "ref": "e139"} targetId=<page-id>
```

### Step 4: Send Message
```bash
# Type your message
browser action=act profile=openclaw request={"kind": "type", "ref": "e96", "text": "Your message here"} targetId=<page-id>

# Press Enter to send
browser action=act profile=openclaw request={"key": "Enter", "kind": "press", "ref": "e96"} targetId=<page-id>
```

### Step 5: Get Response
```bash
# Take snapshot to see response
browser action=snapshot profile=openclaw targetId=<page-id>
```

## Alternative: Using the Script

### Start Browser First
```bash
browser action=start profile=openclaw
```

### Run Chat Script
```bash
node skills/free-ai-chat/scripts/chat.mjs "Your message here"
```

## Supported AI Services
- **Bing Copilot** (primary - free, no login needed)
- URL: https://copilot.microsoft.com

## Features
- Uses Bing Copilot web interface
- No API keys required
- Free unlimited usage
- Works via browser automation

## Limitations
- Requires browser automation
- Session-based (may need re-auth in future)
- Needs browser window to stay open

## Automation Script Example

Here's a simple automation script:

```javascript
// This skill can be called from other agents
// to get free AI responses

async function freeAIChat(prompt) {
  // 1. Ensure browser is running
  // 2. Navigate to copilot.microsoft.com
  // 3. Type message and send
  // 4. Extract response from page
}
```

## Testing
The skill has been tested and confirmed working with Bing Copilot. AI responses are received successfully without any API key.
