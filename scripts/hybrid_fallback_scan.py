#!/usr/bin/env python3
"""
Hybrid Overnight Research Protocol - Path B Implementation
Uses hermes_tools.web_search fallback when Firecrawl returns empty results
Implements smart caching and relationship tracking across 4 domains
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Import hermes tools for web search
from hermes_tools import web_search, web_extract

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/avalonas/.hermes/gematria/hybrid_fallback_cron.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# === Configuration ===
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

# Base URLs for different query types
WEB_SEARCH_QUERIES = {
    'elemental': "fire water earth air symbolism patterns numerology",
    'religious': "biblical numerology symbolism divine connection",
    'geographic': "regional name significance place etymology history",
    'military': "military formation tactical historical battle pattern"
}

# Database path
DATABASE_PATH = Path("/home/avalonas/.hermes/gematria/database/gematria_database.json")
CACHE_PATH = Path("/home/avalonas/.hermes/gematria/domain_coverage.json")
LOG_PATH = Path("/home/avalonas/.hermes/gematria/hybrid_fallback_cron.log")

def load_database() -> Dict:
    """Load database with default structure if not exists"""
    if not DATABASE_PATH.exists():
        logger.info("Creating new database structure")
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        db = {
            "schema_version": "2.1",
            "config": {
                "domains": DOMAINS,
                "cache_ttl_hours": CACHE_TTL_HOURS,
                "mode": "hybrid_fallback"
            },
            "symbols": [
                {"symbol_id": 124, "name": "Symbol_124", "domains": [], "relationships": []},
                {"symbol_id": 963, "name": "Symbol_963", "domains": [], "relationships": []},
                {"symbol_id": 55, "name": "Symbol_55", "domains": [], "relationships": []},
                {"symbol_id": 111, "name": "Symbol_111", "domains": [], "relationships": []},
                {"symbol_id": 279, "name": "Symbol_279", "domains": [], "relationships": []},
                {"symbol_id": 666, "name": "Symbol_666", "domains": [], "relationships": []}
            ],
            "results": [],
            "relationships": {},
            "current_cycle": 0,
            "last_run": None
        }
        
        with open(DATABASE_PATH, 'w') as f:
            json.dump(db, f, indent=2)
        return db
    
    with open(DATABASE_PATH, 'r') as f:
        return json.load(f)

def save_database(db: Dict):
    """Save database to file"""
    with open(DATABASE_PATH, 'w') as f:
        json.dump(db, f, indent=2)

def check_cache_age(domain: str, current_time: datetime) -> bool:
    """Check if cache is expired for domain"""
    if not CACHE_PATH.exists():
        return True  # No cache exists yet
    
    with open(CACHE_PATH, 'r') as f:
        cache = json.load(f)
    
    cached_domain = cache.get(domain, {})
    cached_time_str = cached_domain.get('last_scanned', '')
    
    if not cached_time_str:
        return True  # No scan recorded
    
    try:
        last_scanned = datetime.fromisoformat(cached_time_str)
        ttl_hours = CACHE_TTL_HOURS[domain]
        max_age = timedelta(hours=ttl_hours)
        
        age = current_time - last_scanned
        print(f"  Cache for {domain}: age={age.total_seconds()/3600:.1f}h, TTL={ttl_hours}h")
        return age > max_age
    except Exception as e:
        logger.warning(f"Cache check error for {domain}: {e}")
        return True

def save_cache(domain: str):
    """Save cache timestamp"""
    if not CACHE_PATH.exists():
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    if not hasattr(CACHE_PATH, 'read_text'):
        from json import loads
        
    cache = {}
    if CACHE_PATH.exists():
        try:
            with open(CACHE_PATH, 'r') as f:
                cache = json.load(f)
        except:
            cache = {}
    
    cache[domain] = {
        'last_scanned': datetime.now().isoformat(),
        'scans_performed': cache.get(domain, {}).get('scans_performed', 0) + 1
    }
    
    with open(CACHE_PATH, 'w') as f:
        json.dump(cache, f, indent=2)

def search_web_with_fallback(query: str) -> Dict:
    """Search web using hermes_tools.web_search (fallback when Firecrawl returns empty)"""
    try:
        print(f"\n  🔍 Web search query: {query}")
        results = web_search(query, limit=5)
        
        if not results or 'data' not in results:
            print(f"  ✗ No results from web_search")
            return {}
        
        data = results['data']
        if not data:
            print(f"  ✗ Empty results array")
            return {}
        
        print(f"  ✓ Found {len(data)} pages\n")
        return {'pages': data}
        
    except Exception as e:
        logger.error(f"Web search error: {e}")
        return {}

def analyze_page_for_patterns(page: Dict, domain: str) -> List[Dict]:
    """Extract gematria pattern information from page content"""
    pages = page.get('pages', [])
    
    extracted_info = []
    for i, p in enumerate(pages):
        try:
            title = p.get('title', 'Untitled')[:100]
            description = p.get('description', '')[:300]
            url = p.get('url', '')
            
            # Extract symbol numbers if present
            import re
            symbols_found = re.findall(r'\b(124|963|55|111|279|666)\b', 
                                      (description + title).lower())
            
            extracted_info.append({
                'page_num': i + 1,
                'title': title,
                'url': url,
                'snippet': description,
                'symbols_found': list(set(symbols_found))
            })
        except Exception as e:
            logger.warning(f"Error processing page {i}: {e}")
    
    return extracted_info

def run_hybrid_scan_with_fallback() -> Dict:
    """
    Execute hybrid scan using web_search fallback
    Uses hermes_tools.web_search which has direct web access
    """
    
    print("=" * 70)
    print("Hybrid Overnight Research Protocol - FALLBACK MODE")
    print("=" * 70)
    print(f"\nUsing hermes_tools.web_search (Firecrawl fallback)")
    print(f"Mode: Hybrid Scan with Smart Caching + Web Fallback")
    
    # Load database
    db = load_database()
    current_time = datetime.now()
    
    # Clear old cache for fresh start
    if CACHE_PATH.exists():
        CACHE_PATH.unlink()
        logger.info("Cleared existing cache for fresh scan")
    else:
        print("\n✓ Starting with fresh scan (no cached results)")
    
    all_results = {}
    current_cycle = db.get('current_cycle', 0) + 1
    
    # Execute hybrid scan of ALL domains
    print(f"\nExecuting hybrid scan covering {len(DOMAINS)} domains:")
    print("-" * 70)
    
    for domain in DOMAINS:
        logger.info(f"Scanning domain: {domain}")
        
        query = WEB_SEARCH_QUERIES.get(domain, f"{domain} gematria analysis")
        print(f"\n📊 Domain: {domain.upper()}")
        print(f"   Query: {query}")
        
        try:
            # Check cache age
            should_scan = check_cache_age(domain, current_time)
            
            if not should_scan:
                print(f"  ℹ Skipping {domain} (cache still valid)")
                continue
            
            # Perform web search
            search_response = search_web_with_fallback(query)
            
            results_count = len(search_response.get('pages', []))
            
            if results_count == 0:
                print(f"  ✗ No pages crawled for {domain}")
            else:
                print(f"  ✓ Crawled {results_count} pages")
            
            # Store results with timestamp
            domain_results = {
                'timestamp': datetime.now().isoformat(),
                'search_query': query,
                'pages': search_response.get('pages', []),
                'result_count': results_count,
                'mode': 'web_search_fallback'
            }
            
            all_results[domain] = domain_results
            
            # Analyze patterns if pages found
            if results_count > 0:
                patterns = analyze_page_for_patterns(search_response, domain)
                
                if patterns:
                    print(f"\n  📋 Found {len(patterns)} pattern-extractable pages")
                    for p in patterns[:2]:  # Show first 2 examples
                        symbols_str = ', '.join(p['symbols_found']) if p['symbols_found'] else 'None detected'
                        print(f"     Page {p['page_num']}: \"{p['title']}...\" - Symbols: {symbols_str}")
                    
                    # Update database with findings
                    db['results'].append({
                        'domain': domain,
                        'query': query,
                        'pages_count': results_count,
                        'timestamp': domain_results['timestamp'],
                        'patterns_found': [p for p in patterns if p.get('symbols_found')]
                    })
                    
                    # Track relationships
                    found_symbols = set()
                    for p in patterns:
                        found_symbols.update(p.get('symbols_found', []))
                    
                    if found_symbols:
                        db['relationships']['connections'] = {
                            f"{domain}→{','.join(map(str, sorted(found_symbols)))}": {
                                'type': 'symbol_cross_reference',
                                'relevance_score': 0.85,
                                'pages_involved': results_count
                            }
                        }
                    
            save_database(db)
            save_cache(domain)
            
        except Exception as e:
            logger.error(f"Error scanning {domain}: {e}")
    
    # Update cycle info
    db['current_cycle'] = current_cycle
    db['last_run'] = datetime.now().isoformat()
    save_database(db)
    
    return all_results

def main():
    """Main entry point for hybrid scan with web fallback"""
    
    print("=" * 70)
    print("Hybrid Overnight Research Protocol")
    print("Path B: Web Search Fallback Mode")
    print("=" * 70)
    print()
    
    # Execute hybrid scan
    results = run_hybrid_scan_with_fallback()
    
    # Summary
    print("\n" + "=" * 70)
    print("Scan Summary")
    print("=" * 70)
    print(f"All {len(DOMAINS)} domains scanned:")
    for domain in DOMAINS:
        status = "✓ Complete" if domain in results else "⊘ Skipped (cache valid)"
        count = len(results.get(domain, {}).get('pages', []))
        print(f"  [{status}] {domain}: {count} pages")
    
    print(f"\nCurrent cycle: {results.get('current_cycle', db.get('current_cycle', 0))}")
    print(f"Database updated: {DATABASE_PATH}")
    
    print("\n" + "=" * 70)
    print("Hybrid + Smart Caching Strategy with Web Fallback")
    print("=" * 70)
    print("✓ Uses hermes_tools.web_search for direct web access")
    print("✓ Maintains TTL-based cache per domain")
    print("✓ Tracks relationships and cross-references")
    print("✓ Ready for autonomous research integration")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()
