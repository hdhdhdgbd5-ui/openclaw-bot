"""
OMNIGENIUS - Module 1: Violation Hunter
Scans corporate websites for legal violations (hidden fees, GDPR, ToS)
Uses stealth browser automation
"""

import os
import json
import re
from datetime import datetime
from typing import List, Dict

# Violation patterns to search for
VIOLATION_PATTERNS = {
    "hidden_fees": [
        r"\$[0-9,]+(\.[0-9]{2})?\s*(fee|charge|service|admin)",
        r"activation\s*fee",
        r"setup\s*fee",
        r"cancellation\s*fee",
        r"early\s*termination",
        r"non[- ]?refundable",
        r"convenience\s*fee",
    ],
    "gdpr_violations": [
        r"we\s*may\s*sell\s*your\s*data",
        r"share\s*your\s*information\s*with\s*partners",
        r"marketing\s*purposes",
        r"third[- ]?party\s*advertisers",
        r"tracking\s*technologies",
        r"cookies\s*for\s*advertising",
    ],
    "tos_violations": [
        r"we\s*can\s*change\s*terms\s*without\s*notice",
        r"arbitration\s*waiver",
        r"class\s*action\s*waiver",
        r"sole\s*discretion",
        r"no\s*warranty",
        r"as\s*is\s*basis",
    ]
}

# Target industries to scan
TARGET_INDUSTRIES = [
    {"name": "Insurance", "keywords": ["insurance", "policy", "claim"]},
    {"name": "Banking", "keywords": ["bank", "financial", "account"]},
    {"name": "Telecom", "keywords": ["telecom", "mobile", "wireless", "internet"]},
    {"name": "Subscription Services", "keywords": ["subscription", "membership", "streaming"]},
]


class ViolationHunter:
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or "PRODUCTS/OmniGenius/logs"
        self.findings = []
        os.makedirs(self.output_dir, exist_ok=True)
        
    def scan_website(self, url: str, company_name: str) -> List[Dict]:
        """Scan a single website for violations using stealth browser"""
        findings = []
        
        try:
            from browser import browser
            
            # Use stealth browser to fetch page content
            response = browser(action="snapshot", targetUrl=url)
            
            if response and "text" in response:
                content = response["text"].lower()
                
                # Check each violation category
                for category, patterns in VIOLATION_PATTERNS.items():
                    for pattern in patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            findings.append({
                                "company": company_name,
                                "url": url,
                                "category": category,
                                "pattern": pattern,
                                "matches": matches[:3],  # Limit matches
                                "severity": self._assess_severity(category),
                                "timestamp": datetime.now().isoformat()
                            })
                            
        except Exception as e:
            print(f"[ViolationHunter] Error scanning {url}: {e}")
            
        return findings
    
    def _assess_severity(self, category: str) -> str:
        """Assess violation severity"""
        severity_map = {
            "hidden_fees": "HIGH",
            "gdpr_violations": "MEDIUM", 
            "tos_violations": "LOW"
        }
        return severity_map.get(category, "UNKNOWN")
    
    def log_findings(self, findings: List[Dict] = None):
        """Log findings to file"""
        if findings is None:
            findings = self.findings
            
        if not findings:
            print("[ViolationHunter] No findings to log")
            return
            
        log_file = os.path.join(self.output_dir, f"violations_{datetime.now().strftime('%Y%m%d')}.json")
        
        with open(log_file, 'a') as f:
            for finding in findings:
                f.write(json.dumps(finding) + "\n")
                
        print(f"[ViolationHunter] Logged {len(findings)} findings to {log_file}")
        return log_file
    
    def run_scan(self, companies: List[Dict] = None):
        """Run full violation scan"""
        if companies is None:
            # Default test companies
            companies = [
                {"name": "MegaBank Corp", "url": "https://www.example-bank.com/terms"},
                {"name": "StreamFast TV", "url": "https://www.example-stream.com/pricing"},
            ]
            
        print(f"[ViolationHunter] Starting scan of {len(companies)} companies...")
        
        for company in companies:
            print(f"  Scanning: {company['name']}")
            results = self.scan_website(company["url"], company["name"])
            self.findings.extend(results)
            
        self.log_findings()
        print(f"[ViolationHunter] Scan complete. Found {len(self.findings)} violations.")
        return self.findings


if __name__ == "__main__":
    hunter = ViolationHunter()
    hunter.run_scan()
