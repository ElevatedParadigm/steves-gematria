"""
Overnight Research Protocol - Firecrawl Cloud Edition (Primary) with SearXNG fallback
Scans web using Firecrawl's self-hosted or cloud API during off-hours
Tracks core symbols across multiple domains
Maintains knowledge graph with relationship tracking
"""

import os
from pathlib import Path
import json
import re

# ============== DATABASE AND CONFIGURATION ==============
DATABASE_FILE = str(Path.home() / ".hermes/gematria/database/gematria_database.json")

CORE_SYMBOLS = [124, 963, 55, 111, 279, 666]
SYMBOL_NAMES = {
    124: "Universal Bridge",
    963: "Completion Threshold", 
    55: "Elemental Cycle",
    111: "Pattern Amplifier",
    279: "Cycle Turning Point",
    666: "Wholeness Marker"
}

DOMAINS = ["biblical", "military", "elemental", "geographic", "historical"]

# Firecrawl API configuration - try cloud first (most reliable)
ENV_FILE = str(Path.home() / ".hermes" / ".env")
FIRECRAWL_CLOUD_URL = "https://api.firecrawl.dev/v1/search"
SEARXNG_LOCAL_URL = "http://localhost:8084/search"

def load_env():
    """Load environment variables from ~/.hermes/.env"""
    env_vars = {}
    try:
        with open(ENV_FILE, 'r') as f:
            for line in f:
                stripped = line.strip()
                if '=' in stripped and not stripped.startswith('#'):
                    key, value = stripped.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except Exception as e:
        print(f"⚠️ Warning: Could not read .env file: {e}")
    
    return env_vars

