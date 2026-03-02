"""Quick test for browser-selector skill"""
import asyncio
from browser_selector import BrowserSelector

async def test():
    print("Starting browser selector test...")
    selector = BrowserSelector({'headless': True})
    await selector.start()
    
    print("Navigating to example.com...")
    await selector.navigate('https://example.com')
    
    title = await selector.page.title()
    print(f'Page title: {title}')
    
    # Test getting text
    h1 = await selector.extract_text("h1")
    print(f'H1 text: {h1}')
    
    await selector.close()
    print('Test PASSED!')

if __name__ == "__main__":
    asyncio.run(test())
