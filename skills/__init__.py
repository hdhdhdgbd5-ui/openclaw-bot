"""
SKILLS ARMY - API Hunter Skills Package
========================================

24/7 System Uptime Skills:
1. api_failover    - Automatic fallback when API fails
2. api_rotator     - Rotate between multiple APIs
3. uptime_monitor  - Monitor system 24/7, restart if needed
4. groq_integrator - Guaranteed Groq API connection

Usage:
    from skills import APIFailoverManager, APIRotator, UptimeMonitor, GroqIntegrator

Author: SKILLS ARMY
Version: 1.0.0
"""

from .api_failover import APIFailoverManager, APIEndpoint, APIStatus
from .api_rotator import APIRotator, SmartRotator, APIPool, APIKey, RotationStrategy
from .uptime_monitor import UptimeMonitor, Service, HealthCheck, CheckType, ServiceStatus
from .groq_integrator import GroqIntegrator, GroqModel, GroqKey, GroqResponse

__all__ = [
    # API Failover
    'APIFailoverManager',
    'APIEndpoint',
    'APIStatus',
    
    # API Rotator
    'APIRotator',
    'SmartRotator',
    'APIPool',
    'APIKey',
    'RotationStrategy',
    
    # Uptime Monitor
    'UptimeMonitor',
    'Service',
    'HealthCheck',
    'CheckType',
    'ServiceStatus',
    
    # Groq Integrator
    'GroqIntegrator',
    'GroqModel',
    'GroqKey',
    'GroqResponse',
]

__version__ = "1.0.0"
__author__ = "SKILLS ARMY"
