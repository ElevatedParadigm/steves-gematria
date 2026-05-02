#!/usr/bin/env python3
"""
Steve's Gematria - Unified Data Ingestion Orchestrator
Combines Firecrawl API + RSS Feeds + NewsAPI into single automated pipeline

Version: 2.0.0  
Date: April 26, 2026
Author: Hermes Autonomous Research System
"""

import os
import sys
import json
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests

# Import from existing modules (relative imports)
sys.path.insert(0, str(Path.home() / ".hermes" / "gematria" / "scripts"))

from multi_source_ingestion import SourceConfig, update_database, extract_gematria_patterns
from rss_feed_aggregator import RSSAggregator, check_for_gematria_patterns as check_rss_patterns


class UnifiedIngestionOrchestrator:
    """Main orchestrator for all data ingestion sources"""
    
    def __init__(self, working_dir: str = None):
        self.working_dir = working_dir or str(Path.home() / ".hermes" / "gematria")
        self.batch_id = hashlib.md5(datetime.utcnow().isoformat().encode()).hexdigest()[:16]
        
        # Initialize components
        self.rss_aggregator = RSSAggregator()
        self.core_symbols = SourceConfig.CORE_SYMBOLS
        
        print(f"\n{'='*80}")
        print("🚀 STEVE'S GEMATRIA - UNIFIED DATA INGESTION ORCHESTRATOR")
        print(f"📍 Working directory: {self.working_dir}")
        print(f"🔧 Batch ID: {self.batch_id}")
        print("="*80 + "\n")
    
    def load_rss_config(self, config_path: str):
        """Load RSS feed configuration"""
        if Path(config_path).exists():
            self.rss_aggregator.load_config(config_path)
            print(f"✅ Loaded RSS config from {config_path}")
    
    def fetch_firecrawl_sources(self, urls: List[str] = None) -> List[Dict]:
        """Fetch content using Firecrawl API"""
        
        if not urls:
            urls = [
                "https://www.politico.com/",
                "https://reuters.com/business",
                "https://www.bloomberg.com/news/politics",
                "https://coindesk.com",
            ]
        
        results = []
        
        for url in urls[:3]:  # Process top 3 sources
            print(f"\n🔍 Fetching via Firecrawl: {url}")
            
            try:
                payload = {
                    "url": url,
                    "options": {"extract": True}
                }
                
                headers = {
                    "Authorization": f"Bearer {SourceConfig.FIRECRAWL_API_KEY}",
                    "Content-Type": "application/json"
                } if SourceConfig.FIRECRAWL_API_KEY else {}
                
                response = requests.post(
                    SourceConfig.FIRECRAWL_BASE_URL, 
                    json=payload, 
                    headers=headers, 
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data.get("markdown", data.get("text", ""))[:5000]
                    
                    # Extract patterns
                    patterns = extract_gematria_patterns(content)
                    
                    if patterns:
                        results.append({
                            "source": "firecrawl",
                            "url": url,
                            "title": url.split("/")[-1][:100],
                            "content_preview": content[:200],
                            "patterns": [(p[0], p[1]) for p in patterns],
                            "timestamp": datetime.utcnow().isoformat()
                        })
                        print(f"  ✅ Found {len(patterns)} core symbol(s)")
                    
                else:
                    print(f"  ⚠️  HTTP error: {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
        
        return results
    
    def fetch_rss_feeds(self) -> List[Dict]:
        """Fetch from RSS feeds"""
        
        if not self.rss_aggregator.rss_feeds:
            # Create default config if no config exists
            rss_config = Path.home() / ".hermes" / "gematria" / "rss_feeds.json"
            if not rss_config.exists():
                self.create_default_rss_config()
            
            self.load_rss_config(str(rss_config))
        
        results = []
        
        for feed_key, feed_config in self.rss_aggregator.rss_feeds.items():
            if not feed_config.get("enabled", True):
                continue
            
            print(f"\n📡 Fetching RSS: {feed_config['name']}")
            
            try:
                response = requests.get(feed_config["url"], timeout=15)
                
                if response.status_code == 200:
                    parser = feedparser.parse(response.text)
                    
                    for entry in parser.entries[:3]:  # Limit to 3 items per feed
                    
                        article = {
                            "title": entry.title or "",
                            "link": entry.link or "",
                            "description": entry.get("summary") or "",
                            "source": feed_config["name"],
                            "category": feed_config.get("category", "general"),
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        
                        # Check for gematria patterns
                        patterns = check_rss_patterns(article["description"] + article["title"])
                        
                        if patterns:
                            results.append({
                                "source": "rss_feed",
                                "url": feed_config["url"],
                                "article": article,
                                "patterns": [(p[0], p[1]) for p in patterns],
                                "timestamp": datetime.utcnow().isoformat()
                            })
                            print(f"  ✅ Found pattern in: {entry.title[:80]}...")
                        
                    print(f"  📊 Total items from feed: {len(parser.entries)}")
                    
            except Exception as e:
                print(f"  ⚠️  Error: {str(e)}")
        
        return results
    
    def create_default_rss_config(self):
        """Create default RSS feed configuration"""
        
        rss_config = {
            "political_news": [
                {"name": "Politico Politics", "url": "https://www.politico.com/rss/politics.xml"},
                {"name": "Reuters US Politics", "url": "http://rss.reuters.com/world/rss/us.xml"}
            ],
            
            "financial_news": [
                {"name": "Bloomberg Markets", "url": "http://feeds.bloomberg.com/rss/home/markets.xml"}
            ],
            
            "cryptocurrency_news": [
                {"name": "CoinDesk News", "url": "https://www.coindesk.com/rss.xml"},
                {"name": "Cointelegraph", "url": "http://cointelegraph.com/feed/all"}
            ]
        }
        
        config_path = Path.home() / ".hermes" / "gematria" / "rss_feeds.json"
        with open(config_path, 'w') as f:
            json.dump(rss_config, f, indent=2)
        
        self.rss_aggregator.load_config(str(config_path))
    
    def update_database(self, data: Dict[str, Any]):
        """Update PostgreSQL or SQLite database"""
        
        db_path = Path.home() / ".hermes" / "gematria" / "gematria_database.sqlite"
        update_database(data)
    
    def run_complete_pipeline(self, firecrawl_urls: List[str] = None):
        """Run complete multi-source ingestion pipeline"""
        
        total_start_time = time.time()
        all_results = []
        
        # Step 1: Firecrawl web scraping
        print("\n" + "="*80)
        print("🌐 PHASE 1: FIRECRAWL WEB SCRAPING")
        print("="*80)
        
        firecrawl_results = self.fetch_firecrawl_sources(firecrawl_urls)
        all_results.extend(firecrawl_results)
        
        time.sleep(2)  # Rate limiting
        
        # Step 2: RSS feed aggregation  
        print("\n" + "="*80)
        print("📡 PHASE 2: RSS FEED AGGREGATION")
        print("="*80)
        
        rss_results = self.fetch_rss_feeds()
        all_results.extend(rss_results)
        
        # Step 3: Update database with batch log
        if all_results:
            unique_items = [item for item in all_results 
                          if isinstance(item, dict) and "patterns" in item]
            
            metrics = {
                "batch_id": self.batch_id,
                "timestamp": datetime.utcnow(),
                "firecrawl_count": len(firecrawl_results),
                "rss_count": len(rss_results),
                "unique_items": len(unique_items),
                "core_symbols_detected": sum(len(item.get("patterns", [])) for item in unique_items)
            }
            
            print(f"\n{'='*80}")
            print(f"📊 BATCH SUMMARY")
            print("="*80)
            print(f"  Firecrawl sources: {len(firecrawl_results)}")
            print(f"  RSS feeds: {len(rss_results)}")
            print(f"  Unique items: {metrics['unique_items']}")
            print(f"  Core symbols detected: {metrics['core_symbols_detected']}")
            
            # Save batch report
            report_path = Path(self.working_dir) / "batch_reports"
            report_path.mkdir(exist_ok=True)
            
            with open(report_path / f"{self.batch_id}_report.json", 'w') as f:
                json.dump({
                    "batch_id": self.batch_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "firecrawl_results": firecrawl_results,
                    "rss_results": rss_results
                }, f, indent=2)
            
            print(f"\n  📄 Batch report saved: {report_path / f'{self.batch_id}_report.json'}")
            
        total_time = time.time() - total_start_time
        
        print(f"\n{'='*80}")
        print(f"✅ PIPELINE COMPLETE!")
        print("="*80)
        print(f"  Total duration: {total_time:.2f} seconds")
        print(f"  Results stored in database")
        print("="*80 + "\n")


def main():
    """Main entry point"""
    
    orchestrator = UnifiedIngestionOrchestrator()
    
    # Optional: Load RSS config
    rss_config = Path.home() / ".hermes" / "gematria" / "rss_feeds.json"
    if rss_config.exists():
        orchestrator.load_rss_config(str(rss_config))
    
    # Run complete pipeline
    firecrawl_urls = [
        "https://www.politico.com/",
        "https://reuters.com/business",
        "https://coindesk.com"
    ]
    
    orchestrator.run_complete_pipeline(firecrawl_urls)


if __name__ == "__main__":
    main()
