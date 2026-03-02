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

# Tab to find button
page.keyboard.press('Tab')
page.wait_for_timeout(500)
page.keyboard.press('Tab')
page.wait_for_timeout(500)

# Press Enter
page.keyboard.press('Enter')
page.wait_for_timeout(2000)

page.screenshot(path='C:/Users/armoo/.openclaw/workspace/groq_tab.png')
print('Tabbed and pressed Enter')
browser.close()
p.stop()
