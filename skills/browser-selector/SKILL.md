# Browser Selector Skill

A skill for selecting and interacting with elements on web pages using CSS selectors, XPath, and text matching.

## Features

- **CSS Selector Support** - Click, fill, and interact with elements using CSS selectors
- **XPath Support** - Use XPath expressions for complex element selection
- **Text Matching** - Find elements by their visible text content
- **Form Filling** - Automatically fill input fields, textareas, and select options
- **Scrolling** - Scroll to elements, top, bottom, or by pixel amount
- **Copy/Paste** - Copy text from elements or paste content into fields
- **Screenshots** - Take screenshots of specific elements or full page

## Usage

### Python API

```python
from browser_selector import BrowserSelector

# Initialize selector
selector = BrowserSelector()

# Start browser
await selector.start()

# Navigate to page
await selector.navigate("https://example.com")

# Click by CSS selector
await selector.click("#submit-button")

# Click by text
await selector.click_by_text("Submit")

# Click by XPath
await selector.click_by_xpath("//button[@id='submit']")

# Fill form
await selector.fill({
    "#username": "myuser",
    "#password": "secret123",
    "input[name='email']": "test@example.com"
})

# Fill textarea
await selector.fill_textarea("#description", "Your text here")

# Select option
await selector.select("#country", "US")

# Scroll to element
await selector.scroll_to("#footer")

# Scroll to top
await selector.scroll_to_top()

# Scroll to bottom
await selector.scroll_to_bottom()

# Scroll by pixels
await selector.scroll_by(0, 500)

# Copy text from element
text = await selector.copy_text(".content")

# Copy text from multiple elements
texts = await selector.copy_all_text(".items li")

# Paste into field
await selector.paste("#code", "copied-text")

# Take element screenshot
await selector.screenshot_element(".hero", "element.png")

# Take full page screenshot
await selector.screenshot("fullpage.png", full_page=True)

# Hover over element
await selector.hover("#menu-item")

# Double click
await selector.double_click(".item")

# Right click (context menu)
await selector.right_click("#element")

# Wait for element
await selector.wait_for("#dynamic-content")

# Check if element exists
exists = await selector.exists("#button")

# Get element attributes
href = await selector.get_attribute("a", "href")
src = await selector.get_attribute("img", "src")

# Set element attribute
await selector.set_attribute("img#logo", "src", "new-logo.png")

# Take snapshot of page structure
snapshot = await selector.snapshot()

# Close browser
await selector.close()
```

## Selector Types

### CSS Selector
```python
await selector.click("#button")
await selector.click(".classname")
await selector.click("tagname")
await selector.click("div.container input[type='text']")
```

### XPath Selector
```python
await selector.click_by_xpath("//button[@id='submit']")
await selector.click_by_xpath("//div[@class='item' and position()=1]")
await selector.click_by_xpath("//ul/li")
```

### Text Selector
```python
# Click element containing text
await selector.click_by_text("Submit")

# Click link containing text
await selector.click_link("Click here")

# Click button containing text
await selector.click_button("Submit Form")

# Find elements containing text
elements = await selector.find_by_text("Welcome")
```

## Form Operations

### Fill Various Input Types
```python
# Text input
await selector.fill("#name", "John Doe")

# Email input
await selector.fill("#email", "john@example.com")

# Password input
await selector.fill("#password", "secret123")

# Number input
await selector.fill("#age", "25")

# Checkbox
await selector.check("#terms")
await selector.uncheck("#newsletter")

# Radio button
await selector.check("input[name='gender'][value='male']")

# Select dropdown
await selector.select("#country", "US")
await selector.select("#country", "United States")  # by text

# Multi-select
await selector.select_multiple("#colors", ["red", "blue"])

# Textarea
await selector.fill_textarea("#bio", "My biography")
```

## Advanced Operations

### Element State Checks
```python
# Check if visible
is_visible = await selector.is_visible("#button")

# Check if enabled
is_enabled = await selector.is_enabled("#submit")

# Check if checked
is_checked = await selector.is_checked("#agree")

# Check if element exists
exists = await selector.exists("#modal")
```

### JavaScript Execution
```python
# Execute custom JavaScript
result = await selector.evaluate("document.title")

# Execute with arguments
result = await selector.evaluate(
    "(element) => element.textContent",
    "#content"
)
```

## HTTP API

The skill also exposes an HTTP API:

```
POST /api/click
POST /api/click-by-text
POST /api/click-by-xpath
POST /api/fill
POST /api/scroll
POST /api/screenshot
GET  /api/content
POST /api/execute
```

### Example

```bash
# Click element
curl -X POST http://localhost:3001/api/click \
  -H "Content-Type: application/json" \
  -d '{"selector": "#submit-button"}'

# Fill form
curl -X POST http://localhost:3001/api/fill \
  -H "Content-Type: application/json" \
  -d '{"fields": {"#username": "user", "#password": "pass"}}'

# Screenshot
curl -X POST http://localhost:3001/api/screenshot \
  -H "Content-Type: application/json" \
  -d '{"selector": ".main", "filename": "element.png"}'
```

## Configuration

Create `config.json`:

```json
{
  "port": 3001,
  "headless": true,
  "viewport": {
    "width": 1920,
    "height": 1080
  },
  "userAgent": "Mozilla/5.0...",
  "timeout": 30000
}
```

## Requirements

- Python 3.8+
- playwright (pip install playwright)
- playwright install chromium

## Installation

```bash
cd skills/browser-selector
pip install -r requirements.txt
playwright install chromium
```

## License

MIT
