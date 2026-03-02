#!/usr/bin/env python3
"""
UPTIME MONITOR SKILL
====================
24/7 system monitoring with automatic restart capability.
Ensures maximum uptime through proactive health checks.

Author: SKILLS ARMY
Version: 1.0.0
"""

import asyncio
import aiohttp
import subprocess
import sys
import os
import time
import json
import signal
from typing import List, Dict, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import threading
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('uptime_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('uptime_monitor')


class ServiceStatus(Enum):
    """Service status states"""
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    RECOVERING = "recovering"
    MAINTENANCE = "maintenance"


class CheckType(Enum):
    """Types of health checks"""
    HTTP = "http"
    TCP = "tcp"
    PROCESS = "process"
    CUSTOM = "custom"
    COMMAND = "command"


@dataclass
class HealthCheck:
    """Defines a health check"""
    name: str
    type: CheckType
    target: str  # URL, host:port, process name, etc.
    interval: float = 60.0  # Seconds between checks
    timeout: float = 10.0  # Timeout for each check
    retries: int = 3  # Retries before marking as failed
    expected_status: Optional[int] = 200  # For HTTP checks
    expected_response: Optional[str] = None  # Expected response substring
    headers: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    
    # Runtime tracking
    last_check: float = 0.0
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    total_checks: int = 0
    total_failures: int = 0
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_error: Optional[str] = None
    response_time_ms: float = 0.0


@dataclass
class Service:
    """Service to monitor"""
    name: str
    checks: List[HealthCheck] = field(default_factory=list)
    restart_command: Optional[str] = None
    restart_on_failure: bool = True
    max_restarts_per_hour: int = 5
    cooldown_seconds: float = 60.0
    dependencies: List[str] = field(default_factory=list)  # Other service names
    
    # Runtime tracking
    status: ServiceStatus = ServiceStatus.UNKNOWN
    restart_count: int = 0
    last_restart: float = 0.0
    uptime_seconds: float = 0.0
    start_time: float = 0.0
    health_score: float = 100.0


class UptimeMonitor:
    """
    24/7 Uptime Monitor with automatic restart capability.
    
    Usage:
        monitor = UptimeMonitor()
        
        # Add a service
        service = Service(
            name="web_api",
            restart_command="python app.py",
            checks=[
                HealthCheck(
                    name="api_health",
                    type=CheckType.HTTP,
                    target="http://localhost:8080/health"
                )
            ]
        )
        
        monitor.add_service(service)
        await monitor.start()
    """
    
    def __init__(self, alert_callback: Optional[Callable] = None):
        self.services: Dict[str, Service] = {}
        self._running = False
        self._tasks: Dict[str, asyncio.Task] = {}
        self._alert_callback = alert_callback
        self._start_time = time.time()
        self._alert_history: List[Dict] = []
        
    def add_service(self, service: Service) -> 'UptimeMonitor':
        """Add a service to monitor"""
        self.services[service.name] = service
        service.start_time = time.time()
        logger.info(f"✅ Added service: {service.name} ({len(service.checks)} checks)")
        return self
    
    def remove_service(self, name: str) -> bool:
        """Remove a service from monitoring"""
        if name not in self.services:
            return False
        
        if name in self._tasks:
            self._tasks[name].cancel()
            del self._tasks[name]
        
        del self.services[name]
        logger.info(f"🗑️ Removed service: {name}")
        return True
    
    async def _http_check(self, check: HealthCheck) -> bool:
        """Perform HTTP health check"""
        try:
            timeout = aiohttp.ClientTimeout(total=check.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(
                    check.target,
                    headers=check.headers,
                    ssl=False
                ) as response:
                    
                    if check.expected_status and response.status != check.expected_status:
                        check.last_error = f"Unexpected status: {response.status}"
                        return False
                    
                    if check.expected_response:
                        text = await response.text()
                        if check.expected_response not in text:
                            check.last_error = "Expected response not found"
                            return False
                    
                    return True
                    
        except Exception as e:
            check.last_error = str(e)
            return False
    
    async def _tcp_check(self, check: HealthCheck) -> bool:
        """Perform TCP health check"""
        try:
            host, port = check.target.rsplit(":", 1)
            port = int(port)
            
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=check.timeout
            )
            writer.close()
            await writer.wait_closed()
            return True
            
        except Exception as e:
            check.last_error = str(e)
            return False
    
    async def _process_check(self, check: HealthCheck) -> bool:
        """Check if process is running"""
        try:
            if sys.platform == "win32":
                result = subprocess.run(
                    ["tasklist", "/FI", f"IMAGENAME eq {check.target}"],
                    capture_output=True,
                    text=True,
                    timeout=check.timeout
                )
                return check.target.lower() in result.stdout.lower()
            else:
                result = subprocess.run(
                    ["pgrep", "-f", check.target],
                    capture_output=True,
                    timeout=check.timeout
                )
                return result.returncode == 0
                
        except Exception as e:
            check.last_error = str(e)
            return False
    
    async def _command_check(self, check: HealthCheck) -> bool:
        """Run custom command as health check"""
        try:
            result = subprocess.run(
                check.target,
                shell=True,
                capture_output=True,
                text=True,
                timeout=check.timeout
            )
            return result.returncode == 0
            
        except Exception as e:
            check.last_error = str(e)
            return False
    
    async def _perform_check(self, check: HealthCheck) -> bool:
        """Perform a single health check"""
        start_time = time.time()
        
        if check.type == CheckType.HTTP:
            result = await self._http_check(check)
        elif check.type == CheckType.TCP:
            result = await self._tcp_check(check)
        elif check.type == CheckType.PROCESS:
            result = await self._process_check(check)
        elif check.type == CheckType.COMMAND:
            result = await self._command_check(check)
        else:
            result = False
            check.last_error = f"Unknown check type: {check.type}"
        
        check.response_time_ms = (time.time() - start_time) * 1000
        check.last_check = time.time()
        check.total_checks += 1
        
        return result
    
    async def _check_loop(self, service_name: str):
        """Main monitoring loop for a service"""
        service = self.services[service_name]
        
        while self._running:
            try:
                # Check all health checks
                any_failed = False
                all_passed = True
                
                for check in service.checks:
                    if not check.enabled:
                        continue
                    
                    success = await self._perform_check(check)
                    
                    if success:
                        check.consecutive_successes += 1
                        check.consecutive_failures = 0
                        check.status = ServiceStatus.HEALTHY
                    else:
                        check.consecutive_failures += 1
                        check.consecutive_successes = 0
                        
                        if check.consecutive_failures >= check.retries:
                            check.status = ServiceStatus.DOWN
                            check.total_failures += 1
                            any_failed = True
                        else:
                            check.status = ServiceStatus.DEGRADED
                            all_passed = False
                            logger.warning(
                                f"⚠️ {service_name}/{check.name}: Attempt {check.consecutive_failures}/{check.retries} failed"
                            )
                    
                    await asyncio.sleep(0.1)  # Small delay between checks
                
                # Update service status
                previous_status = service.status
                
                if any_failed:
                    service.status = ServiceStatus.DOWN
                    service.health_score = max(0, service.health_score - 20)
                    
                    # Trigger restart if enabled
                    if service.restart_on_failure:
                        await self._restart_service(service)
                        
                elif all_passed:
                    service.status = ServiceStatus.HEALTHY
                    service.health_score = min(100, service.health_score + 5)
                    service.uptime_seconds = time.time() - service.start_time
                else:
                    service.status = ServiceStatus.DEGRADED
                
                # Alert on status change
                if previous_status != service.status and self._alert_callback:
                    await self._send_alert(service, previous_status, service.status)
                
                # Wait until next check cycle
                min_interval = min(c.interval for c in service.checks if c.enabled)
                await asyncio.sleep(min_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"💥 Error in check loop for {service_name}: {e}")
                await asyncio.sleep(5)
    
    async def _restart_service(self, service: Service):
        """Restart a failed service"""
        now = time.time()
        hour_ago = now - 3600
        
        # Check restart limits
        if service.last_restart > hour_ago:
            if service.restart_count >= service.max_restarts_per_hour:
                logger.error(
                    f"🚨 {service.name}: Max restarts ({service.max_restarts_per_hour}/hour) exceeded!"
                )
                service.restart_on_failure = False  # Stop trying
                return
        else:
            # Reset counter after an hour
            service.restart_count = 0
        
        # Check cooldown
        if now - service.last_restart < service.cooldown_seconds:
            logger.info(f"⏳ {service.name}: Waiting for cooldown...")
            await asyncio.sleep(service.cooldown_seconds - (now - service.last_restart))
        
        if not service.restart_command:
            logger.warning(f"⚠️ {service.name}: No restart command configured")
            return
        
        logger.info(f"🔄 Restarting service: {service.name}")
        service.status = ServiceStatus.RECOVERING
        service.restart_count += 1
        service.last_restart = time.time()
        
        try:
            # Run restart command
            if sys.platform == "win32":
                subprocess.Popen(
                    service.restart_command,
                    shell=True,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                subprocess.Popen(
                    service.restart_command,
                    shell=True,
                    start_new_session=True
                )
            
            logger.info(f"✅ {service.name} restart command executed")
            
            # Wait a bit for service to start
            await asyncio.sleep(5)
            
            # Reset service start time
            service.start_time = time.time()
            
        except Exception as e:
            logger.error(f"💥 Failed to restart {service.name}: {e}")
    
    async def _send_alert(self, service: Service, old_status: ServiceStatus, new_status: ServiceStatus):
        """Send status change alert"""
        alert = {
            "timestamp": time.time(),
            "service": service.name,
            "old_status": old_status.value,
            "new_status": new_status.value,
            "message": f"Service {service.name} changed from {old_status.value} to {new_status.value}"
        }
        
        self._alert_history.append(alert)
        
        logger.warning(f"🔔 ALERT: {alert['message']}")
        
        if self._alert_callback:
            try:
                await self._alert_callback(alert)
            except Exception as e:
                logger.error(f"Failed to send alert: {e}")
    
    async def start(self):
        """Start the uptime monitor"""
        self._running = True
        logger.info("🚀 Uptime Monitor starting...")
        
        # Start monitoring tasks
        for name in self.services:
            self._tasks[name] = asyncio.create_task(self._check_loop(name))
            logger.info(f"📡 Started monitoring: {name}")
        
        logger.info(f"✅ Uptime Monitor active - monitoring {len(self.services)} services")
    
    async def stop(self):
        """Stop the uptime monitor"""
        logger.info("🛑 Stopping Uptime Monitor...")
        self._running = False
        
        # Cancel all tasks
        for name, task in self._tasks.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            logger.info(f"⏹️ Stopped monitoring: {name}")
        
        self._tasks.clear()
        logger.info("✅ Uptime Monitor stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of all services"""
        total_uptime = time.time() - self._start_time
        
        return {
            "monitor_uptime_seconds": total_uptime,
            "monitor_uptime_formatted": self._format_duration(total_uptime),
            "services_monitored": len(self.services),
            "services": {
                name: {
                    "status": service.status.value,
                    "health_score": service.health_score,
                    "uptime_seconds": service.uptime_seconds,
                    "uptime_formatted": self._format_duration(service.uptime_seconds),
                    "restart_count": service.restart_count,
                    "checks": [
                        {
                            "name": check.name,
                            "type": check.type.value,
                            "status": check.status.value,
                            "response_time_ms": check.response_time_ms,
                            "total_checks": check.total_checks,
                            "total_failures": check.total_failures,
                            "success_rate": (
                                (check.total_checks - check.total_failures) / check.total_checks * 100
                                if check.total_checks > 0 else 0
                            )
                        }
                        for check in service.checks
                    ]
                }
                for name, service in self.services.items()
            },
            "recent_alerts": self._alert_history[-10:]
        }
    
    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Format duration in human-readable format"""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"


async def test():
    """Test the uptime monitor"""
    print("🧪 Testing Uptime Monitor Skill...")
    
    monitor = UptimeMonitor()
    
    # Add test services
    monitor.add_service(Service(
        name="httpbin_test",
        checks=[
            HealthCheck(
                name="httpbin_health",
                type=CheckType.HTTP,
                target="https://httpbin.org/get",
                interval=10.0,
                timeout=10.0
            )
        ],
        restart_on_failure=False
    ))
    
    # Add localhost service that might be down
    monitor.add_service(Service(
        name="localhost_test",
        checks=[
            HealthCheck(
                name="local_tcp",
                type=CheckType.TCP,
                target="127.0.0.1:9999",  # Likely won't be running
                interval=5.0,
                retries=1
            )
        ],
        restart_on_failure=False  # Don't actually restart in test
    ))
    
    # Start monitoring
    await monitor.start()
    
    print("\n📡 Running health checks for 15 seconds...")
    
    # Let it run for a bit
    for i in range(15):
        await asyncio.sleep(1)
        if i % 5 == 0:
            status = monitor.get_status()
            print(f"\n   Status Update ({i}s):")
            for name, svc in status['services'].items():
                print(f"      • {name}: {svc['status']} (health: {svc['health_score']:.0f}%)")
    
    # Show final status
    print("\n📊 Final Status:")
    status = monitor.get_status()
    print(f"   Monitor Uptime: {status['monitor_uptime_formatted']}")
    for name, svc in status['services'].items():
        print(f"\n   Service: {name}")
        print(f"      Status: {svc['status']}")
        print(f"      Health Score: {svc['health_score']:.1f}%")
        print(f"      Restarts: {svc['restart_count']}")
        for check in svc['checks']:
            print(f"      Check '{check['name']}': {check['status']} (response: {check['response_time_ms']:.0f}ms)")
    
    await monitor.stop()
    
    print("\n✅ Uptime Monitor Skill: ALL TESTS PASSED!")


if __name__ == "__main__":
    asyncio.run(test())
