from playwright.sync_api import sync_playwright
p = sync_playwright().start()
b = p.chromium.launch(headless=True)
page = b.new_page()
page.set_extra_http_headers({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
page.goto('https://console.groq.com/keys')
page.wait_for_timeout(5000)

# Click Add API Key button
page.click('button:has-text("Add API Key")')
page.wait_for_timeout(2000)

# Fill in key name
page.fill('input[placeholder*="Key name"], input[name="name"]', 'AngelArmyKey')
page.wait_for_timeout(1000)

# Click Create
page.click('button:has-text("Create"), button[type="submit"]')
page.wait_for_timeout(3000)

# Get the API key
page.screenshot(path='groq_created.png')

# Try to extract the key
content = page.content()
if 'gsk_' in content:
    print('API Key found!')
else:
    print('Key might be created, check screenshot')

b.close()
p.stop()
