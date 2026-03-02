---
name: custom-reddit
description: Browse, search, and post to Reddit using Playwright browser automation. Read-only works without auth; posting requires credentials.
metadata: {"clawdbot":{"emoji":"📱","requires":{"bins":["python","playwright"]}}}
---

# Custom Reddit (Browser-Based)

Browse, search, and post to Reddit using Playwright browser automation.

**Advantages over API-based reddit skill:**
- Visual browser automation - handles CAPTCHAs and complex interactions
- No API rate limits
- Works with Reddit's dynamic UI
- Can handle OAuth flows visually if needed

## Setup

### For Read-Only (No Setup Required)
Everything works out of the box for reading posts and searching.

### For Posting
Set environment variables:
```bash
export REDDIT_USERNAME="your_username"
export REDDIT_PASSWORD="your_password"
```

Or on Windows:
```powershell
$env:REDDIT_USERNAME="your_username"
$env:REDDIT_PASSWORD="your_password"
```

### Install Playwright (if not already)
```bash
pip install playwright
playwright install chromium
```

## Get Posts (No Auth Required)

```bash
# Hot posts from a subreddit
python {baseDir}/scripts/reddit_browser.py posts wallstreetbets

# New posts
python {baseDir}/scripts/reddit_browser.py posts wallstreetbets --sort new

# Top posts
python {baseDir}/scripts/reddit_browser.py posts wallstreetbets --sort top

# Limit results
python {baseDir}/scripts/reddit_browser.py posts wallstreetbets --limit 5
```

## Search Reddit (No Auth Required)

```bash
# Search all of Reddit
python {baseDir}/scripts/reddit_browser.py search "YOLO stocks"

# Search within a subreddit
python {baseDir}/scripts/reddit_browser.py search "YOLO stocks" --subreddit wallstreetbets

# Limit results
python {baseDir}/scripts/reddit_browser.py search "bitcoin" --limit 5
```

## Submit a Post (Requires Auth)

```bash
# Text post
python {baseDir}/scripts/reddit_browser.py submit yoursubreddit --title "Weekly Discussion" --text "What's on your mind?"

# Link post
python {baseDir}/scripts/reddit_browser.py submit yoursubreddit --title "Great article" --url "https://example.com/article"
```

## Options

### Headless Mode
By default runs headless. To see the browser:
```bash
set HEADLESS=false
python {baseDir}/scripts/reddit_browser.py posts wallstreetbets
```

## Output Format

All commands output JSON:
```json
[
  {
    "id": "abc123",
    "title": "Post Title",
    "score": "1.2k",
    "comments": "45",
    "author": "username",
    "permalink": "https://reddit.com/r/wallstreetbets/comments/abc123/...",
    "url": "https://reddit.com/r/wallstreetbets/comments/abc123"
  }
]
```

## Error Handling

Errors are returned as JSON to stderr:
```json
{"error": "Not logged in - cannot submit post"}
```

## Security Notes

- Credentials are only used for login and stored nowhere
- Browser session is closed after each operation
- No tokens or secrets are persisted
- For production use, consider adding 2FA support

## Troubleshooting

**"No posts found"**: Reddit may be blocking automated requests. Try:
- Run in non-headless mode (`HEADLESS=false`)
- Add delays between requests
- Check if Reddit is accessible in your browser

**Login fails**: 
- Check credentials are correct
- Reddit may require 2FA - not currently supported
- Try logging in manually first

**CAPTCHA**: Browser automation may trigger Reddit CAPTCHAs. Try:
- Running in non-headless mode
- Using a different IP
- Waiting and retrying
