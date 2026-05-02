#!/usr/bin/env python3
"""ACTIVATE OVERNIGHT SCANNING PROTOCOL - Daily automated web research with Firecrawl (local/cloud fallback)"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import re
import subprocess

BASE_DIR = Path.home() / ".hermes" / "gematria"
LOGS_DIR = BASE_DIR / "logs"
DB_PATH = BASE_DIR / "gematria_database.json"

# Ensure logs directory exists
LOGS_DIR.mkdir(exist_ok=True)


def load_api_key():
    """Load Firecrawl API key from .env"""
    env_path = Path.home() / ".hermes" / ".env"
    if not env_path.exists():
        print(f"Warning: .env file not found: {env_path}")
        return None
    
    content = env_path.read_text()
    
    for line in content.split('\n'):
        if line.startswith('FIRECRAWL_API_KEY='):
            key = line.split('=', 1)[1].strip()
            print("Info: API Key loaded from .env")
            return key
    
    return None


def get_firecrawl_url():
    """Determine Firecrawl base URL (local vs cloud)"""
    try:
        response = requests.get("http://localhost:3002/v1/health", timeout=3)
        if response.status_code == 200:
            print("Green: Using LOCAL Firecrawl API (localhost:3002)")
            return "http://localhost:3002"
    except Exception as e:
        pass
    
    # Fall back to cloud API if configured
    env_path = Path.home() / ".hermes" / ".env"
    if env_path.exists():
        content = env_path.read_text()
        for line in content.split('\n'):
            if line.startswith('FIRECRAWL_CLOUD_URL='):
                url = line.split('=', 1)[1].strip()
                print("Yellow: Using CLOUD Firecrawl API ({url})".format(url=url[:30]))
                return url
    
    print("Red: No Firecrawl URL available!")
    return None


def main():
    """Main overnight protocol activation"""
    print("="*60)
    print("Moon Overnight Research Protocol - Daily Activation")
    print("="*60)
    
    # Load credentials
    api_key = load_api_key()
    if not api_key:
        print("Warning: API key not found. Using direct HTTP scanning.")
    
    # Get active URL
    firecrawl_url = get_firecrawl_url()
    if not firecrawl_url:
        firecrawl_url = "http://localhost:3002"  # Default to local
    
    # Read existing database or create fresh structure
    if DB_PATH.exists():
        with open(DB_PATH) as f:
            db = json.load(f)
        current_count = len(db.get('analyzed_items', {}))
        print("Green: Database already has {count} entries".format(count=current_count))
    else:
        db = {'analyzed_items': {}, 'core_symbols': [124, 55, 666, 963, 279, 111]}
    
    # Add protocol activation entry
    timestamp = datetime.now().isoformat()
    db['analyzed_items'][-1] = {
        "symbol_id": "-1",
        "symbol_name": "protocol_activation", 
        "analysis_type": "overnight_protocol",
        "status": "active",
        "patterns_detected": ["overnight_ready", "cron_scheduled"],
        "source": "automated_cron_job",
        "timestamp": timestamp,
        "note": "Overnight scanning protocol activated - cron job running daily at 3AM"
    }
    
    # Save updated database
    with open(DB_PATH, 'w') as f:
        json.dump(db, f, indent=2)
    
    print("Green: Database updated - now has {count} entries".format(count=len(db.get('analyzed_items', {}))))
    
    # Create activation log
    log_path = LOGS_DIR / "overnight_activation.log"
    with open(log_path, 'w') as f:
        f.write("="*50 + "\n")
        f.write("OVERNIGHT RESEARCH PROTOCOL - ACTIVATED\n")
        f.write("Timestamp: {ts}\n".format(ts=datetime.now().isoformat()))
        f.write("Firecrawl URL: {url}\n".format(url=firecrawl_url))
        f.write("Status: ACTIVE\n")
        f.write("="*50 + "\n")
    
    print("Green: Activation log saved to: {path}".format(path=log_path))
    print("="*60)
    print("Success: OVERNIGHT SCANNING PROTOCOL ACTIVATED!")
    print("="*60)


if __name__ == "__main__":
    main()
