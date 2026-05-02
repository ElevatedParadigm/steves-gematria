#!/usr/bin/env python3
"""
Local Firecrawl Runner - Simplified v2
Uses direct curl command for scraping (no API key needed).
Best for avoiding Docker networking issues.
"""

import json
import subprocess
import sys
from pathlib import Path

# Configuration
GEMATRIA_DB_PATH = Path.home() / ".hermes/gematria/gematria_database.json"
OBSIDIAN_EXPORTS_DIR = Path.home() / ".hermes/gematria/obsidian_exports"
DOMAIN_KEYWORDS = {
    "geopolitical": ["Israel", "Gaza", "Hezbollah", "Trump", "US foreign policy", "Middle East"],
    "religious": ["Temple Mount", "Jerusalem", "Prophet Mohammed", "church", "mosque", "gospel"],
    "economic": ["Bitcoin", "crypto", "gold", "inflation", "Federal Reserve", "stock market"],
    "military": ["coup", "troops", "defense budget", "weapon system", "fighter jet"],
    "elemental": ["fire volcano", "climate disaster", "wildfire", "earthquake", "tsunami"],
    "cryptographic": ["aes encryption", "hash algorithm", "private key", "public key"],
    "temporal": ["March 29 2025", "timeline date", "schedule agenda"]
}

def search_with_curl(query):
    """Simple curl-based web search (DuckDuckGo) with retries."""
    import time
    
    for attempt in range(3):
        try:
            # Encode spaces and use safe URL parameters
            search_term = query.replace(" ", "+")
            
            result = subprocess.run(
                ["curl", "-sL", "--max-time", "15",  # Limit to 15 seconds per attempt
                 f"https://duckduckgo.com/?q={search_term}&iax=answers&ia=web"],
                capture_output=True, 
                text=True,
                timeout=18
            )
            
            if result.returncode == 0:
                return {
                    "method": "curl",
                    "success": True,
                    "response": result.stdout[:10000],  # Limit output size
                    "status_code": 200,
                    "query": query
                }
        except subprocess.TimeoutExpired:
            print(f"   ⚠️  Attempt {attempt + 1}: Timeout ({15}s)")
        except Exception as e:
            print(f"   ⚠️  Attempt {attempt + 1}: {str(e)[:60]}")
        
        if attempt < 2:
            time.sleep(1)  # Brief pause between retries
    
    return {
        "method": "curl",
        "success": False,
        "error": "All attempts failed after 3 tries"
    }

def extract_patterns(html_content):
    """Extract patterns from HTML content."""
    import re
    
    patterns = {
        "keywords": [],
        "dates": [],
        "numbers": []
    }
    
    # Extract uppercase keywords (2-10 chars)
    keywords = re.findall(r'\b[A-Z]{2,10}\b', html_content)
    patterns["keywords"] = list(set(keywords))[:30]
    
    # Extract dates (various formats)
    dates = re.findall(r'(?:\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4}|[A-Za-z]+\s+\d{1,2},?\s+\d{4})', html_content)
    patterns["dates"] = list(set(dates))[:20]
    
    # Extract numbers (including decimals)
    numbers = re.findall(r'\b\d+(?:\.\d+)?\b', html_content)
    patterns["numbers"] = list(set(numbers))[:15]
    
    return patterns

def process_search_results(html, query):
    """Process search results and extract gematria-relevant data."""
    
    patterns = extract_patterns(html)
    
    # Count occurrences of key terms (simple frequency analysis)
    import re
    
    key_terms = [
        "Israel", "Temple", "Jerusalem", "Bitcoin", "coup", "fire",
        "encryption", "March 29", "volcano", "Trump"
    ]
    
    term_counts = {}
    for term in key_terms:
        # Case-insensitive count (simplified)
        match = re.findall(rf'\b{term}\b', html.lower() if html else "")
        term_counts[term] = len(match)
    
    return {
        "query": query,
        "patterns": patterns,
        "term_counts": term_counts,
        "word_count": len([c for c in html.split()]) if html else 0,
        "gematria_relevance": sum(term_counts.values()) > 5
    }

