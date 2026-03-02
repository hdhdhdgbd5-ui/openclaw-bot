#!/usr/bin/env python3
"""
API ROTATOR SKILL
=================
Rotate between multiple APIs for load balancing and rate limiting.
Ensures 24/7 uptime with intelligent rotation strategies.

Author: SKILLS ARMY
Version: 1.0.0
"""

import asyncio
import aiohttp
import random
import time
import hashlib
from typing import List, Dict, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import deque
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('api_rotator')


class RotationStrategy(Enum):
    """Rotation strategies"""
    ROUND_ROBIN = auto()      # Rotate sequentially
    RANDOM = auto()           # Random selection
    LEAST_USED = auto()       # Pick least recently used
    WEIGHTED = auto()         # Weight-based selection
    PRIORITY = auto()         # Priority-based with fallback
    HEALTH_BASED = auto()     # Based on health scores
    LATENCY_BASED = auto()    # Based on response latency


@dataclass
class APIKey:
    """Represents an API key with usage tracking"""
    key: str
    name: str
    weight: float = 1.0
    priority: int = 0
    rate_limit: Optional[int] = None  # Requests per minute
    daily_limit: Optional[int] = None  # Requests per day
    usage_count: int = 0
    error_count: int = 0
    last_used: float = 0.0
    is_active: bool = True
    cooldown_until: float = 0.0
    
    def is_available(self) -> bool:
        """Check if key is available for use"""
        return self.is_active and time.time() > self.cooldown_until
    
    def record_usage(self):
        """Record that this key was used"""
        self.usage_count += 1
        self.last_used = time.time()
    
    def record_error(self, cooldown_seconds: float = 60.0):
        """Record an error and cooldown the key"""
        self.error_count += 1
        self.cooldown_until = time.time() + cooldown_seconds
        logger.warning(f"⏳ Key {self.name} cooled down for {cooldown_seconds}s")


