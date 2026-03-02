"""
Reddit Account Creator - Headless (No Chrome Extension!)
Uses Playwright to create Reddit account automatically
"""

from playwright.sync_api import sync_playwright
import json
import os
import random

class RedditCreator:
    def __init__(self, headless=True):
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        self.credentials_file = os.path.expanduser("~/.openclaw/secrets/reddit_credentials.json")
        
    def start(self):
        """Start the browser"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.page = self.context.new_page()
        print("[RedditCreator] Started")
        
    def create_account(self, username, password, email):
        """Create a Reddit account"""
        print(f"[RedditCreator] Creating account: {username}")
        
        # Go to Reddit signup page
        self.page.goto("https://www.reddit.com/register/")
        self.page.wait_for_load_state("networkidle")
        
        # Fill in the registration form
        # Try to find and fill the username field
        try:
            self.page.fill('input[name="username"]', username)
            print(f"[RedditCreator] Filled username")
        except:
            print("[RedditCreator] Could not find username field")
            
        try:
            self.page.fill('input[name="password"]', password)
            print(f"[RedditCreator] Filled password")
        except:
            print("[RedditCreator] Could not find password field")
            
        try:
            self.page.fill('input[name="email"]', email)
            print(f"[RedditCreator] Filled email")
        except:
            print("[RedditCreator] Could not find email field")
            
        # Click the register button
        try:
            self.page.click('button[type="submit"]')
            self.page.wait_for_timeout(3000)
            print("[RedditCreator] Clicked register")
        except:
            print("[RedditCreator] Could not click register")
            
        # Get page content for debugging
        content = self.page.content()
        if "verification" in content.lower() or "email" in content.lower():
            print("[RedditCreator] Email verification may be needed")
            
        return content
        
    def save_credentials(self, username, password):
        """Save credentials to file"""
        os.makedirs(os.path.dirname(self.credentials_file), exist_ok=True)
        credentials = {
            "username": username,
            "password": password
        }
        with open(self.credentials_file, 'w') as f:
            json.dump(credentials, f)
        print(f"[RedditCreator] Credentials saved to {self.credentials_file}")
        
    def close(self):
        """Close browser"""
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
        print("[RedditCreator] Closed")

# Example usage - Generate random username
if __name__ == "__main__":
    import string
    
    # Generate random username
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    username = f"angelarmy{random_suffix}"
    password = "AngelArmy2026!Secure"
    # Note: We'd need a real email for verification
    email = ""  # Would need to use a temp email service
    
    print(f"[RedditCreator] Would create: {username}")
    print("[RedditCreator] But needs email verification - need temp email service")
