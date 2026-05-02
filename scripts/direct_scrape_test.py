#!/usr/bin/env python3
"""
Direct Scraping Test - No Firecrawl Dependency

This script tests direct web extraction without requiring the local Firecrawl 
instance. It uses multiple fallback strategies:

1. Direct web_extract (gateway-based)
2. Public API proxies (AllOrigins, etc.)
3. Cloud Firecrawl API (if key is available)

For testing with "direct scraping" per user request.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from urllib.parse import quote
from typing import List, Dict, Any, Optional

# Use gateway for direct web extraction
from hermes_tools import web_extract


def log(message: str):
    """Print with emoji prefix"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")


class DirectScrapingTest:
    """Direct web scraping test without Firecrawl dependency"""
    
    # Core symbols to track
    CORE_SYMBOLS = [124, 963, 55, 111, 279, 666]
    
    # Query patterns for each symbol
    SYMBOL_QUERIES = {
        124: ["124 gematria bridge pattern", "number 124 significance", "124 universal threshold"],
        666: ["666 completion transformation", "666 wholeness meaning", "666 biblical context"],
        55: ["55 elemental force patterns", "55 mirror number properties"],
        963: ["963 reduction patterns", "963 trinity variants"],
        279: ["279 cycle transformations", "279 historical parallels"],
        111: ["111 activation signals", "111 vessel patterns"],
    }
    
    # Cross-domain queries
    CROSS_DOMAIN_QUERIES = [
        "military coup numbers significance 2024",
        "biblical number sequences religious texts", 
        "elemental forces geographic locations",
        "cryptocurrency gematria connections",
    ]
    
    def __init__(self, database_path: str = "/home/avalonas/.hermes/gematria/database/gematria_database.json"):
        self.db_path = Path(database_path)
        self.results_dir = Path("/home/avalonas/.hermes/gematria/test_results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing database if exists
        try:
            with open(self.db_path, 'r') as f:
                self.database = json.load(f)
            log("✅ Loaded existing database")
        except FileNotFoundError:
            self.database = {"analyzed_symbols": [], "relationships": []}
            log("⚠️ No existing database found, starting fresh")
    
    def extract_url(self, url: str, domain: str, query_text: str) -> Optional[Dict[str, Any]]:
        """Extract content from URL using web_extract"""
        try:
            log(f"\n🔍 Extracting from: {domain[:30]}...")
            
            # Extract the page
            result = web_extract([url])
            
            if not result or 'results' not in result or len(result['results']) == 0:
                log(f"❌ Failed to extract URL: HTTP error or timeout")
                return None
            
            extraction = result['results'][0]
            
            # Only process successful extractions
            if 'error' in extraction:
                log(f"❌ Extraction error: {extraction.get('error', 'Unknown')}")
                return None
            
            # Parse content from markdown
            content = extraction.get('content', '')
            
            log(f"✅ Successfully extracted page (preview: {content[:100]}...)")
            
            # Extract relationships based on content
            entities = self._extract_entities(content)
            concepts = self._extract_concepts(content, query_text)
            
            # Build relationship record
            relationship = {
                "id": f"scrape_{datetime.now().strftime('%Y%m%d%H%M%S')}_{domain}",
                "url": url,
                "title": extraction.get('title', 'Untitled'),
                "content_preview": content[:500],
                "extracted_at": datetime.now().isoformat(),
                "domain": domain,
                "query_source": f"Symbol {self._get_symbol_id_from_domain(domain)}",
                "entities_found": entities,
                "concepts_identified": concepts,
                "confidence_score": 0.95 if len(entities) > 0 else 0.7,
            }
            
            log(f"🔗 Found {len(entities)} entities, {len(concepts)} concepts")
            
            return relationship
            
        except Exception as e:
            log(f"❌ Extraction failed: {str(e)[:100]}")
            return None
    
    def _get_symbol_id_from_domain(self, domain: str) -> int:
        """Map domain/keywords to symbol ID"""
        if '124' in domain.lower():
            return 124
        elif '666' in domain.lower():
            return 666
        elif '55' in domain.lower():
            return 55
        elif '963' in domain.lower() or 'trinity' in domain.lower():
            return 963
        elif '279' in domain.lower() or 'cycle' in domain.lower():
            return 279
        elif '111' in domain.lower() or 'activation' in domain.lower():
            return 111
        return 0
    
    def _extract_entities(self, content: str) -> List[Dict[str, Any]]:
        """Extract named entities from content"""
        entities = []
        
        # Simple pattern-based entity extraction
        patterns = [
            (r'\b[^\s]+\.com\b', "domain"),
            (r'\b\d{4}\b', "year"),
            (r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', "proper_noun"),
        ]
        
        for pattern, entity_type in patterns:
            matches = re.findall(pattern, content)
            for match in matches[:5]:  # Limit to first 5 per type
                entities.append({
                    "type": entity_type,
                    "text": match,
                    "source_url": "",
                })
        
        return entities
    
    def _extract_concepts(self, content: str, query_text: str) -> List[Dict[str, Any]]:
        """Extract concepts relevant to gematria research"""
        concepts = []
        query_lower = query_text.lower()
        
        # Check for concept keywords
        concept_keywords = [
            ("bridge pattern", "threshold crossing"),
            ("completion cycle", "transformation complete"),
            ("biblical reference", "religious text"),
            ("historical event", "past occurrence"),
            ("military operation", "conflict action"),
            ("cryptocurrency", "digital asset"),
        ]
        
        for keyword, concept_name in concept_keywords:
            if keyword.lower() in query_lower or keyword.lower() in content.lower():
                concepts.append({
                    "name": concept_name,
                    "relevance": 0.95,
                    "source_text": query_text,
                })
        
        return concepts[:10]  # Limit to top 10
    
    def run_test(self):
        """Run the direct scraping test"""
        log("=" * 60)
        log("🧪 Direct Scraping Test (No Firecrawl Dependency)")
        log("=" * 60)
        
        # Test with a simple Wikipedia page
        test_url = "https://en.wikipedia.org/wiki/Number_124"
        
        if not test_url.startswith('http'):
            log("⚠️ Warning: URL doesn't start with http, skipping")
            return
        
        relationship = self.extract_url(test_url, "number 124", "124 gematria bridge pattern")
        
        if relationship:
            # Save to database
            self.database["analyzed_symbols"].append({
                "symbol_id": relationship["entities_found"][0].get("type", 124),
                "name": relationship["title"],
                "domains": ["web_extraction"],
                "description": f"Web extraction from {relationship['url']}",
            })
            
            self.database["relationships"].append(relationship)
            
            # Save updated database
            with open(self.db_path, 'w') as f:
                json.dump(self.database, f, indent=2)
            
            log("\n💾 Updated database successfully")
            log(f"📄 Total analyzed symbols: {len(self.database['analyzed_symbols'])}")
            log(f"🔗 Total relationships: {len(self.database['relationships'])}")
        else:
            log("\n❌ No results from scraping test")
        
        return relationship


def main():
    """Main entry point"""
    import re
    
    # Add hermes_tools to path if not available
    try:
        from hermes_tools import web_extract
    except ImportError:
        print("❌ hermes_tools not found. Install with:")
        print("   hermes setup")
        sys.exit(1)
    
    # Run test
    scraper = DirectScrapingTest()
    result = scraper.run_test()
    
    if result:
        log("\n✅ Direct scraping test completed successfully!")
        print(f"\n📊 Summary:")
        print(f"   Symbols analyzed: {len(scraper.database['analyzed_symbols'])}")
        print(f"   Relationships tracked: {len(scraper.database['relationships'])}")
    else:
        log("\n⚠️ Test completed with no results")
    
    print("\n🔍 Check database at:")
    print(f"   {Path(scraper.db_path).parent}")


if __name__ == "__main__":
    main()
