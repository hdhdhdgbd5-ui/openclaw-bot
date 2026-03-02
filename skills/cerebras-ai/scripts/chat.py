#!/usr/bin/env python3
"""
Cerebras AI Chat CLI
====================
Command-line interface for chatting with Cerebras AI.

Usage:
    python chat.py "Your message here"
    python chat.py "Hello" --system "You are a helpful assistant"
    python chat.py "Hello" --stream
"""

import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cerebras_client import CerebrasClient


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Chat with Cerebras AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python chat.py "Hello, how are you?"
  python chat.py "Explain quantum computing" --model llama-3.3-70b-hybrid
  python chat.py "Hello" --system "You are a pirate"
  python chat.py "Count to 10" --stream
  python chat.py --test
        """
    )
    
    parser.add_argument(
        "prompt", 
        nargs="?", 
        help="Message to send to the AI"
    )
    parser.add_argument(
        "-m", "--model",
        default="llama-3.3-70b-hybrid",
        help="Model to use (default: llama-3.3-70b-hybrid)"
    )
    parser.add_argument(
        "-s", "--system",
        help="System prompt"
    )
    parser.add_argument(
        "-t", "--temperature",
        type=float,
        default=0.7,
        help="Temperature (0.0-2.0, default: 0.7)"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=2048,
        help="Max tokens in response (default: 2048)"
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Stream response in real-time"
    )
    parser.add_argument(
        "--key",
        help="API key (or set CEREBRAS_API_KEY env var)"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test API connection"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)

    try:
        # Initialize client
        client = CerebrasClient(api_key=args.key, model=args.model)

        # Test mode
        if args.test:
            print("🧪 Testing Cerebras API connection...")
            print(f"   Model: {args.model}")
            print(f"   Endpoint: {client.base_url}")
            print()
            
            result = client.chat(
                "Say '✅ Cerebras API is working!' if you can hear me.",
                max_tokens=50,
                temperature=0.5
            )
            
            if result.success:
                print("✅ Connection successful!")
                print(f"   Model: {result.model}")
                print(f"   Tokens used: {result.tokens_used}")
                print(f"   Latency: {result.latency_ms:.2f}ms")
                print()
                print("Response:")
                print("-" * 40)
                print(result.content)
                print("-" * 40)
            else:
                print("❌ Connection failed!")
                print(f"   Error: {result.error}")
                sys.exit(1)
            return

        # Regular chat mode
        if not args.prompt:
            parser.print_help()
            print("\n💡 Quick examples:")
            print('   python chat.py "Hello!"')
            print('   python chat.py "Hello!" --test')
            print('   python chat.py "Hello!" --stream')
            sys.exit(0)

        # Send message
        if args.stream:
            print("🤖 Streaming response...\n")
            for chunk in client.chat_stream(
                args.prompt,
                system_prompt=args.system,
                temperature=args.temperature,
                max_tokens=args.max_tokens
            ):
                print(chunk, end="", flush=True)
            print()
        else:
            result = client.chat(
                args.prompt,
                system_prompt=args.system,
                temperature=args.temperature,
                max_tokens=args.max_tokens
            )
            
            if result.success:
                print("\n" + "=" * 50)
                print(result.content)
                print("=" * 50)
                print(f"\n📊 Stats: {result.model} | {result.tokens_used} tokens | {result.latency_ms:.2f}ms")
            else:
                print(f"\n❌ Error: {result.error}")
                sys.exit(1)

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\n📋 To fix:")
        print("   1. Get your API key at: https://cloud.cerebras.ai")
        print("   2. Set it as environment variable:")
        print("      Windows: $env:CEREBRAS_API_KEY='your-key'")
        print("      Linux/Mac: export CEREBRAS_API_KEY='your-key'")
        print("   3. Or save to secrets/cerebras.txt")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
