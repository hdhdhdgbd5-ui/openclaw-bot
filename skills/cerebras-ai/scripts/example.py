#!/usr/bin/env python3
"""
Cerebras AI - Usage Examples
============================
Various examples of how to use the Cerebras client.

Run these examples:
    python examples.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cerebras_client import CerebrasClient, CerebrasMessage, CerebrasModel


def example_basic_chat():
    """Basic chat example"""
    print("\n" + "=" * 50)
    print("EXAMPLE 1: Basic Chat")
    print("=" * 50)
    
    client = CerebrasClient()
    
    result = client.chat("What is Python?")
    
    print(f"Question: What is Python?")
    print(f"\nAnswer: {result.content}")
    print(f"\nStats: {result.tokens_used} tokens, {result.latency_ms:.2f}ms")


def example_with_system_prompt():
    """Chat with system prompt"""
    print("\n" + "=" * 50)
    print("EXAMPLE 2: With System Prompt")
    print("=" * 50)
    
    client = CerebrasClient()
    
    result = client.chat(
        user_message="Explain recursion",
        system_prompt="You are a professor. Use simple terms and include a joke."
    )
    
    print(f"Question: Explain recursion")
    print(f"\nAnswer: {result.content}")


def example_different_model():
    """Use different model"""
    print("\n" + "=" * 50)
    print("EXAMPLE 3: Different Model")
    print("=" * 50)
    
    client = CerebrasClient()
    
    result = client.chat(
        "What is machine learning?",
        model=CerebrasModel.LLAMA_4_MAVERICK_17B_16E.value
    )
    
    print(f"Model: {result.model}")
    print(f"\nAnswer: {result.content}")


def example_streaming():
    """Streaming response"""
    print("\n" + "=" * 50)
    print("EXAMPLE 4: Streaming Response")
    print("=" * 50)
    
    client = CerebrasClient()
    
    print("Streaming: ", end="", flush=True)
    for chunk in client.chat_stream("Count to 5, separated by spaces:"):
        print(chunk, end="", flush=True)
    print()


def example_conversation_history():
    """Multi-turn conversation"""
    print("\n" + "=" * 50)
    print("EXAMPLE 5: Conversation History")
    print("=" * 50)
    
    client = CerebrasClient()
    
    # First message
    history = []
    
    result1 = client.chat("My name is Alex!", history=history)
    history.append(CerebrasMessage(role="user", content="My name is Alex!"))
    history.append(CerebrasMessage(role="assistant", content=result1.content))
    
    print(f"User: My name is Alex!")
    print(f"AI: {result1.content}")
    
    # Second message with context
    result2 = client.chat("What's my name?", history=history)
    history.append(CerebrasMessage(role="user", content="What's my name?"))
    history.append(CerebrasMessage(role="assistant", content=result2.content))
    
    print(f"\nUser: What's my name?")
    print(f"AI: {result2.content}")


def example_custom_parameters():
    """Custom parameters"""
    print("\n" + "=" * 50)
    print("EXAMPLE 6: Custom Parameters")
    print("=" * 50)
    
    client = CerebrasClient()
    
    # Low temperature for consistent answers
    result1 = client.chat(
        "What is 1+1?",
        temperature=0.1,
        max_tokens=10
    )
    print(f"Temp 0.1: {result1.content}")
    
    # High temperature for creative answers
    result2 = client.chat(
        "What is 1+1?",
        temperature=1.5,
        max_tokens=10
    )
    print(f"Temp 1.5: {result2.content}")


def example_direct_api():
    """Direct API usage"""
    print("\n" + "=" * 50)
    print("EXAMPLE 7: Direct API Call")
    print("=" * 50)
    
    import requests
    
    api_key = os.environ.get("CEREBRAS_API_KEY")
    if not api_key:
        # Try secrets file
        secrets_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "secrets", "cerebras.txt"
        )
        if os.path.exists(secrets_path):
            with open(secrets_path, 'r') as f:
                api_key = f.read().strip()
    
    if not api_key:
        print("No API key found, skipping direct API example")
        return
    
    url = "https://api.cerebras.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.3-70b-hybrid",
        "messages": [{"role": "user", "content": "Hello from direct API!"}],
        "max_tokens": 50
    }
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    
    content = result["choices"][0]["message"]["content"]
    print(f"Direct API response: {content}")


def main():
    print("\n" + "🚀 " * 20)
    print("  CEREBRAS AI - USAGE EXAMPLES")
    print("🚀 " * 20)
    
    examples = [
        ("Basic Chat", example_basic_chat),
        ("System Prompt", example_with_system_prompt),
        ("Different Model", example_different_model),
        ("Streaming", example_streaming),
        ("Conversation History", example_conversation_history),
        ("Custom Parameters", example_custom_parameters),
        ("Direct API", example_direct_api),
    ]
    
    # Run all examples
    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n❌ Example '{name}' failed: {e}")
    
    print("\n" + "=" * 50)
    print("All examples completed!")
    print("=" * 50)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
