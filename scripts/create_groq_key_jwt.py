"""
Create Groq API Key using JWT auth
"""

import requests
import json
from pathlib import Path

# JWT token from browser
jwt_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6Imp3ay1saXZlLTEyM2JmMDM1LTA4OGEtNDU4Zi1iZmQ1LWY3Yjk5Y2I5MWQyMCIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsicHJvamVjdC1saXZlLTVjYjM4ODBlLTc3NGUtNDNlYS1hYjkwLWY0ZDMyMzRlMzZkZCJdLCJleHAiOjE3NzE4NDc1MjEsImh0dHBzOi8vZ3JvcS5jb20vb3JnYW5pemF0aW9uIjp7ImlkIjoib3JnXzAxa2oydGpiNXZmM25yeTlqaGJ2enIxM2p3In0sImh0dHBzOi8vc3R5dGNoLmNvbS9vcmdhbml6YXRpb24iOnsib3JnYW5pemF0aW9uX2lkIjoib3JnYW5pemF0aW9uLWxpdmUtOWM1MGIxYjMtNWNjNS00OGRmLWI1ZTgtNmJhNDlhY2MyZTUyIiwic2x1ZyI6Im9yZ18wMWtqMnRqYjV2ZjNucnk5amhidnpyMTNqdyJ9LCJodHRwczovL3N0eXRjaC5jb20vc2Vzc2lvbiI6eyJpZCI6Im1lbWJlci1zZXNzaW9uLWxpdmUtMDFlNmUwMzUtNGQ0Ni00NTI3LTkwMDAtZDliMTBkYTAwZGQzIiwic3RhcnRlZF9hdCI6IjIwMjYtMDItMjJUMTQ6MDM6MDJaIiwibGFzdF9hY2Nlc3NlZF9hdCI6IjIwMjYtMDItMjNUMTE6NDc6MDFaIiwiZXhwaXJlc19hdCI6IjIwMjYtMDMtMjRUMTQ6MDM6MDNaIiwiYXR0cmlidXRlcyI6eyJ1c2VyX2FnZW50IjoiIiwiaXBfYWRkcmVzcyI6IiJ9LCJhdXRoZW50aWNhdGlvbl9mYWN0b3JzIjpbeyJ0eXBlIjoibWFnaWNfbGluayIsImRlbGl2ZXJ5X21ldGhvZCI6ImVtYWlsIiwibGFzdF9hdXRoZW50aWNhdGVkX2F0IjoiMjAyNi0wMi0yMlQxNDowMzowMVoiLCJlbWFpbF9mYWN0b3IiOnsiZW1haWxfaWQiOiJtZW1iZXItZW1haWwtbGl2ZS04MGUyZjIzNy02MDQwLTQxNDEtOTUyZi0xNzUwMzY0MWRjMGQiLCJlbWFpbF9hZGRyZXNzIjoiZTE3MHU2a2VjYmpAcGlubXgubmV0In19XSwicm9sZXMiOlsic3R5dGNoX21lbWJlciIsInN0eXRjaF9hZG1pbiJdfSwiaWF0IjoxNzcxODQ3MjIxLCJpc3MiOiJodHRwczovL2FwaS5zdHl0Y2hiMmIuZ3JvcS5jb20iLCJuYmYiOjE3NzE4NDcyMjEsInN1YiI6Im1lbWJlci1saXZlLTdjOGVkZjZiLTUwNWYtNGRlNi1hYjNlLTcwYWJlYmYyNjUyMiJ9.OPTemir3u9J2bdxafIXOQyCU4HbarKnEX6koXiIIRPQcks42ZHquzhBTGQB5LQxQKsRVVSP2iNkm-p8wihUPShM7KMEp_sjMBwFl1zvBl3tVFkkV_85qO4Bq27kCIfFf6jjEa2b_xINFBuPd3J4bRhCz_rkPbuKklUG12j2qfNEOOziK-UiuNNrVi8kc_2wQvnJUhcWZ5QQLg0lWZfUKsA8SNc_7C4m2DzCQpnlWYNyk5VmrUNKEsqo0R4eMKdcYw8EC1CwTkGfEnKujHSFHKY79uAbnY8ITsAMh_VqQFJUnokAQw93t-AxfQoLmsmfXfcj9fp7OGjVHXtGiBb0nFg"

# Project ID
project_id = "project_01kj2tjbn5f3taw0ma3rqyhgca"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {jwt_token}"
}

print("=" * 60)
print("Creating Groq API Key via API with JWT")
print("=" * 60)

# Try different API endpoints
endpoints = [
    f"https://api.groq.com/v1/projects/{project_id}/api-keys",
    f"https://api.groq.com/v1/api-keys",
    "https://api.groq.com/v1/keys",
    "https://api.groq.com/v1/projects/{project_id}/keys",
]

for endpoint in endpoints:
    print(f"\n[*] Trying: {endpoint}")
    resp = requests.get(endpoint, headers=headers)
    print(f"    Status: {resp.status_code}")
    if resp.status_code != 404:
        print(f"    Response: {resp.text[:500]}")
    
    # Try POST
    print(f"    Trying POST...")
    resp = requests.post(endpoint, headers=headers, json={"name": "Test Key"})
    print(f"    Status: {resp.status_code}")
    if resp.status_code not in [404, 401]:
        print(f"    Response: {resp.text[:500]}")

print("\n[*] Trying GroqCloud API...")

# Try groqcloud API
resp = requests.get(
    "https://api.us.groqcloud.com/v1/projects",
    headers=headers
)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text[:500]}")
