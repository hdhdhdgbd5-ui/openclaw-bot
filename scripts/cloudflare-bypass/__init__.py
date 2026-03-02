"""
Cloudflare Bypass Module
LEGAL - This is for accessing Cloudflare-protected sites we have legitimate access to
Uses multiple methods to bypass Cloudflare protection
"""

import os
import sys
import time
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))

class CloudflareBypasser:
    """Cloudflare bypass using multiple methods"""
    
    def __init__(self, headless=True, use_uc=True):
        self.headless = headless
        self.use_uc = use_uc
        self.driver = None
        self.browser = None
        
    def _init_cloudscraper(self):
        """Initialize cloudscraper (simple method)"""
        try:
            import cloudscraper
            self.scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'mobile': False
                },
                delay=10
            )
            print("[CloudflareBypass] Using cloudscraper")
            return True
        except ImportError:
            print("[CloudflareBypass] cloudscraper not installed")
            return False
            
    def _init_undetected_chromedriver(self):
        """Initialize undetected-chromedriver (robust method)"""
        try:
            import undetected_chromedriver as uc
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Try to find Chrome executable
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ]
            
            chrome_binary = None
            for path in chrome_paths:
                if Path(path).exists():
                    chrome_binary = path
                    break
            
            options = uc.ChromeOptions()
            if self.headless:
                options.add_argument('--headless=new')
                options.add_argument('--disable-gpu')
            
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--profile-directory=Default')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Use existing Chrome if available
            if chrome_binary:
                options.binary_location = chrome_binary
            
            # Try with local Chrome, no version specified (uses system Chrome)
            self.driver = uc.Chrome(options=options, version_main=None, headless=self.headless, use_subprocess=True)
            self.driver.set_page_load_timeout(30)
            print("[CloudflareBypass] Using undetected-chromedriver")
            return True
        except Exception as e:
            print(f"[CloudflareBypass] undetected-chromedriver failed: {e}")
            return False
            
    def _init_drissionpage(self):
        """Initialize DrissionPage (alternative method)"""
        try:
            from DrissionPage import ChromiumPage, ChromiumOptions
            
            co = ChromiumOptions()
            if self.headless:
                co.set_argument('--headless=new')
                co.set_argument('--disable-gpu')
            co.set_argument('--disable-blink-features=AutomationControlled')
            co.set_argument('--no-sandbox')
            co.set_argument('--disable-dev-shm-usage')
            co.set_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            self.browser = ChromiumPage(co)
            print("[CloudflareBypass] Using DrissionPage")
            return True
        except Exception as e:
            print(f"[CloudflareBypass] DrissionPage failed: {e}")
            return False
    
    def _wait_for_cloudflare(self, timeout=30):
        """Wait for Cloudflare challenge to complete"""
        if not self.driver:
            return False
            
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.common.exceptions import TimeoutException
            
            # Wait for either the main content or challenge iframe to disappear
            wait = WebDriverWait(self.driver, timeout)
            
            # Check if Cloudflare challenge is present
            try:
                # Wait for challenge to complete (iframe should disappear or main content appear)
                wait.until(lambda d: len(d.find_elements("css selector", "iframe[src*='challenges']")) == 0 or 
                          len(d.find_elements("css selector", "#cf-challenge-running")) == 0)
                time.sleep(2)  # Extra wait for JS to complete
                return True
            except:
                return False
        except Exception as e:
            print(f"[CloudflareBypass] Wait error: {e}")
            return False
    
    def fetch(self, url, method='auto'):
        """
        Fetch a URL bypassing Cloudflare
        
        Args:
            url: URL to fetch
            method: 'cloudscraper', 'uc', 'drission', or 'auto'
            
        Returns:
            HTML content or None on failure
        """
        # Try DrissionPage first in auto mode (most reliable for Cloudflare)
        if method in ['auto', 'drission']:
            if self._init_drissionpage():
                try:
                    print(f"[CloudflareBypass] DrissionPage navigating to {url}...")
                    self.browser.get(url)
                    time.sleep(10)  # Wait for challenge
                    content = self.browser.html
                    if content and len(content) > 1000:
                        print(f"[CloudflareBypass] DrissionPage SUCCESS")
                        return content
                except Exception as e:
                    print(f"[CloudflareBypass] DrissionPage error: {e}")
        
        # Try cloudscraper second (fast but can't solve JS challenges)
        if method in ['auto', 'cloudscraper']:
            if self._init_cloudscraper():
                try:
                    response = self.scraper.get(url, timeout=30)
                    if response.status_code == 200:
                        # Check if we got actual content or Cloudflare challenge
                        if 'cloudflare' not in response.text.lower() or 'challenge' not in response.text.lower():
                            print(f"[CloudflareBypass] cloudscraper SUCCESS")
                            return response.text
                        print("[CloudflareBypass] cloudscraper got challenge page")
                except Exception as e:
                    print(f"[CloudflareBypass] cloudscraper error: {e}")
        
        # Try undetected-chromedriver as last resort
        if method in ['auto', 'uc']:
            if self._init_undetected_chromedriver():
                try:
                    print(f"[CloudflareBypass] Navigating to {url}...")
                    self.driver.get(url)
                    
                    # Wait for Cloudflare challenge
                    if self._wait_for_cloudflare(timeout=30):
                        time.sleep(3)
                        content = self.driver.page_source
                        if content and len(content) > 1000:
                            print(f"[CloudflareBypass] undetected-chromedriver SUCCESS")
                            return content
                except Exception as e:
                    print(f"[CloudflareBypass] undetected-chromedriver error: {e}")
        
        print("[CloudflareBypass] All methods failed")
        return None
    
    def close(self):
        """Close browser/driver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        if self.browser:
            try:
                self.browser.quit()
            except:
                pass
        print("[CloudflareBypass] Closed")


def bypass_cloudflare(url, method='auto', headless=True):
    """
    Convenience function to bypass Cloudflare
    
    Args:
        url: URL to access
        method: 'cloudscraper', 'uc', 'drission', or 'auto'
        headless: Use headless mode (for UC/Drission)
        
    Returns:
        HTML content or None
    """
    bypasser = CloudflareBypasser(headless=headless)
    try:
        return bypasser.fetch(url, method)
    finally:
        bypasser.close()


# Demo/test function
def test_bypass():
    """Test the Cloudflare bypass"""
    test_urls = [
        "https://groq.com",
        "https://www.cloudflare.com",
        "https://nowsecure.nl",  # Known Cloudflare-protected test site
    ]
    
    print("=" * 50)
    print("Cloudflare Bypass Test")
    print("=" * 50)
    
    bypasser = CloudflareBypasser(headless=False)  # Use visible browser for testing
    
    for url in test_urls:
        print(f"\n🔄 Testing: {url}")
        content = bypasser.fetch(url, method='auto')
        if content:
            print(f"✅ SUCCESS! Got {len(content)} bytes")
            # Print title if available
            if '<title>' in content.lower():
                start = content.lower().find('<title>')
                end = content.lower().find('</title>', start)
                if start > 0 and end > start:
                    title = content[start+7:end]
                    print(f"   Title: {title}")
        else:
            print(f"❌ FAILED")
    
    bypasser.close()
    print("\n" + "=" * 50)
    print("Test complete")
    print("=" * 50)


if __name__ == "__main__":
    test_bypass()
