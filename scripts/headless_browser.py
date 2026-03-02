"""
Headless Browser Automation - No Chrome Extension Required!
Uses Playwright for 24/7 automation
"""

from playwright.sync_api import sync_playwright
import json
import os

class HeadlessBrowser:
    def __init__(self, headless=True):
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        
    def start(self):
        """Start the browser"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        print("[HeadlessBrowser] Started")
        
    def navigate(self, url):
        """Navigate to URL"""
        self.page.goto(url)
        print(f"[HeadlessBrowser] Navigated to {url}")
        
    def click(self, selector):
        """Click element"""
        self.page.click(selector)
        
    def type(self, selector, text):
        """Type text"""
        self.page.fill(selector, text)
        
    def get_content(self):
        """Get page content"""
        return self.page.content()
    
    def get_text(self, selector):
        """Get text from element"""
        return self.page.text_content(selector)
    
    def screenshot(self, path):
        """Take screenshot"""
        self.page.screenshot(path=path)
        
    def close(self):
        """Close browser"""
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
        print("[HeadlessBrowser] Closed")

# Example usage
if __name__ == "__main__":
    browser = HeadlessBrowser(headless=True)
    browser.start()
    browser.navigate("https://www.reddit.com")
    print(browser.get_content()[:500])
    browser.close()
