"""
Browser Automation - Navigation, waiting, dynamic content, data extraction
"""
import asyncio
import json
import re
import time
from typing import Dict, List, Optional, Any, Callable, Union
from urllib.parse import urlparse
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright, Route, Request

class BrowserAutomation:
    """Advanced browser automation for navigation, waiting, and data extraction"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.port = self.config.get("port", 3002)
        self.headless = self.config.get("headless", True)
        self.viewport = self.config.get("viewport", {"width": 1920, "height": 1080})
        self.timeout = self.config.get("timeout", 30000)
        self.stealth = self.config.get("stealth", True)
        
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        self._dialog_handler: Optional[Callable] = None
        self._download_handler: Optional[Callable] = None
        self._request_interceptor: Optional[Callable] = None
        
    async def start(self) -> "BrowserAutomation":
        """Start the browser"""
        self.playwright = await async_playwright().start()
        
        args = ['--disable-blink-features=AutomationControlled']
        if self.config.get("blockAds"):
            args.extend(['--block-tracking-resources'])
            
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=args
        )
        
        self.context = await self.browser.new_context(
            viewport=self.viewport,
            ignore_https_errors=True
        )
        
        if self.stealth:
            await self.context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            """)
        
        self.page = await self.context.new_page()
        
        # Setup handlers
        self.page.on("dialog", self._handle_dialog)
        self.page.on("download", self._handle_download)
        
        return self
        
    async def _handle_dialog(self, dialog):
        if self._dialog_handler:
            await self._dialog_handler(dialog)
        else:
            await dialog.accept()
            
    async def _handle_download(self, download):
        if self._download_handler:
            await self._download_handler(download.path())
            
    def on_dialog(self, handler: Callable):
        """Set dialog handler"""
        self._dialog_handler = handler
        
    def on_download(self, handler: Callable):
        """Set download handler"""
        self._download_handler = handler
        
    # ==================== NAVIGATION ====================
    
    async def navigate(self, url: str, wait_until: str = "domcontentloaded", 
                       timeout: Optional[int] = None) -> "BrowserAutomation":
        """Navigate to URL"""
        if not self.page:
            raise RuntimeError("Browser not started")
        await self.page.goto(url, wait_until=wait_until, timeout=timeout or self.timeout)
        return self
        
    async def navigate_with_retry(self, url: str, retries: int = 3, 
                                  delay: int = 2000) -> "BrowserAutomation":
        """Navigate with retry on failure"""
        last_error = None
        for attempt in range(retries):
            try:
                await self.navigate(url)
                return self
            except Exception as e:
                last_error = e
                if attempt < retries - 1:
                    await asyncio.sleep(delay / 1000)
        raise last_error
        
    async def go_back(self) -> "BrowserAutomation":
        """Go back in history"""
        await self.page.go_back()
        return self
        
    async def go_forward(self) -> "BrowserAutomation":
        """Go forward in history"""
        await self.page.go_forward()
        return self
        
    async def reload(self) -> "BrowserAutomation":
        """Reload page"""
        await self.page.reload()
        return self
        
    # ==================== WAITING ====================
    
    async def wait_for_element(self, selector: str, state: str = "visible",
                               timeout: Optional[int] = None) -> "BrowserAutomation":
        """Wait for element state"""
        await self.page.wait_for_selector(selector, state=state, 
                                          timeout=timeout or self.timeout)
        return self
        
    async def wait_for_text(self, selector: str, text: str, 
                            timeout: Optional[int] = None) -> "BrowserAutomation":
        """Wait for element to contain text"""
        await self.page.wait_for_function(
            f"""(selector, text) => {{
                const el = document.querySelector(selector);
                return el && el.textContent === text;
            }}""",
            selector, text,
            timeout=timeout or self.timeout
        )
        return self
        
    async def wait_for_text_contains(self, selector: str, text: str,
                                     timeout: Optional[int] = None) -> "BrowserAutomation":
        """Wait for element to contain text"""
        await self.page.wait_for_function(
            f"""(selector, text) => {{
                const el = document.querySelector(selector);
                return el && el.textContent.includes(text);
            }}""",
            selector, text,
            timeout=timeout or self.timeout
        )
        return self
        
    async def wait_for_text_match(self, selector: str, pattern: str,
                                  timeout: Optional[int] = None) -> "BrowserAutomation":
        """Wait for text to match regex"""
        await self.page.wait_for_function(
            f"""(selector, pattern) => {{
                const el = document.querySelector(selector);
                return el && new RegExp(pattern).test(el.textContent);
            }}""",
            selector, pattern,
            timeout=timeout or self.timeout
        )
        return self
        
    async def wait_for_url(self, pattern: str, timeout: Optional[int] = None) -> "BrowserAutomation":
        """Wait for URL to match pattern"""
        await self.page.wait_for_url(pattern, timeout=timeout or self.timeout)
        return self
        
    async def wait_for_url_contains(self, substring: str,
                                    timeout: Optional[int] = None) -> "BrowserAutomation":
        """Wait for URL to contain substring"""
        await self.page.wait_for_url(f"*{substring}", timeout=timeout or self.timeout)
        return self
        
    async def wait_for_url_match(self, pattern: str, timeout: Optional[int] = None) -> "BrowserAutomation":
        """Wait for URL to match regex"""
        await self.page.wait_for_url(re.compile(pattern), timeout=timeout or self.timeout)
        return self
        
    async def wait_for_navigation(self, timeout: Optional[int] = None) -> "BrowserAutomation":
        """Wait for navigation to complete"""
        await self.page.wait_for_load_state("networkidle", timeout=timeout or self.timeout)
        return self
        
    async def wait_for_condition(self, condition: Callable, 
                               timeout: Optional[int] = None,
                               interval: int = 100) -> "BrowserAutomation":
        """Wait for custom condition"""
        start_time = time.time()
        while not await condition():
            if (time.time() - start_time) * 1000 > (timeout or self.timeout):
                raise TimeoutError("Condition timeout")
            await asyncio.sleep(interval / 1000)
        return self
        
    async def poll_until(self, condition: Callable, timeout: Optional[int] = None,
                        interval: int = 1000) -> Any:
        """Poll until condition is true, return result"""
        start_time = time.time()
        while True:
            result = await condition()
            if result:
                return result
            if (time.time() - start_time) * 1000 > (timeout or self.timeout):
                raise TimeoutError("Poll timeout")
            await asyncio.sleep(interval / 1000)
            
    # ==================== DYNAMIC CONTENT ====================
    
    async def infinite_scroll(self, selector: str, max_scrolls: int = 10,
                              delay: int = 1000, until_empty: bool = False) -> "BrowserAutomation":
        """Infinite scroll on selector"""
        prev_height = 0
        scrolls = 0
        
        while scrolls < max_scrolls:
            # Scroll to bottom
            await self.page.evaluate(f"""
                const el = document.querySelector('{selector}');
                if (el) el.scrollTop = el.scrollHeight;
                else window.scrollTo(0, document.body.scrollHeight);
            """)
            
            await asyncio.sleep(delay / 1000)
            
            # Check new height
            new_height = await self.page.evaluate("document.body.scrollHeight")
            
            if new_height == prev_height:
                if until_empty:
                    break
                # Try a few more times
                for _ in range(3):
                    await self.page.evaluate("window.scrollBy(0, 500)")
                    await asyncio.sleep(500)
                    new_height = await self.page.evaluate("document.body.scrollHeight")
                    if new_height != prev_height:
                        break
                else:
                    break
                    
            prev_height = new_height
            scrolls += 1
            
        return self
        
    async def wait_for_images(self, selector: str = "img",
                             timeout: Optional[int] = None) -> "BrowserAutomation":
        """Wait for lazy loaded images"""
        await self.page.wait_for_function(
            f"""(selector) => {{
                const imgs = document.querySelectorAll(selector);
                return Array.from(imgs).every(img => img.complete);
            }}""",
            selector,
            timeout=timeout or self.timeout
        )
        return self
        
    async def wait_for_content(self, selector: str,
                              timeout: Optional[int] = None) -> "BrowserAutomation":
        """Wait for lazy content to appear"""
        await self.page.wait_for_selector(selector, state="attached",
                                         timeout=timeout or self.timeout)
        return self
        
    async def wait_for_spa_navigation(self, timeout: Optional[int] = None) -> "BrowserAutomation":
        """Wait for SPA navigation (URL change + content change)"""
        initial_url = self.page.url
        await self.page.wait_for_function(
            f"""(initialUrl) => {{
                return document.readyState === 'complete' && 
                       (window.location.href !== initialUrl || document.body);
            }}""",
            initial_url,
            timeout=timeout or self.timeout
        )
        return self
        
    # ==================== DATA EXTRACTION ====================
    
    async def extract_text(self, selector: str) -> str:
        """Extract text from element"""
        return await self.page.locator(selector).inner_text()
        
    async def extract_all_text(self, selector: str) -> List[str]:
        """Extract text from all matching elements"""
        elements = await self.page.locator(selector).all()
        return [await el.inner_text() for el in elements]
        
    async def extract_html(self, selector: str) -> str:
        """Extract inner HTML"""
        return await self.page.locator(selector).inner_html()
        
    async def extract_outer_html(self, selector: str) -> str:
        """Extract outer HTML"""
        return await self.page.locator(selector).evaluate("el => el.outerHTML")
        
    async def extract_table(self, selector: str, headers: bool = True) -> List[Dict]:
        """Extract table data"""
        return await self.page.evaluate(f"""(selector, headers) => {{
            const table = document.querySelector(selector);
            if (!table) return [];
            
            const rows = Array.from(table.querySelectorAll('tr'));
            if (rows.length === 0) return [];
            
            let headerRow = rows[0];
            let headers_list = [];
            
            if (headers) {{
                headers_list = Array.from(headerRow.querySelectorAll('th, td'))
                    .map(cell => cell.textContent.trim());
            }}
            
            const data_rows = headers ? rows.slice(1) : rows;
            
            return data_rows.map(row => {{
                const cells = Array.from(row.querySelectorAll('th, td'));
                const row_data = {{}};
                
                cells.forEach((cell, index) => {{
                    const key = headers && headers_list[index] ? headers_list[index] : 'col' + index;
                    row_data[key] = cell.textContent.trim();
                }});
                
                return row_data;
            }});
        }}""", selector, headers)
        
    async def extract_json(self, selector: str) -> Any:
        """Extract JSON from element or script"""
        content = await self.page.locator(selector).inner_text()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to extract from script
            script_content = await self.page.evaluate(f"""(selector) => {{
                const el = document.querySelector(selector);
                if (el && el.textContent) {{
                    const match = el.textContent.match(/\\{{[\\s\\S]*\\}}/);
                    return match ? match[0] : el.textContent;
                }}
                return null;
            }}""", selector)
            return json.loads(script_content) if script_content else None
            
    async def extract_structured(self, schema: Dict) -> Dict:
        """Extract structured data based on schema"""
        return await self.page.evaluate(f"""(schema) => {{
            const result = {{}};
            
            for (const [key, value] of Object.entries(schema)) {{
                if (typeof value === 'string') {{
                    // Simple selector
                    const el = document.querySelector(value.replace('::text', ''));
                    if (el) {{
                        result[key] = value.endsWith('::text') ? el.textContent.trim() : el.textContent.trim();
                    }}
                }} else if (Array.isArray(value)) {{
                    // List selector
                    const [list_sel, item_sel] = value;
                    const items = document.querySelectorAll(list_sel);
                    result[key] = Array.from(items).map(item => {{
                        const sub = item.querySelector(item_sel);
                        return sub ? sub.textContent.trim() : item.textContent.trim();
                    }});
                }} else if (typeof value === 'object') {{
                    // Nested object
                    const nested = {{}};
                    for (const [nested_key, nested_value] of Object.entries(value)) {{
                        const el = document.querySelector(nested_value);
                        if (el) nested[nested_key] = el.textContent.trim();
                    }}
                    result[key] = nested;
                }}
            }}
            
            return result;
        }}""", schema)
        
    async def extract_links(self, selector: str = "a") -> List[Dict]:
        """Extract all links"""
        return await self.page.evaluate(f"""(selector) => {{
            const links = Array.from(document.querySelectorAll(selector));
            return links.map(link => ({{
                text: link.textContent.trim(),
                href: link.href
            }}));
        }}""", selector)
        
    async def extract_images(self, selector: str = "img") -> List[Dict]:
        """Extract all images"""
        return await self.page.evaluate(f"""(selector) => {{
            const images = Array.from(document.querySelectorAll(selector));
            return images.map(img => ({{
                src: img.src,
                alt: img.alt,
                width: img.width,
                height: img.height
            }}));
        }}""", selector)
        
    # ==================== NETWORK ====================
    
    async def intercept_requests(self, handler: Callable[[Request], None],
                                url_pattern: Optional[str] = None) -> "BrowserAutomation":
        """Intercept network requests"""
        if url_pattern:
            async def filtered_route(route):
                req = route.request
                if self._matches_pattern(req.url, url_pattern):
                    await handler(req)
                await route.continue_()
            await self.page.route("**/*", filtered_route)
        else:
            self._request_interceptor = handler
            await self.page.route("**/*", self._intercept_wrapper)
        return self
        
    async def _intercept_wrapper(self, route):
        if self._request_interceptor:
            await self._request_interceptor(route.request)
        await route.continue_()
        
    def _matches_pattern(self, url: str, pattern: str) -> bool:
        """Match URL against pattern"""
        if pattern.startswith("**"):
            return pattern[2:] in url
        if "*" in pattern:
            regex = pattern.replace(".", r"\.").replace("*", ".*")
            return bool(re.match(f"^{regex}$", url))
        return pattern in url
        
    async def wait_for_request(self, url_pattern: str, 
                              timeout: Optional[int] = None) -> Request:
        """Wait for specific request"""
        return await self.page.wait_for_request(url_pattern, 
                                                timeout=timeout or self.timeout)
        
    async def mock_response(self, url_pattern: str, status: int = 200,
                           body: Optional[Any] = None,
                           headers: Optional[Dict] = None) -> "BrowserAutomation":
        """Mock API response"""
        async def handle_route(route):
            await route.fulfill(
                status=status,
                body=json.dumps(body) if body else "",
                headers=headers or {"Content-Type": "application/json"}
            )
        await self.page.route(url_pattern, handle_route)
        return self
        
    async def block_requests(self, *patterns: str) -> "BrowserAutomation":
        """Block requests matching patterns"""
        async def block(route):
            await route.abort()
        for pattern in patterns:
            await self.page.route(pattern, block)
        return self
        
    # ==================== STORAGE ====================
    
    async def get_cookies(self) -> List[Dict]:
        """Get all cookies"""
        return await self.context.cookies()
        
    async def get_cookie(self, name: str) -> Optional[Dict]:
        """Get cookie by name"""
        cookies = await self.context.cookies()
        for cookie in cookies:
            if cookie["name"] == name:
                return cookie
        return None
        
    async def set_cookie(self, name: str, value: str, 
                        domain: Optional[str] = None,
                        path: str = "/",
                        expires: Optional[float] = None) -> "BrowserAutomation":
        """Set cookie"""
        cookie = {"name": name, "value": value, "path": path}
        if domain:
            cookie["domain"] = domain
        if expires:
            cookie["expires"] = expires
        await self.context.add_cookies([cookie])
        return self
        
    async def delete_cookie(self, name: str) -> "BrowserAutomation":
        """Delete cookie by name"""
        await self.context.clear_cookies()
        return self
        
    async def clear_cookies(self) -> "BrowserAutomation":
        """Clear all cookies"""
        await self.context.clear_cookies()
        return self
        
    async def get_local_storage(self, key: Optional[str] = None) -> Union[Dict, str]:
        """Get localStorage"""
        if key:
            return await self.page.evaluate(f"localStorage.getItem('{key}')")
        return await self.page.evaluate("Object.fromEntries(Object.entries(localStorage))")
        
    async def set_local_storage(self, key: str, value: str) -> "BrowserAutomation":
        """Set localStorage item"""
        await self.page.evaluate(f"localStorage.setItem('{key}', '{value}')")
        return self
        
    async def remove_local_storage(self, key: str) -> "BrowserAutomation":
        """Remove localStorage item"""
        await self.page.evaluate(f"localStorage.removeItem('{key}')")
        return self
        
    async def clear_local_storage(self) -> "BrowserAutomation":
        """Clear localStorage"""
        await self.page.evaluate("localStorage.clear()")
        return self
        
    async def get_session_storage(self, key: Optional[str] = None) -> Union[Dict, str]:
        """Get sessionStorage"""
        if key:
            return await self.page.evaluate(f"sessionStorage.getItem('{key}')")
        return await self.page.evaluate("Object.fromEntries(Object.entries(sessionStorage))")
        
    async def set_session_storage(self, key: str, value: str) -> "BrowserAutomation":
        """Set sessionStorage item"""
        await self.page.evaluate(f"sessionStorage.setItem('{key}', '{value}')")
        return self
        
    async def clear_session_storage(self) -> "BrowserAutomation":
        """Clear sessionStorage"""
        await self.page.evaluate("sessionStorage.clear()")
        return self
        
    # ==================== UTILITY ====================
    
    def get_url(self) -> str:
        """Get current URL"""
        return self.page.url
        
    async def get_title(self) -> str:
        """Get page title"""
        return await self.page.title()
        
    async def get_content(self) -> str:
        """Get page HTML"""
        return await self.page.content()
        
    # ==================== CLOSE ====================
    
    async def close(self) -> None:
        """Close browser"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


# CLI interface
async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Browser Automation")
    parser.add_argument("--url", "-u", help="URL to navigate")
    parser.add_argument("--extract", "-e", help="Extract data (text/table/json)")
    parser.add_argument("--screenshot", "-s", help="Screenshot filename")
    parser.add_argument("--headless", action="store_true", default=True)
    
    args = parser.parse_args()
    
    automation = BrowserAutomation({"headless": args.headless})
    await automation.start()
    
    if args.url:
        await automation.navigate(args.url)
        
    if args.extract:
        if args.extract == "table":
            data = await automation.extract_table("table")
            print(json.dumps(data, indent=2))
        elif args.extract == "json":
            data = await automation.extract_json("script")
            print(json.dumps(data, indent=2))
        else:
            text = await automation.extract_text(args.extract)
            print(text)
            
    if args.screenshot:
        await automation.page.screenshot(path=args.screenshot, full_page=True)
        
    await automation.close()


if __name__ == "__main__":
    asyncio.run(main())
