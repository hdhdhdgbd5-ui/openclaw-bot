#!/usr/bin/env python3
"""
Mail.tm API - Get Temporary Email Programmatically
No browser needed - pure API calls
"""

import requests
import json
import random
import string

def create_temp_email():
    """Create a temporary email using mail.tm API"""
    
    # Get available domains
    domains_resp = requests.get('https://api.mail.tm/domains')
    domains = domains_resp.json()['hydra:member']
    domain = domains[0]['domain']  # Use first available domain
    
    # Generate random username
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    email = f"{username}@{domain}"
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    
    # Create account
    account_data = {
        "address": email,
        "password": password
    }
    
    create_resp = requests.post('https://api.mail.tm/accounts', json=account_data)
    
    if create_resp.status_code == 201:
        print(f"SUCCESS: Created temp email")
        print(f"Email: {email}")
        print(f"Password: {password}")
        
        # Save credentials
        creds = {
            "email": email,
            "password": password,
            "domain": domain
        }
        
        with open('temp_mail_credentials.json', 'w') as f:
            json.dump(creds, f, indent=2)
        
        # Get auth token
        token_resp = requests.post('https://api.mail.tm/token', json=account_data)
        if token_resp.status_code == 200:
            token = token_resp.json()['token']
            creds['token'] = token
            
            with open('temp_mail_credentials.json', 'w') as f:
                json.dump(creds, f, indent=2)
            
            print(f"Token acquired - ready to check inbox")
        
        return email, password
    else:
        print(f"Failed to create account: {create_resp.text}")
        return None, None

def check_inbox(email, password):
    """Check inbox for messages"""
    
    # Get token
    token_resp = requests.post('https://api.mail.tm/token', 
                              json={"address": email, "password": password})
    
    if token_resp.status_code != 200:
        print("Failed to get token")
        return []
    
    token = token_resp.json()['token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get messages
    messages_resp = requests.get('https://api.mail.tm/messages', headers=headers)
    
    if messages_resp.status_code == 200:
        messages = messages_resp.json()['hydra:member']
        print(f"Found {len(messages)} messages")
        return messages
    else:
        print(f"Failed to get messages: {messages_resp.text}")
        return []

def get_message(email, password, message_id):
    """Get full message content"""
    
    token_resp = requests.post('https://api.mail.tm/token',
                              json={"address": email, "password": password})
    token = token_resp.json()['token']
    headers = {"Authorization": f"Bearer {token}"}
    
    msg_resp = requests.get(f'https://api.mail.tm/messages/{message_id}', headers=headers)
    
    if msg_resp.status_code == 200:
        return msg_resp.json()
    return None

if __name__ == "__main__":
    print("=" * 50)
    print("TEMP MAIL API - Creating disposable email")
    print("=" * 50)
    
    email, password = create_temp_email()
    
    if email:
        print(f"\nEmail ready: {email}")
        print(f"Credentials saved to: temp_mail_credentials.json")
        print(f"\nTo check inbox, run:")
        print(f"  python mailtm_api.py check")
