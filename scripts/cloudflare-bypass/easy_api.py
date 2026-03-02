"""
Cloudflare Bypass - Easy API
Simple function to bypass Cloudflare from any script
"""

import sys
import importlib.util
from pathlib import Path

# Load cloudflare_bypass module
cloudflare_bypass_path = Path(__file__).parent / "__init__.py"
spec = importlib.util.spec_from_file_location("cloudflare_bypass", str(cloudflare_bypass_path))
cloudflare_bypass_module = importlib.util.module_from_spec(spec)
sys.modules["cloudflare_bypass"] = cloudflare_bypass_module
spec.loader.exec_module(cloudflare_bypass_module)


def fetch(url, headless=True):
    """
    Simple function to fetch a URL bypassing Cloudflare
    
    Args:
        url: URL to access
        headless: Use headless browser (recommended)
        
    Returns:
        HTML content or None
    """
    bypasser = cloudflare_bypass_module.CloudflareBypasser(headless=headless)
    try:
        return bypasser.fetch(url, method='drission')  # Use most reliable method
    finally:
        bypasser.close()


# Simple test
if __name__ == "__main__":
    print("Testing easy API...")
    content = fetch("https://groq.com")
    if content:
        print(f"Got {len(content)} bytes from Groq!")
    else:
        print("Failed")
