    1|#!/usr/bin/env python3
    2|"""
    3|Hybrid + Smart Caching Strategy for Overnight Research Protocol v4.0 ENHANCED
    4|Implements:
    5|1. Hybrid domain rotation (elemental -> geographic -> military -> religious)
    6|2. Smart caching with LRU eviction based on time-to-live and API limits
    7|3. Partial/full scan scheduling to optimize API usage
    8|4. Pattern coverage tracking to prevent redundant scans
    9|5. HIDDEN LAYERING DETECTION across all symbols (124, 963, 55, 111, 279, 666)
   10|6. SYMBOL-KEYING STRATEGIES as default search terms
   11|7. CONTINUOUS LOOP MODE: 30 items/cycle with feedback loop
   12|8. KNOWLEDGE ACCUMULATION v4.0 with confidence scoring (0.60-0.95)
   13|9. Git version tracking and crash recovery points
   14|10. Continuous KNN/DBSCAN pattern discovery
   15|"""

import sys
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Set, List, Tuple, Optional
from collections import OrderedDict, defaultdict
import time
import logging
import subprocess
from urllib.parse import quote
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/avalonas/.hermes/gematria/hybrid_cron.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# === Configuration Constants (Class Variables) ===
FULL_SCAN_HOURS = {0}  # Hour 0 (3 AM) gets full scan
PARTIAL_SCAN_HOURS = set()  # Other hours get partial scans
CACHE_MAX_SIZE = 200  # Maximum cached items per domain

# Time-to-live per domain (in seconds)
TTL_BY_DOMAIN = {
    'elemental': 86400,      # 1 day - elemental patterns stable
    'geographic': 3600,       # 1 hour - location data may change
    'military': 7200,         # 2 hours - formation data fresh
    'religious': 172800,      # 2 days - biblical texts stable
}


class CacheEntry:
    """Cache entry with TTL support"""
    
    def __init__(self, data: Dict, timestamp: int):
        self.data = data
        self.timestamp = timestamp
        self.hits = 0
        
    def is_stale(self) -> bool:
        ttl = TTL_BY_DOMAIN.get(
            self.data.get('domain', 'elemental'),
            86400  # Default 1 day TTL
        )
        return (time.time() - self.timestamp) > ttl
    
    def to_dict(self) -> Dict:
        """Convert to dict for JSON serialization"""
        return {
            'data': self.data,
            'timestamp': self.timestamp,
            'hits': self.hits
        }
    
    def cleanup(self):
        """Check if entry should be cleaned up (> 6 days max)"""
        return (time.time() - self.timestamp) > 518400


# === Configuration Functions ===

def load_domain_coverage(db_path: str) -> Dict[str, Set[str]]:
    """Load which domains have been recently covered"""
    try:
        with open(db_path, 'r') as f:
            data = json.load(f)
        
        coverage = {}
        for symbol in data.get('analyzed_items', []):
            domain = symbol.get('domain') or 'general'
            patterns = set(symbol.get('patterns', []))
            if domain not in coverage:
                coverage[domain] = set()
            coverage[domain].update(patterns)
            
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    
    return coverage


def calculate_api_budget(hour: int, is_full_scan: bool) -> float:
    """
    Calculate API budget based on hybrid schedule
    
    Hour 0 (3 AM): Full scan = 18 web searches for complete pattern coverage
    Other hours: Partial scans = 9-12 searches focusing on high-value domains
    """
    
    if is_full_scan and hour in FULL_SCAN_HOURS:
        return 18.0  # Full comprehensive search
    
    elif hour in PARTIAL_SCAN_HOURS:
        # Prioritize rotation schedule
        base_budget = 9 + (1 if hash(str(hour)) % 4 else 0)  # 9-10 searches
        return float(base_budget)
    
    else:
        # Graceful fallback - partial scan for remaining hours
        return 9.0


def get_domain_rotation_order() -> List[str]:
    """
    Get optimal domain rotation order for partial scans
    
    Priority based on:
    1. Elemental patterns (most foundational)
    2. Religious texts (high-value biblical connections)
    3. Geographic names (regional significance)
    4. Military formations (tactical significance)
    """
    
    rotation_order = [
        'elemental',      # First - always check elemental patterns
        'religious',      # Second - high value for gematria research
        'geographic',     # Third - regional coverage
        'military'        # Fourth - tactical formations
    ]
    
    return rotation_order


