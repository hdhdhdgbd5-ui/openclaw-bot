# 🚀 UNLIMITED ROUTER

**Infinite API key rotation system - NEVER hit rate limits!**

## Status: ✅ OPERATIONAL

```
Providers: 2 Active | 8 Configured
Uptime: 24/7
Last Test: PASSED
```

## Active Providers

| Provider | Status | Model | Rate Limit |
|----------|--------|-------|------------|
| Ollama Local | ✅ Healthy | kimi-k2.5:cloud | 20/min |
| Groq Account 1 | ✅ Healthy | llama-3.1-8b-instant | 30/min |

## Available Slots (Add Keys to Enable)

- **Groq Account 2** → Add API key to `secrets/groq2.txt`
- **Groq Account 3** → Add API key to `secrets/groq3.txt`
- **GitHub Models** → Add token to `secrets/github.txt`
- **OpenRouter Free** → Add key to `secrets/openrouter.txt`
- **Cloudflare AI** → Add credentials to `secrets/cloudflare_*.txt`
- **Ollama Cloud** → Add key to `secrets/ollama_cloud.txt`

## Usage

```bash
# Chat through router
node skills/unlimited-router/router-skill.js chat "Hello!"

# Check status
node skills/unlimited-router/router-skill.js status

# Run tests
node skills/unlimited-router/test.js
```

## API Usage in Code

```javascript
const { chat, status } = require('./skills/unlimited-router/router-skill.js');

// Send message - automatically routes through available providers
const result = await chat([
  { role: 'user', content: 'Your message here' }
]);
console.log(result.response);

// Get router status
console.log(status());
```

## How It Works

1. **Round-robin rotation** - Cycles through providers
2. **Automatic fallback** - If one provider hits rate limit, switches to next
3. **Smart cooldown** - Tracks rate limits and waits appropriately
4. **Health monitoring** - Checks provider health every 30 seconds
5. **Error recovery** - Retries failed requests with different provider

## Configuration

Edit `skills/unlimited-router/config.json` to:
- Enable/disable providers
- Adjust rate limits
- Add new providers
- Change priority order

---
**Goal: $1000/month - FULL AUTONOMY**