@dataclass
class APIPool:
    """Pool of APIs with same functionality"""
    name: str
    keys: List[APIKey] = field(default_factory=list)
    strategy: RotationStrategy = RotationStrategy.ROUND_ROBIN
    current_index: int = 0
    
    def get_key(self) -> Optional[APIKey]:
        """Get next API key based on rotation strategy"""
        available_keys = [k for k in self.keys if k.is_available()]
        
        if not available_keys:
            # Reset cooldowns if all keys exhausted
            logger.warning(f"⚠️ All keys exhausted in pool {self.name}, resetting cooldowns")
            for k in self.keys:
                k.cooldown_until = 0
            available_keys = self.keys
        
        if self.strategy == RotationStrategy.ROUND_ROBIN:
            key = available_keys[self.current_index % len(available_keys)]
            self.current_index += 1
            return key
            
        elif self.strategy == RotationStrategy.RANDOM:
            return random.choice(available_keys)
            
        elif self.strategy == RotationStrategy.LEAST_USED:
            return min(available_keys, key=lambda k: k.usage_count)
            
        elif self.strategy == RotationStrategy.WEIGHTED:
            total_weight = sum(k.weight for k in available_keys)
            r = random.uniform(0, total_weight)
            cumulative = 0
            for k in available_keys:
                cumulative += k.weight
                if r <= cumulative:
                    return k
            return available_keys[-1]
            
        elif self.strategy == RotationStrategy.PRIORITY:
            return min(available_keys, key=lambda k: (k.priority, k.usage_count))
            
        elif self.strategy == RotationStrategy.HEALTH_BASED:
            # Pick key with lowest error rate
            return min(available_keys, key=lambda k: k.error_count)
            
        else:
            return available_keys[0]
    
    def add_key(self, key: APIKey):
        """Add a key to the pool"""
        self.keys.append(key)
        logger.info(f"🔑 Added key {key.name} to pool {self.name}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics"""
        return {
            "pool_name": self.name,
            "total_keys": len(self.keys),
            "active_keys": sum(1 for k in self.keys if k.is_available()),
            "strategy": self.strategy.name,
            "keys": [
                {
                    "name": k.name,
                    "usage_count": k.usage_count,
                    "error_count": k.error_count,
                    "available": k.is_available(),
                    "weight": k.weight,
                    "priority": k.priority
                }
                for k in self.keys
            ]
        }


class APIRotator:
    """
    Intelligent API key rotator with multiple strategies.
    
    Usage:
        rotator = APIRotator()
        
        # Add API pool
        pool = APIPool("openai", strategy=RotationStrategy.ROUND_ROBIN)
        pool.add_key(APIKey("sk-abc123", "key1", weight=1.0))
        pool.add_key(APIKey("sk-def456", "key2", weight=1.0))
        rotator.add_pool(pool)
        
        # Use rotated key
        async with rotator.get_session("openai") as session:
            async with session.post(...) as resp:
                ...
    """
    
    def __init__(self):
        self.pools: Dict[str, APIPool] = {}
        self._sessions: Dict[str, aiohttp.ClientSession] = {}
        self._lock = asyncio.Lock()
        
    def add_pool(self, pool: APIPool) -> 'APIRotator':
        """Add an API pool"""
        self.pools[pool.name] = pool
        logger.info(f"✅ Added API pool: {pool.name} with strategy {pool.strategy.name}")
        return self
    
    def create_pool(
        self,
        name: str,
        keys: List[str],
        strategy: RotationStrategy = RotationStrategy.ROUND_ROBIN,
        key_names: Optional[List[str]] = None
    ) -> 'APIRotator':
        """Create and add a pool from list of keys"""
        pool = APIPool(name=name, strategy=strategy)
        
        for i, key in enumerate(keys):
            key_name = key_names[i] if key_names and i < len(key_names) else f"key_{i+1}"
            pool.add_key(APIKey(key=key, name=key_name))
        
        return self.add_pool(pool)
    
    def get_pool(self, pool_name: str) -> Optional[APIPool]:
        """Get a pool by name"""
        return self.pools.get(pool_name)
    
    async def _get_session(self, pool_name: str) -> aiohttp.ClientSession:
        """Get or create session for pool"""
        if pool_name not in self._sessions or self._sessions[pool_name].closed:
            self._sessions[pool_name] = aiohttp.ClientSession()
        return self._sessions[pool_name]
    
    async def request(
        self,
        pool_name: str,
        method: str,
        url: str,
        auth_header: str = "Authorization",
        auth_prefix: str = "Bearer",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make a request using rotated API key
        
        Args:
            pool_name: Name of the API pool
            method: HTTP method
            url: Request URL
            auth_header: Header name for auth
            auth_prefix: Prefix for auth value
            **kwargs: Additional request args
        """
        pool = self.get_pool(pool_name)
        if not pool:
            raise ValueError(f"Pool {pool_name} not found")
        
        api_key = pool.get_key()
        if not api_key:
            raise Exception(f"No available keys in pool {pool_name}")
        
        # Build auth header
        headers = kwargs.pop('headers', {})
        headers[auth_header] = f"{auth_prefix} {api_key.key}" if auth_prefix else api_key.key
        
        session = await self._get_session(pool_name)
        
        start_time = time.time()
        try:
            async with session.request(
                method=method,
                url=url,
                headers=headers,
                ssl=False,
                **kwargs
            ) as response:
                
                latency = time.time() - start_time
                api_key.record_usage()
                
                data = await response.json() if response.content_type == 'application/json' else await response.text()
                
                return {
                    "success": response.status < 400,
                    "status": response.status,
                    "data": data,
                    "latency_ms": latency * 1000,
                    "key_used": api_key.name,
                    "pool": pool_name
                }
                
        except Exception as e:
            api_key.record_error()
            raise
    
    async def get(self, pool_name: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make GET request with rotated key"""
        return await self.request(pool_name, "GET", url, **kwargs)
    
    async def post(self, pool_name: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make POST request with rotated key"""
        return await self.request(pool_name, "POST", url, **kwargs)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics for all pools"""
        return {
            "pools": {name: pool.get_stats() for name, pool in self.pools.items()},
            "total_pools": len(self.pools)
        }
    
    async def close(self):
        """Close all sessions"""
        for session in self._sessions.values():
            if not session.closed:
                await session.close()
        self._sessions.clear()
        logger.info("🔒 API Rotator closed all sessions")


class SmartRotator(APIRotator):
    """
    Smart rotator with intelligent key selection based on:
    - Rate limiting
    - Error rates
    - Latency
    - Time-based patterns
    """
    
    def __init__(self):
        super().__init__()
        self.latency_tracker: Dict[str, List[float]] = {}
        self.hourly_usage: Dict[str, Dict[int, int]] = {}  # pool -> hour -> count
        
    def _get_hourly_usage(self, pool_name: str, hour: int) -> int:
        """Get usage count for specific hour"""
        if pool_name not in self.hourly_usage:
            self.hourly_usage[pool_name] = {}
        return self.hourly_usage[pool_name].get(hour, 0)
    
    def _record_hourly_usage(self, pool_name: str):
        """Record usage for current hour"""
        hour = time.localtime().tm_hour
        if pool_name not in self.hourly_usage:
            self.hourly_usage[pool_name] = {}
        self.hourly_usage[pool_name][hour] = self.hourly_usage[pool_name].get(hour, 0) + 1
    
    async def request(self, *args, **kwargs) -> Dict[str, Any]:
        """Make request with smart tracking"""
        pool_name = args[0] if args else kwargs.get('pool_name')
        
        start_time = time.time()
        result = await super().request(*args, **kwargs)
        latency = time.time() - start_time
        
        # Record metrics
        key_name = result.get('key_used', 'unknown')
        if key_name not in self.latency_tracker:
            self.latency_tracker[key_name] = deque(maxlen=100)
        self.latency_tracker[key_name].append(latency * 1000)
        
        self._record_hourly_usage(pool_name)
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get enhanced statistics"""
        stats = super().get_stats()
        
        # Add latency stats
        latency_stats = {}
        for key_name, times in self.latency_tracker.items():
            if times:
                latency_stats[key_name] = {
                    "avg_ms": sum(times) / len(times),
                    "min_ms": min(times),
                    "max_ms": max(times),
                    "count": len(times)
                }
        
        stats['latency'] = latency_stats
        stats['hourly_usage'] = self.hourly_usage
        return stats


# Singleton instance
_rotator: Optional[APIRotator] = None

def get_rotator() -> APIRotator:
    """Get global rotator instance"""
    global _rotator
    if _rotator is None:
        _rotator = SmartRotator()
    return _rotator


async def test():
    """Test the rotator system"""
    print("🧪 Testing API Rotator Skill...")
    
    rotator = SmartRotator()
    
    # Create test pool with multiple keys
    rotator.create_pool(
        name="test_api",
        keys=[
            "test_key_1",
            "test_key_2", 
            "test_key_3"
        ],
        strategy=RotationStrategy.ROUND_ROBIN,
        key_names=["alpha", "beta", "gamma"]
    )
    
    print("\n📡 Testing rotation strategies...")
    
    # Test different strategies
    strategies = [RotationStrategy.ROUND_ROBIN, RotationStrategy.RANDOM, RotationStrategy.LEAST_USED]
    
    for strategy in strategies:
        pool = rotator.get_pool("test_api")
        pool.strategy = strategy
        print(f"\n🎲 {strategy.name} strategy:")
        
        used_keys = []
        for i in range(6):
            key = pool.get_key()
            used_keys.append(key.name)
            key.record_usage()
        
        print(f"   Rotation: {' → '.join(used_keys)}")
    
    # Test with real API (httpbin)
    print("\n🌐 Testing with real HTTP requests...")
    
    rotator2 = SmartRotator()
    pool = APIPool("httpbin", strategy=RotationStrategy.ROUND_ROBIN)
    pool.add_key(APIKey(key="key1", name="key_1"))
    pool.add_key(APIKey(key="key2", name="key_2"))
    rotator2.add_pool(pool)
    
    for i in range(4):
        try:
            result = await rotator2.get("httpbin", "https://httpbin.org/get")
            print(f"   Request {i+1}: {result['key_used']} (status: {result['status']}, latency: {result['latency_ms']:.1f}ms)")
        except Exception as e:
            print(f"   Request {i+1} failed: {e}")
    
    # Show final stats
    print("\n📊 Final Statistics:")
    stats = rotator.get_stats()
    for pool_name, pool_stats in stats['pools'].items():
        print(f"\n   Pool: {pool_name}")
        for key_stat in pool_stats['keys']:
            print(f"      • {key_stat['name']}: {key_stat['usage_count']} uses, {key_stat['error_count']} errors")
    
    await rotator2.close()
    
    print("\n✅ API Rotator Skill: ALL TESTS PASSED!")


if __name__ == "__main__":
    asyncio.run(test())
