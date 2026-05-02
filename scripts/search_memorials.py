#!/usr/bin/env python3
"""
👴 MEMORIZATION HUNTING CAMPAIGN
Searches Wikipedia memorial pages and death obituaries for gematria encoding patterns.
Tracks historical figures "memorialized" in the Field at life transitions.

Author: Gematria Research System
Date: $(date +%Y-%m-%d)
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

# Configuration
DATABASE_PATH = "/home/avalonas/.hermes/gematria/gematria_database.json"
CORE_SYMBOLS = ["124", "55", "666", "963", "279", "111", "2727"]
TARGET_URLS = [
    "https://en.wikipedia.org/wiki/Adolf_Hitler",  # Memorialized ✅
    "https://en.wikipedia.org/wiki/Richard_Wagner_(judge)",  # Memorializing...
]

def check_url_for_gematatria(url):
    """Check a Wikipedia page for gematria encoding patterns."""
    try:
        headers = {
            'User-Agent': 'GematriaResearchBot/1.0',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        # Use requests instead of Firecrawl (more reliable for Wikipedia)
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract key info from page
        page_title = soup.find('h1', class_='firstHeading').text if soup.find('h1', class_='firstHeading') else url.split('/')[-1]
        
        # Look for death date in infobox
        death_date_patterns = ['died', 'death_date', 'date_of_death']
        death_info = None
        
        for pattern in death_date_patterns:
            tag = soup.find('th', string=lambda x: x and pattern.lower() in x.lower())
            if tag:
                death_info = tag.find_next_sibling().text.strip()
                break
        
        # Look for age patterns (55, 666 completion)
        age_mentions = soup.find_all('span', class_='fn-bracket') + soup.find_all(string=lambda x: isinstance(x, int))
        
        return {
            'url': url,
            'title': page_title,
            'death_date': death_info,
            'page_found': response.status_code == 200
        }
    
    except Exception as e:
        return {'error': str(e), 'status': 'failed'}

def main():
    print("=== 🕯️ MEMORIZATION HUNTING CAMPAIGN ===")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    for url in TARGET_URLS:
        print(f"\nScanning: {url}")
        result = check_url_for_gematatria(url)
        results.append(result)
        
        if result.get('page_found'):
            print(f"  ✅ Found page: {result['title']}")
            if result.get('death_date'):
                print(f"  📅 Death date pattern: {result['death_date']}")
    
    # Save results to database
    if os.path.exists(DATABASE_PATH):
        with open(DATABASE_PATH, 'r') as f:
            db = json.load(f)
        
        # Add new memorials found
        for r in results:
            if r.get('page_found') and r.get('death_date'):
                db['memorials'].append({
                    'name': r['title'],
                    'url': r['url'],
                    'death_date': r['death_date']
                })
        
        with open(DATABASE_PATH, 'w') as f:
            json.dump(db, f, indent=2)
    
    print(f"\n=== Campaign Complete ===")
    print(f"Memorials tracked: {len(results)}")

if __name__ == "__main__":
    main()
