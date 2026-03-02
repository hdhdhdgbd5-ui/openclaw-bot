"""
Groq API Test Script
Usage: python scripts/test_groq.py
Requires: GROQ_API_KEY environment variable or pass as argument
"""

import os
import sys
from pathlib import Path

# Try to import groq
try:
    from groq import Groq
except ImportError:
    print("Installing groq package...")
    os.system(f"{sys.executable} -m pip install groq -q")
    from groq import Groq

def test_groq_api(api_key=None):
    """Test the Groq API with a simple request"""
    
    # Get API key from argument, environment, or file
    if not api_key:
        api_key = os.environ.get('GROQ_API_KEY')
    
    if not api_key:
        # Try to read from secrets file
        secrets_path = Path.home() / ".openclaw" / "secrets" / "groq_api_key.txt"
        if secrets_path.exists():
            api_key = secrets_path.read_text().strip()
    
    if not api_key:
        print("❌ No API key found!")
        print("Please set GROQ_API_KEY environment variable or create ~/.openclaw/secrets/groq_api_key.txt")
        return False
    
    try:
        print(f"🔄 Testing Groq API with key: {api_key[:10]}...")
        
        client = Groq(api_key=api_key)
        
        # Make a simple chat completion request
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Say 'Hello from Groq!' in a creative way.",
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=100,
        )
        
        response = chat_completion.choices[0].message.content
        print(f"✅ Success! Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Get API key from command line if provided
    api_key = sys.argv[1] if len(sys.argv) > 1 else None
    success = test_groq_api(api_key)
    sys.exit(0 if success else 1)
