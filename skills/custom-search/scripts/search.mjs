#!/usr/bin/env node

/**
 * Custom Web Search - Uses DuckDuckGo HTML (free, no API key required)
 * 
 * This script scrapes DuckDuckGo's HTML results page to get search results
 * without needing any API key.
 */

function usage() {
  console.error(`Usage: search.mjs "query" [-n 5] [--safe]`);
  console.error(`  -n <count>: Number of results (default: 5, max: 10)`);
  console.error(`  --safe: Enable safe search (default: on)`);
  process.exit(2);
}

const args = process.argv.slice(2);
if (args.length === 0 || args[0] === "-h" || args[0] === "--help") usage();

const query = args[0];
let n = 5;
let safeSearch = "on";

for (let i = 1; i < args.length; i++) {
  const a = args[i];
  if (a === "-n") {
    n = Math.max(1, Math.min(10, Number.parseInt(args[i + 1] ?? "5", 10)));
    i++;
    continue;
  }
  if (a === "--safe") {
    safeSearch = "on";
    continue;
  }
  if (a === "--no-safe") {
    safeSearch = "off";
    continue;
  }
  console.error(`Unknown arg: ${a}`);
  usage();
}

const encodedQuery = encodeURIComponent(query);
const ddgUrl = `https://html.duckduckgo.com/html/?q=${encodedQuery}&kl=${safeSearch}`;

console.error(`Searching: ${query}`);
console.error(`URL: ${ddgUrl}`);

const resp = await fetch(ddgUrl, {
  headers: {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html",
  },
});

if (!resp.ok) {
  throw new Error(`DuckDuckGo search failed (${resp.status}): ${resp.statusText}`);
}

const html = await resp.text();

// Parse results from HTML
const results = [];
const resultRegex = /<a rel="nofollow" class="result__a" href="([^"]+)"[^>]*>([\s\S]*?)<\/a>[\s\S]*?<a class="result__snippet"[^>]*>([\s\S]*?)<\/a>/g;

let match;
while ((match = resultRegex.exec(html)) !== null && results.length < n) {
  const url = match[1];
  // DuckDuckGo uses redirect URLs - extract original URL
  let cleanUrl = url;
  if (url.includes("uddg=")) {
    try {
      const urlParams = new URLSearchParams(url.split("?")[1]);
      cleanUrl = decodeURIComponent(urlParams.get("uddg") || url);
    } catch (e) {
      // keep original
    }
  }
  
  const title = match[2].replace(/<[^>]+>/g, "").trim();
  const snippet = match[3].replace(/<[^>]+>/g, "").trim();
  
  if (title && cleanUrl) {
    results.push({ title, url: cleanUrl, snippet });
  }
}

// Fallback: simpler regex if the above doesn't work well
if (results.length === 0) {
  const simpleRegex = /<a[^>]*class="result__a"[^>]*href="(https?:\/\/[^"]+)"[^>]*>([^<]+)<\/a>/g;
  while ((match = simpleRegex.exec(html)) !== null && results.length < n) {
    let url = match[1];
    if (url.includes("uddg=")) {
      try {
        const urlParams = new URLSearchParams(url.split("?")[1]);
        url = decodeURIComponent(urlParams.get("uddg") || url);
      } catch (e) {}
    }
    const title = match[2].replace(/<[^>]+>/g, "").trim();
    if (title && url) {
      results.push({ title, url, snippet: "" });
    }
  }
}

console.log(`## Search Results for: ${query}\n`);

if (results.length === 0) {
  console.log("No results found.");
} else {
  for (const r of results) {
    console.log(`- **${r.title}**`);
    console.log(`  ${r.url}`);
    if (r.snippet) {
      console.log(`  ${r.snippet}`);
    }
    console.log();
  }
}

console.error(`\nFound ${results.length} results.`);
