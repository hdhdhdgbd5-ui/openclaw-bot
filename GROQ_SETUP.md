# Groq API Setup Guide

## Overview
Groq is a fast LLM inference provider with free tier (~500k tokens/day). This guide helps you set up and use the Groq API.

## Getting an API Key

### Method 1: Manual (Recommended for now)
Due to Cloudflare protection blocking automation, manual key creation is needed:

1. Go to: https://console.groq.com/keys
2. Log in (already have account: e170u6kecbj@pinmx.net)
3. Click "Create API Key"
4. Enter a name (e.g., "OpenClaw")
5. Copy the generated key

### Method 2: Save Your Key
```powershell
# Save to the secrets folder
$key = "your-groq-api-key-here"
$key | Out-File -FilePath "$env:USERPROFILE\.openclaw\secrets\groq_api_key.txt" -Encoding utf8
```

## Environment Variable
```powershell
# Set as environment variable
$env:GROQ_API_KEY = "your-groq-api-key-here"
```

## Testing
```powershell
# Run the test script
python scripts/test_groq.py

# Or with key as argument
python scripts/test_groq.py "your-api-key"
```

## Usage Example
```python
from groq import Groq

client = Groq(api_key="your-api-key")

chat_completion = client.chat.completions.create(
    messages=[{"role": "user", "content": "Hello!"}],
    model="llama-3.3-70b-versatile",
)

print(chat_completion.choices[0].message.content)
```

## Available Models
- llama-3.3-70b-versatile
- llama-3.1-70b-versatile
- llama-3.1-8b-instant
- mixtral-8x7b-32768
- gemma2-9b-it

## Rate Limits (Free Tier)
- ~500k tokens/day
- ~30 requests/minute

## Issues?
- If you get "No cfToken" error, Cloudflare is blocking automation
- Manual key creation via browser is the workaround
