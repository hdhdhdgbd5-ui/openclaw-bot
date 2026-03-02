from DrissionPage import ChromiumPage, ChromiumOptions
import time
import json
import os
from pathlib import Path

# Setup - Credentials must be provided via environment variables or secrets file
# Never hardcode credentials!

# Get email from environment or secrets file
email = os.environ.get('KAGGLE_EMAIL')
password = os.environ.get('KAGGLE_PASSWORD')

if not email:
    secrets_path = Path.home() / ".openclaw" / "secrets" / "kaggle_credentials.json"
    if secrets_path.exists():
        with open(secrets_path) as f:
            creds = json.load(f)
            email = creds.get('email')
            password = creds.get('password')

if not email:
    raise ValueError("KAGGLE_EMAIL not set and secrets file not found!")
    
if not password:
    raise ValueError("KAGGLE_PASSWORD not set!")

fullname = os.environ.get('KAGGLE_FULLNAME', 'Angel Army')

def register_kaggle():
    page = ChromiumPage()
    page.get('https://www.kaggle.com/account/login?phase=startRegisterTab&returnUrl=%2F')
    
    # Wait for page to load
    time.sleep(5)
    
    try:
        # Fill email
        page.ele('xpath://input[@name="email"]').input(email)
        
        # Fill password
        page.ele('xpath://input[@name="password"]').input(password)
        
        # Fill full name
        page.ele('xpath://input[@name="displayName"]').input(fullname)
        
        print("Filled basic info. Please handle CAPTCHA.")
    except Exception as e:
        print(f"Error finding elements: {e}")
        # Try to find by placeholder again with wait
        try:
            page.ele('@placeholder=Enter your email address', timeout=20).input(email)
            page.ele('@placeholder=Enter password').input(password)
            page.ele('@placeholder=Enter your full name').input(fullname)
            print("Filled info using placeholders.")
        except Exception as e2:
            print(f"Failed again: {e2}")
            page.get_screenshot('kaggle_error.png')
            return False
    
    start_time = time.time()
    while time.time() - start_time < 300: # 5 mins
        if "Check your email" in page.html or "verification" in page.url:
            print("Successfully moved to verification page!")
            return True
        time.sleep(5)
    
    print("Timed out.")
    return False

if __name__ == "__main__":
    register_kaggle()
