#!/usr/bin/env python3
import requests

print("="*60)
print("Firecrawl API Test")
print("="*60)

try:
    r = requests.post(
        'http://localhost:3002/search',
        json={'query': 'gematria patterns'},
        timeout=15
    )
    
    print(f"\nStatus Code: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        results_count = len(data.get('data', []))
        print(f"✅ SUCCESS - Found {results_count} results")
        if data.get('data'):
            first = data['data'][0]
            print(f"\nFirst result preview:")
            for key in ['url', 'title'][:2]:
                if key in first:
                    val = str(first[key])[:80]
                    print(f"  {key}: {val}")
    else:
        print(f"Response: {r.text[:300]}")
        
except requests.exceptions.ConnectionError as e:
    print(f"⚠️ Connection error: {str(e)[:60]}")
except Exception as e:
    print(f"✗ Error: {str(e)[:80]}")

print("\n" + "="*60)
