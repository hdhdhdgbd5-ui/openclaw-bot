"""
Dev.to Auto-Poster - Headless (No Chrome Extension!)
Uses Playwright to post to Dev.to
"""

from playwright.sync_api import sync_playwright
import json
import os

class DevToPoster:
    def __init__(self, headless=True):
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        self.credentials_file = os.path.expanduser("~/.openclaw/secrets/devto_credentials.json")
        
    def start(self):
        """Start the browser"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        self.page = self.context.new_page()
        print("[DevToPoster] Started")
        
    def post_article(self, title, content, tags=None):
        """Post an article to Dev.to"""
        # Dev.to allows anonymous posting via their API
        import requests
        
        url = "https://dev.to/api/articles"
        payload = {
            "article": {
                "title": title,
                "body_markdown": content,
                "tags": tags or ["ai", "tools", "productivity", "free"],
                "published": True
            }
        }
        
        response = requests.post(url, json=payload)
        if response.status_code == 201:
            data = response.json()
            print(f"[DevToPoster] Posted successfully! URL: {data.get('url')}")
            return data
        else:
            print(f"[DevToPoster] Error: {response.status_code} - {response.text}")
            return None
        
    def close(self):
        """Close browser"""
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
        print("[DevToPoster] Closed")

# Example usage
if __name__ == "__main__":
    poster = DevToPoster(headless=True)
    poster.start()
    
    # Sample post about our products
    title = "🚀 12 Free AI Tools I Built to Make Money"
    content = """
I've been building a suite of free AI tools to help with different income streams:

**For Freelancers & Solopreneurs:**
- **ContractGenius** - Generate professional contracts in seconds
- **ContentGenius** - Blog posts, emails, social media content
- **InsightGenius** - Market research & competitor analysis
- **CareerGenius** - Resume optimization & interview prep
- **StoreGenius** - E-commerce product descriptions

**For Personal Finance:**
- **RentVault** - Rental agreement generator
- **BudgetVault** - Smart budget tracking

**For Productivity:**
- **StreakVault** - Habit tracking that actually sticks
- **FocusMaster** - Deep work sessions

All free to use! Would love feedback!

#AI #Tools #Productivity #Free #SideHustle
"""
    
    result = poster.post_article(title, content)
    poster.close()
    
    if result:
        print(f"✅ Posted! View at: {result.get('url')}")
