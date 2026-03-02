#!/usr/bin/env python3
"""
Cerebras AI Client
==================
Python client for Cerebras API with llama-3.3-70b-hybrid model support.

Author: SKILLS ARMY
Version: 1.0.0
"""

import os
import sys
import time
import json
import logging
from typing import List, Dict, Optional, Any, AsyncGenerator, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

# Try to import requests, provide helpful error if missing
try:
    import requests
except ImportError:
    print("ERROR: 'requests' library not found. Install with: pip install requests")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('cerebras-client')


class CerebrasModel(Enum):
    """Available Cerebras models"""
    LLAMA_3_3_70B_HYBRID = "llama-3.3-70b-hybrid"
    LLAMA_4_SCOUT_17B_16E = "llama-4-scout-17b-16e"
    LLAMA_4_MAVERICK_17B_16E = "llama-4-maverick-17b-16e"


@dataclass
class CerebrasMessage:
    """Message for Cerebras chat completion"""
    role: str  # system, user, assistant
    content: str
    name: Optional[str] = None

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary"""
        result = {"role": self.role, "content": self.content}
        if self.name:
            result["name"] = self.name
        return result


@dataclass
class CerebrasResponse:
    """Cerebras API response"""
    success: bool
    content: Optional[str] = None
    model: Optional[str] = None
    tokens_used: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: float = 0.0
    error: Optional[str] = None
    raw_response: Optional[Dict] = None
    finish_reason: Optional[str] = None

    def __str__(self) -> str:
        if self.success:
            return f"CerebrasResponse(success=True, tokens={self.tokens_used}, latency={self.latency_ms:.2f}ms)"
        return f"CerebrasResponse(success=False, error={self.error})"


class CerebrasClient:
    """Cerebras API Client"""

    DEFAULT_BASE_URL = "https://api.cerebras.ai/v1"
    DEFAULT_MODEL = "llama-3.3-70b-hybrid"
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 2048

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 60,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize Cerebras client

        Args:
            api_key: Cerebras API key (or set CEREBRAS_API_KEY env var)
            base_url: API endpoint URL
            model: Default model to use
            timeout: Request timeout in seconds
            max_retries: Max retry attempts on failure
            retry_delay: Delay between retries in seconds
        """
        # Get API key from parameter, env var, or secrets file
        self.api_key = api_key or os.environ.get("CEREBRAS_API_KEY")
        
        # Try to load from secrets file
        if not self.api_key:
            secrets_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "secrets", "cerebras.txt"
            )
            if os.path.exists(secrets_path):
                with open(secrets_path, 'r') as f:
                    self.api_key = f.read().strip()

        if not self.api_key:
            raise ValueError(
                "Cerebras API key not found. Set CEREBRAS_API_KEY environment variable "
                "or create secrets/cerebras.txt file with your API key."
            )

        self.base_url = base_url or os.environ.get("CEREBRAS_BASE_URL", self.DEFAULT_BASE_URL)
        self.model = model or self.DEFAULT_MODEL
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

        logger.info(f"CerebrasClient initialized with model: {self.model}")

    def _build_messages(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        history: Optional[List[CerebrasMessage]] = None
    ) -> List[Dict[str, str]]:
        """Build message list for API request"""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if history:
            for msg in history:
                messages.append(msg.to_dict())

        messages.append({"role": "user", "content": user_message})
        return messages

    def _make_request(
        self,
        messages: List[Dict],
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        stream: bool = False,
        **kwargs
    ) -> Union[CerebrasResponse, AsyncGenerator]:
        """Make API request with retry logic"""
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        payload.update(kwargs)

        last_error = None
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                
                response = self.session.post(
                    url,
                    json=payload,
                    timeout=self.timeout,
                    stream=stream
                )

                latency_ms = (time.time() - start_time) * 1000

                if response.status_code == 200:
                    if stream:
                        return self._handle_stream(response)
                    
                    data = response.json()
                    return self._parse_response(data, latency_ms)
                    
                elif response.status_code == 401:
                    return CerebrasResponse(
                        success=False,
                        error="Authentication failed. Check your API key."
                    )
                    
                elif response.status_code == 429:
                    # Rate limited
                    wait_time = response.headers.get("Retry-After", self.retry_delay * (attempt + 1))
                    logger.warning(f"Rate limited. Waiting {wait_time}s before retry...")
                    time.sleep(float(wait_time))
                    continue
                    
                else:
                    error_msg = f"API error: {response.status_code}"
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", {}).get("message", error_msg)
                    except:
                        error_msg = response.text[:200]
                    
                    last_error = error_msg
                    logger.warning(f"Request failed (attempt {attempt + 1}): {error_msg}")
                    
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    
                    return CerebrasResponse(success=False, error=error_msg)

            except requests.exceptions.Timeout:
                last_error = "Request timed out"
                logger.warning(f"Timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                    
            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection error: {str(e)}"
                logger.warning(f"Connection error (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                    
            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
                logger.error(f"Unexpected error: {e}")
                break

        return CerebrasResponse(success=False, error=last_error or "Unknown error")

    def _parse_response(self, data: Dict, latency_ms: float) -> CerebrasResponse:
        """Parse API response"""
        try:
            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})
            
            return CerebrasResponse(
                success=True,
                content=message.get("content", ""),
                model=data.get("model"),
                tokens_used=data.get("usage", {}).get("total_tokens", 0),
                prompt_tokens=data.get("usage", {}).get("prompt_tokens", 0),
                completion_tokens=data.get("usage", {}).get("completion_tokens", 0),
                latency_ms=latency_ms,
                finish_reason=choice.get("finish_reason"),
                raw_response=data
            )
        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
            return CerebrasResponse(
                success=False,
                error=f"Failed to parse response: {str(e)}",
                raw_response=data
            )

    def _handle_stream(self, response) -> AsyncGenerator[str, None]:
        """Handle streaming response"""
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]
                    if data == '[DONE]':
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except:
                        pass

    def chat(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        history: Optional[List[CerebrasMessage]] = None,
        **kwargs
    ) -> CerebrasResponse:
        """
        Send a chat message to Cerebras API

        Args:
            user_message: The user's message
            system_prompt: Optional system prompt
            model: Override default model
            temperature: Sampling temperature (0.0 - 2.0)
            max_tokens: Max tokens in response
            history: Previous messages for context
            **kwargs: Additional API parameters

        Returns:
            CerebrasResponse object
        """
        effective_model = model or self.model
        messages = self._build_messages(user_message, system_prompt, history)
        
        logger.info(f"Sending chat request (model: {effective_model})")
        
        return self._make_request(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            model=effective_model,
            **kwargs
        )

    def chat_stream(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        **kwargs
    ):
        """
        Stream chat response from Cerebras API

        Args:
            user_message: The user's message
            system_prompt: Optional system prompt
            model: Override default model
            temperature: Sampling temperature
            max_tokens: Max tokens in response

        Yields:
            Response chunks as strings
        """
        effective_model = model or self.model
        messages = self._build_messages(user_message, system_prompt)
        
        logger.info(f"Starting streaming chat (model: {effective_model})")
        
        generator = self._make_request(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            model=effective_model,
            stream=True,
            **kwargs
        )
        
        for chunk in generator:
            yield chunk


