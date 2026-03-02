from playwright.sync_api import sync_playwright
p = sync_playwright().start()
b = p.chromium.launch(headless=False)  # headed mode
page = b.new_page()
page.goto('https://console.groq.com/keys')
page.wait_for_timeout(5000)
page.screenshot(path='groq_console.png')
print('Please click Add API Key and create a key manually!')
print('Or I can try to click it...')
b.close()
p.stop()
