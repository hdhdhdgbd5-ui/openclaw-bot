"""
Reddit Automation - Headless (No Chrome Extension!)
Uses Playwright for 24/7 Reddit posting
"""

from playwright.sync_api import sync_playwright
import json
import os

class RedditBot:
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
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        self.page = self.context.new_page()
        print("[RedditBot] Started")
        
    def load_credentials(self):
        """Load Reddit credentials"""
        if os.path.exists(self.credentials_file):
            with open(self.credentials_file, 'r') as f:
                return json.load(f)
        return None
    
    def login(self, username, password):
        """Login to Reddit"""
        self.page.goto("https://www.reddit.com/login/")
        self.page.wait_for_load_state("networkidle")
        
        # Type username
        self.page.fill('input[name="username"]', username)
        self.page.fill('input[name="password"]', password)
        self.page.click('button[type="submit"]')
        
        self.page.wait_for_load_state("networkidle")
        print(f"[RedditBot] Logged in as {username}")
        
    def create_app(self, app_name, redirect_uri="http://localhost:8080"):
        """Create a Reddit script app"""
        self.page.goto("https://www.reddit.com/prefs/apps")
        self.page.wait_for_load_state("networkidle")
        
        # Click "create another app" button
        self.page.click('a[href*="apps"]')
        self.page.wait_for_timeout(1000)
        
        # Fill in app details
        self.page.fill('input[name="name"]', app_name)
        self.page.fill('input[name="redirect_uri"]', redirect_uri)
        
        # Select script type
        self.page.click('button:has-text("script")')
        
        # Create app
        self.page.click('button:has-text("create app")')
        self.page.wait_for_timeout(2000)
        
        # Get client ID and secret from the page
        # (This would need to be customized based on Reddit's UI)
        
        print(f"[RedditBot] App '{app_name}' created")
        
    def post(self, subreddit, title, text=None, url=None):
        """Post to a subreddit"""
        self.page.goto(f"https://www.reddit.com/r/{subreddit}/submit")
        self.page.wait_for_load_state("networkidle")
        
        # Fill in title
        self.page.fill('input[name="title"]', title)
        
        if text:
            # Click text post button and fill content
            self.page.click('button:has-text("Text")')
            self.page.fill('div[contenteditable="true"]', text)
        elif url:
            self.page.fill('input[name="url"]', url)
            
        # Submit
        self.page.click('button:has-text("Post")')
        self.page.wait_for_timeout(2000)
        
        print(f"[RedditBot] Posted to r/{subreddit}: {title}")
        
    def close(self):
        """Close browser"""
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
        print("[RedditBot] Closed")

# Example usage
if __name__ == "__main__":
    # This requires credentials - user needs to provide them
    # bot = RedditBot(headless=True)
    # bot.start()
    # bot.login("username", "password")
    # bot.post("test", "Test Post", text="This is a test")
    # bot.close()
    print("[RedditBot] Ready! Add credentials to use.")
