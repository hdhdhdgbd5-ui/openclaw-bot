"""Quick test for account-creator skill"""
import asyncio
from account_creator import AccountCreator, ProfileGenerator

async def test():
    print("Testing Profile Generator...")
    generator = ProfileGenerator()
    profile = generator.generate()
    print(f"Generated profile: {profile['username']}, {profile['email']}")
    
    print("\nStarting browser for account creator test...")
    creator = AccountCreator({'headless': True})
    await creator.start()
    
    # Test email generation
    print("\nGenerating temp email...")
    email = await creator.generate_email()
    print(f"Generated email: {email}")
    
    await creator.close()
    print('\nTest PASSED!')

if __name__ == "__main__":
    asyncio.run(test())
