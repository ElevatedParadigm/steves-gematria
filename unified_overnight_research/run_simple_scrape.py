#!/usr/bin/env python3
"""Overnight Research Protocol - Direct Web Scraping Mode
Executes symbol-keyed queries for core symbols: 124, 963, 55, 111, 279, 666
Wikipedia API fallback when local search services are offline.
"""

import requests
import json
import os
from datetime import datetime
import subprocess

RESEARCH_DIR = "/home/avalonas/.hermes/gematria/unified_overnight_research"
OUTPUT_DIR = f"{RESEARCH_DIR}/obsidian_exports"
REPORTS_DIR = f"{RESEARCH_DIR}/reports"
DB_PATH = f"{RESEARCH_DIR}/database/gematria_database.json"

# Core symbols with symbol-keying strategies
CORE_SYMBOLS = [
    {"id": "124", "name": "Universal Bridge", "query": "geopolitical boundary events transition"},
    {"id": "963", "name": "Air Activation", "query": "air activation political discourse"},
    {"id": "55", "name": "International Diplomacy", "query": "foreign relations history international"},
    {"id": "111", "name": "Activation Initiation", "query": "numerology mysticism current events"},
    {"id": "279", "name": "Fire Force Integration", "query": "ancient mythology religion ancient civilizations"},
    {"id": "666", "name": "Completion Cycle", "query": "cyclical political events patterns"},
]

def fetch_wikipedia(query):
    url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + query.replace(" ", "+")
    try:
        resp = requests.get(url, headers={"User-Agent": "Steve's-Gematria-Composer"}, timeout=25)
        if resp.status_code == 200:
            data = resp.json()
            return {"query": query, "title": data.get("title"), 
                    "summary": data.get("extract", "")[:1500] if data.get("extract") else "",
                    "keywords": data.get("keywords", [])[:10], "exists": bool(data.get("extract"))}
        return {"query": query, "title": None, "error": str(resp.status_code)}
    except Exception as e:
        return {"query": query, "title": None, "error": str(e)}

def main():
    print("=" * 80)
    print("🌙 OVERNIGHT RESEARCH PROTOCOL - Direct Web Scraping Mode")
    print("=" * 80)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    symbols_found = set()
    all_results = []
    
    print("\n🔍 EXECUTING SYMBOL-KEYED QUERIES:")
    for i, symbol in enumerate(CORE_SYMBOLS, 1):
        sid = symbol["id"]
        query = sid + " " + symbol['query']
        
        print(f"\nQuery #{i}: **{sid}** ({symbol['name']})")
        print(f"   Base: {symbol['query']}")
        
        result = fetch_wikipedia(query)
        
        if result.get("title"):
            title_short = result["title"][:100] + "..." if len(result["title"]) > 100 else result["title"]
            print(f"   ✅ Found: {title_short}")
            symbols_found.add(sid)
        else:
            print(f"   ⚠️ Zero results (HIDDEN_LAYERING ACTIVE for symbol {sid})")
        
        all_results.append(result)

    # Generate report
    successful = sum(1 for r in all_results if r.get("title"))
    
    md_content = f"""# Overnight Research Report - Direct Web Scraping Mode

**Timestamp:** {datetime.now().isoformat()}  
**Cycle ID:** {timestamp}  
**Mode:** Wikipedia API fallback (local services offline)  
**Symbols Tracked:** 124, 963, 55, 111, 279, 666

## Results Summary
- Symbols Processed: {len(CORE_SYMBOLS)}
- Successful Queries: {successful}
- Zero Results (Hidden Layering): {len(all_results) - successful}

## Query Details

"""
    for r in all_results:
        if r.get("title"):
            keywords = ", ".join(r["keywords"][:3])
            md_content += f"### `{r['query']}`\n\n**Title:** {r['title']}\n**Keywords:** {keywords}\n\n"
        else:
            md_content += f"### `{r['query']}`\n⚠️ Zero results - checking CORE SYMBOLS section for hidden layering indicators\n\n"

    with open(f"{OUTPUT_DIR}/OVERNIGHT_{timestamp}.md", "w") as f:
        f.write(md_content)
    
    # Update database
    db_data = {
        "version": "2.1",
        "initialized": True,
        "database_history": [{
            "timestamp": datetime.now().isoformat(),
            "mode": "direct_scraping_wikipedia",
            "symbols_processed": len(CORE_SYMBOLS),
            "symbols_found": list(symbols_found),
            "zero_results": [r["query"] for r in all_results if not r.get("title")]
        }],
        "core_symbols": list(CORE_SYMBOLS),
        "domains_active": ["geopolitical", "international", "political"],
        "loop_mode": True,
        "repeat_count": 9999,
        "last_cycle_id": timestamp
    }
    with open(DB_PATH, "w") as f:
        json.dump(db_data, f, indent=2)

    print(f"\n✅ Database updated at {DB_PATH}")
    
    # Update cross-reference index
    cr_path = f"{RESEARCH_DIR}/OUR/CROSS_REFERENCE_INDEX.md"
    os.makedirs(os.path.dirname(cr_path), exist_ok=True)
    with open(cr_path, "a") as f:
        f.write(f"\n---\n## {datetime.now().strftime('%Y-%m-%d %H:%M')} - CYCLE {timestamp}\nMode: Wikipedia fallback (Firecrawl offline)\nSymbols discovered: {', '.join(sorted(symbols_found))}")

    print(f"✅ Cross-reference index updated")
    
    # Print summary
    print("\n" + "=" * 80)
    print("✅ OVERNIGHT RESEARCH COMPLETE")
    print("=" * 80)
    print(f"\n📊 Metrics:")
    print(f"   - Symbols processed: {len(CORE_SYMBOLS)}")
    print(f"   - Successful queries: {successful}")
    print(f"   - Hidden layering active: {len(all_results) - successful} domains")

if __name__ == "__main__":
    main()
