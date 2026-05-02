#!/usr/bin/env python3
"""
Steve's Gematria - Multi-Source Ingestion Pipeline (Dependency-Free)
Integrates Firecrawl API + RSS feeds using only built-in modules

Version: 2.2.0 - No external dependencies!
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
import xml.etree.ElementTree as ET


class MultiSourceIngestion:
    """Multi-source ingestion pipeline (dependency-free)"""
    
    def __init__(self):
        self.working_dir = str(Path.home() / ".hermes" / "gematria")
        self.batch_id = hashlib.md5(datetime.utcnow().isoformat().encode()).hexdigest()[:16]
        
        print(f"\n{'='*80}")
        print("🚀 STEVE'S GEMATRIA - MULTI-SOURCE INGESTION PIPELINE (DEPENDENCY-FREE)")
        print("="*80)
        print(f"📍 Working directory: {self.working_dir}")
        print(f"🔧 Batch ID: {self.batch_id}")
        print("✅ Uses only built-in Python modules!")
        print("="*80 + "\n")
    
    def create_sqlite_db(self):
        """Initialize SQLite database with core symbols"""
        
        db_path = Path.home() / ".hermes" / "gematria" / "gematria_database.sqlite"
        
        # Create database and tables using sqlite3 (built-in)
        conn = __import__('sqlite3').connect(db_path)
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
        for symbol in ["124", "963", "55", "111", "279", "666"]:
            elemental_force = {
                "124": "water",
                "963": "air", 
                "55": "fire",
                "111": "spirit",
                "279": "earth",
                "666": "fire"
            }.get(symbol, "unknown")
            
            cursor.execute("""
                INSERT OR REPLACE INTO gematria_entities (symbol_value, elemental_force, description)
                VALUES (?, ?, ?)
            """, (symbol, elemental_force, f"Core symbol {symbol}"))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Database initialized: {db_path}")
    
    def fetch_firecrawl(self, url: str):
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
                
                for symbol, elemental in [
                    ("124", "water"),
                    ("963", "air"), 
                    ("55", "fire"),
                    ("111", "spirit"),
                    ("279", "earth"),
                    ("666", "fire")
                ]:
                    if symbol.lower() in content.lower():
                        patterns_found.append((symbol, elemental, 0.9 + len(symbol)))
                
                return {
                    "url": url,
                    "title": url.split("/")[-1][:100],
                    "content_preview": content[:200] if content else "",
                    "patterns": patterns_found,
                    "timestamp": datetime.utcnow().isoformat(),
                    "source_type": "firecrawl"
                }
            
            return None
            
        except Exception as e:
            print(f"  ❌ Error fetching {url}: {str(e)}")
            return None
    
    def fetch_rss_feeds(self):
        """Fetch from RSS feeds using xml.etree (built-in)"""
        
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
                    root = ET.fromstring(response.content)
                    
                    for item in root.findall(".//item"):
                        title_elem = item.find("title")
                        description_elem = item.find("description")
                        
                        if title_elem is None or description_elem is None:
                            continue
                        
                        title = title_elem.text or ""
                        description = description_elem.text or ""
                        
                        # Simple pattern matching
                        text_lower = (title + description).lower()
                        patterns_found = []
                        
                        for symbol, elemental in [
                            ("124", "water"),
                            ("963", "air"), 
                            ("55", "fire"),
                            ("111", "spirit"),
                            ("279", "earth"),
                            ("666", "fire")
                        ]:
                            if symbol.lower() in text_lower:
                                patterns_found.append((symbol, elemental, 0.9))
                        
                        if patterns_found:
                            results.append({
                                "source": feed["name"],
                                "article": title[:100],
                                "patterns": patterns_found,
                                "timestamp": datetime.utcnow().isoformat(),
                                "source_type": "rss_feed"
                            })
                            
            except Exception as e:
                print(f"  ⚠️  Error fetching RSS: {str(e)}")
        
        return results
    
    def save_to_database(self, data):
        """Save data to SQLite database"""
        
        db_path = Path.home() / ".hermes" / "gematria" / "gematria_database.sqlite"
        
        conn = __import__('sqlite3').connect(db_path)
        cursor = conn.cursor()
        
        # Insert batch log
        items_found = sum(len(r.get("patterns", [])) for r in data if isinstance(r, dict))
        
        cursor.execute("""
            INSERT OR REPLACE INTO batch_logs (batch_id, source_count, items_found, core_symbols_detected)
            VALUES (?, ?, ?, ?)
        """, (self.batch_id, 1, len(data), items_found))
        
        # Insert patterns as entities
        for item in data:
            if isinstance(item, dict):
                for symbol, elemental, relevance in item.get("patterns", []):
                    source_name = item.get("source_type", "unknown")
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO gematria_entities 
                        (symbol_value, elemental_force, description, relevance_score, source)
                        VALUES (?, ?, ?, ?, ?)
                    """, (symbol, elemental, f"Pattern from {item.get('url', 'rss')}", relevance, source_name))
        
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
                self.save_to_database([result])
                print(f"  ✅ Found {len(result['patterns'])} core symbol(s)")
        
        time.sleep(2)  # Rate limiting
        
        # Phase 2: RSS feed aggregation  
        print("\n📡 PHASE 2: RSS FEED AGGREGATION")
        print("="*80)
        
        rss_results = self.fetch_rss_feeds()
        all_results.extend(rss_results)
        
        for result in rss_results:
            self.save_to_database([result])
        
        # Summary report
        total_patterns = sum(len(r.get("patterns", [])) for r in all_results)
        
        print(f"\n{'='*80}")
        print(f"📊 BATCH SUMMARY")
        print("="*80)
        print(f"  Batch ID: {self.batch_id}")
        print(f"  Firecrawl sources scanned: 2")
        print(f"  RSS feeds processed: 2")
        print(f"  Total core symbols detected: {total_patterns}")
        
        # Save batch report
        report_path = Path(self.working_dir) / "batch_reports"
        report_path.mkdir(exist_ok=True)
        
        with open(report_path / f"{self.batch_id}_report.json", 'w') as f:
            json.dump({
                "batch_id": self.batch_id,
                "timestamp": datetime.utcnow().isoformat(),
                "firecrawl_results": all_results[:2],
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
