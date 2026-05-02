#!/usr/bin/env python3
"""
Minimal Overnight Research Engine - Standalone version
No external dependencies beyond firecrawl-py
"""

import os
import sys
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime
import requests
from firecrawl import FirecrawlApp

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG = {
    "api_key_env": "~/.hermes/.env",
    "output_dir": Path.home() / ".hermes/gematria/obsidian_exports",
    "research_iterations": 2,
    "domains": [
        {"name": "geographic", "keywords": ["mountains", "rivers", "cities", "valleys"]},
        {"name": "military", "keywords": ["division", "battalion", "regiment", "company"]},
        {"name": "elemental", "keywords": ["fire force", "water force", "earth force", "air force"]},
        {"name": "religious", "keywords": ["temple", "covenant", "sacred", "prophet"]},
    ],
}

CONFIG["output_dir"] = CONFIG["output_dir"].resolve()

# Load API key from environment
ENV_PATH = Path.home() / ".hermes" / ".env"
FIRECRAWL_API_KEY = ""
if ENV_PATH.exists():
    with open(ENV_PATH) as f:
        for line in f:
            if line.startswith("FIRECRAWL_API_KEY="):
                FIRECRAWL_API_KEY = line.strip().split("=")[1]
                break

# ============================================================================
# MAIN RESEARCH FUNCTION
# ============================================================================

def extract_keywords_for_domain(domain_name: str, keywords: list) -> list:
    """Extract research topics from domain keywords."""
    # Simple deterministic generation based on domain
    base_topics = [
        f"Analysis of {domain_name} patterns",
        f"Connection between {domain_name} and gematria symbols",
        f"Historical context for {domain_name} references",
        f"Modern interpretations of {domain_name} terminology",
    ]
    return base_topics[:2]

def query_firecrawl(topics: list, domain: dict) -> list:
    """Query Firecrawl API for research topics."""
    if not FIRECRAWL_API_KEY:
        print(f"⚠️  Warning: No FIRECRAWL_API_KEY found in {CONFIG['api_key_env']}")
        print("   Skipping cloud research cycle.")
        return []
    
    app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
    
    # Generate search queries from topics
    search_queries = [
        f"{topic} gematria analysis" for topic in topics[:3]
    ]
    
    results = []
    for query in search_queries:
        try:
            # Simple Wikipedia scrape - this is just a test/scrape operation
            scrape_result = app.scrape(
                url="http://localhost:3002/v1/scrape?url=https://en.wikipedia.org/wiki/Number",  # Using local Firecrawl instance
            )
            
            if "content" in scrape_result or "markdown" in scrape_result:
                results.append({
                    "topic": query,
                    "timestamp": datetime.now().isoformat(),
                    "domain": domain["name"],
                    "source_type": "wiki",
                })
        except Exception as e:
            print(f"   Note: Could not fetch {query}: {str(e)[:50]}...")
    
    return results

def process_and_save_results(cycle_number: int, cycle_results: list):
    """Process and save research cycle results."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    
    # Generate deterministic report content
    report_content = f"""# Overnight Research - Cycle {cycle_number}

**Timestamp:** {timestamp}
**API Mode:** Cloud API ({'✓ Active' if FIRECRAWL_API_KEY else '✗ Inactive'})

## Cycle Results

"""
    
    if cycle_results:
        for result in cycle_results:
            report_content += f"### {result.get('topic', 'Unknown Topic')}\n\n"
            report_content += f"*Domain:* {result.get('domain', 'N/A')}\n"
            report_content += f"*Type:* {result.get('source_type', 'unknown')}\n"
            report_content += "---\n\n"
    else:
        report_content += "_No results collected this cycle._\n"
    
    report_path = CONFIG["output_dir"] / f"overnight_research_cycle_{cycle_number}_{timestamp}.md"
    
    with open(report_path, "w") as f:
        f.write(report_content)
    
    print(f"✓ Saved cycle {cycle_number} results to: {report_path}")
    return report_path

def main():
    """Main research loop."""
    print("=" * 60)
    print("🌙 Overnight Research Engine - Standalone Mode")
    print("=" * 60)
    print(f"\n📍 Output Directory: {CONFIG['output_dir']}")
    print(f"🔑 API Key Status: {'✓ Configured' if FIRECRAWL_API_KEY else '✗ Not Found'}")
    
    base_time = time.time()
    
    for cycle in range(1, CONFIG["research_iterations"] + 1):
        print(f"\n{'─' * 50}")
        print(f"🔄 Starting Research Cycle {cycle} of {CONFIG['research_iterations']}")
        
        # Wait between cycles to avoid rate limiting
        if cycle > 1:
            wait_time = 60 * (cycle - 1)  # 60s, then 120s
            print(f"⏳ Waiting {wait_time}s before next cycle...")
            time.sleep(wait_time)
        
        # Run research for each domain
        all_results = []
        for domain in CONFIG["domains"]:
            print(f"\n   📍 Domain: {domain['name'].title()}")
            
            topics = extract_keywords_for_domain(domain["name"], domain.get("keywords", []))
            results = query_firecrawl(topics, domain)
            
            if results:
                all_results.extend(results)
        
        # Process and save cycle results
        cycle_results = all_results[:5]  # Limit to 5 per cycle
        report_path = process_and_save_results(cycle, cycle_results)
        
        print(f"\n   ✓ Cycle {cycle} complete!")

    # Check elapsed time
    elapsed = int(time.time() - base_time)
    print(f"\n{'─' * 50}")
    print(f"✅ All research cycles complete! Total time: {elapsed}s")
    
    print("\n📊 Generated reports:")
    for p in CONFIG["output_dir"].glob("overnight_research_cycle_*.md"):
        print(f"   - {p}")

if __name__ == "__main__":
    main()
