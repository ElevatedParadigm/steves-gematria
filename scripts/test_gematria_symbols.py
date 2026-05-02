#!/usr/bin/env python3
"""
🧙‍♂️ STEVE'S GEMATRIA OVERNIGHT RESEARCH - SYMBOL TEST RUN
============================================================
Testing with URLs likely to contain core gematria symbols.

© Steve's Gematria System
"""

import json
from pathlib import Path
from rich.console import Console
from datetime import datetime
import re

BASE_DIR = Path.home() / ".hermes" / "gematria"
GEMATRIA_DB = BASE_DIR / "gematria_database.json"


class GematriaSymbolTester:
    """Test web scraping for gematria symbols."""
    
    CORE_SYMBOLS = {
        "124": {"name": "Universal Bridge", "domain": "Water"},
        "963": {"name": "Frequency/Air", "domain": "Air"},
        "55": {"name": "Fire/Elemental Force", "domain": "Fire"},
        "111": {"name": "Activation/Spirit", "domain": "Spirit"},
        "279": {"name": "Cycle Turning", "domain": "Earth"},
        "666": {"name": "Completion/Wholeness", "domain": "Fire"}
    }

    def __init__(self, db_path: Path):
        self.db_path = db_path
    
    def fetch_page(self, url: str) -> dict:
        """Fetch and parse a webpage."""
        print(f"  🔍 Fetching: {url[:80]}...")
        
        try:
            import requests
            
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; GematriaResearch/1.0)",
                "Accept-Language": "en-US,en;q=0.9"
            }
            
            response = requests.get(
                url, 
                headers=headers,
                timeout=30,
                allow_redirects=True
            )
            
            if response.status_code != 200:
                return {"success": False, "url": url, "error": f"HTTP {response.status_code}"}
            
            html = response.text
            
            # Remove script/style tags
            clean_html = re.sub(r'<script.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
            clean_html = re.sub(r'<style.*?</style>', '', clean_html, flags=re.DOTALL | re.IGNORECASE)
            
            # Extract headings
            markdown_content = ""
            for heading_level in [1, 2, 3]:
                heading_tag = f'h{heading_level}'
                for match in re.finditer(f'<{heading_tag}[^>]*>(.*?)</{heading_tag}>', clean_html, re.IGNORECASE | re.DOTALL):
                    text = match.group(1).strip()
                    if text:
                        markdown_content += f"#{heading_level} {text[:200]}\n\n"
            
            # Extract paragraphs (first 5)
            para_count = 0
            for match in re.finditer(r'<p[^>]*>(.*?)</p>', clean_html, re.IGNORECASE | re.DOTALL):
                if para_count >= 5:
                    break
                text = match.group(1).strip()
                if text and len(text) < 2000:
                    markdown_content += f"{text[:500]}\n\n"
                    para_count += 1
            
            title_match = re.search(r'<title>(.*?)</title>', clean_html, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else ""
            
            desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
            description = desc_match.group(1).strip()[:300] if desc_match else ""
            
            return {"success": True, "url": response.url, "markdown": markdown_content[:20000], "title": title[:300], "description": description}
            
        except Exception as e:
            return {"success": False, "url": url, "error": f"{type(e).__name__}: {str(e)[:150]}"}

    def detect_symbol_patterns(self, content: str) -> list:
        """Detect which core symbols appear in the scraped content."""
        found_symbols = []
        
        for symbol_value in self.CORE_SYMBOLS.keys():
            if symbol_value.lower() in content.lower():
                found_symbols.append(symbol_value)
        
        return sorted(found_symbols)

    def extract_domains(self, content: str) -> list:
        """Extract which domains appear in the content."""
        domain_keywords = {
            "Political": ["government", "politics", "elected", "senate", "congress", "administration"],
            "Military": ["troop", "deployment", "defence", "army", "military", "soldier", "bunker"],
            "Elemental": ["fire", "water", "air", "earth", "volcano", "tsunami", "hurricane"],
            "Religious": ["god", "faith", "church", "pray", "bible", "temple", "sacred"],
            "Geopolitical": ["nato", "trade", "embargo", "sanctions", "diplomatic", "treaty"]
        }
        
        found_domains = []
        content_lower = content.lower()
        
        for domain, keywords in domain_keywords.items():
            for keyword in keywords:
                if keyword in content_lower and domain not in found_domains:
                    found_domains.append(domain)
        
        return found_domains
    
    def extract_elemental_forces(self, content: str) -> list:
        """Extract which elemental forces appear in the content."""
        elemental_keywords = {
            "fire": ["fire", "burning", "hot", "inferno"],
            "water": ["water", "wet", "rain", "ocean", "river", "tsunami", "flood"],
            "air": ["wind", "air", "breath", "fly", "soar"],
            "earth": ["earth", "land", "ground", "stone", "mountain", "soil"]
        }
        
        found_elements = []
        content_lower = content.lower()
        
        for element, keywords in elemental_keywords.items():
            for keyword in keywords:
                if keyword in content_lower and element not in found_elements:
                    found_elements.append(element)
                    break
        
        return found_elements

    def analyze_and_store(self, article_data: dict):
        """Analyze scraped content and store findings in database."""
        
        if not article_data.get("success"):
            print(f"    ❌ Skipping analysis - fetch failed")
            return
        
        symbols_found = self.detect_symbol_patterns(article_data["markdown"])
        domains_found = self.extract_domains(article_data["markdown"])
        elements_found = self.extract_elemental_forces(article_data["markdown"])
        
        analysis_record = {
            "analysis_id": f"overnight_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "source_url": article_data["url"],
            "title": article_data.get("title", "")[:500],
            "description": article_data.get("description", "")[:500],
            "symbols_detected": symbols_found,
            "domains_detected": domains_found,
            "elements_detected": elements_found,
            "analysis_time": datetime.now().isoformat(),
            "markdown_snippet": article_data["markdown"][:10000]
        }
        
        if not self.db_path.exists():
            db = {"metadata": {}, "entries": {}, "images": [], "overnight_analyses": []}
        else:
            try:
                with open(self.db_path, 'r') as f:
                    db = json.load(f)
                
                if "overnight_analyses" not in db:
                    db["overnight_analyses"] = []
                    
            except Exception as e:
                print(f"    ⚠️  Error loading database: {e}")
                db = {"overnight_analyses": []}
        
        db["overnight_analyses"].append(analysis_record)
        
        if "metadata" in db and isinstance(db["metadata"], dict):
            try:
                db["metadata"]["last_updated"] = datetime.now().isoformat()
            except:
                pass
        
        with open(self.db_path, 'w') as f:
            json.dump(db, f, indent=2)
        
        print(f"    ✓ Analysis stored! ({len(symbols_found)} symbols detected)")
        if domains_found:
            print(f"      Domains: {', '.join(domains_found)}")
        if elements_found:
            print(f"      Elements: {', '.join(elements_found)}")

    
def main():
    """Test run with symbol-rich URLs."""
    
    console = Console()
    
    print("""
=======================================================
🧙‍♂️ STEVE'S GEMATRIA OVERNIGHT RESEARCH - SYMBOL TEST
=======================================================
Testing Wikipedia articles likely to contain gematria symbols.

Core Symbols: 124, 963, 55, 111, 279, 666
=======================================================

✅ API Status: 
   Using FREE requests library (no API key needed!)
""")

    scraper = GematriaSymbolTester(GEMATRIA_DB)
    
    # URLs likely to contain our core symbols
    test_urls = [
        # Number-themed articles - most likely to hit gematria numbers!
        "https://en.wikipedia.org/wiki/124_(number)",
        "https://en.wikipedia.org/wiki/963_(number)",
        "https://en.wikipedia.org/wiki/55_(number)",
        "https://en.wikipedia.org/wiki/666",  # Most likely!
        "https://en.wikipedia.org/wiki/Triple_six",
        
        # Spiritual/numerology related
        "https://en.wikipedia.org/wiki/Angelic_number_111",
        "https://en.wikipedia.org/wiki/Numerology",
        
        # Elemental themes
        "https://en.wikipedia.org/wiki/Fire",
        "https://en.wikipedia.org/wiki/Water_(element)"
    ]
    
    print(f"\n🔍 Scraping {len(test_urls)} URLs for symbol patterns...")
    
    total_symbols = []
    for i, url in enumerate(test_urls, 1):
        print(f"\n  [{i}/{len(test_urls)}] Testing: {url[:60]}...")
        
        article_data = scraper.fetch_page(url)
        
        if article_data.get("success"):
            symbols = scraper.detect_symbol_patterns(article_data["markdown"])
            domains = scraper.extract_domains(article_data["markdown"])
            elements = scraper.extract_elemental_forces(article_data["markdown"])
            
            # Store analysis regardless
            scraper.analyze_and_store(article_data)
            
            if symbols or domains or elements:
                print(f"    📊 Patterns:")
                if symbols:
                    display_symbols = []
                    for s in symbols[:3]:  # Show max 3
                        sym_name = scraper.CORE_SYMBOLS[s]["name"]
                        display_symbols.append(f"{s} ({sym_name})")
                    print(f"       {', '.join(display_symbols)}")
                if domains:
                    print(f"       Domains: {', '.join(domains)}")
                if elements:
                    print(f"       Elements: {', '.join(elements)}")
                
                total_symbols.extend(symbols)
        else:
            print(f"    ❌ Failed to fetch")
            print(f"       Error: {article_data.get('error', 'Unknown')[:100]}")
    
    # Summary
    print(f"\n📊 TEST COMPLETE - Pattern Summary:")
    unique_symbols = sorted(set(total_symbols))
    print(f"   Unique symbols found in this test run: {len(unique_symbols)}")
    for sym in unique_symbols:
        name = scraper.CORE_SYMBOLS[sym]["name"]
        print(f"   ✓ {sym}: {name}")
    
    return len(unique_symbols) > 0


if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n⚠️  No core symbols detected in this test run")
    except ImportError as e:
        print(f"\n❌ Missing dependency: {e}")
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {str(e)[:200]}")
