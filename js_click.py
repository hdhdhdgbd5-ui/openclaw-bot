from playwright.sync_api import sync_playwright
import os

p = sync_playwright().start()
chrome_path = os.path.expanduser('~\\\\AppData\\\\Local\\\\Google\\\\Chrome\\\\User Data\\\\Profile 1')

browser = p.chromium.launch_persistent_context(
    user_data_dir=chrome_path,
    headless=False,
    args=['--no-sandbox']
)
page = browser.new_page()
page.goto('https://console.groq.com/keys')
page.wait_for_timeout(5000)

# Press Escape to close dialog
page.keyboard.press('Escape')
page.wait_for_timeout(1000)

# Use JavaScript to click
result = page.evaluate('''
() => {
    const buttons = Array.from(document.querySelectorAll('button'));
    const addBtn = buttons.find(b => b.textContent.includes('Add API Key'));
    if (addBtn) {
        addBtn.click();
        return 'Clicked!';
    }
    return 'Not found';
}
''')
print(result)

page.wait_for_timeout(2000)
page.screenshot(path='C:/Users/armoo/.openclaw/workspace/groq_js_click.png')
browser.close()
p.stop()
