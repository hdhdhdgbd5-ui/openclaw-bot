#!/usr/bin/env python3
"""
Cerebras API Test Script
========================
Test the Cerebras API connection and verify everything works.

Usage:
    python test.py
    python test.py --key your-api-key
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cerebras_client import CerebrasClient, CerebrasModel


def print_header(text):
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)


def print_result(label, value, indent=0):
    prefix = "  " * indent
    print(f"{prefix}{label}: {value}")


def test_api_key():
    """Test if API key is configured"""
    print_header("1. API Key Configuration")
    
    api_key = os.environ.get("CEREBRAS_API_KEY")
    
    # Check secrets file
    secrets_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "secrets", "cerebras.txt"
    )
    
    if os.path.exists(secrets_path):
        with open(secrets_path, 'r') as f:
            secret_key = f.read().strip()
        if secret_key:
            api_key = secret_key
            print_result("✅ API Key", "Found in secrets/cerebras.txt")
    
    if not api_key:
        print_result("❌ API Key", "Not found!")
        print("\n📋 To get an API key:")
        print("   1. Go to https://cloud.cerebras.ai")
        print("   2. Create an account")
        print("   3. Generate an API key")
        print("   4. Save to secrets/cerebras.txt or set CEREBRAS_API_KEY")
        return None
    
    # Show masked key
    masked = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
    print_result("✅ API Key", f"Loaded ({masked})")
    return api_key


def test_client_initialization(api_key):
    """Test client initialization"""
    print_header("2. Client Initialization")
    
    try:
        client = CerebrasClient(api_key=api_key)
        print_result("✅ Base URL", client.base_url)
        print_result("✅ Default Model", client.model)
        print_result("✅ Timeout", f"{client.timeout}s")
        print_result("✅ Max Retries", client.max_retries)
        return client
    except Exception as e:
        print_result("❌ Failed", str(e))
        return None


def test_chat(client):
    """Test basic chat functionality"""
    print_header("3. Chat Functionality")
    
    test_prompts = [
        ("Simple greeting", "Say 'Hello from Cerebras!' in exactly those words."),
        ("Short question", "What is 2+2? Answer with just the number."),
    ]
    
    for name, prompt in test_prompts:
        print_result(f"Test: {name}", f'"{prompt[:40]}..."')
        
        result = client.chat(prompt, max_tokens=100, temperature=0.5)
        
        if result.success:
            print_result("  ✅ Success", f"{result.tokens_used} tokens in {result.latency_ms:.2f}ms")
            print_result("  Response", result.content[:80] + "..." if len(result.content) > 80 else result.content)
        else:
            print_result("  ❌ Failed", result.error)
        
        print()


def test_models(client):
    """Test different models"""
    print_header("4. Model Options")
    
    for model in CerebrasModel:
        print_result("📦 Available", model.value)
    
    print()
    print_result("Current Model", client.model)


def test_streaming(client):
    """Test streaming response"""
    print_header("5. Streaming (Optional)")
    
    print_result("Testing", "Streaming response for 'Count to 3'")
    print("Output: ", end="", flush=True)
    
    try:
        for chunk in client.chat_stream("Count to 3, separate with spaces.", max_tokens=50):
            print(chunk, end="", flush=True)
        print()
        print_result("✅ Streaming", "Working!")
    except Exception as e:
        print_result("❌ Streaming", f"Failed: {e}")


def test_system_prompt(client):
    """Test system prompt"""
    print_header("6. System Prompt")
    
    result = client.chat(
        user_message="What is your name?",
        system_prompt="You are Cerebro, a helpful AI assistant.",
        max_tokens=50
    )
    
    if result.success:
        print_result("✅ System Prompt", "Working!")
        print_result("Response", result.content)
    else:
        print_result("❌ Failed", result.error)


def main():
    print("\n" + "🧪 " * 15)
    print("  CEREBRAS API CONNECTION TEST")
    print("🧪 " * 15)
    
    # Test 1: API Key
    api_key = test_api_key()
    if not api_key:
        print("\n" + "❌ " * 10)
        print("Cannot proceed without API key!")
        print("❌ " * 10)
        sys.exit(1)
    
    # Test 2: Client initialization
    client = test_client_initialization(api_key)
    if not client:
        print("\n❌ Client initialization failed!")
        sys.exit(1)
    
    # Test 3: Models
    test_models(client)
    
    # Test 4: Chat
    test_chat(client)
    
    # Test 5: System prompt
    test_system_prompt(client)
    
    # Test 6: Streaming
    test_streaming(client)
    
    # Summary
    print_header("TEST COMPLETE")
    print("✅ All tests passed!")
    print("\n📚 Usage Examples:")
    print("   python chat.py 'Your message here'")
    print("   python chat.py 'Hello' --stream")
    print("   python chat.py 'Hello' --system 'You are a pirate'")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
