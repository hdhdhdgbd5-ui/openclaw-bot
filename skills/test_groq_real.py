import asyncio
import sys
sys.path.insert(0, '.')
from groq_integrator import GroqIntegrator

async def test():
    groq = GroqIntegrator()
    groq.load_key_from_file('C:\\Users\\armoo\\.openclaw\\workspace\\secrets\\groq.txt', 'primary', 0)
    
    print('Testing Groq API with real key...')
    response = await groq.chat('Say hello', max_tokens=10)
    
    if response.success:
        print(f'SUCCESS!')
        print(f'Response: {response.content}')
        print(f'Latency: {response.latency_ms:.1f}ms')
        print(f'Key used: {response.key_used}')
    else:
        print(f'ERROR: {response.error}')
    
    await groq.close()

asyncio.run(test())