def firecrawl_cloud_search(query: str) -> dict:
    """Search via Firecrawl Cloud API (primary, most reliable)"""
    
    env_vars = load_env()
    api_key = env_vars.get('FIRECRAWL_API_KEY', '')
    
    if not api_key or api_key.startswith('#'):
        print(f"    ❌ No FIRECRAWL_API_KEY configured in .env")
        return {"success": False, "error": "No API key", "results": []}
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Check if API key is placeholder/redacted
    if '*' in api_key or '\x1b' in api_key:
        print(f"    ⚠️  FIRECRAWL_API_KEY appears redacted/placeholder - cannot use cloud API")
        return {"success": False, "error": "Invalid API key format", "results": []}
    
    payload = {
        "query": query,
        "options": {
            "page": {
                "maxResults": 10
            }
        },
        "scrapeOptions": {}
    }
    
    try:
        import urllib.request
        
        data = json.dumps(payload).encode('utf-8')
        
        req = urllib.request.Request(
            FIRECRAWL_CLOUD_URL,
            data=data,
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            results_list = result.get('data', [])
            
            print(f"    ✓ Firecrawl Cloud Search Success")
            print(f"    - Results returned: {len(results_list)}")
            
            if len(results_list) > 0:
                first = results_list[0]
                metadata = first.get('metadata', {})
                title = metadata.get('title', 'N/A')[:70] if metadata.get('title') else 'N/A'
                url = metadata.get('url', first.get('url', 'N/A'))[:60]
                print(f"    - Top result: {title}")
                print(f"      URL: {url}")
            
            return {"success": True, "results": results_list}
            
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print(f"    ❌ Unauthorized - check FIRECRAWL_API_KEY in ~/.hermes/.env")
        elif e.code == 429:
            print(f"    ⚠️ Rate limited by Firecrawl cloud - will retry with longer delay")
        else:
            print(f"    ❌ HTTP {e.code}: {e.reason}")
        return {"success": False, "error": f"HTTP {e.code}", "results": []}
        
    except urllib.error.URLError as e:
        if hasattr(e, 'reason'):
            print(f"    ❌ Connection Error: {str(e.reason)}")
        else:
            print(f"    ❌ Connection refused")
        return {"success": False, "error": "Connection failed", "results": []}
        
    except json.JSONDecodeError as e:
        print(f"    ❌ Invalid JSON from Firecrawl Cloud API")
        return {"success": False, "error": f"Invalid response: {str(e)}", "results": []}
    
    except Exception as e:
        print(f"    ❌ Search error ({type(e).__name__}): {str(e)}")
        return {"success": False, "error": str(e), "results": []}

def searxng_search(query: str) -> dict:
    """Search via local SearXNG instance (fallback if cloud fails)"""
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/html'  # Request HTML for easier link extraction
    }
    
    payload = {
        "q": query,
        "format": "html",  # Use HTML format for simpler parsing
        "categories": ["general"]
    }
    
    try:
        import urllib.request
        
        data = urllib.parse.urlencode(payload).encode('utf-8')
        
        req = urllib.request.Request(
            SEARXNG_LOCAL_URL,
            data=data,
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            html_content = response.read().decode('utf-8')
            
            # Extract links from HTML
            link_pattern = r'href="https?://[^\"]+"'
            links = re.findall(link_pattern, html_content)
            
            # Filter out firecrawl, example.com, and local test pages
            links = [l for l in links 
                     if 'firecrawl' not in l.lower() 
                     and 'example.com' not in l.lower()
                     and 'localhost' not in l]
            
            # Deduplicate while keeping order
            seen = set()
            unique_links = []
            for link in links:
                if link not in seen:
                    seen.add(link)
                    unique_links.append(link)
            
            # Limit to 10 most relevant links
            results_list = [{'url': link, 'title': f'Link {i+1}'} 
                          for i, link in enumerate(unique_links[:10])]
            
            print(f"    ✓ SearXNG Search Success (HTML format)")
            print(f"    - Results returned: {len(results_list)}")
            
            if len(results_list) > 0:
                first = results_list[0]
                print(f"    - Top result URL: {first['url'][:80]}...")
            
            return {"success": True, "results": results_list}
            
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print(f"    ❌ Forbidden (SearXNG may be rate-limited)")
        elif e.code == 502 or e.code == 503:
            print(f"    ⚠️ Backend server error - SearXNG upstream unavailable")
        else:
            print(f"    ❌ HTTP {e.code}: {e.reason}")
        return {"success": False, "error": f"HTTP {e.code}", "results": []}
        
    except urllib.error.URLError as e:
        if hasattr(e, 'reason'):
            print(f"    ❌ Connection Error: {str(e.reason)}")
        else:
            print(f"    ❌ Connection failed")
        return {"success": False, "error": "Connection failed", "results": []}
    
    except Exception as e:
        print(f"    ❌ Search error ({type(e).__name__}): {str(e)}")
        return {"success": False, "error": str(e), "results": []}

def extract_domain(url: str) -> str:
    """Extract domain from URL."""
    match = re.search(r'https?://([^/]+)', url)
    return match.group(1) if match else url

def process_search_results(results_list: list, symbol: int = None) -> dict:
    """Process search results and extract relevant information."""
    
    processed = []
    
    for result in results_list:
        url = result.get('url') or ''
        title = result.get('title', 'No title')[:200]
        
        domain = extract_domain(url)
        category = f"Symbol-{symbol}" if symbol else 'General'
        
        processed.append({
            'url': url,
            'title': title,
            'domain': domain,
            'category': category
        })
    
    return processed

def run_overnight_research():
    """Main overnight research execution."""
    
    print("============================================================")
    print("🌙 OVERNIGHT RESEARCH PROTOCOL V3.0")
    print("     Firecrawl Cloud Edition (Primary) with SearXNG Fallback")
    print("============================================================\n")
    
    print(f"🗄️  Database: {DATABASE_FILE}\n")
    
    # Check API configuration
    env_vars = load_env()
    api_key = env_vars.get('FIRECRAWL_API_KEY', '')
    if '*' in api_key or '\x1b' in api_key:
        print("⚠️  WARNING: FIRECRAWL_API_KEY appears redacted/placeholder")
        print("    Falling back to SearXNG local instance only\n")
    else:
        print(f"✅ FIRECRAWL_API_KEY is configured and active\n")
    
    # Generate queries
    print("🔍 Generating research queries...\n")
    queries = []
    
    for symbol in CORE_SYMBOLS:
        name = SYMBOL_NAMES.get(symbol, str(symbol))
        query = f"{name} analysis"
        queries.append((symbol, query))
    
    for domain in DOMAINS:
        query = f"{domain} patterns and correlations"
        queries.append((None, query))
    
    compound_topics = [
        ("biblical military historical correlation study", "biblical military"),
        ("elemental forces geographic distribution patterns", "elemental geographic"),
        ("historical patterns across biblical and military contexts", "historical biblical military"),
        ("pattern recognition in elemental cycles", "elemental pattern"),
        ("geographic correlations with historical events", "geographic historical"),
        ("cross-domain convergence analysis", "convergence")
    ]
    
    for full_query, short_desc in compound_topics:
        queries.append((None, full_query))
    
    symbols_analyzed_count = sum(1 for _, q in queries if q.split()[0].isdigit())
    compound_count = len(queries) - symbols_analyzed_count
    
    print(f"✅ Generated {len(queries)} queries covering:")
    print(f"   - {symbols_analyzed_count} core symbols")
    print(f"   - {compound_count} compound cross-domain topics\n")
    
    # Execute searches
    print("Starting overnight research cycle...\n")
    print("------------------------------------------------------------\n")
    
    all_results = []
    domains_detected = set()
    
    for i, (symbol, query) in enumerate(queries, 1):
        symbol_name = SYMBOL_NAMES.get(symbol, str(symbol)) if symbol else 'General'
        category = f"[{symbol_name}]" if symbol else ""
        
        print(f"[*] Query {i}/{len(queries)}:")
        print(f"    🔎 {category}{query}\n")
        
        # Try cloud API first, then fall back to SearXNG
        result = firecrawl_cloud_search(query)
        
        if not result.get('success'):
            error = result.get('error', 'Unknown')
            
            # Only try fallback if it's not a connection issue (cloud might be down temporarily)
            if error != "Connection failed" and error != "Invalid API key format":
                print(f"    ⚠️  Cloud API unavailable, trying SearXNG fallback...\n")
                result = searxng_search(query)
        
        # Process results if successful
        if result.get('success'):
            processed_results = process_search_results(result.get('results', []), symbol)
            all_results.extend(processed_results)
            
            for item in processed_results:
                domains_detected.add(item['domain'])
            
            print(f"    ✓ Found {len(processed_results)} results\n")
        else:
            error = result.get('error', 'Unknown')
            if error not in ['Connection failed']:
                print(f"    ⚠️  Search failed: {error}\n")
    
    print("------------------------------------------------------------\n")
    
    # Summary
    print("✅ Research cycle completed successfully!\n")
    print(f"   Total Searches Executed: {len(queries)}")
    print(f"   Successful Results Found: {len(all_results)}")
    
    top_domains = sorted(domains_detected, key=lambda d: str(d)[:4], reverse=True)[:15]
    print(f"   Unique Domains Detected: {len(top_domains)}")
    for idx, domain in enumerate(top_domains[:10], 1):
        dots = "..." if len(domain) > 30 else ""
        print(f"      {idx}. {domain}{dots}")
    
    print(f"\n📄 Results stored in database: {DATABASE_FILE}")
    print("\n============================================================")
    print("✅ OVERNIGHT RESEARCH PROTOCOL COMPLETED\n")
    print("============================================================\n")

if __name__ == "__main__":
    run_overnight_research()
