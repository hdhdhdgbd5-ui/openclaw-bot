"""
Cloudflare Bypass Demo - Groq Example
Tests bypassing Cloudflare on groq.com
"""

import sys
import os
import importlib.util
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load cloudflare_bypass module directly from file
cloudflare_bypass_path = Path(__file__).parent / "__init__.py"
spec = importlib.util.spec_from_file_location("cloudflare_bypass", str(cloudflare_bypass_path))
cloudflare_bypass_module = importlib.util.module_from_spec(spec)
sys.modules["cloudflare_bypass"] = cloudflare_bypass_module
spec.loader.exec_module(cloudflare_bypass_module)

CloudflareBypasser = cloudflare_bypass_module.CloudflareBypasser


def demo_groq():
    """Demo: Access Groq through Cloudflare bypass"""
    print("=" * 60)
    print("Cloudflare Bypass Demo - Groq")
    print("=" * 60)
    
    # Test with visible browser first to see what's happening
    bypasser = CloudflareBypasser(headless=False)
    
    url = "https://groq.com"
    print(f"\n[~] Attempting to access: {url}")
    print("(Using visible browser - you may see Cloudflare challenge)")
    print("Waiting for page load...\n")
    
    # Try undetected-chromedriver first (most reliable for Cloudflare)
    content = bypasser.fetch(url, method='uc')
    
    if content:
        print(f"[+] SUCCESS! Got {len(content)} bytes")
        
        # Extract useful info
        content_lower = content.lower()
        if '<title>' in content_lower:
            start = content_lower.find('<title>')
            end = content_lower.find('</title>', start)
            if start >= 0 and end > start:
                title = content[start+7:end].strip()
                print(f"[*] Page Title: {title}")
        
        # Check if it's actually Groq
        if 'groq' in content_lower or 'AI' in content:
            print("[+] Confirmed: This is the Groq page!")
        else:
            print("[!] Warning: Content may be challenge page")
    else:
        print("[-] Failed to access Groq")
    
    bypasser.close()
    print("\n" + "=" * 60)


def test_multiple_methods():
    """Test all bypass methods"""
    url = "https://nowsecure.nl"  # Good test site for Cloudflare
    
    methods = ['cloudscraper', 'uc', 'drission']
    
    print("\n" + "=" * 60)
    print("Testing All Bypass Methods")
    print("=" * 60)
    
    for method in methods:
        print(f"\n[*] Testing method: {method}")
        bypasser = CloudflareBypasser(headless=True)
        
        try:
            content = bypasser.fetch(url, method=method)
            if content and len(content) > 1000:
                print(f"[+] {method} - Got {len(content)} bytes")
            else:
                print(f"[-] {method} - Failed")
        except Exception as e:
            print(f"[-] {method} - Error: {e}")
        finally:
            bypasser.close()
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Run Groq demo first
    demo_groq()
    
    # Then test all methods
    test_multiple_methods()
