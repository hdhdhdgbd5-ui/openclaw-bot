"""Quick test for browser-automation skill"""
import asyncio
from browser_automation import BrowserAutomation

async def test():
    print("Starting browser automation test...")
    automation = BrowserAutomation({'headless': True})
    await automation.start()
    
    print("Navigating to example.com...")
    await automation.navigate('https://example.com')
    
    title = await automation.get_title()
    print(f'Page title: {title}')
    
    # Test data extraction
    h1 = await automation.extract_text("h1")
    print(f'H1 text: {h1}')
    
    # Test getting links
    links = await automation.extract_links("a")
    print(f'Found {len(links)} links')
    
    await automation.close()
    print('Test PASSED!')

if __name__ == "__main__":
    asyncio.run(test())
