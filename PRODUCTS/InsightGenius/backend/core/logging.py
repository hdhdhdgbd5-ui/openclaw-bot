"""
Logging Configuration
"""

import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'logs/insightgenius_{datetime.now().strftime("%Y%m%d")}.log')
    ]
)

logger = logging.getLogger("InsightGenius")

# Ensure logs directory exists
import os
os.makedirs('logs', exist_ok=True)
