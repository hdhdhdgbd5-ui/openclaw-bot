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

# Click + Add API Key
page.click('button:has-text(\"+ Add API Key\")')
page.wait_for_timeout(2000)

page.screenshot(path='C:/Users/armoo/.openclaw/workspace/groq_create.png')
print('Clicked Add API Key!')
browser.close()
p.stop()
