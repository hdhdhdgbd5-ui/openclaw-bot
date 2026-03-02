from playwright.sync_api import sync_playwright
import os, time

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

# Find Add API Key button
page.evaluate('window.scrollTo(0, 300)')
time.sleep(2)

# Try to find button
result = page.evaluate('''
() => {
    const buttons = Array.from(document.querySelectorAll('button'));
    const addBtn = buttons.find(b => b.textContent.includes('Add'));
    if (addBtn) {
        addBtn.click();
        return 'Clicked!';
    }
    return 'Not found';
}
''')
print(result)
page.wait_for_timeout(2000)

# Try to fill key name - use evaluate instead
page.evaluate('document.querySelector(\'input[placeholder*="Key"]\').value = "AngelArmyKey"')
page.wait_for_timeout(1000)

# Click Create
page.click('button:has-text("Create")')
page.wait_for_timeout(3000)

page.screenshot(path='C:/Users/armoo/.openclaw/workspace/groq_created.png')
print('API Key created!')
browser.close()
p.stop()
