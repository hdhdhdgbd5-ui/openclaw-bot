# Marketing Credentials Report - Generated 2026-02-23

## Summary
ALL major posting platforms require authentication. No platforms found that allow truly anonymous posting.

## Platform Authentication Requirements

### 1. Reddit
- **Auth Required**: YES
- **Method**: Username/Password login + optional 2FA
- **API**: Requires OAuth (needs account)
- **Credentials Needed**:
  - `REDDIT_USERNAME` 
  - `REDDIT_PASSWORD`
  - (Optional) 2FA code if enabled
- **Script**: `scripts/reddit_bot.py` (requires credentials)
- **Creator**: `scripts/reddit_creator.py` (can create but needs email verification)

### 2. Hacker News
- **Auth Required**: YES
- **Method**: HN Account (no API available for submissions)
- **API**: READ-ONLY only - https://hacker-news.firebaseio.com/v0/
- **Credentials Needed**: HN Username (create at https://news.ycombinator.com)
- **Note**: No public API for submitting stories

### 3. IndieHackers
- **Auth Required**: YES  
- **Method**: OAuth or account login
- **Credentials Needed**: 
  - IndieHackers account (free to create)
- **Post Types**: Show & Tell, Products

### 4. Twitter/X
- **Auth Required**: YES
- **Method**: Twitter API v2 (needs developer account)
- **Credentials Needed**:
  - Twitter Developer Account (requires application)
  - API Key + API Secret
  - Access Token + Access Token Secret
  - OR OAuth 2.0 credentials
- **Note**: Free tier has limited posts/month

### 5. Dev.to
- **Auth Required**: YES
- **Method**: API Key (header)
- **Credentials Needed**: `DEVTO_API_KEY`
- **Script**: `scripts/devto_poster.py` (tested - returns 401 without key)
- **How to get**: https://dev.to/settings/extensions

### 6. Product Hunt
- **Auth Required**: YES
- **Method**: OAuth 2.0
- **Credentials Needed**:
  - Product Hunt Developer App
  - Client ID + Client Secret
- **Note**: Submitting products requires maker account

## Products Ready for Marketing

### Deployed (4):
1. **RentVault** - https://hdhdhdgbd5-ui.github.io/RentVault
2. **StreakVault** - https://hdhdhdgbd5-ui.github.io/StreakVault
3. **FocusMaster** - https://hdhdhdgbd5-ui.github.io/FocusMaster
4. **BudgetVault** - https://hdhdhdgbd5-ui.github.io/BudgetVault

### Pending Deployment:
- ContractGenius, ContentGenius, InsightGenius, CareerGenius
- StoreGenius, SaaSGenius, VideoGenius, CryptoTradeGenius

## Ready-Made Reddit Posts (from POST_TO_REDDIT_NOW.md)

### r/personalfinance - ContractGenius
**Title:** I built a free tool that reads contracts and tells you what's sketchy - because I got burned by a gym membership
**Link:** https://hdhdhdgbd5-ui.github.io/ContractGenius

### r/marketing - ContentGenius  
**Title:** I got tired of staring at blank docs, so I built an AI that actually understands your brand voice
**Link:** https://hdhdhdgbd5-ui.github.io/ContentGenius

### r/entrepreneur - StoreGenius
**Title:** I built a dropshipping store generator after wasting $2K on "gurus" - here's what I learned
**Link:** https://hdhdhdgbd5-ui.github.io/StoreGenius

### r/webdev - SaaSGenius
**Title:** After rebuilding the same auth system 5 times, I open-sourced my SaaS boilerplate
**Link:** https://hdhdhdgbd5-ui.github.io/SaaSGenius

### r/cryptocurrency - CryptoTradeGenius
**Title:** I reverse-engineered whale alerts that platforms charge $200/month for - made it free
**Link:** https://hdhdhdgbd5-ui.github.io/CryptoTradeGenius

### r/youtubers - VideoGenius
**Title:** My CTR jumped from 2% to 5.7% after using this script formula - here's the tool I built
**Link:** https://hdhdhdgbd5-ui.github.io/VideoGenius

## What Credentials Are Needed From Tez

To enable automatic marketing, Tez needs to provide:

1. **Reddit Account** (easiest start)
   - Username: _______________
   - Password: _______________

2. **OR** Create new Reddit account using:
   - Use `scripts/reddit_creator.py` + `scripts/temp_mail_auto.py`
   - Need: Temp email automation working

3. **Dev.to API Key** (optional)
   - Get from: https://dev.to/settings/extensions

4. **Twitter Developer Account** (optional, harder)
   - Apply at: https://developer.twitter.com

## Alternative: Automated Account Creation

The system CAN create accounts automatically if:
1. Temp email service works (DrissionPage + browser needed)
2. Phone verification not required

Current Blocker: Browser automation needs Chrome extension OR working headless browser.

## Status: BLOCKED

**Cannot post anywhere without credentials from Tez.**

- Reddit: Needs login credentials
- HackerNews: No write API
- IndieHackers: Needs account
- Twitter: Needs developer API
- Dev.to: Needs API key
- Product Hunt: Needs OAuth

**RECOMMENDED ACTION**: Ask Tez for Reddit credentials (simplest path to start marketing)
