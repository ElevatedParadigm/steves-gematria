#!/usr/bin/env python3
"""
Local Firecrawl Runner
Handles web search/crawl without Docker networking issues.
Tries localhost:3002 (Docker), then falls back to cloud API or curl-based scraping.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("[!] Installing requests...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])

# Load environment variables from .env
def load_env_vars():
    env_path = Path.home() / ".hermes" / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#") and line.startswith("FIRECRAWL"):
                    key, _, value = line.partition("=")
                    return {key.strip().replace("$", ""): value.strip().strip('"\'')}
    return {}

env_vars = load_env_vars()
FIRECRAWL_API_KEY = env_vars.get("FIRECRAWL_API_KEY", "").strip().strip("'\"")

# Configuration
LOCAL_DOCKER_URL = "http://localhost:3002/v1/search"
CLOUD_FIRECRAWL_URL = "https://api.firecrawl.dev/v1/search"

GEMATRIA_DB_PATH = Path.home() / ".hermes/gematria/gematria_database.json"
OBSIDIAN_EXPORTS_DIR = Path.home() / ".hermes/gematria/obsidian_exports"
OBSIDIAN_EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Domain keywords (from Phase 1 configuration)
DOMAIN_KEYWORDS = {
    "geopolitical": ["Israel", "Gaza", "Lebanon", "Hezbollah", "Iran", "Saudi Arabia", "Putin", 
                     "Trump", "Biden", "US elections", "Middle East peace", "NATO"],
    "religious": ["Jesus", "Allah", "Prophet Mohammed", "Buddha", "Krishna", "Temple Mount",
                  "Jerusalem", "Gospel", "Quran", "Torah", "Vedas", "Church", "Mosque"],
    "economic": ["Bitcoin", "crypto", "inflation", "interest rates", "stock market",
                 "Federal Reserve", "Wall Street", "gold", "silver", "stocks"],
    "military": ["coup", "troops", "deployment", "weapon", "bomber", "fighter jet",
                 "defense budget", "soldier", "army", "navy", "marines"],
    "elemental": ["fire", "volcano", "eruption", "tornado", "hurricane", "earthquake",
                  "wildfire", "tsunami", "flood", "drought", "climate"],
    "cryptographic": ["aes-128", "aes-256", "sha384", "encryption", "private key",
                      "public key", "certificate", "hash", "signature", "algorithm"],
    "temporal": ["March 29 2025", "April 4 2025", "March 27 2026", "timeline",
                 "schedule", "agenda", "deadline"]
}

def search_firecrawl_docker(search_term, options=None):
    """Try local Docker container first."""
    payload = {
        "query": search_term,
        "options": options or {"pageOptions": {"perPage": 5}},
        "includeData": True
    }
    try:
        headers = {}  # No auth for localhost Docker
        response = requests.post(LOCAL_DOCKER_URL, json=payload, timeout=30)
        return {
            "method": "docker",
            "success": response.status_code == 200,
            "response": response.json() if response.ok else None,
            "status_code": response.status_code
        }
    except Exception as e:
        return {
            "method": "docker", 
            "success": False,
            "error": str(e),
            "status_code": None
        }

def search_firecrawl_cloud(search_term, options=None):
    """Use cloud Firecrawl API."""
    payload = {
        "query": search_term,
        "options": options or {"pageOptions": {"perPage": 5}},
        "includeData": True
    }
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}" if FIRECRAWL_API_KEY else ""
        }
        response = requests.post(CLOUD_FIRECRAWL_URL, json=payload, headers=headers, timeout=30)
        return {
            "method": "cloud",
            "success": response.status_code == 200,
            "response": response.json() if response.ok else None,
            "status_code": response.status_code,
            "error_message": response.text[:500] if not response.ok else None
        }
    except Exception as e:
        return {
            "method": "cloud",
            "success": False,
            "error": str(e),
            "status_code": None,
            "error_message": None
        }

def search_with_curl(search_term):
    """Fallback using curl command (no API key needed, searches DuckDuckGo)."""
    try:
        result = subprocess.run(
            ["curl", "-s", "-L", "--max-time", "30", 
             f"https://duckduckgo.com/?q={search_term.replace(' ', '+')}",
             "&kl=wt-wt"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return {
                "method": "curl",
                "success": True,
                "response": result.stdout[:5000],  # Limit output size
                "status_code": 200
            }
        return {"method": "curl", "success": False, "error": f"Exit code: {result.returncode}"}
    except Exception as e:
        return {
            "method": "curl", 
            "success": False,
            "error": str(e)
        }

def search_web(term):
    """Intelligent routing: try Docker -> Cloud -> Curl fallback."""
    print(f"\n🔍 Searching for: '{term}'")
    
    # Try 1: Local Docker (fastest, preferred)
    print("   → Trying localhost:3002 (Docker)...")
    result = search_firecrawl_docker(term)
    
    if result["success"]:
        print(f"   ✅ SUCCESS via Docker: {len(result['response']['data']) if result['response'] else 0} results")
        return result
    
    # Try 2: Cloud API (if API key configured)
    if FIRECRAWL_API_KEY:
        print("   ⚠️  Docker failed. Trying cloud API...")
        result = search_firecrawl_cloud(term)
        
        if result["success"]:
            print(f"   ✅ SUCCESS via Cloud: {len(result['response']['data']) if result['response'] else 0} results")
            return result
    
    # Try 3: Curl fallback (DuckDuckGo, no API needed)
    print("   ⚠️  Cloud failed or no key. Trying curl/DuckDuckGo...")
    result = search_with_curl(term)
    
    if result["success"]:
        print(f"   ✅ SUCCESS via Curl: DuckDuckGo search complete")
        return result
    
    # All methods failed
    print(f"   ❌ ALL METHODS FAILED: {result.get('error', 'Unknown error')}")
    return result

def extract_patterns(html_content):
    """Simple pattern extraction from HTML."""
    import re
    
    patterns = {
        "keywords": [],
        "dates": [],
        "numbers": []
    }
    
    # Extract keywords (uppercase words, 2-10 chars)
    keywords = re.findall(r'\b[A-Z]{2,10}\b', html_content)
    patterns["keywords"] = list(set(keywords))[:30]
    
    # Extract dates (YYYY-MM-DD or Month DD YYYY)
    dates = re.findall(r'(?:\d{4}-\d{2}-\d{2}|[A-Za-z]+\s+\d{1,2}\s+\d{4})', html_content)
    patterns["dates"] = list(set(dates))[:20]
    
    # Extract numbers (with or without decimals)
    numbers = re.findall(r'\b\d+(?:\.\d+)?\b', html_content)
    patterns["numbers"] = list(set(numbers))[:15]
    
    return patterns

def enrich_with_domain_context(query_term, term_type=None):
    """Add domain-specific keywords to search query."""
    context = ""
    if term_type:
        # Add relevant keywords for the detected domain
        related_domains = {
            "geopolitical": ["Israel", "Gaza", "Putin", "Trump", "US foreign policy"],
            "religious": ["Temple Mount", "Jerusalem", "Prophet", "church"],
            "economic": ["Bitcoin", "inflation", "stock market", "crypto"],
            "military": ["army", "troops", "war", "defense"],
            "elemental": ["fire", "climate", "disaster", "natural"],
            "cryptographic": ["encryption", "aes", "hash", "algorithm"],
            "temporal": ["timeline", "date", "schedule", "deadline"]
        }
        context = ", ".join(related_domains.get(term_type, []))
    
    return f"{query_term} {context}".strip()

def crawl_url(url):
    """Crawl a specific URL using Firecrawl."""
    print(f"\n📄 Crawling URL: {url[:80]}...")
    
    # Try Docker first
    payload = {"url": url, "includeData": True}
    try:
        response = requests.post(LOCAL_DOCKER_URL, json=payload, timeout=30)
        if response.status_code == 200:
            return {
                "method": "docker",
                "success": True,
                "markdown": response.json().get("markdown", "")[:5000],
                "html": response.json().get("html", "")[:5000]
            }
    
    except:
        pass
    
    # Try cloud API
    if FIRECRAWL_API_KEY:
        payload = {"url": url, "includeData": True}
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {FIRECRAWL_API_KEY}"
            }
            response = requests.post(LOCAL_DOCKER_URL.replace("localhost", "api.firecrawl.dev"), json=payload, headers=headers, timeout=30)
            if response.status_code == 200:
                return {
                    "method": "cloud",
                    "success": True,
                    "markdown": response.json().get("markdown", "")[:5000],
                    "html": response.json().get("html", "")[:5000]
                }
        except:
            pass
    
    return {
        "method": "unknown",
        "success": False,
        "error": "Could not crawl URL with Firecrawl"
    }

def main():
    """Main orchestrator for Level 1 Trigger."""
    
    print("\n" + "="*60)
    print("🔥 LOCAL FIRECRAWL RUNNER - LEVEL 1 TRIGGER")
    print("="*60 + "\n")
    
    # Check if running as test or actual search
    import sys
    args = sys.argv[1:]
    
    if not args:
        # Run demo search on all domains
        print("\n📊 DEMO MODE: Searching one keyword per domain\n")
        
        results = {}
        for domain_type, keywords in DOMAIN_KEYWORDS.items():
            term = keywords[0]  # Search first keyword per domain
            enriched = enrich_with_domain_context(term, domain_type)
            result = search_web(enriched)
            
            results[domain_type] = {
                "query": enriched,
                **result
            }
        
        # Save results to database
        db_path = Path.home() / ".hermes/gematria/database/firecrawl_searches.json"
        with open(db_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: {db_path}")
        
        # Extract patterns from results
        all_keywords = set()
        for domain, res in results.items():
            if "keywords" in res.get("response", {}):
                all_keywords.update(res["response"]["keywords"])
        
        print(f"\n📊 Top keywords found: {', '.join(list(all_keywords)[:20])}")
        
    elif len(args) == 1 and args[0] == "--single":
        # Single search mode (used by Level 1 trigger)
        if len(args) != 2:
            print("Usage: python local_firecrawl.py --single <search_term>")
            sys.exit(1)
        
        term = args[1]
        result = search_web(term)
        
        # Save single result
        save_path = Path.home() / ".hermes/gematria/database/firecrawl_last_search.json"
        with open(save_path, 'w') as f:
            json.dump(result, f, indent=2)
        
    else:
        print("Usage:\n  (no args) - Run demo mode: search one keyword per domain\n  --single <term> - Single search for Level 1 trigger")
    
    return results if 'results' in locals() else result

if __name__ == "__main__":
    main()