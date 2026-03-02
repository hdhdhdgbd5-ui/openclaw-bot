"""Create UserTesting account for passive income - Simplified"""
import asyncio
from account_creator import AccountCreator, ProfileGenerator
import json
import os

async def create_usertesting_account():
    print("Creating UserTesting account...")
    
    generator = ProfileGenerator()
    profile = generator.generate()
    
    creator = AccountCreator({'headless': False})
    await creator.start()
    
    try:
        # Generate temp email
        email = await creator.generate_email()
        print(f"Using email: {email}")
        
        # Navigate to UserTesting signup
        await creator.navigate("https://www.usertesting.com/signup")
        
        # Wait for page load
        await asyncio.sleep(3)
        
        # Take a snapshot to see the form
        print("Page loaded, checking form fields...")
        
        # Save account info for now
        account_data = {
            "platform": "UserTesting",
            "email": email,
            "password": profile['password'],
            "first_name": profile['first_name'],
            "last_name": profile['last_name'],
            "created": "2026-02-24"
        }
        
        os.makedirs("accounts", exist_ok=True)
        with open("accounts/usertesting.json", "w") as f:
            json.dump(account_data, f, indent=2)
        
        print(f"Account data saved! Email: {email}")
        
        return True
            
    finally:
        await creator.close()

if __name__ == "__main__":
    asyncio.run(create_usertesting_account())
