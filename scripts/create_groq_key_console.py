"""
Create Groq API Key using console API
"""

import requests
import json
from pathlib import Path

# Session cookies from browser
cookies = {
    "stytch_session": "DzkYKnJAEiwYvjqX0QaFgFws8JRHSVgAaS6TQREIRhUk",
}

# Project ID
project_id = "project_01kj2tjbn5f3taw0ma3rqyhgca"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Origin": "https://console.groq.com",
    "Referer": "https://console.groq.com/"
}

print("=" * 60)
print("Creating Groq API Key via Console API")
print("=" * 60)

# Try console API endpoints
endpoints = [
    f"https://console.groq.com/api/keys?projectId={project_id}",
    f"https://console.groq.com/api/projects/{project_id}/keys",
    "https://console.groq.com/api/keys",
]

for endpoint in endpoints:
    print(f"\n[*] Trying GET: {endpoint}")
    resp = requests.get(endpoint, cookies=cookies, headers=headers)
    print(f"    Status: {resp.status_code}")
    if resp.status_code not in [404, 401]:
        print(f"    Response: {resp.text[:500]}")
    
    print(f"    Trying POST...")
    resp = requests.post(endpoint, cookies=cookies, headers=headers, json={"name": "Test Key"})
    print(f"    Status: {resp.status_code}")
    if resp.status_code not in [404, 401]:
        print(f"    Response: {resp.text[:500]}")

# Try with the actual API that the console uses
print("\n[*] Trying fetch from console page...")
resp = requests.get("https://console.groq.com/keys", cookies=cookies, headers=headers)
print(f"Status: {resp.status_code}")

# Look for API routes in the page
if 'apiKeys' in resp.text or 'api-keys' in resp.text:
    print("[*] Found mentions of API keys in page")
