# Browser Automation Skill

Advanced browser automation for navigating, waiting, handling dynamic content, and extracting data from web pages.

## Features

- **URL Navigation** - Navigate to URLs with various wait conditions
- **Element Waiting** - Wait for elements to appear, disappear, or change
- **Dynamic Content** - Handle SPAs, lazy-loaded content, infinite scroll
- **Data Extraction** - Extract text, tables, JSON, structured data
- **Network Interception** - Capture and modify network requests
- **Cookie Management** - Get, set, delete cookies
- **Local Storage** - Read and write localStorage/sessionStorage

## Usage

### Python API

```python
from browser_automation import BrowserAutomation

# Initialize automation
automation = BrowserAutomation()

# Start browser
await automation.start()

# Navigate with wait conditions
await automation.navigate("https://example.com", wait_until="networkidle")

# Wait for element
await automation.wait_for_element("#content", state="visible")

# Wait for text
await automation.wait_for_text(".status", "Ready")

# Wait for navigation
await automation.wait_for_url("**/dashboard/**")

# Handle dynamic content - infinite scroll
await automation.infinite_scroll(".posts", max_scrolls=10)

# Handle lazy loaded images
await automation.wait_for_images(".lazy-image")

# Extract data
data = await automation.extract_text(".title")
data = await automation.extract_table("table.data")
data = await automation.extract_json(".json-data")
data = await automation.extract_structured({
    "title": "h1.title",
    "items": ["ul.items li.item"]
})

# Extract all links
links = await automation.extract_links()

# Extract all images
images = await automation.extract_images()

# Network interception
await automation.intercept_requests(lambda req: print(req.url))
await automation.wait_for_request("**/api/data**")

# Get cookies
cookies = await automation.get_cookies()

# Set cookies
await automation.set_cookie("session", "abc123", domain="example.com")

# Get localStorage
storage = await automation.get_local_storage()

# Set localStorage
await automation.set_local_storage("theme", "dark")

# Get sessionStorage
session = await automation.get_session_storage()

# Handle alerts
automation.on_dialog(lambda dialog: dialog.accept("answer"))

# Download handling
automation.on_download(lambda path: print(f"Downloaded: {path}"))

# Close browser
await automation.close()
```

## Navigation

### Basic Navigation
```python
# Navigate to URL
await automation.navigate("https://example.com")

# Navigate and wait for load
await automation.navigate("https://example.com", wait_until="load")

# Navigate and wait for DOM
await automation.navigate("https://example.com", wait_until="domcontentloaded")

# Navigate and wait for network idle
await automation.navigate("https://example.com", wait_until="networkidle")

# Navigate with timeout
await automation.navigate("https://example.com", timeout=60000)
```

### Navigation with Retry
```python
# Retry navigation on failure
await automation.navigate_with_retry(
    "https://unreliable-site.com",
    retries=3,
    delay=2000
)
```

## Waiting

### Wait for Elements
```python
# Wait for element to be visible
await automation.wait_for_element("#content", state="visible")

# Wait for element to be attached
await automation.wait_for_element(".dynamic", state="attached")

# Wait for element to be hidden
await automation.wait_for_element(".loading", state="hidden")

# Wait for element to be detached
await automation.wait_for_element(".old", state="detached")
```

### Wait for Text
```python
# Wait for text to appear
await automation.wait_for_text(".status", "Ready")

# Wait for text to contain
await automation.wait_for_text_contains(".message", "Hello")

# Wait for text to match regex
await automation.wait_for_text_match(".id", r"ID: \d+")
```

### Wait for URL
```python
# Wait for URL to match
await automation.wait_for_url("**/dashboard/**")

# Wait for URL to contain
await automation.wait_for_url_contains("/api/")

# Wait for URL to match regex
await automation.wait_for_url_match(r"https?://.*\.example\.com/.*")
```

### Custom Wait
```python
# Wait for custom condition
await automation.wait_for_condition(
    lambda: automation.page.evaluate("document.querySelector('.ready') !== null")
)
```

## Dynamic Content

### Infinite Scroll
```python
# Infinite scroll on selector
await automation.infinite_scroll(".posts", max_scrolls=10, delay=1000)

# Infinite scroll until no more content
await automation.infinite_scroll(".feed", until_empty=True)

# Custom scroll behavior
await automation.infinite_scroll(
    ".items",
    scroll_action=lambda: automation.page.evaluate("window.scrollBy(0, 500)")
)
```

