#!/usr/bin/env python3
"""
🌍 SIMPLE WEB SCANNER FOR GEMATRIA PATTERNS
Direct HTTP-based scanner without Firecrawl dependency.
Tests specific target URLs for gematria encoding patterns.
"""

import requests
from datetime import datetime
import json

TARGET_URLS = [
    "https://en.wikipedia.org/wiki/Adolf_Hitler",  # Known memorialization site
    "https://www.forbes.com/sites/analyticsinsight",
    "https://brainforge.ai/",
]

# Core symbols to search for
SYMBOLS = [124, 55, 666, 963, 279]

def scan_url(url):
    """Scan a URL for gematria patterns."""
    try:
        headers = {'User-Agent': 'GematriaScanner/1.0'}
        response = requests.get(url, headers=headers, timeout=15)
        
        # Look for known pattern strings
        found_patterns = []
        symbol_texts = {
            124: "Universal Threshold Bridge",
            55: "Life Cycle Completion", 
            666: "Completion Code",
            963: "Integration Cycle"
        }
        
        # Search for text containing our symbols
        for symbol, text in symbol_texts.items():
            if text.lower() in response.text.lower():
                found_patterns.append(text)
        
        return {
            'url': url,
            'status': response.status_code,
            'patterns_found': found_patterns,
            'scan_time': datetime.now().isoformat()
        }
    except Exception as e:
        return {'url': url, 'error': str(e)}

def main():
    print("🌍 SIMPLE WEB SCANNER - GEMATRIA PATTERNS")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    for url in TARGET_URLS:
        print(f"\nScanning: {url}")
        result = scan_url(url)
        results.append(result)
        
        if result.get('status') == 200:
            patterns = result.get('patterns_found', [])
            if patterns:
                print(f"   ✅ Found patterns: {', '.join(patterns)}")
            else:
                print(f"   ℹ️  No known gematria patterns detected")
        else:
            print(f"   ❌ Status: {result.get('status')}")
    
    # Save results to database
    DB_PATH = "/home/avalonas/.hermes/gematria/simple_scan_results.json"
    with open(DB_PATH, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📊 Scan complete! Results saved to:")
    print(f"   {DB_PATH}")

if __name__ == "__main__":
    main()
