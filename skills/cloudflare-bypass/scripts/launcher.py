"""
Cloudflare Bypass - Python Version
Uses undetected-chromedriver to bypass Cloudflare protection

Usage:
    python launcher.py <url> [--headless] [--timeout <seconds>]
"""

import sys
import time
import argparse
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

try:
    import undetected_chromedriver as uc
except ImportError:
    print("Error: undetected-chromedriver not installed")
    print("Install with: pip install undetected-chromedriver")
    sys.exit(1)


USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
]


def wait_for_cloudflare(driver, timeout=30):
    """Wait for Cloudflare challenge to complete"""
    print("[Cloudflare] Waiting for challenge...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        # Check if Cloudflare challenge is still present
        page_source = driver.page_source.lower()
        
        if 'cloudflare' not in page_source and 'checking your browser' not in page_source:
            print("[Cloudflare] Challenge completed!")
            return True
        
        # Also check for specific Cloudflare elements
        try:
            challenge = driver.find_elements(By.ID, 'challenge-form')
            if not challenge:
                # Give it a bit more time
                time.sleep(2)
                if 'cloudflare' not in driver.page_source.lower():
                    print("[Cloudflare] Challenge completed!")
                    return True
        except:
            pass
        
        time.sleep(1)
    
    print("[Cloudflare] Timeout waiting for challenge")
    return False


def has_cloudflare_protection(driver):
    """Check if page still has Cloudflare protection"""
    page_source = driver.page_source.lower()
    return ('cloudflare' in page_source or 
            'checking your browser' in page_source or
            'challenge-form' in page_source)


def main():
    parser = argparse.ArgumentParser(description='Cloudflare Bypass - Python Version')
    parser.add_argument('url', help='URL to navigate to')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--timeout', type=int, default=30, help='Timeout in seconds')
    parser.add_argument('--proxy', type=str, default=None, help='Proxy server')
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("Cloudflare Bypass Launcher (Python)")
    print("=" * 50)
    print(f"Target URL: {args.url}")
    print(f"Headless: {args.headless}")
    print(f"Timeout: {args.timeout}s")
    print("=" * 50)
    
    options = uc.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument(f'--user-agent={USER_AGENTS[0]}')
    
    if args.headless:
        options.add_argument('--headless=new')
    
    if args.proxy:
        options.add_argument(f'--proxy-server={args.proxy}')
    
    try:
        print("\n[+] Launching undetected Chrome...")
        driver = uc.Chrome(options=options, headless=args.headless)
        
        print(f"[+] Navigating to {args.url}")
        driver.get(args.url)
        
        # Wait for Cloudflare
        wait_for_cloudflare(driver, args.timeout)
        
        # Check status
        title = driver.title
        print(f"\n[+] Page title: {title}")
        
        if has_cloudflare_protection(driver):
            print("[!] WARNING: May still have Cloudflare protection")
        else:
            print("[+] Successfully bypassed Cloudflare!")
        
        # Print some content
        content = driver.page_source
        print(f"\n[+] Page loaded, content length: {len(content)} bytes")
        print(f"[+] First 500 chars: {content[:500]}")
        
        print("\n[+] Keeping browser open for 10 seconds...")
        time.sleep(10)
        
    except Exception as e:
        print(f"\n[-] Error: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass


if __name__ == '__main__':
    main()
