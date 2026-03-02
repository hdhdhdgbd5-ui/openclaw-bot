"""
Account Creator - Automated account creation with temp mail and email verification
"""
import asyncio
import json
import re
import time
import os
import random
import string
from typing import Dict, List, Optional, Any
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
import aiohttp

class ProfileGenerator:
    """Generate random profile data for account creation"""
    
    FIRST_NAMES = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", 
                   "Michael", "Linda", "William", "Elizabeth", "David", "Barbara",
                   "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah"]
    
    LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
                  "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez"]
    
    DOMAINS = ["example.com", "mail.com", "test.com", "demo.com"]
    
    def __init__(self, seed: Optional[int] = None):
        if seed:
            random.seed(seed)
            
    def generate_username(self, prefix: str = "user") -> str:
        """Generate random username"""
        suffix = ''.join(random.choices(string.digits, k=4))
        return f"{prefix}{suffix}"
    
    def generate_password(self, length: int = 12) -> str:
        """Generate secure password"""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choices(chars, k=length))
    
    def generate_email(self, domain: Optional[str] = None) -> str:
        """Generate random email"""
        first = random.choice(self.FIRST_NAMES).lower()
        last = random.choice(self.LAST_NAMES).lower()
        num = random.randint(1, 999)
        if domain:
            return f"{first}.{last}{num}@{domain}"
        return f"{first}.{last}{num}@{random.choice(self.DOMAINS)}"
    
    def generate_phone(self) -> str:
        """Generate random phone number"""
        return f"+1{random.randint(2000000000, 9999999999)}"
    
    def generate(self) -> Dict:
        """Generate complete profile"""
        first_name = random.choice(self.FIRST_NAMES)
        last_name = random.choice(self.LAST_NAMES)
        
        return {
            "first_name": first_name,
            "last_name": last_name,
            "name": f"{first_name} {last_name}",
            "username": self.generate_username(),
            "password": self.generate_password(),
            "email": self.generate_email(),
            "phone": self.generate_phone(),
            "address": {
                "street": f"{random.randint(1, 9999)} {random.choice(['Main', 'Oak', 'Pine', 'Maple'])} St",
                "city": random.choice(["New York", "Los Angeles", "Chicago", "Houston"]),
                "state": random.choice(["NY", "CA", "IL", "TX"]),
                "zip": str(random.randint(10000, 99999)),
                "country": "US"
            }
        }


