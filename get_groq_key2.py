from playwright.sync_api import sync_playwright
import os

# Try to use existing browser profile
p = sync_playwright().start()
b = p.chromium.launch(
    headless=False,
    user_data_dir=os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data")
)
page = b.new_page()
page.goto('https://console.groq.com/keys')
page.wait_for_timeout(5000)
page.screenshot(path='groq_with_profile.png')
print('URL:', page.url)
print('Title:', page.title())
b.close()
p.stop()
