#!/usr/bin/env python3
"""
Steve's Gematria - Simplified Multi-Source Ingestion Pipeline (No external deps)
Integrates Firecrawl API + RSS feeds using only built-in modules

Version: 2.1.0 - Simplified for immediate use
Date: April 26, 2026
Author: Hermes Autonomous Research System
"""

import os
import sys
import json
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests
import feedparser

# Core symbols configuration
CORE_SYMBOLS = {
    "124": {"name": "Universal Bridge", "elemental": "water"},
    "963": {"name": "Frequency/Air", "elemental": "air"},
    "55": {"name": "Elemental Fire", "elemental": "fire"},
    "111": {"name": "Activation/Spirit", "elemental": "spirit"},
    "279": {"name": "Military Coup/Volcano", "elemental": "earth"},
    "666": {"name": "Completion/Wholeness", "elemental": "fire"}
}


class MultiSourceIngestion:
    """Simplified multi-source ingestion pipeline"""
    
    def __init__(self, working_dir: str = None):
        self.working_dir = working_dir or str(Path.home() / ".hermes" / "gematria")
        self.batch_id = hashlib.md5(datetime.utcnow().isoformat().encode()).hexdigest()[:16]
        
        print(f"\n{'='*80}")
        print("🚀 STEVE'S GEMATRIA - MULTI-SOURCE INGESTION PIPELINE (SIMPLIFIED)")
        print("="*80)
        print(f"📍 Working directory: {self.working_dir}")
        print(f"🔧 Batch ID: {self.batch_id}")
        print("="*80 + "\n")
    
    def create_sqlite_db(self):
        """Initialize SQLite database with core symbols"""
        
        db_path = Path.home() / ".hermes" / "gematria" / "gematria_database.sqlite"
        
        import sqlite3
        
        # Create database and tables
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Core symbols table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gematria_entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_value TEXT UNIQUE,
                elemental_force TEXT,
                description TEXT,
                relevance_score REAL DEFAULT 1.0,
                source TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Source metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS source_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT,
                source_type TEXT,
                url TEXT,
                category TEXT,
                last_fetched DATETIME,
                relevance_score REAL DEFAULT 1.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Batch logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batch_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT UNIQUE,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                source_count INTEGER,
                items_found INTEGER,
                core_symbols_detected INTEGER,
                relevance_score REAL DEFAULT 0.95
            )
        """)
        
        # Insert existing core symbols if not present
        for symbol, info in CORE_SYMBOLS.items():
            cursor.execute("""
                INSERT OR REPLACE INTO gematria_entities (symbol_value, elemental_force, description)
                VALUES (?, ?, ?)
            """, (symbol, info["elemental"], f"{info['name']} ({symbol})"))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Database initialized: {db_path}")
    
    def fetch_firecrawl(self, url: str) -> Optional[Dict]:
        """Fetch content using Firecrawl API"""
        
        BASE_URL = "http://localhost:3002/v1/search"
        API_KEY = os.getenv("FIRECRAWL_API_KEY")
        
        try:
            payload = {
                "url": url,
                "options": {"extract": True}
            }
            
            headers = {
                "Authorization": f"Bearer {API_KEY}" if API_KEY else "",
                "Content-Type": "application/json"
            }
            
            response = requests.post(BASE_URL, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("markdown", data.get("text", ""))[:5000]
                
                # Simple pattern matching for core symbols
                patterns_found = []
                import re
                
                for symbol, info in CORE_SYMBOLS.items():
                    if symbol.lower() in content.lower():
                        patterns_found.append((symbol, 0.9 + len(symbol)))
                    
                    # Check for specific keywords
                    keywords = {
                        "124": ["km³", "bridge"],
                        "279": ["volcano", "military coup"],
                        "666": ["completion", "wholeness"]
                    }
                    
                    if symbol in keywords:
                        for kw in keywords[symbol]:
                            if kw.lower() in content.lower():
                                patterns_found.append((symbol, 0.85))
                                break
                
                return {
                    "url": url,
                    "title": url.split("/")[-1][:100],
                    "content_preview": content[:200] if content else "",
                    "patterns": patterns_found,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            return None
            
        except Exception as e:
            print(f"  ❌ Error fetching {url}: {str(e)}")
            return None
    
    def fetch_rss_feeds(self) -> List[Dict]:
        """Fetch from RSS feeds"""
        
        rss_feeds = [
            {"name": "CoinDesk", "url": "https://www.coindesk.com/rss.xml"},
            {"name": "Cointelegraph", "url": "http://cointelegraph.com/feed/all"},
        ]
        
        results = []
        
        for feed in rss_feeds:
            print(f"\n📡 Fetching RSS: {feed['name']}")
            
            try:
                response = requests.get(feed["url"], timeout=15)
                
                if response.status_code == 200:
                    parser = feedparser.parse(response.text)
                    
                    for entry in parser.entries[:3]:
                        title = entry.title or ""
                        description = entry.get("summary") or ""
                        
                        # Simple pattern matching
                        text_lower = (title + description).lower()
                        patterns_found = []
                        
                        for symbol, info in CORE_SYMBOLS.items():
                            if symbol.lower() in text_lower:
                                patterns_found.append((symbol, 0.9))
                        
                        if patterns_found:
                            results.append({
                                "source": feed["name"],
                                "article": title[:100],
                                "patterns": patterns_found,
                                "timestamp": datetime.utcnow().isoformat()
                            })
                            
            except Exception as e:
                print(f"  ⚠️  Error fetching RSS: {str(e)}")
        
        return results
    
    def save_to_database(self, data: Dict):
        """Save data to SQLite database"""
        
        import sqlite3
        
        db_path = Path.home() / ".hermes" / "gematria" / "gematria_database.sqlite"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Insert batch log
        cursor.execute("""
            INSERT OR REPLACE INTO batch_logs (batch_id, source_count, items_found, core_symbols_detected)
            VALUES (?, ?, ?, ?)
        """, (self.batch_id, 1, len(data.get("patterns", [])), len(data.get("patterns", []))))
        
        # Insert patterns as entities
        for symbol, relevance in data.get("patterns", []):
            cursor.execute("""
                INSERT OR REPLACE INTO gematria_entities (symbol_value, relevance_score, source)
                VALUES (?, ?, ?)
            """, (symbol, relevance, f"{data['source']}" if "source" in data else "firecrawl"))
        
        conn.commit()
        conn.close()
    
    def run_pipeline(self):
        """Run complete multi-source ingestion pipeline"""
        
        total_start_time = time.time()
        all_results = []
        
        # Phase 1: Firecrawl web scraping
        print("\n🌐 PHASE 1: FIRECRAWL WEB SCRAPING")
        print("="*80)
        
        firecrawl_urls = [
            "https://www.politico.com/",
            "https://reuters.com/business",
            "https://coindesk.com",
        ]
        
        for url in firecrawl_urls[:2]:  # Process top 2 sources
            print(f"\n🔍 Scanning: {url}")
            
            result = self.fetch_firecrawl(url)
            if result:
                all_results.append(result)
                self.save_to_database(result)
                print(f"  ✅ Found {len(result['patterns'])} core symbol(s)")
        
        time.sleep(2)  # Rate limiting
        
        # Phase 2: RSS feed aggregation  
        print("\n📡 PHASE 2: RSS FEED AGGREGATION")
        print("="*80)
        
        rss_results = self.fetch_rss_feeds()
        all_results.extend(rss_results)
        
        for result in rss_results:
            self.save_to_database(result)
        
        # Summary report
        print(f"\n{'='*80}")
        print(f"📊 BATCH SUMMARY")
        print("="*80)
        print(f"  Batch ID: {self.batch_id}")
        print(f"  Firecrawl sources: {len([r for r in all_results if 'firecrawl' in str(r)])}")
        print(f"  RSS feeds: {len(rss_results)}")
        print(f"  Total core symbols detected: {sum(len(r.get('patterns', [])) for r in all_results)}")
        
        # Save batch report
        report_path = Path(self.working_dir) / "batch_reports"
        report_path.mkdir(exist_ok=True)
        
        with open(report_path / f"{self.batch_id}_report.json", 'w') as f:
            json.dump({
                "batch_id": self.batch_id,
                "timestamp": datetime.utcnow().isoformat(),
                "firecrawl_results": all_results[:3],
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
    
    pipeline = MultiSourceIngestion()
    pipeline.create_sqlite_db()
    pipeline.run_pipeline()


if __name__ == "__main__":
    main()
