# Account Creation Skill

Automated account creation with temp mail, email verification, and account registration on any site.

## Features

- **Temp Mail Integration** - Generate and use temporary email addresses
- **Email Verification** - Automatically receive and parse verification emails
- **Account Registration** - Fill registration forms automatically
- **CAPTCHA Handling** - Built-in CAPTCHA detection and handling
- **Session Management** - Save created accounts for later use
- **Profile Support** - Create multiple account profiles with different data
- **Proxy Support** - Use proxies for account creation

## Supported Temp Mail Services

- **pinmx.net** - Primary (https://pinmx.net)
- **temp-mail.io** - Alternative
- **guerrillamail.com** - Alternative
- **10minutemail.com** - Alternative

## Usage

### Python API

```python
from account_creator import AccountCreator

# Initialize creator
creator = AccountCreator()

# Start browser
await creator.start()

# Generate temp email
email = await creator.generate_email()
print(f"Email: {email}")

# Create account on site
account = await creator.create_account(
    url="https://example.com/register",
    email=email,
    fields={
        "username": "myuser",
        "password": "SecurePass123!",
        "#first_name": "John",
        "#last_name": "Doe"
    },
    submit_selector="#register-button",
    verify_email=True
)

print(f"Account created: {account}")

# Wait for verification
verification = await creator.wait_for_verification(email, timeout=120000)
print(f"Verified: {verification}")

# Save account
await creator.save_account("my-account", account)

# Close browser
await creator.close()
```

### With Profile Data

```python
from account_creator import AccountCreator
from account_creator.profile import ProfileGenerator

# Generate random profile
generator = ProfileGenerator()
profile = generator.generate()
print(f"Username: {profile['username']}")
print(f"Password: {profile['password']}")
print(f"Email: {profile['email']}")

# Use profile for registration
creator = AccountCreator()
await creator.start()

account = await creator.create_account(
    url="https://site.com/register",
    email=profile["email"],
    fields={
        "username": profile["username"],
        "password": profile["password"]
    },
    verify_email=True
)
```

### Manual Email Verification

```python
# If you have your own email
creator = AccountCreator()
await creator.start()

# Go to site and start registration manually
await creator.navigate("https://site.com/register")

# Enter your email
await creator.fill("#email", "your-email@example.com")

# Wait for verification code
code = await creator.wait_for_verification_code(
    email="your-email@example.com",
    mail_service="gmail",  # or custom IMAP
    timeout=120000
)

# Enter code
await creator.fill("#verification-code", code)
```

### Save/Load Sessions

```python
# Save created account
await creator.save_account("account-name", {
    "email": email,
    "username": "user",
    "password": "pass",
    "url": "https://site.com"
})

# Load account
account = await creator.load_account("account-name")
await creator.navigate(account["url"])

# Auto-fill credentials
await creator.fill("#username", account["username"])
await creator.fill("#password", account["password"])
```

## Email Services

### Built-in Temp Mail

```python
# Auto-detect service
email = await creator.generate_email()  # Uses default service

# Specify service
email = await creator.generate_email(service="pinmx")
email = await creator.generate_email(service="temp-mail")
email = await creator.generate_email(service="guerrilla")
```

### IMAP Email (Gmail, Outlook, etc.)

```python
# Wait for verification from real email
code = await creator.wait_for_verification_code(
    email="your@gmail.com",
    mail_service="gmail",
    imap={
        "host": "imap.gmail.com",
        "port": 993,
        "username": "your@gmail.com",
        "password": "app-password"
    }
)
```

## Field Filling

### Auto Field Detection

```python
# Fields are auto-detected by name, id, placeholder
fields = {
    "username": "myuser",      # Finds input[name="username"] or #username
    "email": "test@mail.com",  # Finds input[type="email"]
    "password": "pass123",      # Finds input[type="password"]
    "name": "John Doe",        # Finds input[name="name"]
    "phone": "+1234567890"     # Finds input[name="phone"]
}
```

### Explicit Selectors

```python
fields = {
    "#username-field": "myuser",
    "input[name='email']": "test@mail.com",
    ".password-input": "pass123"
}
```

### Select Dropdowns

```python
fields = {
    "#country": "US",           # Select by value
    "#country:text": "United States",  # Select by text
    "select[name='timezone']": "America/New_York"
}
```

### Checkboxes

```python
# Auto-check
fields = {
    "#terms": True,     # Checks checkbox
    "#newsletter": True
}
```

## CAPTCHA Handling

### Auto Detection

```python
# Enable auto CAPTCHA detection
creator = AccountCreator({
    "auto_captcha": True,
    "captcha_service": "2captcha",
    "captcha_api_key": "YOUR_API_KEY"
})

# Will automatically detect and solve CAPTCHA
await creator.create_account(url, email, fields)
```

### Manual CAPTCHA

```python
# Pause for manual CAPTCHA solve
await creator.create_account(
    url, email, fields,
    pause_for_captcha=True  # Browser stays open, solve manually
)
```

## Configuration

```json
{
  "port": 3003,
  "headless": false,
  "temp_mail_service": "pinmx",
  "auto_verify": true,
  "verify_timeout": 120000,
  "save_accounts_dir": "./accounts",
  "captcha": {
    "auto_solve": false,
    "service": "2captcha",
    "api_key": ""
  },
  "proxy": {
    "enabled": false,
    "server": "http://proxy:port",
    "username": "",
    "password": ""
  }
}
```

## HTTP API

```
POST /api/email/generate
GET  /api/email/messages
POST /api/email/verify
POST /api/account/create
GET  /api/account/list
POST /api/account/save
POST /api/account/load
```

## Examples

### Complete Registration Flow

```python
from account_creator import AccountCreator

async def register_on_site(site_url):
    creator = AccountCreator({"headless": False})
    await creator.start()
    
    try:
        # Generate temp email
        email = await creator.generate_email()
        print(f"Using email: {email}")
        
        # Create account
        account = await creator.create_account(
            url=f"{site_url}/register",
            email=email,
            fields={
                "username": "auto_user_" + str(int(time.time())),
                "password": "SecurePass123!",
                "#terms": True
            },
            submit_selector="button[type='submit']",
            verify_email=True,
            verify_timeout=180000
        )
        
        print(f"Account created: {account}")
        return account
        
    finally:
        await creator.close()
```

### Batch Account Creation

```python
async def create_multiple_accounts(site_url, count=5):
    accounts = []
    
    for i in range(count):
        creator = AccountCreator()
        await creator.start()
        
        try:
            email = await creator.generate_email()
            account = await creator.create_account(
                url=f"{site_url}/register",
                email=email,
                fields={
                    "username": f"user{i}_{int(time.time())}",
                    "password": "TestPass123!"
                },
                verify_email=True
            )
            accounts.append(account)
            
            # Save each account
            await creator.save_account(f"account_{i}", account)
            
        finally:
            await creator.close()
            
    return accounts
```

## Requirements

- Python 3.8+
- playwright
- aiohttp
- imaplib (built-in)
- email (built-in)

## Installation

```bash
cd skills/account-creator
pip install -r requirements.txt
playwright install chromium
```

## License

MIT
