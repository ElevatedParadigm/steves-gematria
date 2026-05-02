#!/usr/bin/env python3
"""
Steves Gematria - SearXNG Integration Module
Replace DuckDuckGo/Brave Search with unlimited private SearXNG access
"""

import requests
import json
from datetime import datetime
from pathlib import Path

class SearXNGSearch:
    """
    Privacy-first search engine using SearXNG as unlimited replacement
    for DuckDuckGo and Brave Search APIs.
    """
    
    def __init__(self, base_url="http://localhost:8084", session_timeout=30):
        """
        Initialize SearXNG client
        
        Args:
            base_url: Local SearXNG instance URL
            session_timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Steve Gematria Research)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        })
        self.timeout = session_timeout
    
    def search(self, query: str, language: str = "en") -> dict:
        """
        Perform privacy-first web search via SearXNG
        
        Args:
            query: Search query string
            language: Language code (default: en)
        
        Returns:
            Dict containing search results in standard format
        """
        # Clean and encode query
        clean_query = query.replace('"', "'")  # Escape quotes for SearXNG
        
        try:
            response = self.session.get(
                f"{self.base_url}/search",
                params={
                    'q': clean_query,
                    'language': language,
                    'categories': 'general',
                    'safesearch': 0,
                    'p': 1
                },
                timeout=self.timeout
            )
            
            # SearXNG returns HTML but we can parse it or use JSON if enabled
            if response.status_code == 200:
                return {
                    'success': True,
                    'raw_response': response.text[:500],  # First 500 chars
                    'query': clean_query,
                    'url': f"{self.base_url}/search?q={clean_query}"
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}",
                    'raw_response': response.text[:200] if response.text else ''
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'query': query
            }
    
    def search_json(self, query: str, language: str = "en") -> dict:
        """
        Search using JSON format (if enabled in SearXNG settings)
        
        Note: This requires 'json' to be added to formats in settings.yml
              and limiter set to false. See WEB_SEARCH_INFRASTRUCTURE_README.md
        
        Args:
            query: Search query string
            language: Language code (default: en)
        
        Returns:
            Dict containing search results in JSON format or fallback info
        """
        clean_query = query.replace('"', "'")
        
        try:
            response = self.session.get(
                f"{self.base_url}/search",
                params={
                    'q': clean_query,
                    'format': 'json',
                    'language': language,
                    'categories': 'general'
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return {
                        'success': True,
                        'json_response': data,
                        'query': clean_query
                    }
                except json.JSONDecodeError:
                    # Fallback to HTML parsing
                    return {
                        'success': True,
                        'html_mode': True,
                        'raw_response': response.text[:500],
                        'query': clean_query
                    }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code} - JSON format not enabled",
                    'recommendation': "Add 'json' to formats in SearXNG settings.yml"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"Connection error: {str(e)}",
                'query': query
            }
    
    def batch_search(self, queries: list[str], language: str = "en") -> dict:
        """
        Batch search multiple queries
        
        Args:
            queries: List of query strings to search
            language: Language code (default: en)
        
        Returns:
            Dict with all results indexed by query
        """
        results = {}
        for i, query in enumerate(queries):
            key = f"query_{i+1}"
            result = self.search(query, language=language)
            results[key] = result
        
        return {
            'total_queries': len(queries),
            'successful': sum(1 for r in results.values() if r.get('success')),
            'results': results
        }


def overnight_research_scan(
    symbols: list[int],
    domains: list[str],
    search_engine: SearXNGSearch = None,
    output_dir: str = "/home/avalonas/.hermes/gematria"
) -> dict:
    """
    Overnight web scan using SearXNG instead of DuckDuckGo
    
    Args:
        symbols: List of core symbol numbers to track
        domains: Domain categories to search
        search_engine: SearXNGSearch instance (optional)
        output_dir: Directory for results
        
    Returns:
        Dict with timestamped scan results
    """
    if search_engine is None:
        search_engine = SearXNGSearch()
    
    # Generate target queries
    targets = []
    for symbol in symbols:
        for domain in domains:
            targets.append(f"{domain} {symbol} gematria")
            targets.append(f"numerology patterns {symbol}")
    
    print(f"[🔍] Starting overnight scan with SearXNG...")
    print(f"[✅] Unlimited private searches - no rate limits!")
    print(f"[🛡️] Privacy-first: local only, no tracking")
    
    # Execute batch search
    results = search_engine.batch_search(targets)
    
    # Save timestamped results
    output_path = Path(output_dir) / "searxng_overnight_scan.json"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    data = {
        "timestamp": timestamp,
        "search_engine": "SearXNG (localhost:8084)",
        "symbols_tracked": symbols,
        "domains_searched": domains,
        "total_targets": len(targets),
        "successful": results.get('successful', 0),
        "results": {k: v for k, v in list(results.items())[:10]}  # First 10 results
    }
    
    try:
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"[✅] Results saved to {output_path}")
    except Exception as e:
        print(f"[⚠️] Could not save results: {e}")
    
    return data


# ============================================================================
# LLM Integration Configuration (OpenAI/OpenClaw/Groq)
# ============================================================================

LLM_SEARCH_CONFIG = """
# SearXNG Integration for Your LLM Agents
# Add this to your OpenAI, OpenClaw, Groq, or any tool calling LLM configuration

# Environment variables for Brave Search API proxy:
BRAVE_API_BASE_URL=http://localhost:8084  # Points to local SearXNG instance  
BRAVE_API_KEY=your_dummy_key_here         # Can be empty or any value - ignored

# Or in your tool/function calling setup, use a wrapper that returns SearXNG results
# when Brave Search is called. This gives you unlimited private searches!

# Example Python wrapper for LLM tools:

import requests

def brave_search(query: str):
    """
    Wrapper that redirects LLM calls to local SearXNG
    
    When your LLM thinks it's calling Brave Search API,
    it actually queries your local SearXNG instance!
    
    Args:
        query: Search query from the LLM
        
    Returns:
        JSON response in format compatible with Brave Search API
    """
    try:
        response = requests.get(
            "http://localhost:8084/search",
            params={
                'q': query,
                'format': 'json'  # If enabled in settings.yml
            },
            timeout=30
        )
        
        if response.status_code == 200:
            try:
                return response.json()  # Return as JSON
            except:
                return {"results": [], "answer": ""}
        else:
            return {"error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        return {"error": str(e)}

# Your LLM now has unlimited, private searches!
"""

if __name__ == "__main__":
    import sys
    
    # Example usage
    print("🔮 Steve's Gematria - SearXNG Search Integration")
    print("=" * 50)
    
    # Create search instance
    searcher = SearXNGSearch()
    
    # Test search
    print("\n[🧪] Testing SearXNG integration...")
    result = searcher.search("bitcoin gematria analysis", language="en")
    print(f"[✅] Search successful: {result['success']}")
    if 'url' in result:
        print(f"[🔗] See results at: {result['url']}")
    
    # Example overnight scan
    print("\n[🌙] Simulating overnight research scan...")
    scan_results = overnight_research_scan(
        symbols=[124, 963, 55],
        domains=["cryptocurrency", "technology"],
        output_dir="/home/avalonas/.hermes/gematria"
    )
    
    print(f"\n[✅] Scan complete: {scan_results['successful']}/{scan_results['total_targets']} successful")