def main():
    """Main entry point for CLI usage"""
    import argparse

    parser = argparse.ArgumentParser(description="Cerebras AI Chat")
    parser.add_argument("prompt", nargs="?", help="Message to send to AI")
    parser.add_argument("-m", "--model", help="Model to use")
    parser.add_argument("-s", "--system", help="System prompt")
    parser.add_argument("-t", "--temperature", type=float, default=0.7, help="Temperature (0-2)")
    parser.add_argument("--max-tokens", type=int, default=2048, help="Max tokens")
    parser.add_argument("--stream", action="store_true", help="Stream response")
    parser.add_argument("--key", help="API key (or set CEREBRAS_API_KEY)")
    parser.add_argument("--test", action="store_true", help="Run connection test")

    args = parser.parse_args()

    try:
        client = CerebrasClient(api_key=args.key, model=args.model)

        if args.test:
            print("Testing Cerebras API connection...")
            result = client.chat(
                "Say 'Cerebras API is working!' if you can hear me.",
                max_tokens=50
            )
            if result.success:
                print(f"\n✓ Connection successful!")
                print(f"  Model: {result.model}")
                print(f"  Tokens: {result.tokens_used}")
                print(f"  Latency: {result.latency_ms:.2f}ms")
                print(f"\nResponse: {result.content}")
            else:
                print(f"\n✗ Connection failed: {result.error}")
                sys.exit(1)
            return

        if not args.prompt:
            parser.print_help()
            print("\nExamples:")
            print('  python chat.py "Hello!"')
            print('  python chat.py "Hello!" --model llama-3.3-70b-hybrid')
            print('  python chat.py "Hello!" --system "You are a pirate"')
            sys.exit(0)

        if args.stream:
            print("Streaming response:\n")
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
                print(f"\n{result.content}")
                print(f"\n[Model: {result.model} | Tokens: {result.tokens_used} | Latency: {result.latency_ms:.2f}ms]")
            else:
                print(f"\nError: {result.error}")
                sys.exit(1)

    except ValueError as e:
        print(f"\nError: {e}")
        print("\nGet your API key at: https://cloud.cerebras.ai")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nInterrupted.")
        sys.exit(0)


if __name__ == "__main__":
    main()
