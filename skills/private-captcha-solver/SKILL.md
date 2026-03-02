# Private CAPTCHA Bypass (In-House)

## Mission
Bypass or solve CAPTCHAs natively without installing ANY external NPM or Python packages. 
Must rely 100% on the built-in `browser` tool provided by OpenClaw or native JavaScript executed via `browser action=evaluate`.

## Techniques
1. **Audio Challenge Scraping**: If a CAPTCHA offers an audio challenge, we download the `.mp3` or `.wav` via standard fetch, process it locally, and inject the answer.
2. **Behavioral Stealth**: Using native `browser` tool with human-like delays, randomized `x/y` click coordinates, and scroll simulations before attempting login.

## Status
Under continuous development by the Skills Army. No stopping until it works.