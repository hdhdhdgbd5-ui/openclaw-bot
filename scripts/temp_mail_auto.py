#!/usr/bin/env python3
"""
Temp-Mail.org Automation - Enhanced Version
"""

import sys
import time
from DrissionPage import ChromiumPage, ChromiumOptions

def get_temp_email():
    options = ChromiumOptions()
    options.headless(False)
    options.set_argument('--disable-blink-features=AutomationControlled')
    options.set_argument('--no-sandbox')
    
    browser = ChromiumPage(options)
    
    try:
        print("Opening temp-mail.org...")
        browser.get('https://temp-mail.org')
        
        # Wait longer for page to fully load
        print("Waiting for page to load...")
        time.sleep(5)
        
        # Try multiple selectors
        selectors = [
            'css:input#email',
            'css:input[type="text"]',
            'css:.emailbox-input',
            'css:[data-clipboard-target]',
            'css:#mail',
        ]
        
        for selector in selectors:
            try:
                print(f"Trying selector: {selector}")
                elem = browser.ele(selector, timeout=3)
                if elem:
                    email = elem.value or elem.text or elem.attr('value')
                    if email and '@' in str(email):
                        print(f"SUCCESS: Email = {email}")
                        
                        # Save to file
                        with open('temp_email.txt', 'w', encoding='utf-8') as f:
                            f.write(str(email))
                        
                        return str(email)
            except Exception as e:
                print(f"  Selector failed: {e}")
                continue
        
        # If all else fails, try to find by @ symbol
        print("Trying regex search...")
        html = browser.html
        import re
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html)
        if emails:
            email = emails[0]
            print(f"Found via regex: {email}")
            with open('temp_email.txt', 'w', encoding='utf-8') as f:
                f.write(email)
            return email
        
        print("Could not find email. Keeping browser open for inspection.")
        print(f"URL: {browser.url}")
        input("Press Enter to close...")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        browser.quit()
    
    return None

if __name__ == "__main__":
    email = get_temp_email()
    if email:
        print(f"\nEMAIL ACQUIRED: {email}")
    else:
        print("\nFailed to acquire email")
