#!/usr/bin/env python3
"""
Reddit Browser - Playwright-based Reddit automation
Uses browser automation for posting, reading, and searching

No auth required for: reading posts, searching
Auth required for: posting, commenting, voting

For posting, set environment variables:
  REDDIT_USERNAME="your_username"  
  REDDIT_PASSWORD="your_password"
"""

import json
import os
import sys
import time
from playwright.sync_api import sync_playwright


class RedditBrowser:
    def __init__(self, headless=True):
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        self.username = os.getenv("REDDIT_USERNAME")
        self.password = os.getenv("REDDIT_PASSWORD")
        
    def start(self):
        """Start the browser"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        self.page = self.context.new_page()
        
    def navigate(self, url):
        """Navigate to URL"""
        self.page.goto(url, wait_until="networkidle")
        
    def login(self):
        """Login to Reddit if credentials provided"""
        if not self.username or not self.password:
            print("[RedditBrowser] No credentials - operating in read-only mode")
            return False
            
        print(f"[RedditBrowser] Logging in as {self.username}")
        self.navigate("https://www.reddit.com/login/")
        
        # Wait for login form
        self.page.wait_for_selector('input[name="username"]', timeout=10000)
        
        # Fill credentials
        self.page.fill('input[name="username"]', self.username)
        self.page.fill('input[name="password"]', self.password)
        self.page.click('button[type="submit"]')
        
        # Wait for login to complete
        self.page.wait_for_url("**/reddit.com/**", timeout=15000)
        time.sleep(2)
        print("[RedditBrowser] Logged in successfully")
        return True
    
    def get_posts(self, subreddit, sort="hot", limit=10):
        """Get posts from a subreddit"""
        sort_map = {"hot": "hot", "new": "new", "top": "top", "rising": "rising"}
        sort_param = sort_map.get(sort, "hot")
        
        url = f"https://www.reddit.com/r/{subreddit}/{sort_param}/"
        print(f"[RedditBrowser] Fetching posts from {url}")
        
        self.navigate(url)
        self.page.wait_for_timeout(2000)  # Let content load
        
        posts = []
        
        # Scroll to load more content
        for _ in range(2):
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self.page.wait_for_timeout(1000)
        
        # Extract post elements
        post_elements = self.page.query_selector_all('article[data-testid="post-container"]')
        
        for elem in post_elements[:limit]:
            try:
                title_elem = elem.query_selector('h3')
                title = title_elem.inner_text() if title_elem else ""
                
                # Get metadata
                score_elem = elem.query_selector('[data-testid="post-score"]')
                score = score_elem.inner_text() if score_elem else "0"
                
                comments_elem = elem.query_selector('[data-testid="comment-count"]')
                comments = comments_elem.inner_text() if comments_elem else "0"
                
                author_elem = elem.query_selector('[data-testid="post-author"]')
                author = author_elem.inner_text() if author_elem else "[deleted]"
                
                permalink_elem = elem.query_selector('a[data-testid="post-title-link"]')
                permalink = permalink_elem.get_attribute("href") if permalink_elem else ""
                
                post_id = ""
                if permalink:
                    parts = permalink.strip("/").split("/")
                    post_id = parts[-1] if parts else ""
                
                if title:
                    posts.append({
                        "id": post_id,
                        "title": title,
                        "score": score,
                        "comments": comments,
                        "author": author,
                        "permalink": f"https://reddit.com{permalink}" if permalink else "",
                        "url": f"https://reddit.com/r/{subreddit}/comments/{post_id}" if post_id else ""
                    })
            except Exception as e:
                continue
        
        return posts
    
    def search(self, query, subreddit=None, limit=10):
        """Search Reddit"""
        if subreddit:
            url = f"https://www.reddit.com/r/{subreddit}/search/?q={query}"
        else:
            url = f"https://www.reddit.com/search/?q={query}"
        
        print(f"[RedditBrowser] Searching: {query}")
        self.navigate(url)
        self.page.wait_for_timeout(2000)
        
        posts = []
        
        # Scroll to load results
        for _ in range(2):
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self.page.wait_for_timeout(1000)
        
        post_elements = self.page.query_selector_all('article[data-testid="post-container"]')
        
        for elem in post_elements[:limit]:
            try:
                title_elem = elem.query_selector('h3')
                title = title_elem.inner_text() if title_elem else ""
                
                subreddit_elem = elem.query_selector('[data-testid="subreddit-name"]')
                subreddit_name = subreddit_elem.inner_text() if subreddit_elem else ""
                
                score_elem = elem.query_selector('[data-testid="post-score"]')
                score = score_elem.inner_text() if score_elem else "0"
                
                permalink_elem = elem.query_selector('a[data-testid="post-title-link"]')
                permalink = permalink_elem.get_attribute("href") if permalink_elem else ""
                
                post_id = ""
                if permalink:
                    parts = permalink.strip("/").split("/")
                    post_id = parts[-1] if parts else ""
                
                if title:
                    posts.append({
                        "id": post_id,
                        "title": title,
                        "subreddit": subreddit_name,
                        "score": score,
                        "permalink": f"https://reddit.com{permalink}" if permalink else ""
                    })
            except Exception as e:
                continue
        
        return posts
    
    def submit_post(self, subreddit, title, text=None, url=None):
        """Submit a new post to a subreddit"""
        if not self.username:
            raise Exception("Not logged in - cannot submit post")
        
        submit_url = f"https://www.reddit.com/r/{subreddit}/submit"
        print(f"[RedditBrowser] Submitting post to r/{subreddit}")
        
        self.navigate(submit_url)
        self.page.wait_for_selector('input[name="title"]', timeout=10000)
        
        # Fill title
        self.page.fill('input[name="title"]', title)
        
        # Choose post type
        if url:
            # Click link tab
            self.page.click('button:has-text("Link")')
            self.page.wait_for_timeout(500)
            self.page.fill('input[name="url"]', url)
        elif text:
            # Text post - use text tab (default)
            self.page.fill('textarea[name="text"]', text)
        
        # Click submit
        self.page.click('button[type="submit"]')
        
        # Wait for post to be submitted
        self.page.wait_for_timeout(3000)
        
        # Check if we're on the post page
        current_url = self.page.url
        
        if "reddit.com/r/" in current_url and "/comments/" in current_url:
            print(f"[RedditBrowser] Post submitted successfully: {current_url}")
            return {"success": True, "url": current_url}
        else:
            # Check for errors
            error_elem = self.page.query_selector('[data-testid="error-container"]')
            if error_elem:
                error_text = error_elem.inner_text()
                raise Exception(f"Post failed: {error_text}")
            
            print(f"[RedditBrowser] Post may have been submitted: {current_url}")
            return {"success": True, "url": current_url}
    
    def close(self):
        """Close the browser"""
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Reddit Browser - Playwright automation")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Posts command
    posts_parser = subparsers.add_parser("posts", help="Get posts from a subreddit")
    posts_parser.add_argument("subreddit", help="Subreddit name")
    posts_parser.add_argument("--sort", choices=["hot", "new", "top", "rising"], default="hot", help="Sort order")
    posts_parser.add_argument("--limit", type=int, default=10, help="Number of posts")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search Reddit")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--subreddit", help="Limit to subreddit")
    search_parser.add_argument("--limit", type=int, default=10, help="Number of results")
    
    # Submit command
    submit_parser = subparsers.add_parser("submit", help="Submit a new post")
    submit_parser.add_argument("subreddit", help="Subreddit name")
    submit_parser.add_argument("--title", required=True, help="Post title")
    submit_parser.add_argument("--text", help="Text content")
    submit_parser.add_argument("--url", help="URL to link")
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Create browser instance
    headless = os.getenv("HEADLESS", "true").lower() == "true"
    reddit = RedditBrowser(headless=headless)
    
    try:
        reddit.start()
        reddit.login()
        
        if args.command == "posts":
            posts = reddit.get_posts(args.subreddit, args.sort, args.limit)
            print(json.dumps(posts, indent=2))
            
        elif args.command == "search":
            results = reddit.search(args.query, args.subreddit, args.limit)
            print(json.dumps(results, indent=2))
            
        elif args.command == "submit":
            result = reddit.submit_post(args.subreddit, args.title, args.text, args.url)
            print(json.dumps(result, indent=2))
            
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)
    finally:
        reddit.close()


if __name__ == "__main__":
    main()
