"""
Create Groq API Key using DrissionPage
"""

import sys
import time
import os
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from DrissionPage import ChromiumPage, ChromiumOptions

def create_groq_api_key():
    """Create a Groq API key using DrissionPage"""
    
    print("=" * 60)
    print("Creating Groq API Key")
    print("=" * 60)
    
    # Setup browser - NOT headless so we can see Cloudflare challenge
    co = ChromiumOptions()
    # co.set_argument('--headless=new')  # Commented out - need visible for CF
    co.set_argument('--disable-gpu')
    co.set_argument('--disable-blink-features=AutomationControlled')
    co.set_argument('--no-sandbox')
    co.set_argument('--disable-dev-shm-usage')
    co.set_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    print("[*] Starting browser...")
    browser = ChromiumPage(co)
    
    try:
        # Navigate to API keys page
        url = "https://console.groq.com/keys"
        print(f"[*] Navigating to {url}...")
        browser.get(url)
        
        # Wait for page to load
        print("[*] Waiting for page to load (20 seconds for CF)...")
        time.sleep(20)  # Wait for Cloudflare
        
        # Check if we're on the right page
        print(f"[*] Current URL: {browser.url}")
        print(f"[*] Page title: {browser.title}")
        
        # Look for the Create API Key button
        try:
            # Try to find and click Create API Key button
            create_btn = browser.ele('text:Create API Key', timeout=10)
            if create_btn:
                print("[+] Found 'Create API Key' button")
                create_btn.click()
                time.sleep(3)
                
                # Fill in the name
                name_input = browser.ele('text:Display Name', timeout=5)
                if name_input:
                    print("[+] Found name input field")
                    name_input.input('OpenClaw API Key')
                    time.sleep(1)
                    
                    # Look for Create button in the dialog
                    # Try pressing Enter to submit
                    browser.keys.enter()
                    time.sleep(5)
                    
                    # Check if key was created - look for the key in the page
                    page_text = browser.html
                    
                    # Look for API key pattern (gsk_)
                    import re
                    api_key_match = re.search(r'gsk_[a-zA-Z0-9]{20,}', page_text)
                    if api_key_match:
                        api_key = api_key_match.group(0)
                        print(f"[+] SUCCESS! API Key found: {api_key[:15]}...")
                        
                        # Save to file
                        secrets_dir = Path.home() / ".openclaw" / "secrets"
                        secrets_dir.mkdir(parents=True, exist_ok=True)
                        secrets_file = secrets_dir / "groq_api_key.txt"
                        secrets_file.write_text(api_key)
                        print(f"[+] Saved to {secrets_file}")
                        return True
                    else:
                        print("[-] API key not found in response")
                        # Check for errors
                        if 'Error' in page_text or 'error' in page_text:
                            print(f"[!] There may be an error")
                else:
                    print("[-] Could not find name input")
            else:
                print("[-] Could not find Create API Key button")
                # Print page content for debugging
                print(f"[*] Page HTML length: {len(browser.html)}")
                
        except Exception as e:
            print(f"[!] Error: {e}")
            import traceback
            traceback.print_exc()
        
        return False
        
    finally:
        browser.quit()
        print("\n" + "=" * 60)


if __name__ == "__main__":
    success = create_groq_api_key()
    if success:
        print("\n[+] API KEY CREATED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\n[-] FAILED TO CREATE API KEY")
        sys.exit(1)
