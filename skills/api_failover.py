#!/usr/bin/env python3
"""
API FAILOVER SKILL
==================
Automatic fallback when primary API fails.
Ensures 24/7 uptime with seamless failover.

Author: SKILLS ARMY
Version: 1.0.0
"""

import asyncio
import aiohttp
import random
import time
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('api_failover')


class APIStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"


@dataclass
class APIEndpoint:
    """Represents an API endpoint with health tracking"""
    name: str
    base_url: str
    priority: int = 0  # Lower = higher priority
    timeout: float = 30.0
    retries: int = 3
    health_score: float = 100.0
    last_check: float = 0.0
    status: APIStatus = APIStatus.HEALTHY
    fail_count: int = 0
    success_count: int = 0
    headers: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.headers:
            self.headers = {"Content-Type": "application/json", "User-Agent": "SkillsArmy-APIFailover/1.0"}


class APIFailoverManager:
    """
    Manages multiple API endpoints with automatic failover.
    
    Usage:
        manager = APIFailoverManager()
        manager.add_endpoint(APIEndpoint("primary", "https://api1.example.com", priority=1))
        manager.add_endpoint(APIEndpoint("backup", "https://api2.example.com", priority=2))
        
        result = await manager.request("GET", "/data")
    """
    
    def __init__(self, health_check_interval: float = 60.0, max_failures: int = 3):
        self.endpoints: List[APIEndpoint] = []
        self.health_check_interval = health_check_interval
        self.max_failures = max_failures
        self._session: Optional[aiohttp.ClientSession] = None
        self._current_index = 0
        self._lock = asyncio.Lock()
        self._health_check_task: Optional[asyncio.Task] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    def add_endpoint(self, endpoint: APIEndpoint) -> 'APIFailoverManager':
        """Add an API endpoint to the pool"""
        self.endpoints.append(endpoint)
        # Sort by priority
        self.endpoints.sort(key=lambda e: e.priority)
        logger.info(f"✅ Added API endpoint: {endpoint.name} ({endpoint.base_url}) [Priority: {endpoint.priority}]")
        return self
    
    def remove_endpoint(self, name: str) -> bool:
        """Remove an API endpoint by name"""
        for i, ep in enumerate(self.endpoints):
            if ep.name == name:
                self.endpoints.pop(i)
                logger.info(f"🗑️ Removed API endpoint: {name}")
                return True
        return False
    
    def _get_healthy_endpoints(self) -> List[APIEndpoint]:
        """Get list of healthy endpoints sorted by priority"""
        healthy = [ep for ep in self.endpoints if ep.status != APIStatus.DOWN]
        healthy.sort(key=lambda e: (e.priority, -e.health_score))
        return healthy
    
    async def _check_endpoint_health(self, endpoint: APIEndpoint) -> bool:
        """Check if an endpoint is healthy"""
        try:
            session = await self._get_session()
            start_time = time.time()
            
            async with session.get(
                f"{endpoint.base_url}/health",
                headers=endpoint.headers,
                timeout=aiohttp.ClientTimeout(total=10),
                ssl=False
            ) as response:
                latency = time.time() - start_time
                
                if response.status == 200:
                    endpoint.health_score = min(100, endpoint.health_score + 10)
                    endpoint.fail_count = 0
                    endpoint.success_count += 1
                    endpoint.status = APIStatus.HEALTHY
                    logger.debug(f"💚 {endpoint.name} is healthy ({latency*1000:.0f}ms)")
                    return True
                else:
                    raise Exception(f"Health check failed: {response.status}")
                    
        except Exception as e:
            endpoint.fail_count += 1
            endpoint.health_score = max(0, endpoint.health_score - 20)
            
            if endpoint.fail_count >= self.max_failures:
                endpoint.status = APIStatus.DOWN
                logger.warning(f"💔 {endpoint.name} marked as DOWN ({endpoint.fail_count} failures)")
            else:
                endpoint.status = APIStatus.DEGRADED
                logger.warning(f"⚠️ {endpoint.name} is degraded ({endpoint.fail_count}/{self.max_failures} failures)")
            
            return False
    
    async def _health_check_loop(self):
        """Background health check loop"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                logger.info("🏥 Running health checks...")
                
                tasks = [self._check_endpoint_health(ep) for ep in self.endpoints]
                await asyncio.gather(*tasks, return_exceptions=True)
                
                healthy_count = len(self._get_healthy_endpoints())
                logger.info(f"📊 Health check complete: {healthy_count}/{len(self.endpoints)} endpoints healthy")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"💥 Health check error: {e}")
    
    async def start_health_monitoring(self):
        """Start background health monitoring"""
        if self._health_check_task is None or self._health_check_task.done():
            self._health_check_task = asyncio.create_task(self._health_check_loop())
            logger.info("🔄 Health monitoring started")
    
    async def stop_health_monitoring(self):
        """Stop background health monitoring"""
        if self._health_check_task and not self._health_check_task.done():
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
            logger.info("⏹️ Health monitoring stopped")
    
    async def request(
        self,
        method: str,
        path: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make a request with automatic failover
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path
            **kwargs: Additional arguments for aiohttp
            
        Returns:
            Response data
            
        Raises:
            Exception: If all endpoints fail
        """
        healthy_endpoints = self._get_healthy_endpoints()
        
        if not healthy_endpoints:
            # Try to revive endpoints if all are down
            logger.warning("🚨 All endpoints down! Attempting recovery...")
            for ep in self.endpoints:
                ep.status = APIStatus.DEGRADED
                ep.fail_count = 0
            healthy_endpoints = self.endpoints
        
        last_error = None
        
        for endpoint in healthy_endpoints:
            for attempt in range(endpoint.retries):
                try:
                    session = await self._get_session()
                    url = f"{endpoint.base_url.rstrip('/')}/{path.lstrip('/')}"
                    
                    headers = {**endpoint.headers, **kwargs.pop('headers', {})}
                    timeout = aiohttp.ClientTimeout(total=endpoint.timeout)
                    
                    logger.info(f"🎯 Request via {endpoint.name}: {method} {path}")
                    
                    async with session.request(
                        method=method,
                        url=url,
                        headers=headers,
                        timeout=timeout,
                        ssl=False,
                        **kwargs
                    ) as response:
                        
                        if response.status < 500:  # 5xx errors trigger failover
                            data = await response.json() if response.content_type == 'application/json' else await response.text()
                            
                            # Update health on success
                            endpoint.success_count += 1
                            endpoint.fail_count = 0
                            endpoint.health_score = min(100, endpoint.health_score + 5)
                            
                            return {
                                "success": True,
                                "endpoint": endpoint.name,
                                "status": response.status,
                                "data": data,
                                "attempt": attempt + 1
                            }
                        else:
                            raise Exception(f"Server error: {response.status}")
                            
                except Exception as e:
                    last_error = e
                    endpoint.fail_count += 1
                    logger.warning(f"⚠️ {endpoint.name} attempt {attempt + 1} failed: {e}")
                    await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
            
            # Mark endpoint as degraded after all retries fail
            if endpoint.fail_count >= self.max_failures:
                endpoint.status = APIStatus.DOWN
                logger.error(f"💔 {endpoint.name} marked DOWN after {endpoint.retries} retries")
        
        # All endpoints failed
        raise Exception(f"All API endpoints failed. Last error: {last_error}")
    
    async def get(self, path: str, **kwargs) -> Dict[str, Any]:
        """Convenience method for GET requests"""
        return await self.request("GET", path, **kwargs)
    
    async def post(self, path: str, **kwargs) -> Dict[str, Any]:
        """Convenience method for POST requests"""
        return await self.request("POST", path, **kwargs)
    
    async def close(self):
        """Close the session"""
        await self.stop_health_monitoring()
        if self._session and not self._session.closed:
            await self._session.close()
            logger.info("🔒 API Failover Manager closed")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of all endpoints"""
        return {
            "endpoints": [
                {
                    "name": ep.name,
                    "url": ep.base_url,
                    "status": ep.status.value,
                    "health_score": ep.health_score,
                    "fail_count": ep.fail_count,
                    "success_count": ep.success_count,
                    "priority": ep.priority
                }
                for ep in self.endpoints
            ],
            "healthy_count": len(self._get_healthy_endpoints()),
            "total_count": len(self.endpoints)
        }


# Singleton instance for global use
_failover_manager: Optional[APIFailoverManager] = None

def get_failover_manager() -> APIFailoverManager:
    """Get global failover manager instance"""
    global _failover_manager
    if _failover_manager is None:
        _failover_manager = APIFailoverManager()
    return _failover_manager


async def test():
    """Test the failover system"""
    print("🧪 Testing API Failover Skill...")
    
    manager = APIFailoverManager()
    
    # Add test endpoints (using httpbin for testing)
    manager.add_endpoint(APIEndpoint(
        name="primary",
        base_url="https://httpbin.org",
        priority=1,
        timeout=10.0
    ))
    
    manager.add_endpoint(APIEndpoint(
        name="backup",
        base_url="https://httpbin.org",
        priority=2,
        timeout=10.0
    ))
    
    # Start health monitoring
    await manager.start_health_monitoring()
    
    try:
        # Test GET request
        print("\n📡 Testing GET request...")
        result = await manager.get("/get")
        print(f"✅ Success: {result['endpoint']} responded with status {result['status']}")
        
        # Test POST request
        print("\n📡 Testing POST request...")
        result = await manager.post("/post", json={"test": "data"})
        print(f"✅ Success: {result['endpoint']} responded with status {result['status']}")
        
        # Get status
        print("\n📊 System Status:")
        status = manager.get_status()
        for ep in status['endpoints']:
            print(f"  • {ep['name']}: {ep['status']} (health: {ep['health_score']:.0f}%)")
        
        print("\n✅ API Failover Skill: ALL TESTS PASSED!")
        
    finally:
        await manager.close()


if __name__ == "__main__":
    asyncio.run(test())
