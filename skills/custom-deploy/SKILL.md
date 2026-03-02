---
name: custom-deploy
description: Deploy static sites to GitHub Pages, Vercel, Netlify, and Cloudflare Pages using native APIs. No external CLI dependencies required.
metadata: {"clawdbot":{"emoji":"🚀","requires":{"bins":["node","curl"]}}}
---

# Custom Deploy

Multi-platform deployment tool that uses native APIs to deploy static sites. No external CLI dependencies required.

## When to Use
- Deploying static websites to free hosting platforms
- CI/CD pipelines for automated deployments
- Quick deployments without installing platform-specific CLIs
- Multi-platform deployments from a single tool

---

## Supported Platforms

| Platform | Free Tier | Custom Domain | SSL | Notes |
|----------|-----------|---------------|-----|-------|
| GitHub Pages | ✅ | ✅ | ✅ | Requires GitHub repo |
| Vercel | ✅ | ✅ | ✅ | Best for frontend |
| Netlify | ✅ | ✅ | ✅ | Great features |
| Cloudflare Pages | ✅ | ✅ | ✅ | Fastest CDN |

---

## Quick Start

### 1. Set up Environment Variables

```bash
# GitHub Pages
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"

# Vercel
export VERCEL_TOKEN="xxxxxxxxxxxx"

# Netlify  
export NETLIFY_TOKEN="xxxxxxxxxxxx"

# Cloudflare Pages
export CLOUDFLARE_API_TOKEN="xxxxxxxxxxxx"
export CLOUDFLARE_ACCOUNT_ID="xxxxxxxxxxxx"
```

### 2. Deploy!

```bash
# GitHub Pages
deploy.mjs github-pages ./dist --repo owner/my-app

# Vercel
deploy.mjs vercel ./dist --project my-app --prod

# Netlify
deploy.mjs netlify ./dist --project my-app

# Cloudflare Pages
deploy.mjs cloudflare ./dist --project my-app
```

---

## GitHub Pages Deployment

Deploy static sites to GitHub Pages using the GitHub API.

### Required Arguments
- `github-pages` - Platform
- `<path>` - Directory to deploy
- `--repo` - GitHub repository (format: `owner/repo`)

### Optional Arguments
- `--branch` - Branch to deploy to (default: `gh-pages`)
- `--token` - GitHub token (or use `GITHUB_TOKEN` env var)

### Example
```bash
# Basic deployment
deploy.mjs github-pages ./dist --repo myuser/my-website

# Custom branch
deploy.mjs github-pages ./build --repo myuser/my-app --branch main

# With custom token
deploy.mjs github-pages ./public --repo myuser/portfolio --token ghp_xxx
```

### Environment Setup

Create a GitHub Personal Access Token:
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` scope
3. Export: `export GITHUB_TOKEN="your_token_here"`

### Output
```
Deploying to GitHub Pages: owner/repo (branch: gh-pages)
Uploading 42 files...
✅ Deployed to GitHub Pages!
   URL: https://owner.github.io/repo/
```

---

## Vercel Deployment

Deploy to Vercel using their API (not the CLI).

### Required Arguments
- `vercel` - Platform
- `<path>` - Directory to deploy
- `--project` - Vercel project name

### Optional Arguments
- `--token` - Vercel token (or use `VERCEL_TOKEN` env var)
- `--prod` - Deploy to production (default: preview)

### Example
```bash
# Preview deployment
deploy.mjs vercel ./dist --project my-app

# Production deployment
deploy.mjs vercel ./build --project my-app --prod
```

### Environment Setup

Get Vercel API token:
1. Go to Vercel → Settings → Tokens
2. Create new token
3. Export: `export VERCEL_TOKEN="your_token_here"`

### Output
```
Deploying to Vercel: my-app (preview)
Uploading 42 files...
Building deployment...
   Status: READY
✅ Deployed to Vercel!
   URL: https://my-app-abc123.vercel.app
```

---

## Netlify Deployment

Deploy to Netlify using their API.

### Required Arguments
- `netlify` - Platform
- `<path>` - Directory to deploy

### Optional Arguments
- `--token` - Netlify token (or use `NETLIFY_TOKEN` env var)
- `--site-id` - Specific site ID to deploy to

### Example
```bash
# Deploy to new or existing site
deploy.mjs netlify ./dist --project my-site

# Deploy to specific site
deploy.mjs netlify ./build --site-id abc123
```

### Environment Setup

Get Netlify API token:
1. Go to Netlify → User settings → Applications → API tokens
2. Create new token
3. Export: `export NETLIFY_TOKEN="your_token_here"`

### Output
```
Deploying to Netlify...
Uploading 42 files...
✅ Deployed to Netlify!
   URL: https://my-site.netlify.app
