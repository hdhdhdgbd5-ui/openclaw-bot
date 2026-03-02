#!/usr/bin/env python3
"""Check temp mail inbox for verification emails"""

import json
import requests

# Load credentials
with open('../temp_mail_credentials.json', 'r') as f:
    creds = json.load(f)

EMAIL = creds['email']
PASSWORD = creds['password']

# Get token
token_resp = requests.post('https://api.mail.tm/token', 
                          json={"address": EMAIL, "password": PASSWORD})

if token_resp.status_code == 200:
    token = token_resp.json()['token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check messages
    messages_resp = requests.get('https://api.mail.tm/messages', headers=headers)
    
    if messages_resp.status_code == 200:
        messages = messages_resp.json()['hydra:member']
        
        print(f"Found {len(messages)} messages for {EMAIL}")
        
        for msg in messages:
            print(f"\nFrom: {msg['from']['address']}")
            print(f"Subject: {msg['subject']}")
            print(f"Date: {msg['createdAt']}")
            
            # Get full message
            msg_detail = requests.get(f"https://api.mail.tm/messages/{msg['id']}", headers=headers)
            if msg_detail.status_code == 200:
                content = msg_detail.json()
                # Look for verification links
                import re
                links = re.findall(r'https?://[^\s<>"]+', content.get('text', '') + content.get('html', ''))
                if links:
                    print(f"Links found: {links}")
    else:
        print(f"Error: {messages_resp.text}")
else:
    print(f"Failed to get token: {token_resp.text}")
