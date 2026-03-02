#!/usr/bin/env node

/**
 * Custom URL Extractor - Extract content from URLs
 * 
 * This script extracts readable content from URLs.
 * Uses a simple HTML parser to get the main content.
 */

function usage() {
  console.error(`Usage: extract.mjs "url1" ["url2" ...]`);
  console.error(`  Extracts readable content from web pages`);
  process.exit(2);
}

const args = process.argv.slice(2);
if (args.length === 0 || args[0] === "-h" || args[0] === "--help") usage();

const urls = args.filter(a => !a.startsWith("-"));

if (urls.length === 0) {
  console.error("No URLs provided");
  usage();
}

/**
 * Extract readable text from HTML
 */
function extractText(html) {
  // Remove scripts, styles, nav, header, footer
  let text = html
    .replace(/<script[\s\S]*?<\/script>/gi, "")
    .replace(/<style[\s\S]*?<\/style>/gi, "")
    .replace(/<nav[\s\S]*?<\/nav>/gi, "")
    .replace(/<header[\s\S]*?<\/header>/gi, "")
    .replace(/<footer[\s\S]*?<\/footer>/gi, "")
    .replace(/<aside[\s\S]*?<\/aside>/gi, "")
    .replace(/<!--[\s\S]*?-->/g, "")
    .replace(/<noscript[\s\S]*?<\/noscript>/gi, "")
    .replace(/<iframe[\s\S]*?<\/iframe>/gi, "");
  
  // Try to get article/main content
  const articleMatch = text.match(/<article[\s\S]*?<\/article>/i);
  const mainMatch = text.match(/<main[\s\S]*?<\/main>/i);
  
  let content = "";
  if (articleMatch) {
    content = articleMatch[0];
  } else if (mainMatch) {
    content = mainMatch[0];
  } else {
    // Get body content
    const bodyMatch = text.match(/<body[\s\S]*?<\/body>/i);
    content = bodyMatch ? bodyMatch[0] : text;
  }
  
  // Convert HTML to plain text
  text = content
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/<\/p>/gi, "\n\n")
    .replace(/<\/div>/gi, "\n")
    .replace(/<\/h[1-6]>/gi, "\n\n")
    .replace(/<\/li>/gi, "\n")
    .replace(/<[^>]+>/g, "")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\n{3,}/g, "\n\n");
  
  return text.trim();
}

/**
 * Fetch and extract content from a URL
 */
async function fetchUrl(url) {
  console.error(`Fetching: ${url}`);
  
  const resp = await fetch(url, {
    headers: {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml",
      "Accept-Language": "en-US,en;q=0.9",
    },
  });
  
  if (!resp.ok) {
    throw new Error(`HTTP ${resp.status}: ${resp.statusText}`);
  }
  
  const html = await resp.text();
  const text = extractText(html);
  
  return {
    url,
    title: extractTitle(html),
    content: text,
  };
}

/**
 * Extract title from HTML
 */
function extractTitle(html) {
  const titleMatch = html.match(/<title[^>]*>([^<]+)<\/title>/i);
  if (titleMatch) {
    return titleMatch[1].trim();
  }
  const h1Match = html.match(/<h1[^>]*>([^<]+)<\/h1>/i);
  if (h1Match) {
    return h1Match[1].trim();
  }
  return "";
}

// Process all URLs
for (const url of urls) {
  try {
    const result = await fetchUrl(url);
    
    console.log(`# ${result.title || url}`);
    console.log(`Source: ${url}`);
    console.log("\n---\n");
    
    // Limit output to ~5000 chars
    const maxChars = 5000;
    let content = result.content;
    if (content.length > maxChars) {
      content = content.slice(0, maxChars) + "\n\n...[truncated]";
    }
    
    console.log(content);
    console.log("\n---\n");
    
  } catch (error) {
    console.error(`Error fetching ${url}: ${error.message}`);
  }
}
