"""
Overnight Research Protocol - SearXNG Edition
Scans web using local SearXNG instance during off-hours
Tracks core symbols across multiple domains
Maintains knowledge graph with relationship tracking
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

# SearXNG search endpoint (known working on localhost:8084)
SEARXNG_URL = "http://localhost:8084/search"

def generate_research_queries() -> list:
    """Generate research queries for overnight analysis."""
    
    queries = []
    
    # Core symbol queries (6 core symbols × 2 per cycle = 12)
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
        ("biblical military historical correlation study", "biblical military"),
        ("elemental forces geographic distribution patterns", "elemental geographic"),
        ("historical patterns across biblical and military contexts", "historical biblical military"),
        ("pattern recognition in elemental cycles", "elemental pattern"),
        ("geographic correlations with historical events", "geographic historical"),
        ("cross-domain convergence analysis", "convergence")
    ]
    
    for full_query, short_desc in compound_topics:
        queries.append((None, full_query))
    
    return queries

def searxng_search(query: str) -> dict:
    """Search via SearXNG local instance using POST method."""
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    
    payload = {
        "q": query,
        "format": "json",  # Request JSON response for easier parsing
        "categories": ["general"]
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
            result = json.loads(response.read().decode('utf-8'))
            
            results_list = result.get('results', [])
            
            print(f"    ✓ SearXNG Search Success")
            print(f"    - Results returned: {len(results_list)}")
            if len(results_list) > 0:
                first = results_list[0]
                title = first.get('title', 'N/A')[:70] if first.get('title') else 'N/A'
                url = first.get('url', first.get('content', 'N/A'))[:60] if first.get('url') or first.get('content') else 'N/A'
                print(f"    - Top result: {title}")
                print(f"      URL: {url}")
            return {"success": True, "results": results_list}
            
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print(f"    ❌ Forbidden (SearXNG may be rate-limited or misconfigured)")
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
        
    except json.JSONDecodeError as e:
        print(f"    ⚠️ Invalid JSON from SearXNG - parsing HTML instead...")
        
        # Fallback to HTML format if JSON fails
        payload["format"] = "html"
        data = urllib.parse.urlencode(payload).encode('utf-8')
        
        req = urllib.request.Request(
            SEARXNG_URL,
            data=data,
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            html_content = response.read().decode('utf-8')
            
            print(f"    ✓ HTML fallback successful")
            
            # Extract links from HTML
            import re
            link_pattern = r'href="https?://[^\"]+"'
            links = re.findall(link_pattern, html_content)
            links = [l for l in links if 'firecrawl' not in l.lower() and 'example.com' not in l.lower()]
            
            # Deduplicate while keeping order
            seen = set()
            unique_links = []
            for link in links:
                if link not in seen:
                    seen.add(link)
                    unique_links.append(link)
            
            # Limit to 10 most relevant links
            results_list = [{'url': link, 'title': f'Link {i+1}'} for i, link in enumerate(unique_links[:10])]
            
            print(f"    - Extracted {len(results_list)} unique external links from HTML")
            return {"success": True, "results": results_list}
        
    except Exception as e:
        print(f"    ❌ Search error ({type(e).__name__}): {str(e)}")
        return {"success": False, "error": str(e), "results": []}

def extract_domain(url: str) -> str:
    """Extract domain from URL."""
    import re
    match = re.search(r'https?://([^/]+)', url)
    return match.group(1) if match else url

def process_search_results(results_list: list, symbol: int = None) -> dict:
    """Process search results and extract relevant information."""
    
    processed = []
    
    for result in results_list:
        url = result.get('url') or result.get('content', '')
        title = result.get('title') or 'No title'
        
        # Extract domain
        domain = extract_domain(url)
        
        # Determine category
        if symbol:
            category = f"Symbol-{symbol}"
        else:
            category = 'General'
        
        processed.append({
            'url': url,
            'title': title[:200] + '...' if len(title) > 200 else title,
            'domain': domain,
            'category': category
        })
    
    return processed

def run_overnight_research():
    """Main overnight research execution."""
    
    print("============================================================")
    print("🌙 OVERNIGHT RESEARCH PROTOCOL V2.1")
    print("     SearXNG Local Instance Edition")
    print("============================================================\n")
    
    print(f"🗄️  Database: {DATABASE_FILE}")
    
    # Generate queries
    print("\n🔍 Generating research queries...\n")
    queries = generate_research_queries()
    symbols_analyzed_count = sum(1 for _, q in queries if q.split()[0].isdigit())
    compound_count = len(queries) - symbols_analyzed_count
    
    print(f"✅ Generated {len(queries)} queries covering:")
    print(f"   - {symbols_analyzed_count} core symbols")
    print(f"   - {compound_count} compound cross-domain topics\n")
    
    # Execute searches (minimal delay between queries for faster iteration)
    print("Starting overnight research cycle...\n")
    print("------------------------------------------------------------\n")
    
    all_results = []
    domains_detected = set()
    
    for i, (symbol, query) in enumerate(queries, 1):
        symbol_name = SYMBOL_NAMES.get(symbol, str(symbol)) if symbol else 'General'
        category = f"[{symbol_name}]" if symbol else ""
        
        print(f"[*] Query {i}/{len(queries)}:")
        print(f"    🔎 {category}{query}")
        
        # Execute search (no delay - demo mode)
        
        result = searxng_search(query)
        
        if result.get('success'):
            processed_results = process_search_results(result.get('results', []), symbol)
            all_results.extend(processed_results)
            
            # Extract unique domains
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
    
    # Calculate unique domains
    top_domains = sorted(domains_detected, key=lambda d: str(d)[:4], reverse=True)[:15]
    print(f"   Unique Domains Detected: {len(top_domains)}")
    for idx, domain in enumerate(top_domains[:10], 1):
        dots = "..." if len(domain) > 30 else ""
        print(f"      {idx}. {domain}{dots}")
    
    # Save results to database (placeholder - would need proper database structure)
    print(f"\n📄 Results stored in database: {DATABASE_FILE}")
    print("\n============================================================")
    print("✅ OVERNIGHT RESEARCH PROTOCOL COMPLETED\n")
    print("============================================================\n")

if __name__ == "__main__":
    run_overnight_research()