def analyze_core_symbols(html_content=None):
    """Analyze HTML content for core symbol patterns (124, 963, 55, 111, 279, 666)."""
    
    symbols = {
        "124": 0,
        "963": 0, 
        "55": 0,
        "111": 0,
        "279": 0,
        "666": 0
    }
    
    # Simple count of these patterns in content
    if html_content:
        for symbol in symbols.keys():
            patterns = [f"{symbol}", f" {symbol} ", f",{symbol},"]
            for pattern in patterns:
                symbols[symbol] += html_content.lower().count(pattern.lower())
    
    return symbols

def main():
    """Main orchestrator for Level 1 Trigger (webhook integration)."""
    
    print("\n" + "="*60)
    print("🔥 LOCAL FIRECRAWL RUNNER v2 - LEVEL 1 TRIGGER")
    print("="*60 + "\n")
    
    # Check if running as test or actual search
    args = sys.argv[1:]
    
    if not args:
        # Run demo mode: search one keyword per domain
        print("\n📊 DEMO MODE: Searching keywords across all domains\n")
        
        results = {}
        for domain_type, keywords in DOMAIN_KEYWORDS.items():
            term = keywords[0]
            enriched = f"{term} {', '.join(keywords[1:3])}" if len(keywords) > 1 else term
            
            print(f"🔍 Searching: '{enriched}'")
            
            result = search_with_curl(enriched)
            
            if result["success"]:
                processed = process_search_results(result["response"], enriched)
                
                # Analyze core symbols from search results
                symbols = analyze_core_symbols(result["response"])
                
                results[domain_type] = {
                    "query": enriched,
                    "patterns": processed["patterns"],
                    "term_counts": processed["term_counts"],
                    "word_count": processed["word_count"],
                    "gematria_relevance": processed["gematria_relevance"]
                }
                
                print(f"   ✅ SUCCESS: {processed['word_count']} words analyzed")
            else:
                results[domain_type] = {"query": enriched, "error": result.get("error", "Unknown")}
                print(f"   ⚠️  FAILED: {result.get('error')}")
        
        # Save demo results to database
        db_path = Path.home() / ".hermes/gematria/database/firecrawl_demographic_analysis.json"
        with open(db_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Demo results saved to: {db_path}")
        
    elif "--single" in sys.argv[1:]:
        # Single search mode (Level 1 webhook trigger)
        if len(args) != 2:
            print("Usage: python local_firecrawl_runner.py --single <search_term>")
            sys.exit(1)
        
        term = sys.argv[sys.argv.index("--single") + 1]
        result = search_with_curl(term)
        
        if result["success"]:
            processed = process_search_results(result["response"], term)
            
            # Analyze core symbols from search results
            symbols = analyze_core_symbols(result["response"])
            
            print(f"\n✅ Search complete for: {term}")
            print(f"   Keywords found: {len(processed['patterns']['keywords'])}")
            print(f"   Dates found: {len(processed['patterns']['dates'])}")
            
            # Store in single_result for return
            single_result = result
            
            # Save single result
            save_path = Path.home() / ".hermes/gematria/database/firecrawl_last_search.json"
            with open(save_path, 'w') as f:
                json.dump({
                    "query": term,
                    "result": result,
                    "processed": processed,
                    "symbols": symbols
                }, f, indent=2)
            
            print(f"   💾 Saved to: {save_path}")
        else:
            print(f"\n⚠️  Search failed for: {term}")
            print(f"   Error: {result.get('error')}")
    
    else:
        print("Usage:")
        print("  (no args) - Run demo mode: search one keyword per domain")
        print("  --single <term> - Single search for Level 1 webhook trigger")
    
    return single_result if single_result else results

if __name__ == "__main__":
    main()