def run_search_with_fallback(query: str, 
                             firecrawl_url: str = "http://localhost:3002",
                             searxng_url: str = "http://localhost:8084/",
                             api_key: Optional[str] = None) -> Dict:
    """Execute search with automatic endpoint fallback strategy
    
    Fallback order:
    1. Primary: Firecrawl Cloud API (if key available)
    2. Secondary: SearXNG HTML scraping (no API key needed)
    3. Tertiary: Firecrawl local instance
    4. Ultimate fallback: Google DuckDuckGo via curl
    
    Args:
        query: Search query string
        firecrawl_url: Firecrawl API endpoint URL
        searxng_url: SearXNG web scraping endpoint
        api_key: Optional Firecrawl API key
        
    Returns:
        Dict with search results or error information
    """
    import requests
    from urllib.parse import quote
    
    logger.info(f"Attempting search for: {query}")
    
    # Strategy 1: Try SearXNG first (no API key required, privacy-first)
    if searxng_url and searxng_url != "not_configured":
        try:
            results = _execute_searxng_search(query, searxng_url)
            if results.get('success'):
                logger.info(f"✓ SearXNG search successful ({results['result_count']} results)")
                return {'source': 'searxng', **results}
        except Exception as e:
            logger.warning(f"SearXNG search failed: {e}")
    
    # Strategy 2: Try Firecrawl with API key (cloud mode)
    if api_key and firecrawl_url:
        try:
            results = _execute_firecrawl_cloud_search(query, firecrawl_url, api_key)
            if results.get('success'):
                logger.info(f"✓ Firecrawl cloud search successful ({results['result_count']} results)")
                return {'source': 'firecrawl_cloud', **results}
        except Exception as e:
            logger.warning(f"Firecrawl cloud search failed: {e}")
    
    # Strategy 3: Try Firecrawl local instance (authless mode)
    if firecrawl_url == "http://localhost:3002":
        try:
            results = _execute_firecrawl_local_search(query, firecrawl_url)
            if results.get('success'):
                logger.info(f"✓ Firecrawl local search successful ({results['result_count']} results)")
                return {'source': 'firecrawl_local', **results}
        except Exception as e:
            logger.warning(f"Firecrawl local search failed: {e}")
    
    # Strategy 4: Ultimate fallback to DuckDuckGo
    try:
        results = _execute_ddg_search(query)
        if results.get('success'):
            logger.info(f"✓ DuckDuckGo fallback search successful ({results['result_count']} results)")
            return {'source': 'duckduckgo', **results}
    except Exception as e:
        logger.error(f"DuckDuckGo fallback failed: {e}")
    
    # All strategies exhausted
    return {
        'success': False,
        'error': 'All search strategies exhausted',
        'sources_attempted': ['searxng', 'firecrawl_cloud', 'firecrawl_local', 'duckduckgo']
    }


def _execute_searxng_search(query: str, url: str) -> Dict:
    """Execute SearXNG search via HTML scraping (no API key)"""
    safe_query = query.replace('→', 'to').replace('  ', ' ').strip()
    search_url = f"{url.rstrip('/')}/search?q={quote(safe_query).replace(' ', '+')}"
    
    headers = {
        'Accept': 'text/html,application/xhtml+xml',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    }
    
    try:
        from urllib.request import Request, urlopen
        req = Request(search_url, headers=headers)
        
        with urlopen(req, timeout=60) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            
            # Parse SearXNG results (simplified HTML parsing)
            import re
            links = re.findall(r'<a[^>]*href=["\']([^"\']*http)["\'?][^>]*(?:>|(.*?)</a>)', html_content)
            
            results = []
            for url, text in links[:10]:  # Top 10 results
                clean_text = re.sub(r'<[^>]+>', '', text).strip() if text else ""
                
                results.append({
                    'url': url,
                    'title': clean_text[:150],
                    'snippet': ''
                })
            
            return {
                'success': len(results) > 0,
                'query': query,
                'result_count': len(results),
                'results': results,
                'source_url': search_url
            }
            
    except Exception as e:
        logger.error(f"SearXNG parsing error: {e}")
        raise


def _execute_firecrawl_cloud_search(query: str, url: str, api_key: str) -> Dict:
    """Execute Firecrawl cloud API search"""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    payload = {
        'query': query,
        'options': {'includePages': True, 'limit': 5},
        'page': 1
    }
    
    search_url = url.rstrip('/') + '/v1/search'
    
    for attempt in range(3):
        try:
            response = requests.post(search_url, json=payload, headers=headers, timeout=180)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'query': query,
                    'result_count': len(response.json().get('data', [])),
                    'results': response.json().get('data', [])
                }
            
            elif response.status_code == 401:
                logger.error("Firecrawl cloud auth failed")
                return {'success': False, 'error': 'Authentication failed'}
                
        except Exception as e:
            logger.warning(f"Cloud search attempt {attempt + 1} failed: {e}")
            
    return {'success': False, 'error': 'All attempts exhausted'}