class TempMailService:
    """Temp mail service integration"""
    
    def __init__(self, service: str = "pinmx"):
        self.service = service
        self.email = None
        self.session = None
        
    async def generate_email(self) -> str:
        """Generate temp email address"""
        if self.service == "pinmx":
            return await self._pinmx_generate()
        elif self.service == "temp-mail":
            return await self._temp_mail_generate()
        elif self.service == "guerrilla":
            return await self._guerrilla_generate()
        else:
            # Default to pinmx
            return await self._pinmx_generate()
    
    async def _pinmx_generate(self) -> str:
        """Generate email via pinmx.net"""
        try:
            async with aiohttp.ClientSession() as session:
                # Pinmx typically provides random email
                async with session.get("https://pinmx.net/api/mailbox/random") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.email = data.get("email")
                        return self.email
        except Exception as e:
            print(f"Pinmx error: {e}")
        
        # Fallback: generate random email and hope it works
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        self.email = f"{username}@pinmx.net"
        return self.email
    
    async def _temp_mail_generate(self) -> str:
        """Generate email via temp-mail.io"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.temp-mail.io/v3/email/new") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.email = data.get("email")
                        return self.email
        except Exception as e:
            print(f"Temp-mail error: {e}")
        
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        self.email = f"{username}@temp-mail.io"
        return self.email
    
    async def _guerrilla_generate(self) -> str:
        """Generate email via guerrillamail"""
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        self.email = f"{username}@guerrillamail.com"
        return self.email
    
    async def get_messages(self, timeout: int = 30000) -> List[Dict]:
        """Get email messages"""
        if not self.email:
            raise RuntimeError("No email generated")
            
        if self.service == "pinmx":
            return await self._pinmx_get_messages(timeout)
        elif self.service == "temp-mail":
            return await self._temp_mail_get_messages(timeout)
        elif self.service == "guerrilla":
            return await self._guerrilla_get_messages(timeout)
        return []
    
    async def _pinmx_get_messages(self, timeout: int) -> List[Dict]:
        """Get messages from pinmx"""
        try:
            # Extract username from email
            username = self.email.split("@")[0]
            
            async with aiohttp.ClientSession() as session:
                start = time.time()
                while time.time() - start < timeout / 1000:
                    async with session.get(f"https://pinmx.net/api/mailbox/{username}/messages") as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            messages = data.get("messages", [])
                            if messages:
                                return messages
                    await asyncio.sleep(2)
        except Exception as e:
            print(f"Pinmx get messages error: {e}")
        return []
    
    async def _temp_mail_get_messages(self, timeout: int) -> List[Dict]:
        """Get messages from temp-mail"""
        try:
            async with aiohttp.ClientSession() as session:
                start = time.time()
                while time.time() - start < timeout / 1000:
                    async with session.get(f"https://api.temp-mail.io/v3/email/{self.email}/messages") as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            messages = data.get("items", [])
                            if messages:
                                return messages
                    await asyncio.sleep(2)
        except Exception as e:
            print(f"Temp-mail get messages error: {e}")
        return []
    
    async def _guerrilla_get_messages(self, timeout: int) -> List[Dict]:
        """Get messages from guerrillamail"""
        try:
            async with aiohttp.ClientSession() as session:
                # Use their API
                token = self.email.split("@")[0]
                start = time.time()
                while time.time() - start < timeout / 1000:
                    async with session.get(
                        "https://api.guerrillamail.com/ajax.php",
                        params={"a": "get_email_list", "token": token}
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            messages = data.get("list", [])
                            if messages:
                                return messages
                    await asyncio.sleep(2)
        except Exception as e:
            print(f"Guerrilla get messages error: {e}")
        return []
    
    async def get_message_body(self, message_id: str) -> str:
        """Get full message body"""
        if self.service == "pinmx":
            try:
                username = self.email.split("@")[0]
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://pinmx.net/api/mailbox/{username}/message/{message_id}") as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            return data.get("body", "")
            except Exception as e:
                print(f"Error getting message body: {e}")
        return ""
    
    async def wait_for_verification_email(self, timeout: int = 120000) -> Optional[Dict]:
        """Wait for verification email"""
        start_time = time.time()
        
        while time.time() - start_time < timeout / 1000:
            messages = await self.get_messages(timeout=5000)
            
            for msg in messages:
                subject = msg.get("subject", "").lower()
                if "verif" in subject or "confirm" in subject or "activate" in subject:
                    # Get full body
                    msg_id = msg.get("id")
                    if msg_id:
                        body = await self.get_message_body(msg_id)
                        msg["body"] = body
                    return msg
                    
            await asyncio.sleep(2)
            
        return None


class IMAPEmailChecker:
    """Check real email via IMAP (Gmail, Outlook, etc.)"""
    
    def __init__(self, imap_config: Dict):
        self.config = imap_config
        self.host = imap_config.get("host")
        self.port = imap_config.get("port", 993)
        self.username = imap_config.get("username")
        self.password = imap_config.get("password")
        
    async def wait_for_verification_code(self, timeout: int = 120000) -> Optional[str]:
        """Wait for verification code in email"""
        import imaplib
        import email
        
        start_time = time.time()
        
        # Connect
        mail = imaplib.IMAP4_SSL(self.host, self.port)
        mail.login(self.username, self.password)
        
        while time.time() - start_time < timeout / 1000:
            try:
                # Select inbox
                status, _ = mail.select("INBOX")
                if status != "OK":
                    await asyncio.sleep(5)
                    continue
                    
                # Search for recent emails
                _, message_ids = mail.search(None, "ALL")
                ids = message_ids[0].split()
                
                # Check last few emails
                for msg_id in ids[-10:]:
                    _, msg_data = mail.fetch(msg_id, "(RFC822)")
                    msg = email.message_from_bytes(msg_data[0][1])
                    
                    subject = msg.get("subject", "")
                    if "verif" in subject.lower() or "code" in subject.lower():
                        # Get body
                        if msg.is_multipart:
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True)
                                    if body:
                                        body = body.decode()
                                        # Extract code
                                        codes = re.findall(r"\b\d{4,8}\b", body)
                                        if codes:
                                            mail.close()
                                            mail.logout()
                                            return codes[0]
                        else:
                            body = msg.get_payload(decode=True)
                            if body:
                                body = body.decode()
                                codes = re.findall(r"\b\d{4,8}\b", body)
                                if codes:
                                    mail.close()
                                    mail.logout()
                                    return codes[0]
                                    
            except Exception as e:
                print(f"IMAP error: {e}")
                
            await asyncio.sleep(5)
            
        mail.close()
        mail.logout()
        return None


class AccountCreator:
    """Automated account creation with email verification"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.port = self.config.get("port", 3003)
        self.headless = self.config.get("headless", True)
        self.temp_mail_service = self.config.get("temp_mail_service", "pinmx")
        self.auto_verify = self.config.get("auto_verify", True)
        self.verify_timeout = self.config.get("verify_timeout", 120000)
        self.save_dir = self.config.get("save_accounts_dir", "./accounts")
        
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        self.temp_mail: Optional[TempMailService] = None
        self.current_email: Optional[str] = None
        self.created_account: Optional[Dict] = None
        
        # Ensure save directory exists
        Path(self.save_dir).mkdir(parents=True, exist_ok=True)
        
    async def start(self) -> "AccountCreator":
        """Start browser"""
        self.playwright = await async_playwright().start()
        
        # Proxy config
        proxy = None
        if self.config.get("proxy", {}).get("enabled"):
            proxy_config = self.config["proxy"]
            proxy = {
                "server": proxy_config.get("server"),
                "username": proxy_config.get("username"),
                "password": proxy_config.get("password")
            }
        
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            ignore_https_errors=True
        )
        
        # Add stealth script
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)
        
        self.page = await self.context.new_page()
        
        # Initialize temp mail
        self.temp_mail = TempMailService(self.temp_mail_service)
        
        return self
        
    async def navigate(self, url: str, wait_until: str = "domcontentloaded") -> "AccountCreator":
        """Navigate to URL"""
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        await self.page.goto(url, wait_until=wait_until)
        return self
    
    async def click(self, selector: str) -> "AccountCreator":
        """Click element by selector"""
        await self.page.click(selector)
        return self
    
    async def fill(self, selector: str, value: str) -> "AccountCreator":
        """Fill input field"""
        await self.page.fill(selector, value)
        return self
    
    async def fill_multiple(self, fields: Dict[str, str]) -> "AccountCreator":
        """Fill multiple fields"""
        for selector, value in fields.items():
            await self.page.fill(selector, value)
        return self
    
    async def select(self, selector: str, value: str) -> "AccountCreator":
        """Select option"""
        await self.page.select_option(selector, value)
        return self
    
    async def scroll_to(self, selector: str) -> "AccountCreator":
        """Scroll to element"""
        await self.page.locator(selector).scroll_into_view_if_needed()
        return self
    
    async def wait_for(self, selector: str, timeout: Optional[int] = None) -> "AccountCreator":
        """Wait for element"""
        await self.page.wait_for_selector(selector, timeout=timeout or 30000)
        return self
    
    async def get_text(self, selector: str) -> str:
        """Get text from element"""
        return await self.page.locator(selector).inner_text()
    
    async def get_attribute(self, selector: str, attr: str) -> Optional[str]:
        """Get element attribute"""
        return await self.page.locator(selector).get_attribute(attr)
    
    async def screenshot(self, filename: str = "screenshot.png") -> "AccountCreator":
        """Take screenshot"""
        await self.page.screenshot(path=filename)
        return self
        
    async def generate_email(self, service: Optional[str] = None) -> str:
        """Generate temp email"""
        if service:
            self.temp_mail = TempMailService(service)
        self.current_email = await self.temp_mail.generate_email()
        return self.current_email
        
    async def create_account(self, url: str, email: str,
                            fields: Dict[str, Any],
                            submit_selector: str = "button[type='submit']",
                            verify_email: bool = True,
                            verify_timeout: Optional[int] = None,
                            pause_for_captcha: bool = False) -> Dict:
        """Create account on website"""
        
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
            
        # Navigate to registration page
        await self.page.goto(url, wait_until="domcontentloaded")
        await self.page.wait_for_load_state("networkidle")
        
        # Fill fields
        for selector, value in fields.items():
            await self._fill_field(selector, value)
            
        # Handle CAPTCHA if needed
        if pause_for_captcha:
            input("Press Enter after solving CAPTCHA...")
        else:
            # Try to detect and handle CAPTCHA
            await self._handle_captcha()
            
        # Submit form
        await self.page.click(submit_selector)
        
        # Wait a bit for submission
        await asyncio.sleep(2)
        
        # Store account info
        account = {
            "email": email,
            "url": url,
            "fields": fields,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Add username if found in fields
        for key in ["username", "user", "login"]:
            if key in fields:
                account["username"] = fields[key]
                break
                
        if "password" in fields:
            account["password"] = fields["password"]
            
        self.created_account = account
        
        # Verify email if requested
        if verify_email:
            verification = await self.wait_for_verification(
                email or self.current_email,
                timeout=verify_timeout or self.verify_timeout
            )
            account["verified"] = verification is not None
            account["verification"] = verification
            
        return account
    
    async def _fill_field(self, selector: str, value: Any) -> None:
        """Fill a form field"""
        # Handle boolean (checkbox)
        if isinstance(value, bool):
            if value:
                await self.page.check(selector)
            else:
                await self.page.uncheck(selector)
            return
            
        # Check if it's a select by text
        if ":text" in selector:
            real_selector = selector.replace(":text", "")
            # Get option by text and select
            await self.page.select_option(real_selector, value)
            return
            
        # Regular fill
        await self.page.fill(selector, str(value))
        
    async def _handle_captcha(self) -> None:
        """Attempt to handle CAPTCHA"""
        # Check for common CAPTCHA indicators
        captcha_selectors = [
            "iframe[src*='recaptcha']",
            ".g-recaptcha",
            "#captcha",
            "input[name='captcha']",
            "[data-sitekey]"
        ]
        
        for sel in captcha_selectors:
            if await self.page.locator(sel).count() > 0:
                print(f"CAPTCHA detected: {sel}")
                # For now, just log it - real solving would need 2captcha or similar
                break
                
    async def wait_for_verification(self, email: str, 
                                   timeout: Optional[int] = None) -> Optional[Dict]:
        """Wait for email verification"""
        timeout = timeout or self.verify_timeout
        
        # Use temp mail service
        if self.temp_mail:
            return await self.temp_mail.wait_for_verification_email(timeout)
            
        return None
        
    async def wait_for_verification_code(self, email: str,
                                        mail_service: str = "gmail",
                                        imap_config: Optional[Dict] = None,
                                        timeout: Optional[int] = None) -> Optional[str]:
        """Wait for verification code"""
        timeout = timeout or self.verify_timeout
        
        if mail_service == "imap" and imap_config:
            checker = IMAPEmailChecker(imap_config)
            return await checker.wait_for_verification_code(timeout)
            
        # Try to extract from temp mail
        if self.temp_mail:
            msg = await self.temp_mail.wait_for_verification_email(timeout)
            if msg:
                body = msg.get("body", "")
                # Extract code patterns
                codes = re.findall(r"\b\d{4,8}\b", body)
                if codes:
                    return codes[0]
                    
        return None
        
    async def save_account(self, name: str, account: Dict) -> None:
        """Save account to file"""
        filepath = Path(self.save_dir) / f"{name}.json"
        with open(filepath, "w") as f:
            json.dump(account, f, indent=2)
            
    async def load_account(self, name: str) -> Optional[Dict]:
        """Load account from file"""
        filepath = Path(self.save_dir) / f"{name}.json"
        if filepath.exists():
            with open(filepath, "r") as f:
                return json.load(f)
        return None
        
    async def list_accounts(self) -> List[str]:
        """List saved accounts"""
        return [f.stem for f in Path(self.save_dir).glob("*.json")]
        
    async def delete_account(self, name: str) -> bool:
        """Delete saved account"""
        filepath = Path(self.save_dir) / f"{name}.json"
        if filepath.exists():
            filepath.unlink()
            return True
        return False
        
    async def close(self) -> None:
        """Close browser"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


# CLI interface
async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Account Creator")
    parser.add_argument("--url", "-u", help="Registration URL")
    parser.add_argument("--email", "-e", help="Email address")
    parser.add_argument("--username", help="Username")
    parser.add_argument("--password", help="Password")
    parser.add_argument("--headless", action="store_true", default=True)
    parser.add_argument("--save", "-s", help="Save account name")
    parser.add_argument("--verify", action="store_true", help="Wait for email verification")
    
    args = parser.parse_args()
    
    creator = AccountCreator({"headless": args.headless})
    await creator.start()
    
    try:
        # Generate or use provided email
        if args.email:
            email = args.email
        else:
            email = await creator.generate_email()
        print(f"Email: {email}")
        
        if args.url:
            fields = {}
            if args.username:
                fields["username"] = args.username
            if args.password:
                fields["password"] = args.password
                
            account = await creator.create_account(
                url=args.url,
                email=email,
                fields=fields,
                verify_email=args.verify
            )
            
            print(f"Account created: {json.dumps(account, indent=2)}")
            
            if args.save:
                await creator.save_account(args.save, account)
                print(f"Saved as: {args.save}")
                
    finally:
        await creator.close()


if __name__ == "__main__":
    asyncio.run(main())
