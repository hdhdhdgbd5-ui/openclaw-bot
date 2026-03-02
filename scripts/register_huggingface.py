#!/usr/bin/env python3
"""
Register HuggingFace Account using temp email
"""

import json
import time
from DrissionPage import ChromiumPage, ChromiumOptions

# Load temp email credentials
with open('../temp_mail_credentials.json', 'r') as f:
    creds = json.load(f)

EMAIL = creds['email']
PASSWORD = 'TempPass2026!Secure'  # HF password

def register_huggingface():
    options = ChromiumOptions()
    options.headless(False)  # Show browser for visibility
    options.set_argument('--disable-blink-features=AutomationControlled')
    options.set_argument('--no-sandbox')
    
    browser = ChromiumPage(options)
    
    try:
        print("Opening HuggingFace signup...")
        browser.get('https://huggingface.co/join')
        time.sleep(3)
        
        # Fill email
        print(f"Entering email: {EMAIL}")
        email_input = browser.ele('css:input[type="email"]', timeout=5)
        email_input.input(EMAIL)
        time.sleep(1)
        
        # Fill password
        print("Entering password...")
        pass_input = browser.ele('css:input[type="password"]', timeout=5)
        pass_input.input(PASSWORD)
        time.sleep(1)
        
        # Click Next/Submit
        print("Clicking Next...")
        next_btn = browser.ele('css:button[type="submit"]', timeout=5)
        next_btn.click()
        
        time.sleep(5)
        
        print(f"Current URL: {browser.url}")
        print(f"Page title: {browser.title}")
        
        # Check if registration successful
        if 'join' not in browser.url.lower() or 'verify' in browser.url.lower():
            print("Registration form submitted!")
            print(f"Email used: {EMAIL}")
            print("Check temp mail inbox for verification link")
            
            # Keep browser open for verification
            input("Press Enter after verifying email to save session...")
            
            # Save HF credentials
            hf_creds = {
                "email": EMAIL,
                "password": PASSWORD,
                "service": "huggingface"
            }
            
            with open('C:\\Users\\armoo\\.openclaw\\secrets\\huggingface_credentials.json', 'w') as f:
                json.dump(hf_creds, f, indent=2)
            
            print("Credentials saved!")
        else:
            print("Registration may have failed or needs verification")
            input("Press Enter to close...")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to close...")
    finally:
        browser.quit()

if __name__ == "__main__":
    register_huggingface()
