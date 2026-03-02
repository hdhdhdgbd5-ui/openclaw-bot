"""
Browser Selector - Click, fill, scroll, copy/paste, screenshot elements
"""
import asyncio
import json
import os
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright

class BrowserSelector:
    """Browser automation for element selection and interaction"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.port = self.config.get("port", 3001)
        self.headless = self.config.get("headless", True)
        self.viewport = self.config.get("viewport", {"width": 1920, "height": 1080})
        self.user_agent = self.config.get("userAgent")
        self.timeout = self.config.get("timeout", 30000)
        
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._server = None
        
    async def start(self) -> "BrowserSelector":
        """Start the browser"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        self.context = await self.browser.new_context(
            viewport=self.viewport,
            user_agent=self.user_agent
        )
        self.page = await self.context.new_page()
        return self
        
    async def navigate(self, url: str, wait_until: str = "domcontentloaded") -> "BrowserSelector":
        """Navigate to URL"""
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        await self.page.goto(url, wait_until=wait_until, timeout=self.timeout)
        return self
        
    # ==================== CLICK OPERATIONS ====================
    
    async def click(self, selector: str, timeout: Optional[int] = None) -> "BrowserSelector":
        """Click element by CSS selector"""
        await self.page.click(selector, timeout=timeout or self.timeout)
        return self
        
    async def click_by_text(self, text: str, timeout: Optional[int] = None) -> "BrowserSelector":
        """Click element containing text"""
        await self.page.get_by_text(text, exact=False).click(timeout=timeout or self.timeout)
        return self
        
    async def click_by_xpath(self, xpath: str, timeout: Optional[int] = None) -> "BrowserSelector":
        """Click element by XPath"""
        await self.page.locator(f"xpath={xpath}").click(timeout=timeout or self.timeout)
        return self
        
    async def click_link(self, text: str, timeout: Optional[int] = None) -> "BrowserSelector":
        """Click link by text"""
        await self.page.get_by_role("link", name=text).click(timeout=timeout or self.timeout)
        return self
        
    async def click_button(self, text: str, timeout: Optional[int] = None) -> "BrowserSelector":
        """Click button by text"""
        await self.page.get_by_role("button", name=text).click(timeout=timeout or self.timeout)
        return self
        
    async def double_click(self, selector: str, timeout: Optional[int] = None) -> "BrowserSelector":
        """Double click element"""
        await self.page.dblclick(selector, timeout=timeout or self.timeout)
        return self
        
    async def right_click(self, selector: str, timeout: Optional[int] = None) -> "BrowserSelector":
        """Right click element (context menu)"""
        await self.page.click(selector, button="right", timeout=timeout or self.timeout)
        return self
        
    async def hover(self, selector: str, timeout: Optional[int] = None) -> "BrowserSelector":
        """Hover over element"""
        await self.page.hover(selector, timeout=timeout or self.timeout)
        return self
        
    # ==================== FILL OPERATIONS ====================
    
    async def fill(self, fields: Dict[str, str]) -> "BrowserSelector":
        """Fill multiple input fields"""
        for selector, value in fields.items():
            await self.page.fill(selector, value)
        return self
        
    async def fill_field(self, selector: str, value: str) -> "BrowserSelector":
        """Fill a single field"""
        await self.page.fill(selector, value)
        return self
        
    async def fill_textarea(self, selector: str, value: str) -> "BrowserSelector":
        """Fill textarea"""
        await self.page.fill(selector, value)
        return self
        
    async def select(self, selector: str, value: str) -> "BrowserSelector":
        """Select option by value or label"""
        await self.page.select_option(selector, value)
        return self
        
    async def select_multiple(self, selector: str, values: List[str]) -> "BrowserSelector":
        """Select multiple options"""
        await self.page.select_option(selector, values)
        return self
        
    async def check(self, selector: str) -> "BrowserSelector":
        """Check checkbox"""
        await self.page.check(selector)
        return self
        
    async def uncheck(self, selector: str) -> "BrowserSelector":
        """Uncheck checkbox"""
        await self.page.uncheck(selector)
        return self
        
    # ==================== SCROLL OPERATIONS ====================
    
    async def scroll_to(self, selector: str) -> "BrowserSelector":
        """Scroll to element"""
        await self.page.locator(selector).scroll_into_view_if_needed()
        return self
        
    async def scroll_to_top(self) -> "BrowserSelector":
        """Scroll to top of page"""
        await self.page.evaluate("window.scrollTo(0, 0)")
        return self
        
    async def scroll_to_bottom(self) -> "BrowserSelector":
        """Scroll to bottom of page"""
        await self.page.evaluate("""
            () => {
                const body = document.body;
                const html = document.documentElement;
                const height = Math.max(
                    body ? body.scrollHeight : 0,
                    html ? html.scrollHeight : 0
                );
                window.scrollTo(0, height);
            }
        """)
        return self
        
    async def scroll_by(self, x: int, y: int) -> "BrowserSelector":
        """Scroll by pixel amount"""
        await self.page.evaluate(f"window.scrollBy({x}, {y})")
        return self
        
    # ==================== COPY/PASTE OPERATIONS ====================
    
    async def copy_text(self, selector: str) -> str:
        """Copy text from element"""
        return await self.page.locator(selector).inner_text()
        
    async def copy_all_text(self, selector: str) -> List[str]:
        """Copy text from all matching elements"""
        elements = await self.page.locator(selector).all()
        return [await el.inner_text() for el in elements]
        
    async def copy_attribute(self, selector: str, attr: str) -> str:
        """Copy attribute value from element"""
        return await self.page.locator(selector).get_attribute(attr)
        
    async def paste(self, selector: str, text: str) -> "BrowserSelector":
        """Paste text into field (clears field first)"""
        await self.page.fill(selector, text)
        return self
        
    # ==================== SCREENSHOT OPERATIONS ====================
    
    async def screenshot(self, filename: str = "screenshot.png", 
                        full_page: bool = False,
                        selector: Optional[str] = None) -> "BrowserSelector":
        """Take screenshot"""
        if selector:
            element = await self.page.locator(selector)
            await element.screenshot(path=filename)
        else:
            await self.page.screenshot(path=filename, full_page=full_page)
        return self
        
    async def screenshot_element(self, selector: str, filename: str) -> "BrowserSelector":
        """Take screenshot of specific element"""
        await self.page.locator(selector).screenshot(path=filename)
        return self
        
    # ==================== ELEMENT STATE CHECKS ====================
    
    async def exists(self, selector: str) -> bool:
        """Check if element exists"""
        return await self.page.locator(selector).count() > 0
        
    async def is_visible(self, selector: str) -> bool:
        """Check if element is visible"""
        return await self.page.locator(selector).is_visible()
        
    async def is_enabled(self, selector: str) -> bool:
        """Check if element is enabled"""
        return await self.page.locator(selector).is_enabled()
        
    async def is_checked(self, selector: str) -> bool:
        """Check if checkbox/radio is checked"""
        return await self.page.locator(selector).is_checked()
        
    # ==================== ATTRIBUTE OPERATIONS ====================
    
    async def get_attribute(self, selector: str, attr: str) -> Optional[str]:
        """Get element attribute"""
        return await self.page.locator(selector).get_attribute(attr)
        
    async def set_attribute(self, selector: str, attr: str, value: str) -> "BrowserSelector":
        """Set element attribute"""
        await self.page.evaluate(
            f"""(selector, attr, value) => {{
                const el = document.querySelector(selector);
                if (el) el.setAttribute(attr, value);
            }}""",
            selector, attr, value
        )
        return self
        
    # ==================== WAIT OPERATIONS ====================
    
    async def wait_for(self, selector: str, timeout: Optional[int] = None) -> "BrowserSelector":
        """Wait for element to appear"""
        await self.page.wait_for_selector(selector, timeout=timeout or self.timeout)
        return self
        
    async def wait_for_navigation(self, timeout: Optional[int] = None) -> "BrowserSelector":
        """Wait for navigation to complete"""
        await self.page.wait_for_load_state("networkidle", timeout=timeout or self.timeout)
        return self
        
    async def wait_for_text(self, selector: str, text: str, timeout: Optional[int] = None) -> "BrowserSelector":
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
        
    # ==================== FIND OPERATIONS ====================
    
    async def find_by_text(self, text: str) -> List[str]:
        """Find all elements containing text"""
        elements = await self.page.get_by_text(text, exact=False).all()
        return [await el.inner_text() for el in elements]
        
    # ==================== JAVASCRIPT OPERATIONS ====================
    
    async def evaluate(self, script: str, selector: Optional[str] = None) -> Any:
        """Execute JavaScript"""
        if selector:
            return await self.page.evaluate(
                f"""(selector) => {{
                    const el = document.querySelector(selector);
                    {script}
                }}""",
                selector
            )
        return await self.page.evaluate(script)
        
    # ==================== SNAPSHOT ====================
    
    async def snapshot(self) -> Dict:
        """Get snapshot of page structure"""
        return await self.page.content()
        
    async def get_dom(self) -> str:
        """Get page HTML"""
        return await self.page.content()
        
    # ==================== CLOSE ====================
    
    async def close(self) -> None:
        """Close browser"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    # ==================== UTILITY ====================
    
    async def get_title(self) -> str:
        """Get page title"""
        return await self.page.title()
        
    async def get_url(self) -> str:
        """Get current URL"""
        return self.page.url
        
    async def extract_text(self, selector: str) -> str:
        """Extract text from element"""
        return await self.page.locator(selector).inner_text()
            
    # ==================== HTTP SERVER ====================
    
    async def start_server(self) -> None:
        """Start HTTP API server"""
        from aiohttp import web
        
        async def handle_click(request):
            data = await request.json()
            await self.click(data.get("selector"))
            return web.json_response({"success": True})
            
        async def handle_fill(request):
            data = await request.json()
            await self.fill(data.get("fields", {}))
            return web.json_response({"success": True})
            
        async def handle_scroll(request):
            data = await request.json()
            selector = data.get("selector")
            if selector:
                await self.scroll_to(selector)
            elif data.get("to") == "top":
                await self.scroll_to_top()
            elif data.get("to") == "bottom":
                await self.scroll_to_bottom()
            else:
                await self.scroll_by(data.get("x", 0), data.get("y", 0))
            return web.json_response({"success": True})
            
        async def handle_screenshot(request):
            data = await request.json()
            await self.screenshot(
                data.get("filename", "screenshot.png"),
                data.get("fullPage", False),
                data.get("selector")
            )
            return web.json_response({"success": True, "filename": data.get("filename")})
            
        async def handle_content(request):
            content = await self.page.content()
            return web.json_response({"content": content})
            
        app = web.Application()
        app.router.add_post("/api/click", handle_click)
        app.router.add_post("/api/fill", handle_fill)
        app.router.add_post("/api/scroll", handle_scroll)
        app.router.add_post("/api/screenshot", handle_screenshot)
        app.router.add_get("/api/content", handle_content)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "localhost", self.port)
        await site.start()
        print(f"Browser Selector API running on http://localhost:{self.port}")


# CLI interface
async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Browser Selector")
    parser.add_argument("--url", "-u", help="URL to navigate")
    parser.add_argument("--click", "-c", help="Click selector")
    parser.add_argument("--fill", "-f", help="Fill fields (JSON)")
    parser.add_argument("--screenshot", "-s", help="Screenshot filename")
    parser.add_argument("--headless", action="store_true", default=True)
    parser.add_argument("--server", action="store_true", help="Start HTTP server")
    
    args = parser.parse_args()
    
    config = {"headless": args.headless, "port": 3001}
    selector = BrowserSelector(config)
    
    await selector.start()
    
    if args.server:
        await selector.start_server()
        await asyncio.Event().wait()
    else:
        if args.url:
            await selector.navigate(args.url)
            
        if args.click:
            await selector.click(args.click)
            
        if args.fill:
            fields = json.loads(args.fill)
            await selector.fill(fields)
            
        if args.screenshot:
            await selector.screenshot(args.screenshot)
            
    await selector.close()


if __name__ == "__main__":
    asyncio.run(main())
