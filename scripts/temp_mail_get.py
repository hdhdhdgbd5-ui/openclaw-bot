#!/usr/bin/env python3
"""
Temp-Mail.org Automation - Get Temporary Email Address
"""

import sys
import time
from DrissionPage import ChromiumPage, ChromiumOptions

def get_temp_email():
    """Navigate to temp-mail.org and extract the email address"""
    
    options = ChromiumOptions()
    options.headless(False)  # Show browser so user can see
    options.set_argument('--disable-blink-features=AutomationControlled')
    options.set_argument('--no-sandbox')
    options.set_user_agent(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    )
    
    browser = ChromiumPage(options)
    
    try:
        print("Opening temp-mail.org...")
        browser.get('https://temp-mail.org')
        browser.wait.doc_loaded()
        
        # Wait for page to fully load
        time.sleep(3)
        
        # Try to find and click the copy button or get email directly
        print("Looking for email address...")
        
        # Method 1: Try to find input with email
        email_input = browser.ele('css:input#email', timeout=5)
        if email_input:
            email = email_input.value
            print(f"Email found: {email}")
            return email
        
        # Method 2: Try to find the email display element
        email_elem = browser.ele('css:.emailbox-input', timeout=5)
        if email_elem:
            email = email_elem.text or email_elem.value
            print(f"Email found: {email}")
            return email
        
        # Method 3: Look for any element containing @ symbol
        page_text = browser.html
        import re
        emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', page_text)
        if emails:
            email = emails[0]
            print(f"Email found: {email}")
            return email
        
        print("Could not find email automatically")
        print(f"Current URL: {browser.url}")
        print(f"Page title: {browser.title}")
        
        # Keep browser open for manual inspection
        input("Press Enter to close browser...")
        return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        browser.quit()

if __name__ == "__main__":
    email = get_temp_email()
    if email:
        print(f"\nTEMP EMAIL: {email}")
        # Save to file
        with open('temp_email.txt', 'w') as f:
            f.write(email)
        print("Saved to temp_email.txt")
    else:
        print("\nFailed to get email")
        sys.exit(1)
