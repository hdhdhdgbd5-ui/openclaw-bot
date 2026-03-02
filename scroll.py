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

# Scroll down
page.evaluate('window.scrollTo(0, 500)')
page.wait_for_timeout(1000)

page.screenshot(path='C:/Users/armoo/.openclaw/workspace/groq_scrolled.png')
print('Scrolled')
browser.close()
p.stop()
