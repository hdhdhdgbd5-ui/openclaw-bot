"""
Create Groq API Key using direct API call
"""

import requests
import json
from pathlib import Path

# Session cookies from browser - FRESH
cookies = {
    "stytch_session": "DzkYKnJAEiwYvjqX0QaFgFws8JRHSVgAaS6TQREIRhUk",
    "stytch_session_jwt": "eyJhbGciOiJSUzI1NiIsImtpZCI6Imp3ay1saXZlLTEyM2JmMDM1LTA4OGEtNDU4Zi1iZmQ1LWY3Yjk5Y2I5MWQyMCIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsicHJvamVjdC1saXZlLTVjYjM4ODBlLTc3NGUtNDNlYS1hYjkwLWY0ZDMyMzRlMzZkZCJdLCJleHAiOjE3NzE4NDc1MjEsImh0dHBzOi8vZ3JvcS5jb20vb3JnYW5pemF0aW9uIjp7ImlkIjoib3JnXzAxa2oydGpiNXZmM25yeTlqaGJ2enIxM2p3In0sImh0dHBzOi8vc3R5dGNoLmNvbS9vcmdhbml6YXRpb24iOnsib3JnYW5pemF0aW9uX2lkIjoib3JnYW5pemF0aW9uLWxpdmUtOWM1MGIxYjMtNWNjNS00OGRmLWI1ZTgtNmJhNDlhY2MyZTUyIiwic2x1ZyI6Im9yZ18wMWtqMnRqYjV2ZjNucnk5amhidnpyMTNqdyJ9LCJodHRwczovL3N0eXRjaC5jb20vc2Vzc2lvbiI6eyJpZCI6Im1lbWJlci1zZXNzaW9uLWxpdmUtMDFlNmUwMzUtNGQ0Ni00NTI3LTkwMDAtZDliMTBkYTAwZGQzIiwic3RhcnRlZF9hdCI6IjIwMjYtMDItMjJUMTQ6MDM6MDJaIiwibGFzdF9hY2Nlc3NlZF9hdCI6IjIwMjYtMDItMjNUMTE6NDc6MDFaIiwiZXhwaXJlc19hdCI6IjIwMjYtMDMtMjRUMTQ6MDM6MDNaIiwiYXR0cmlidXRlcyI6eyJ1c2VyX2FnZW50IjoiIiwiaXBfYWRkcmVzcyI6IiJ9LCJhdXRoZW50aWNhdGlvbl9mYWN0b3JzIjpbeyJ0eXBlIjoibWFnaWNfbGluayIsImRlbGl2ZXJ5X21ldGhvZCI6ImVtYWlsIiwibGFzdF9hdXRoZW50aWNhdGVkX2F0IjoiMjAyNi0wMi0yMlQxNDowMzowMVoiLCJlbWFpbF9mYWN0b3IiOnsiZW1haWxfaWQiOiJtZW1iZXItZW1haWwtbGl2ZS04MGUyZjIzNy02MDQwLTQxNDEtOTUyZi0xNzUwMzY0MWRjMGQiLCJlbWFpbF9hZGRyZXNzIjoiZTE3MHU2a2VjYmpAcGlubXgubmV0In19XSwicm9sZXMiOlsic3R5dGNoX21lbWJlciIsInN0eXRjaF9hZG1pbiJdfSwiaWF0IjoxNzcxODQ3MjIxLCJpc3MiOiJodHRwczovL2FwaS5zdHl0Y2hiMmIuZ3JvcS5jb20iLCJuYmYiOjE3NzE4NDcyMjEsInN1YiI6Im1lbWJlci1saXZlLTdjOGVkZjZiLTUwNWYtNGRlNi1hYjNlLTcwYWJlYmYyNjUyMiJ9.OPTemir3u9J2bdxafIXOQyCU4HbarKnEX6koXiIIRPQcks42ZHquzhBTGQB5LQxQKsRVVSP2iNkm-p8wihUPShM7KMEp_sjMBwFl1zvBl3tVFkkV_85qO4Bq27kCIfFf6jjEa2b_xINFBuPd3J4bRhCz_rkPbuKklUG12j2qfNEOOziK-UiuNNrVi8kc_2wQvnJUhcWZ5QQLg0lWZfUKsA8SNc_7C4m2DzCQpnlWYNyk5VmrUNKEsqo0R4eMKdcYw8EC1CwTkGfEnKujHSFHKY79uAbnY8ITsAMh_VqQFJUnokAQw93t-AxfQoLmsmfXfcj9fp7OGjVHXtGiBb0nFg"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json"
}

# Organization and Project IDs from user-preferences
org_id = "org_01kj2tjb5vf3nry9jhbvzr13jw"
project_id = "project_01kj2tjbn5f3taw0ma3rqyhgca"

# Try to create API key
print("=" * 60)
print("Creating Groq API Key via API")
print("=" * 60)

# First, try listing existing keys
print("\n[*] Listing existing API keys...")
resp = requests.get(
    f"https://api.groq.com/v1/projects/{project_id}/api-keys",
    cookies=cookies,
    headers=headers
)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text[:1000]}")

# Try to create a new key
print("\n[*] Creating new API key...")
create_data = {
    "name": "OpenClaw API Key"
}

resp = requests.post(
    f"https://api.groq.com/v1/projects/{project_id}/api-keys",
    cookies=cookies,
    headers=headers,
    json=create_data
)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text}")

if resp.status_code in [200, 201]:
    try:
        data = resp.json()
        api_key = data.get("secret_key") or data.get("key")
        if api_key:
            print(f"\n[+] SUCCESS! API Key: {api_key[:20]}...")
            
            # Save to file
            secrets_dir = Path.home() / ".openclaw" / "secrets"
            secrets_dir.mkdir(parents=True, exist_ok=True)
            secrets_file = secrets_dir / "groq_api_key.txt"
            secrets_file.write_text(api_key)
            print(f"[+] Saved to {secrets_file}")
        else:
            print(f"[!] Response data: {data}")
    except:
        print(f"[!] Could not parse response: {resp.text}")
else:
    print(f"[-] Failed to create API key")
