#!/usr/bin/env python3
"""
Browser automation via CDP for API key registration
"""

import requests
import json
import time
import subprocess

CDP_URL = "http://127.0.0.1:18800"
EMAIL = "rainyfay@dollicons.com"

def get_page_info():
    """Get current page info from CDP"""
    try:
        resp = requests.get(f"{CDP_URL}/json")
        return resp.json()
    except Exception as e:
        print(f"Error getting page info: {e}")
        return []

def execute_javascript(page_id, script):
    """Execute JavaScript on the page"""
    try:
        ws_url = f"{CDP_URL}/devtools/page/{page_id}"
        # We'd need websocket client for this
        print(f"Would execute on {page_id}: {script[:50]}...")
    except Exception as e:
        print(f"Error executing JS: {e}")

def main():
    print("Browser Automation via CDP")
    pages = get_page_info()
    for page in pages:
        print(f"  - {page.get('title', 'Unknown')} ({page.get('url', 'Unknown')})")
    
    # HuggingFace registration steps
    steps = [
        "Navigate to https://huggingface.co/join",
        f"Fill email: {EMAIL}",
        "Fill password",
        "Click Next",
        "Check mail for verification",
        "Get API token from settings"
    ]
    
    print("\nRegistration Steps for HuggingFace:")
    for i, step in enumerate(steps, 1):
        print(f"  {i}. {step}")

if __name__ == "__main__":
    main()
