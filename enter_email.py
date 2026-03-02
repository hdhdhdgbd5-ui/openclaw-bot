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

# Fill email
page.fill('input[type=email]', 'e170u6kecbj@pinmx.net')
page.wait_for_timeout(1000)

# Click Continue
page.click('button:has-text("Continue")')
page.wait_for_timeout(3000)

page.screenshot(path='C:/Users/armoo/.openclaw/workspace/groq_email.png')
print('Email entered!')
browser.close()
p.stop()
