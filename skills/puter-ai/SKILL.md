# Puter.js AI Integration Skill

## Overview
This skill provides free AI chat capabilities using Puter.js library. It enables AI interactions using Gemini models without any API keys or billing.

## ⚠️ IMPORTANT: Puter.js Requirements

**Puter.js uses a "User Pays" model:**
- Users need a free Puter account (https://puter.com)
- Each user gets free AI credits as part of their account
- Developers pay $0 - users cover their own usage
- No API keys required, but authentication is needed

## Quick Start

### Option 1: Use the HTML Test Page (Recommended for Testing)

1. Serve the test page using any HTTP server:
   ```bash
   npx serve skills/puter-ai/scripts
   # or
   python -m http.server 8000 -d skills/puter-ai/scripts
   ```

2. Open http://localhost:8000/test.html (or the port shown) in your browser

3. The first time you use it, you'll need to sign in to Puter (free account)

4. Enter your message and click Send!

### Option 2: Use the Chat Script

```bash
# Make sure browser is running
browser action=start profile=openclaw

# Run the chat script
node skills/puter-ai/scripts/chat.mjs "Your message here"
```

### Option 3: Direct Browser Console

In any browser console, you can use:
```javascript
<script src="https://js.puter.com/v2/"></script>
<script>
  puter.ai.chat("Hello!", { model: "gemini-2.5-flash-lite" })
    .then(console.log);
</script>
```

## Supported Models

- `gemini-2.5-flash-lite` - Fast, lightweight Gemini model (recommended)
- `gemini-2.0-flash` - Standard Gemini model
- `gpt-5-nano` - OpenAI nano model
- And more available via Puter.js

## Usage Examples

### Basic Chat
```javascript
puter.ai.chat("What is JavaScript?", { model: "gemini-2.5-flash-lite" })
  .then(response => console.log(response));
```

### With Streaming
```javascript
const resp = await puter.ai.chat('Tell me about AI', {
  model: 'gemini-2.5-flash-lite', 
  stream: true 
});
for await (const part of resp) {
  console.log(part?.text);
}
```

### With Images
```javascript
puter.ai.chat("What do you see?", "https://example.com/image.jpg", {
  model: "gpt-5-nano"
}).then(console.log);
```

## Files in This Skill

- `chat.mjs` - Main chat script for automation
- `test.mjs` - Test script (basic)
- `test2.mjs` - Test script (navigates to puter.ai)
- `test.html` - HTML test page with UI
- `server.mjs` - Simple HTTP server for testing
- `chat-website.mjs` - Script to interact with Puter.ai website

## Testing the Skill

### Start Browser
```bash
browser action=start profile=openclaw
```

### Run Basic Test
```bash
node skills/puter-ai/scripts/test2.mjs
```

### Test HTML Page
1. Start a web server in the scripts directory
2. Open the test.html in a browser
3. Sign in with free Puter account
4. Test the chat functionality

## Integration Notes

This skill demonstrates Puter.js integration. For production use:

1. Users must have a Puter account (free at https://puter.com)
2. The "User Pays" model means users get free AI credits
3. No API key management needed
4. Works entirely client-side

## Alternative: Free AI Chat (Bing Copilot)

If you need a working free AI solution immediately without account creation, use the existing `free-ai-chat` skill:

```bash
# Uses Bing Copilot - no account needed
node skills/free-ai-chat/scripts/chat.mjs "Your message"
```

## Troubleshooting

### "puter is not defined"
- Make sure `<script src="https://js.puter.com/v2/"></script>` is loaded
- Wait for script to fully load before calling puter.ai

### Authentication errors
- Sign in at https://puter.com to create free account
- AI credits are provided free with account

### Network errors
- Check internet connection
- Puter.js requires access to js.puter.com

## References

- Puter.js Docs: https://docs.puter.com
- Puter.js on NPM: @heyputer/puter.js
- GitHub: https://github.com/HeyPuter/puter
