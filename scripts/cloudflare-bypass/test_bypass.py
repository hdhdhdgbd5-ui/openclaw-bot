"""
Quick Cloudflare Bypass Test
Simple test to verify bypass works
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


if __name__ == "__main__":
    print("=" * 60)
    print("Cloudflare Bypass Quick Test")
    print("=" * 60)
    
    # Test with nowsecure.nl - known Cloudflare test site
    url = "https://nowsecure.nl"
    print(f"\n[*] Testing with: {url}")
    
    # Use DrissionPage (confirmed working)
    bypasser = CloudflareBypasser(headless=True)
    
    content = bypasser.fetch(url, method='drission')
    
    if content and len(content) > 1000:
        print(f"[+] SUCCESS! Got {len(content)} bytes")
        
        # Check for cloudflare challenges
        if 'cloudflare' in content.lower() and 'challenge' in content.lower():
            print("[!] Warning: May still have challenge")
        else:
            print("[+] Clean page - no Cloudflare challenge!")
            
        # Get page title
        content_lower = content.lower()
        if '<title>' in content_lower:
            start = content_lower.find('<title>')
            end = content_lower.find('</title>', start)
            if start >= 0 and end > start:
                title = content[start+7:end].strip()
                print(f"[*] Page title: {title}")
    else:
        print("[-] Failed")
    
    bypasser.close()
    print("\n" + "=" * 60)
