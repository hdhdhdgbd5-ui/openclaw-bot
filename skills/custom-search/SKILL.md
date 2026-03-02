---
name: custom-search
description: Free web search using DuckDuckGo HTML. No API keys required - uses direct HTML scraping for search and content extraction.
homepage: https://duckduckgo.com
metadata: {"clawdbot":{"emoji":"🔍","requires":{"bins":["node"]},"noApiKey":true}}
---

# Custom Search

Free web search skill using DuckDuckGo HTML scraping. No API keys required!

## Search

```bash
node {baseDir}/scripts/search.mjs "query"
node {baseDir}/scripts/search.mjs "query" -n 10
```

## Options

- `-n <count>`: Number of results (default: 5, max: 10)
- `--safe`: Enable safe search (default: on)
- `--no-safe`: Disable safe search

## Extract content from URL

```bash
node {baseDir}/scripts/extract.mjs "https://example.com/article"
node {baseDir}/scripts/extract.mjs "https://url1" "https://url2"
```

## Features

- **No API key needed** - Uses DuckDuckGo HTML scraping
- **Free unlimited searches** - No rate limits
- **Content extraction** - Built-in HTML to text converter
- **Safe search** - Enabled by default

## How it works

1. **Search**: Scrapes DuckDuckGo's HTML results page
2. **Extract**: Parses HTML to extract readable text content

## Notes

- Results are parsed from DuckDuckGo's HTML interface
- Safe search is ON by default (can be disabled with --no-safe)
- Max 10 results per search
- Content extraction works best with article/main content