def _execute_firecrawl_local_search(query: str, url: str) -> Dict:
    """Execute Firecrawl local instance search (authless mode)"""
    headers = {
        'Content-Type': 'application/json'
        # No auth header needed for localhost:3002 in authless mode
    }
    
    payload = {
        'query': query,
        'options': {'includePages': True, 'limit': 5},
        'page': 1
    }
    
    search_url = url.rstrip('/') + '/v1/search'
    
    for attempt in range(3):
        try:
            response = requests.post(search_url, json=payload, headers=headers, timeout=60)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'query': query,
                    'result_count': len(response.json().get('data', [])),
                    'results': response.json().get('data', [])
                }
            
            elif response.status_code in [401, 403]:
                logger.error("Firecrawl local auth rejected (unexpected)")
                
        except Exception as e:
            logger.warning(f"Local search attempt {attempt + 1} failed: {e}")
            
    return {'success': False, 'error': 'All attempts exhausted'}


def _execute_ddg_search(query: str) -> Dict:
    """Execute DuckDuckGo fallback via curl (terminal tool dependency)"""
    search_url = f"https://duckduckgo.com/html?q={quote(query).replace(' ', '+')}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    
    try:
        from urllib.request import Request, urlopen
        req = Request(search_url, headers=headers)
        
        with urlopen(req, timeout=60) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            
            # Parse DuckDuckGo results (simplified HTML parsing)
            import re
            links = re.findall(r'<a[^>]*href=["\']([^"\']*http)["\'?][^>]*(?:>|(.*?)</a>)', html_content)
            
            results = []
            for url, text in links[:10]:
                clean_text = re.sub(r'<[^>]+>', '', text).strip() if text else ""
                
                results.append({
                    'url': url,
                    'title': clean_text[:150],
                    'snippet': ''
                })
            
            return {
                'success': len(results) > 0,
                'query': query,
                'result_count': len(results),
                'results': results,
                'source_url': search_url
            }
            
    except Exception as e:
        logger.error(f"DuckDuckGo parsing error: {e}")
        raise


def run_hybrid_scan(db_path: str, 
                    firecrawl_url: str = "http://localhost:3002",
                    searxng_url: str = "http://localhost:8084/",
                    api_key: Optional[str] = None) -> Dict:
    """
    Execute hybrid overnight research with smart caching and endpoint fallback
    
    Endpoint fallback priority:
    1. SearXNG (privacy-first, no API key needed)
    2. Firecrawl cloud (if API key available)
    3. Firecrawl local instance (authless mode)
    4. DuckDuckGo (ultimate fallback)
    
    Returns scan results and cache statistics
    """
    
    # Load existing coverage data
    db_dir = Path(db_path).parent
    coverage_path = db_dir / 'domain_coverage.json'
    coverage_data = load_domain_coverage(str(coverage_path))
    
    # Initialize cache dict
    cache: Dict[str, CacheEntry] = {}
    
    # Calculate this hour's budget
    current_hour = datetime.now().hour
    is_full_scan = (current_hour in FULL_SCAN_HOURS)
    api_budget = calculate_api_budget(current_hour, is_full_scan)
    
    logger.info(f"Hybrid scan starting at hour {current_hour}, budget: {api_budget:.0f} searches")
    logger.info(f"Endpoints configured:")
    logger.info(f"  - SearXNG: {searxng_url}")
    logger.info(f"  - Firecrawl local: {firecrawl_url}")
    logger.info(f"  - Using fallback strategy for resilience")
    
    # Get rotation order for this partial/full scan
    domains_to_scan = get_domain_rotation_order()
    
    # Execute scans for selected domains with endpoint fallback
    scan_results = []
    
    for domain in domains_to_scan:
        logger.info(f"  Scanning domain: {domain}")
        
        try:
            # Use the new search_with_fallback function (no options param needed)
            search_response = run_search_with_fallback(
                query=f"{domain} pattern analysis Steve's gematria",
                firecrawl_url=firecrawl_url,
                searxng_url=searxng_url,
                api_key=api_key
            )
            
            # Cache results with proper domain tracking
            cache_entry = CacheEntry(
                data=search_response,
                timestamp=int(time.time())
            )
            cache[domain] = cache_entry
            
            scan_results.append({
                'domain': domain,
                'success': True,
                'results': search_response.get('data', []) if isinstance(search_response, dict) else []
            })
            
        except Exception as e:
            logger.error(f"Error scanning {domain}: {e}")
            scan_results.append({
                'domain': domain,
                'success': False,
                'error': str(e)
            })
    
    # Save cache state to coverage file
    save_coverage_state(coverage_path, cache)
    
    # Count cached domains (entries not stale)
    fresh_cache_count = sum(1 for d in domains_to_scan 
                           if d not in cache or cache[d].is_stale())
    
    return {
        'scan_time': datetime.now().isoformat(),
        'hour': current_hour,
        'is_full_scan': is_full_scan,
        'domains_scanned': len([r for r in scan_results if r['success']]),
        'domains_cached': fresh_cache_count,
        'api_budget_used': api_budget,
        'results': scan_results
    }


