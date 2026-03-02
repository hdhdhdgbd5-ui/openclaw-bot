# Cerebras AI Integration Skill

## Overview
This skill provides AI chat capabilities using the Cerebras API. It offers fast inference with the Llama-3.3-70b-hybrid model.

## Prerequisites
1. **Cerebras API Key** - Get yours at https://cloud.cerebras.ai
2. Save the API key to: `secrets/cerebras.txt`

## Quick Start

### Option 1: Using the Python Script (Recommended)

```bash
# Set your API key (or save to secrets/cerebras.txt)
$env:CEREBRAS_API_KEY = "your-api-key-here"

# Run a simple chat
python skills/cerebras-ai/scripts/chat.py "Hello, how are you?"

# Run with custom model
python skills/cerebras-ai/scripts/chat.py "Your prompt" --model llama-3.3-70b-hybrid

# Run with system prompt
python skills/cerebras-ai/scripts/chat.py "Your question" --system "You are a helpful assistant"
```

### Option 2: Using the Module in Your Code

```python
from skills.cerebras-ai.scripts.cerebras_client import CerebrasClient, CerebrasModel

# Initialize client
client = CerebrasClient()

# Chat with AI
response = client.chat("What is the meaning of life?")
print(response.content)
```

### Option 3: Direct API Calls

```python
import requests

api_key = "your-api-key"
url = "https://api.cerebras.ai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
data = {
    "model": "llama-3.3-70b-hybrid",
    "messages": [
        {"role": "user", "content": "Hello!"}
    ]
}

response = requests.post(url, headers=headers, json=data)
print(response.json())
```

## Supported Models

- `llama-3.3-70b-hybrid` - **Default** - Fast hybrid Llama model
- `llama-4-scout-17b-16e` - Efficient Llama 4 scout model  
- `llama-4-maverick-17b-16e` - Powerful Llama 4 model

## Configuration

### API Key Setup
```bash
# Option 1: Environment variable
$env:CEREBRAS_API_KEY = "your-key"

# Option 2: Save to file
# File: secrets/cerebras.txt
# Content: your-api-key-here
```

### Environment Variables
- `CEREBRAS_API_KEY` - Your Cerebras API key
- `CEREBRAS_BASE_URL` - API endpoint (default: https://api.cerebras.ai/v1)

## Features

- **Fast Inference** - Cerebras offers industry-leading inference speed
- **Simple API** - OpenAI-compatible API format
- **Streaming Support** - Real-time response streaming
- **Multiple Models** - Access to latest Llama models
- **Error Handling** - Built-in retry logic and error handling
- **Usage Tracking** - Monitor token usage and costs

## Usage Examples

### Basic Chat
```python
from cerebras_client import CerebrasClient
client = CerebrasClient()
result = client.chat("Hello!")
print(result.content)
```

### With System Prompt
```python
result = client.chat(
    user_message="Explain quantum computing",
    system_prompt="You are a physics professor. Be detailed."
)
```

### Streaming Responses
```python
for chunk in client.chat_stream("Count to 5"):
    print(chunk, end="", flush=True)
```

### Using Different Models
```python
result = client.chat(
    "Your prompt",
    model="llama-4-maverick-17b-16e"
)
```

## Integration with Other Skills

This skill can be used by other agents:

```python
# In another skill or agent
import sys
sys.path.insert(0, 'skills/cerebras-ai/scripts')
from cerebras_client import CerebrasClient

def ai_response(prompt):
    client = CerebrasClient()
    return client.chat(prompt)
```

## Testing

```bash
# Test the API connection
python skills/cerebras-ai/scripts/test.py

# Test with custom prompt
python skills/cerebras-ai/scripts/chat.py "Say 'Cerebras works!' if you can hear me"
```

## Files in This Skill

- `cerebras_client.py` - Main client library
- `chat.py` - Command-line chat interface
- `test.py` - API connection test
- `example.py` - Usage examples

## Troubleshooting

### "API key not found"
- Make sure CEREBRAS_API_KEY is set or secrets/cerebras.txt exists
- Get your key at https://cloud.cerebras.ai

### "Rate limit exceeded"
- Wait a moment and retry
- Check your API quota at Cerebras dashboard

### "Connection error"
- Check internet connection
- Verify API endpoint is accessible

## API Reference

### Endpoint
```
POST https://api.cerebras.ai/v1/chat/completions
```

### Request Body
```json
{
  "model": "llama-3.3-70b-hybrid",
  "messages": [
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.7,
  "max_tokens": 1024,
  "stream": false
}
```

### Response
```json
{
  "id": "...",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "llama-3.3-70b-hybrid",
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "Hello! How can I help?"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

## Notes

- Cerebras offers competitive pricing for API usage
- The llama-3.3-70b-hybrid model provides excellent performance
- API is compatible with OpenAI Python library with minor changes