### Lazy Loading
```python
# Wait for lazy images
await automation.wait_for_images(".lazy", timeout=30000)

# Wait for lazy content
await automation.wait_for_content(".lazy-content")
```

### SPAs (Single Page Apps)
```python
# Wait for route change
await automation.wait_for_route("/dashboard")

# Wait for SPA navigation
await automation.wait_for_spa_navigation()
```

### Polling
```python
# Poll until condition
await automation.poll_until(
    lambda: automation.page.evaluate("document.querySelectorAll('.item').length > 10"),
    timeout=30000,
    interval=1000
)
```

## Data Extraction

### Text Extraction
```python
# Extract text from selector
text = await automation.extract_text("h1.title")

# Extract text from all matches
texts = await automation.extract_all_text(".items li")

# Extract inner HTML
html = await automation.extract_html(".content")

# Extract outer HTML
outer_html = await automation.extract_outer_html(".item")
```

### Table Extraction
```python
# Extract table as list of dicts
data = await automation.extract_table("table.data")
# Result: [{"col1": "val1", "col2": "val2"}, ...]

# Extract with headers
data = await automation.extract_table("table.data", headers=True)
```

### JSON Extraction
```python
# Extract JSON from element
data = await automation.extract_json("#data")

# Extract from script tag
data = await automation.extract_json("script[type='application/json']")
```

### Structured Extraction
```python
# Extract structured data
data = await automation.extract_structured({
    "title": "h1.title",
    "description": ".desc",
    "price": ".price::text",
    "items": ["ul.products li"],
    "metadata": {
        "author": ".author",
        "date": ".date"
    }
})
```

### Links & Images
```python
# Extract all links
links = await automation.extract_links()
# Result: [{"text": "Link Text", "href": "https://..."}]

# Extract links from container
links = await automation.extract_links(".nav a")

# Extract all images
images = await automation.extract_images()
# Result: [{"src": "url", "alt": "alt text"}]

# Extract images from container
images = await automation.extract_images(".gallery img")
```

## Network

### Request Interception
```python
# Intercept all requests
def log_request(req):
    print(f"{req.method} {req.url}")

await automation.intercept_requests(log_request)

# Intercept specific pattern
await automation.intercept_requests(
    lambda req: print(req.url),
    url_pattern="**/api/**"
)
```

### Wait for Request
```python
# Wait for specific request
request = await automation.wait_for_request("**/api/data**")

# Get request data
print(request.url)
print(request.post_data)
print(request.headers)
```

### Mock Responses
```python
# Mock API response
await automation.mock_response(
    "**/api/user",
    status=200,
    body={"name": "John", "email": "john@example.com"}
)
```

### Block Requests
```python
# Block requests
await automation.block_requests("**/analytics/**")
await automation.block_requests("**/ads/**")
```

## Storage

### Cookies
```python
# Get all cookies
cookies = await automation.get_cookies()

# Get cookie by name
session = await automation.get_cookie("session")

# Set cookie
await automation.set_cookie("theme", "dark", path="/", domain="example.com")

# Delete cookie
await automation.delete_cookie("session")

# Delete all cookies
await automation.clear_cookies()
```

### LocalStorage
```python
# Get all localStorage
storage = await automation.get_local_storage()

# Get localStorage item
token = await automation.get_local_storage("token")

# Set localStorage item
await automation.set_local_storage("theme", "dark")

# Remove localStorage item
await automation.remove_local_storage("theme")

# Clear localStorage
await automation.clear_local_storage()
```

### SessionStorage
```python
# Same API as localStorage
session = await automation.get_session_storage()
await automation.set_session_storage("key", "value")
```

## HTTP API

```
POST /api/navigate
GET  /api/wait/element
GET  /api/wait/text
GET  /api/wait/url
POST /api/extract/text
POST /api/extract/table
POST /api/extract/json
POST /api/extract/structured
GET  /api/extract/links
GET  /api/extract/images
GET  /api/cookies
POST /api/cookies
DELETE /api/cookies
GET  /api/storage/local
POST /api/storage/local
GET  /api/storage/session
POST /api/storage/session
```

## Configuration

```json
{
  "port": 3002,
  "headless": true,
  "viewport": {
    "width": 1920,
    "height": 1080
  },
  "timeout": 30000,
  "stealth": true,
  "blockAds": true
}
```

## Requirements

- Python 3.8+
- playwright
- aiohttp

## Installation

```bash
cd skills/browser-automation
pip install -r requirements.txt
playwright install chromium
```

## License

MIT
