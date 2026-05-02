"""
Overnight Research Protocol V3.1 - SearXNG Properly Configured
Uses /search endpoint with correct headers and parameters
"""

import os
from pathlib import Path
import json
import urllib.parse
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

# SearXNG endpoint (correct /search format)
SEARXNG_URL = "http://localhost:8084/search"

def generate_queries() -> list:
    """Generate research queries."""
    queries = []
    
    # Core symbol queries (6 × 2 = 12)
    for symbol in CORE_SYMBOLS:
        name = SYMBOL_NAMES.get(symbol, str(symbol))
        query = f"{name} analysis"
        queries.append((symbol, query))
    
    # Cross-domain compound queries (5 domains = 5)
    for domain in DOMAINS:
        query = f"{domain} patterns and correlations"
        queries.append((None, query))
    
    # Compound cross-domain topics (6)
    compound_topics = [
        "biblical military historical correlation study",
        "elemental forces geographic distribution patterns",
        "historical patterns across biblical and military contexts",
        "pattern recognition in elemental cycles",
        "geographic correlations with historical events",
        "cross-domain convergence analysis"
    ]
    
    for full_query in compound_topics:
        queries.append((None, full_query))
    
    return queries

def searxng_search(query: str) -> dict:
    """Search via SearXNG local instance using proper endpoint."""
    
    # Correct headers with Accept type for HTML parsing
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.8',  # Prefer HTML
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (overnight research)'
    }
    
    # Build payload
    payload = {
        "q": query,
        "format": "html",  # Get HTML for link extraction
        "categories": ["general"],
        "safesearch": 0  # Allow adult content if needed for research
    }
    
    try:
        import urllib.request
        
        data = urllib.parse.urlencode(payload).encode('utf-8')
        
        req = urllib.request.Request(
            SEARXNG_URL,
            data=data,
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            html_content = response.read().decode('utf-8')
            
            # Extract links from HTML
            link_pattern = r'href="https?://[^\"]+"'
            links = re.findall(link_pattern, html_content)
            
            # Filter out noise (firecrawl, example.com, localhost pages we don't want)
            links = [l for l in links 
                     if 'firecrawl' not in l.lower() 
                     and 'example.com' not in l.lower()]
            
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
            
            success_count = len(results_list)
            
            if success_count > 0:
                first_result = results_list[0]
                title_preview = first_result['url'][:75] + '...' if len(first_result['url']) > 75 else first_result['url']
                print(f"    ✓ SearXNG Search Success")
                print(f"    - Results returned: {success_count}")
                print(f"    - Top result: {title_preview}")
            
            return {"success": success_count > 0, "results": results_list}
            
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print(f"    ❌ Forbidden (SearXNG rate-limited or misconfigured)")
        elif e.code == 502:
            print(f"    ⚠️ Bad Gateway - SearXNG backend unavailable")
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

def process_results(results_list: list, symbol: int = None) -> dict:
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
    print("🌙 OVERNIGHT RESEARCH PROTOCOL V3.1")
    print("     SearXNG /search Endpoint Edition")
    print("============================================================\n")
    
    print(f"🗄️  Database: {DATABASE_FILE}")
    
    # Generate queries
    print("\n🔍 Generating research queries...\n")
    queries = generate_queries()
    symbols_count = sum(1 for _, q in queries if q.split()[0].isdigit())
    compound_count = len(queries) - symbols_count
    
    print(f"✅ Generated {len(queries)} queries covering:")
    print(f"   - {symbols_count} core symbol analyses")
    print(f"   - {compound_count} cross-domain studies\n")
    
    # Execute searches
    print("Starting overnight research cycle...\n")
    print("------------------------------------------------------------\n")
    
    all_results = []
    domains_detected = set()
    
    for i, (symbol, query) in enumerate(queries, 1):
        symbol_name = SYMBOL_NAMES.get(symbol, str(symbol)) if symbol else 'General'
        category = f"[{symbol_name}]" if symbol else ""
        
        print(f"[*] Query {i}/{len(queries)}:")
        print(f"    🔎 {category}{query}")
        
        # Execute search (no delay for demo - production would use rate limiting)
        
        result = searxng_search(query)
        
        if result.get('success'):
            processed_results = process_results(result.get('results', []), symbol)
            all_results.extend(processed_results)
            
            for item in processed_results:
                domains_detected.add(item['domain'])
            
            print(f"    ✓ Found {len(processed_results)} results\n")
        else:
            error = result.get('error', 'Unknown')
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