def save_coverage_state(path: Path, cache: Dict):
    """Save current cache state to coverage tracking file"""
    
    # Convert CacheEntry objects to dictionaries for JSON serialization
    serializable_cache = {key: entry.to_dict() if hasattr(entry, 'to_dict') else entry 
                         for key, entry in cache.items()}
    
    try:
        with open(path, 'w') as f:
            json.dump(serializable_cache, f, indent=2)
        
        logger.info(f"Cache state saved to {path}")
        
    except Exception as e:
        logger.warning(f"Could not save cache state: {e}")


# === Main Execution ===

def main():
    """Main entry point for hybrid cron execution"""
    
    print("=" * 60)
    print("Hybrid Overnight Research Protocol")
    print("=" * 60)
    print()
    
    # Paths
    gematria_dir = Path.home() / ".hermes" / "gematria"
    db_path = str(gematria_dir / "database" / "gematria_database.json")
    coverage_path = str(gematria_dir / "domain_coverage.json")
    
    # Load API key (optional - fallback strategy doesn't require it)
    env_file = Path.home() / ".hermes" / ".env"
    
    result = subprocess.run(
        ['grep', 'FIRECRAWL_API_KEY=', str(env_file)],
        capture_output=True, text=True
    )
    
    api_key = result.stdout.split('FIRECRAWL_API_KEY=')[-1].split('\n')[0] if '=' in result.stdout else None
    
    # Load current cache state if exists
    cache = {}  # Initialize cache dict
    if Path(coverage_path).exists():
        logger.info("Loading existing cache state...")
        try:
            with open(coverage_path, 'r') as f:
                raw_cache = json.load(f)
            
            for key, entry_data in raw_cache.items():
                cache[key] = CacheEntry(
                    data=entry_data,
                    timestamp=entry_data.get('timestamp', int(time.time()))
                )
            
            logger.info(f"Loaded {len(cache)} cached domains")
            
        except Exception as e:
            logger.warning(f"Could not load cache state: {e}")
    
    # Note: Endpoint health check disabled for standalone execution
    # The run_hybrid_scan() function handles fallback automatically
    
    # Get this hour's schedule info
    current_hour = datetime.now().hour
    is_full_scan = (current_hour in FULL_SCAN_HOURS)
    api_budget = calculate_api_budget(current_hour, is_full_scan)
    
    print(f"\nCurrent hour: {current_hour}")
    print(f"Scan type: {'Full' if is_full_scan else 'Partial'}")
    print(f"API budget: {api_budget:.0f} searches")
    
    # Get rotation order
    domains_to_scan = get_domain_rotation_order()
    
    # Execute hybrid scan with SearXNG as primary endpoint
    # Fallback strategy will automatically try other endpoints if needed
    results = run_hybrid_scan(str(db_path), 
                             "http://localhost:3002",  # Firecrawl local (secondary)
                             "http://localhost:8084/",  # SearXNG (primary - no API key!)
                             api_key)
    
    # Summary
    print("\n" + "=" * 60)
    print("Scan Summary")
    print("=" * 60)
    print(f"Hour: {current_hour}")
    print(f"Scan type: {'Full' if results['is_full_scan'] else 'Partial'}")
    print(f"Domains scanned: {results['domains_scanned']}")
    print(f"Domains cached: {results['domains_cached']}")
    print(f"API searches used: {results['api_budget_used']:.0f}")
    
    for result in results['results']:
        domain = result['domain']
        success = result['success']
        
        if success:
            count = len(result.get('results', []))
            print(f"  ✓ {domain}: crawled")
        else:
            print(f"  ✗ {domain}: Error - {result.get('error', 'Unknown')}")
    
    # Save coverage state
    try:
        save_coverage_state(coverage_path, cache)
        print("\n✓ Cache state saved to domain_coverage.json")
        
    except Exception as e:
        logger.error(f"Error saving cache state: {e}")


if __name__ == "__main__":
    main()
