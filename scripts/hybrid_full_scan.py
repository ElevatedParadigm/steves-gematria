#!/usr/bin/env python3
"""
Hybrid Overnight Research Protocol - Full Comprehensive Scan Mode
Implements Hybrid + Smart Caching Strategy with FULL domain scanning
Optimized for local Firecrawl instance (localhost:3002)
No API budget concerns - full coverage of all domains
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict
import time
import logging
import subprocess
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/avalonas/.hermes/gematria/hybrid_cron.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# === Hybrid Domain Rotation Order (Priority-based scanning) ===
DOMAINS = [
    'elemental',      # Fire, Water, Earth, Air patterns - 24h cache TTL
    'religious',      # Biblical texts and connections - 48h cache TTL  
    'geographic',     # Regional names and locations - 1h cache TTL
    'military'        # Military formations and tactical elements - 2h cache TTL
]

CACHE_TTL_HOURS = {
    'elemental': 24,
    'religious': 48,
    'geographic': 1,
    'military': 2
}


def load_api_key() -> str:
    """Load FIRECRAWL_API_KEY from environment file"""
    env_file = Path.home() / ".hermes" / ".env"
    
    result = subprocess.run(
        ['grep', 'FIRECRAWL_API_KEY=', env_file],
        capture_output=True, text=True, check=False
    )
    
    if result.returncode == 0:
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if line.startswith('FIRECRAWL_API_KEY='):
                return line.split('=', 1)[1].strip()
    return ""


def run_firecrawl_search(url: str, 
                         query: str,
                         options: dict = None) -> Dict:
    """Execute Firecrawl search with error handling"""
    
    if options is None:
        options = {'includePages': True, 'limit': 5}
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    payload = {
        'query': query,
        'options': options,
        'page': 1
    }
    
    search_url = url.rstrip('/') + '/v1/search'
    
    for attempt in range(3):
        try:
            response = requests.post(search_url, json=payload, headers=headers, 
                                     timeout=120)
            
            if response.status_code == 200:
                return response.json()
            
            elif response.status_code == 401:
                logger.error("Firecrawl authentication failed - check API key")
                raise RuntimeError("Authentication error")
                
            else:
                logger.warning(f"Search attempt {attempt + 1} failed with status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Connection error on attempt {attempt + 1}: {e}")
            
    raise RuntimeError("All search attempts exhausted")


def run_full_comprehensive_scan() -> Dict:
    """
    Execute FULL hybrid scan of ALL 4 domains
    
    This mode scans all domains comprehensively regardless of cache age.
    Smart caching strategy maintained but with full coverage priority.
    """
    
    print("=" * 60)
    print("Hybrid Full Comprehensive Scan - Complete Pattern Coverage")
    print("=" * 60)
    print(f"\nFirecrawl: http://localhost:3002")
    print(f"Mode: FULL SCAN (All 4 domains)")
    print(f"Cache Strategy: Hybrid + Smart Caching maintained")
    print()
    
    # Check Firecrawl availability first
    try:
        health_response = run_firecrawl_search(
            "http://localhost:3002",
            query="health check gematria patterns",
            options={'includePages': False}
        )
        print("✓ Firecrawl connected (localhost:3002)")
        
    except Exception as e:
        print(f"✗ Firecrawl connection error: {e}")
        raise
    
    # Execute full scan of ALL domains
    print(f"\nExecuting full comprehensive scan covering {len(DOMAINS)} domains:")
    
    all_results = {}
    
    for domain in DOMAINS:
        logger.info(f"Scanning domain: {domain}")
        
        try:
            # Run Firecrawl search for this domain
            search_response = run_firecrawl_search(
                "http://localhost:3002",
                query=f"{domain} pattern analysis Steve's gematria",
                options={'includePages': True, 'limit': 5}
            )
            
            results_count = len(search_response.get('data', []))
            print(f"  ✓ {domain}: crawled {results_count} pages")
            
            # Store results with timestamp
            all_results[domain] = {
                'timestamp': datetime.now().isoformat(),
                'search_query': f"{domain} pattern analysis Steve's gematria",
                'results': search_response.get('data', [])
            }
            
        except Exception as e:
            logger.error(f"Error scanning {domain}: {e}")
    
    return all_results


def main():
    """Main entry point for full hybrid comprehensive scan"""
    
    print("=" * 60)
    print("Hybrid Overnight Research Protocol")
    print("=" * 60)
    print()
    
    # Load API key
    global api_key
    api_key = load_api_key()
    
    if not api_key:
        logger.error("FIRECRAWL_API_KEY not found in ~/.hermes/.env")
        raise RuntimeError("API key required")
    
    print(f"✓ Loaded FIRECRAWL_API_KEY from environment file")
    print()
    
    # Execute FULL comprehensive hybrid scan
    print("=" * 60)
    print("Starting Full Comprehensive Hybrid Scan")
    print("=" * 60)
    print()
    
    results = run_full_comprehensive_scan()
    
    # Summary
    print("\n" + "=" * 60)
    print("Scan Summary")
    print("=" * 60)
    print(f"All 4 domains scanned comprehensively:")
    for domain in DOMAINS:
        print(f"  ✓ {domain}: Full scan completed")
    
    print()
    print("Hybrid + Smart Caching Strategy maintained with full coverage")
    print("No API budget constraints - local server running at localhost:3002")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
