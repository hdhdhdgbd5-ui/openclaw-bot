from playwright.sync_api import sync_playwright

p = sync_playwright().start()
b = p.chromium.launch(headless=False)
page = b.new_page()

# Try Craigslist Germany
page.goto('https://dusseldorf.craigslist.org/')
page.wait_for_timeout(3000)

# Click create to post
page.click('a:has-text("post")')
page.wait_for_timeout(2000)

page.screenshot(path='C:/Users/armoo/.openclaw/workspace/craigslist_post.png')
print('Clicked post')
b.close()
p.stop()