```

---

## Cloudflare Pages Deployment

Deploy to Cloudflare Pages using their API.

### Required Arguments
- `cloudflare` - Platform
- `<path>` - Directory to deploy
- `--project` - Cloudflare Pages project name

### Optional Arguments
- `--token` - Cloudflare token (or use `CLOUDFLARE_API_TOKEN` env var)
- `--account-id` - Cloudflare account ID (or use `CLOUDFLARE_ACCOUNT_ID` env var)

### Example
```bash
# Deploy to Cloudflare Pages
deploy.mjs cloudflare ./dist --project my-app

# With explicit credentials
deploy.mjs cloudflare ./build --project my-app --account-id xxx --token xxx
```

### Environment Setup

Get Cloudflare API token:
1. Go to Cloudflare → Profile → API Tokens
2. Create Custom Token with `Pages:Edit` permission
3. Get Account ID from Cloudflare dashboard URL
4. Export both:
```bash
export CLOUDFLARE_API_TOKEN="your_token_here"
export CLOUDFLARE_ACCOUNT_ID="your_account_id"
```

### Output
```
Deploying to Cloudflare Pages: my-app
Creating new Cloudflare Pages project...
Uploading 42 files...
✅ Deployed to Cloudflare Pages!
   Project: my-app
   Check: https://dash.cloudflare.com/xxx/pages
```

---

## Command Reference

### Full Options

| Option | Description |
|--------|-------------|
| `<platform>` | Platform: `github-pages`, `vercel`, `netlify`, `cloudflare` |
| `<path>` | Directory to deploy |
| `--token <token>` | API token (overrides env var) |
| `--repo <owner/repo>` | GitHub repository (GitHub Pages) |
| `--branch <name>` | Branch to deploy (default: gh-pages) |
| `--project <name>` | Project name (Vercel/Netlify/Cloudflare) |
| `--site-id <id>` | Site ID (Netlify) |
| `--account-id <id>` | Account ID (Cloudflare) |
| `--domain <domain>` | Custom domain |
| `--prod` | Production deployment (Vercel) |

---

## Environment Variables

| Variable | Platform | Required |
|----------|----------|----------|
| `GITHUB_TOKEN` | GitHub Pages | Yes |
| `VERCEL_TOKEN` | Vercel | Yes |
| `NETLIFY_TOKEN` | Netlify | Yes |
| `CLOUDFLARE_API_TOKEN` | Cloudflare | Yes |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare | Yes |

---

## Security Notes

1. **Never commit tokens** - Use environment variables
2. **Use minimal scopes** - Only grant necessary permissions
3. **Rotate tokens regularly** - Especially compromised
4. **Revoke unused tokens** - if Clean up old access

---

## Troubleshooting

### GitHub Pages
- **404 error after deploy**: Check repo exists and branch is correct
- **Token error**: Ensure token has `repo` scope

### Vercel
- **Project not found**: Will create automatically if doesn't exist
- **Build fails**: Check project settings in Vercel dashboard

### Netlify
- **Site not found**: Provide `--site-id` or create via dashboard
- **Large files**: Netlify has 50MB soft limit per deploy

### Cloudflare
- **Account ID error**: Find in dashboard URL or settings
- **Permission denied**: Ensure token has `Pages:Edit` permission

---

## Quick Comparison

| Feature | GitHub Pages | Vercel | Netlify | Cloudflare |
|---------|--------------|--------|---------|------------|
| Setup Speed | Fast | Fast | Fast | Fast |
| CDN | GitHub | Vercel | Netlify | Cloudflare |
| CI/CD Built-in | ❌ | ✅ | ✅ | ✅ |
| Forms | ❌ | ✅ | ✅ | ✅ |
| Edge Functions | ❌ | ✅ | ✅ | ✅ |
| Best For | Docs, simple sites | Frontend apps | Full features | Speed |

---

## Automation Example

```bash
#!/bin/bash
# deploy-all.sh - Deploy to multiple platforms

export GITHUB_TOKEN="ghp_xxx"
export VERCEL_TOKEN="xxx"
export NETLIFY_TOKEN="xxx"
export CLOUDFLARE_API_TOKEN="xxx"
export CLOUDFLARE_ACCOUNT_ID="xxx"

# Build first
npm run build

# Deploy to all platforms
deploy.mjs github-pages ./dist --repo myuser/my-app
deploy.mjs vercel ./dist --project my-app --prod
deploy.mjs netlify ./dist --project my-app
deploy.mjs cloudflare ./dist --project my-app
```
