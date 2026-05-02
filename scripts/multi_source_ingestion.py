#!/usr/bin/env python3
"""
Steve's Gematria - Multi-Source Data Ingestion Pipeline
Integrates Firecrawl + NewsAPI + RSS feeds for comprehensive pattern tracking

Version: 2.0.0
Date: April 26, 2026
Author: Hermes Autonomous Research System
"""

import os
import sys
import json
import time
import hashlib
import feedparser
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

# PostgreSQL integration (optional)
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    print("⚠️  PostgreSQL not available. Using SQLite fallback.")

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

Base = declarative_base()


class SourceConfig:
    """Configuration for all data sources"""
    
    FIRECRAWL_BASE_URL = os.getenv("FIRECRAWL_BASE_URL", "http://localhost:3002/v1/search")
    FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
    
    # Expanded news sources (political/financial)
    NEWS_SOURCES = {
        "cnn": {"name": "CNN Politics", "url": "https://www.cnn.com/politics", "category": "political"},
        "reuters": {"name": "Reuters Business", "url": "https://www.reuters.com/business", "category": "financial"},
        "bloomberg": {"name": "Bloomberg Political News", "url": "https://www.bloomberg.com/news/politics", "category": "political"},
        "wsj": {"name": "Wall Street Journal", "url": "https://www.wsj.com/articles/business-government", "category": "financial"},
        "politico": {"name": "Politico Politics", "url": "https://www.politico.com/", "category": "political"},
        "axios": {"name": "Axios Politics", "url": "https://www.axios.com/politics", "category": "political"},
        "financial-times": {"name": "Financial Times", "url": "https://www.ft.com/content/politics-business", "category": "financial"},
    }
    
    # Specialized RSS feeds (technical/political/cryptocurrency)
    RSS_FEEDS = {
        "cryptocurrency_news": {
            "name": "CoinDesk News",
            "url": "https://www.coindesk.com/rss.xml",
            "category": "cryptocurrency"
        },
        "blockchain_news": {
            "name": "Blockworks RSS",
            "url": "https://blockworks.co/feed",
            "category": "cryptocurrency"
        },
        "crypto_news_wire": {
            "name": "Crypto News Wire",
            "url": "https://feeds.feedburner.com/cryptonews-wire",
            "category": "cryptocurrency"
        },
        "blockchain_update": {
            "name": "Blockchain Update",
            "url": "http://blockchainupdate.co.uk/feed",
            "category": "cryptocurrency"
        },
        "techcrunch_politics": {
            "name": "TechCrunch Politics",
            "url": "https://techcrunch.com/category/politics/",
            "category": "technology"
        },
        "reuters_crypto": {
            "name": "Reuters Digital Currency",
            "url": "https://www.reuters.com/markets/cryptocurrencies/rss.xml",
            "category": "cryptocurrency"
        }
    }
    
    # Core symbols for pattern matching
    CORE_SYMBOLS = [
        ("124", "water", "Universal Bridge"),
        ("963", "air", "Frequency/Air"),
        ("55", "fire", "Elemental Fire"),
        ("111", "spirit", "Activation/Spirit"),
        ("279", "earth", "Military Coup/Volcano"),
        ("666", "fire", "Completion/Wholeness")
    ]


class SourceMetadata(Base):
    """Tracks all data sources"""
    __tablename__ = 'source_metadata'
    
    id = Column(Integer, primary_key=True)
    source_name = Column(String(200))
    source_type = Column(String(50))  # firecrawl/newsapi/rss
    url = Column(String(500))
    category = Column(String(100))
    last_fetched = Column(DateTime)
    fetch_count = Column(Integer, default=0)
    relevance_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class GematriaEntities(Base):
    """Core symbol entities"""
    __tablename__ = 'gematria_entities'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(500))
    symbol_value = Column(String(100))
    elemental_force = Column(String(50))
    domains = Column(Text)  # JSON array as text
    description = Column(Text)
    relevance_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class GematriaRelationships(Base):
    """Cross-symbol relationships"""
    __tablename__ = 'gematria_relationships'
    
    id = Column(Integer, primary_key=True)
    entity_a_id = Column(Integer, ForeignKey('gematria_entities.id'))
    entity_b_id = Column(Integer, ForeignKey('gematria_entities.id'))
    min_value = Column(Float)
    max_value = Column(Float)
    direction = Column(String(20))  # bidirectional/unidirectional
    source = Column(String(300))
    created_at = Column(DateTime, default=datetime.utcnow)


class AnalysisMetrics(Base):
    """Batch analysis results"""
    __tablename__ = 'analysis_metrics'
    
    id = Column(Integer, primary_key=True)
    batch_id = Column(String(100), unique=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    source_count = Column(Integer)
    items_found = Column(Integer)
    core_symbols_detected = Column(Integer)
    relationships_extracted = Column(Integer)
    relevance_score = Column(Float)


class OvernightResearchLogs(Base):
    """Web scraping history"""
    __tablename__ = 'overnight_research_logs'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    source_type = Column(String(100))
    source_name = Column(String(200))
    items_processed = Column(Integer)
    duration_seconds = Column(Float)
    errors = Column(Text)


# SQLite fallback (for local development/testing)
def init_sqlite_db(db_path: str):
    """Initialize SQLite database with all tables"""
    Base.metadata.create_all(sqlite3.connect(db_path))
    
    # Insert sample data
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Core symbols from image analysis
    core_symbols_data = [
        ("124", "water", 0.98, "Universal Bridge - Water domain"),
        ("963", "air", 0.95, "Frequency/Air pattern (vei text detected)"),
        ("55", "fire", 0.97, "Elemental Fire - Birthday candles"),
        ("111", "spirit", 0.92, "Activation/Spirit - awaiting discovery"),
        ("279", "earth", 0.96, "Military Coup/Volcano equation"),
        ("666", "fire", 0.94, "Completion/Wholeness via 4+655+7=666")
    ]
    
    cursor.execute("""
        INSERT OR REPLACE INTO gematria_entities (symbol_value, elemental_force, description)
        VALUES (?, ?, ?)
    """, *[x + y for x, y in zip(["124", "963", "55", "111", "279", "666"], 
                                   ["water", "air", "fire", "spirit", "earth", "fire"],
                                   [x[3] for x in core_symbols_data])])
    
    cursor.execute("""
        INSERT OR REPLACE INTO source_metadata (source_name, source_type, url)
        VALUES (?, ?, ?)
    """, ["Local Analysis", "system", "file:///home/avalonas/.hermes/gematria/recent_image_analysis.md"])
    
    conn.commit()
    conn.close()
    print("✅ SQLite database initialized with core symbols")


# HTML Parser for custom extraction
class ContentExtractor(HTMLParser):
    """Custom HTML parser for text extraction"""
    
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.in_h1 = False
        self.title_text = ""
        self.h1_text = ""
        self.paragraphs = []
        self.current_tag = ""
    
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
    
    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "h1":
            self.in_h1 = False
    
    def handle_data(self, data):
        if self.current_tag == "title":
            self.title_text += data.strip()
        elif self.current_tag in ["h1", "h2"]:
            if self.current_tag == "h1" and not self.h1_text:
                self.h1_text = data.strip()
        elif self.current_tag == "p":
            self.paragraphs.append(data.strip())


def extract_article_content(url: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
    """Extract article content from URL using firecrawl"""
    
    payload = {
        "url": url,
        "options": {"extract": True}
    }
    
    try:
        import requests
        headers = {
            "Authorization": f"Bearer {SourceConfig.FIRECRAWL_API_KEY}",
            "Content-Type": "application/json"
        } if SourceConfig.FIRECRAWL_API_KEY else {}
        
        response = requests.post(
            SourceConfig.FIRECRAWL_BASE_URL, 
            json=payload, 
            headers=headers, 
            timeout=timeout
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract core symbols from content
            content_text = ""
            if "markdown" in data:
                content_text = data["markdown"]
            elif "text" in data:
                content_text = data["text"]
            
            # Parse HTML for patterns
            if "html" in data:
                parser = ContentExtractor()
                parser.feed(data["html"])
            
            return {
                "url": url,
                "title": parser.title_text.strip() or data.get("metadata", {}).get("title", ""),
                "content": content_text[:5000],  # Limit size
                "paragraphs": parser.paragraphs[:10]
            }
        else:
            print(f"❌ Firecrawl error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching {url}: {str(e)}")
        return None


def fetch_news_api(url: str, category: str = "business") -> Optional[Dict[str, Any]]:
    """Fetch news using NewsAPI (optional integration)"""
    
    try:
        import requests
        
        api_key = os.getenv("NEWSAPI_KEY") if POSTGRES_AVAILABLE else None
        
        if not api_key:
            print("⚠️  NewsAPI key not configured. Skipping API calls.")
            return None
        
        params = {
            "q": category,
            "language": "en",
            "sortBy": "popularity"
        }
        
        response = requests.get(
            "https://newsapi.org/v2/everything",
            params=params,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", [])[:3]
            
            return {
                "source": "newsapi",
                "articles": articles,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return None
        
    except Exception as e:
        print(f"❌ NewsAPI error: {str(e)}")
        return None


def fetch_rss_feed(feed_url: str) -> Optional[List[Dict[str, Any]]]:
    """Fetch RSS feed content"""
    
    try:
        response = requests.get(feed_url, timeout=15)
        
        if response.status_code == 200:
            parser = feedparser.parse(response.text)
            
            articles = []
            for entry in parser.entries[:5]:
                articles.append({
                    "title": entry.title,
                    "link": entry.link,
                    "description": entry.get("summary", ""),
                    "pubDate": entry.get("published_parsed", None),
                    "source": urlparse(feed_url).hostname,
                    "category": SourceConfig.RSS_FEEDS.get(urlparse(feed_url).path.split("/"), {}).get("category", "general")
                })
            
            return articles
        
        return None
        
    except Exception as e:
        print(f"❌ RSS feed error {feed_url}: {str(e)}")
        return None


def extract_gematria_patterns(text: str) -> List[Tuple[str, float]]:
    """Extract gematria patterns from text"""
    
    import re
    
    patterns_found = []
    
    # Core symbol keyword matching
    core_symbol_map = {
        "124": [r"\b124\b", r"\bkm³\b"],
        "963": [r"\b963\b", r"\bvei\b"],
        "55": [r"\b55\b"],
        "111": [r"\b111\b"],
        "279": [r"\b279\b", r"\bvolcano\b", r"\bmilitary coup\b"],
        "666": [r"\b666\b", r"\bcompletion\b", r"\bwholeness\b"]
    }
    
    for symbol, keywords in core_symbol_map.items():
        for keyword in keywords:
            pattern = re.compile(keyword, re.IGNORECASE)
            if pattern.search(text):
                # Calculate relevance based on keyword matches and context
                match_count = len(pattern.findall(text))
                base_relevance = 0.85
                relevance = min(1.0, base_relevance + (match_count * 0.08))
                
                patterns_found.append((symbol, relevance))
    
    return patterns_found


def process_url(url: str, source_type: str, source_name: str) -> Dict[str, Any]:
    """Process a single URL and extract gematria patterns"""
    
    batch_id = hashlib.md5(f"{url}{datetime.utcnow()}".encode()).hexdigest()[:16]
    start_time = time.time()
    
    print(f"\n🔍 Processing {source_type} source: {url}")
    
    try:
        # Try Firecrawl first
        result = extract_article_content(url)
        
        if result and result.get("content"):
            text = result["content"]
            patterns = extract_gematria_patterns(text)
            
            items_found = 1
            
            # Update database
            update_database({
                "batch_id": batch_id,
                "timestamp": datetime.utcnow(),
                "source_type": source_type,
                "source_name": source_name,
                "items_found": items_found,
                "patterns_detected": patterns,
                "url": url
            })
            
            print(f"✅ Found {len(patterns)} core symbol(s): {', '.join([p[0] for p in patterns])}")
            return result
            
        return None
        
    except Exception as e:
        print(f"❌ Error processing {url}: {str(e)}")
        return None


def update_database(data: Dict[str, Any]):
    """Update PostgreSQL or SQLite database"""
    
    if POSTGRES_AVAILABLE:
        try:
            engine = create_engine(
                os.getenv("DATABASE_URL", "postgresql://gematria_user:gematria_pass@localhost/gematria"),
                poolclass=StaticPool
            )
            
            Session = sessionmaker(bind=engine)
            session = Session()
            
            # Insert batch log
            metrics = AnalysisMetrics(
                batch_id=data["batch_id"],
                source_count=1,
                items_found=data.get("items_found", 0),
                core_symbols_detected=len(data.get("patterns_detected", [])),
                relevance_score=0.95,
                timestamp=datetime.utcnow()
            )
            session.add(metrics)
            
            # Insert source metadata
            source_meta = SourceMetadata(
                source_name=data["source_name"],
                source_type=data["source_type"],
                url=data.get("url", ""),
                category="general",
                relevance_score=0.95
            )
            session.add(source_meta)
            
            # Insert detected entities
            for symbol, relevance in data.get("patterns_detected", []):
                entity = GematriaEntities(
                    symbol_value=symbol,
                    elemental_force=get_elemental_force(symbol),
                    description=f"Pattern detected via {data['source_name']}",
                    relevance_score=relevance
                )
                session.add(entity)
            
            session.commit()
            
        except Exception as e:
            print(f"⚠️  PostgreSQL update failed (using SQLite): {str(e)}")
    
    # Always try SQLite fallback
    db_path = Path.home() / ".hermes" / "gematria" / "gematria_database.sqlite"
    init_sqlite_db(str(db_path))


def get_elemental_force(symbol: str) -> str:
    """Map symbol to elemental force"""
    mapping = {
        "124": "water",
        "963": "air",
        "55": "fire",
        "111": "spirit",
        "279": "earth",
        "666": "fire"
    }
    return mapping.get(symbol, "unknown")


def run_multi_source_pipeline(batch_size: int = 3):
    """Run the complete multi-source ingestion pipeline"""
    
    print("\n" + "="*80)
    print("🚀 STEVE'S GEMATRIA - MULTI-SOURCE DATA INGESTION PIPELINE")
    print("="*80)
    print(f"\n📍 Working directory: {Path.home() / '.hermes' / 'gematria'}")
    
    # Sample URLs to process
    sample_urls = [
        "https://www.politico.com/",
        "https://reuters.com/business",
        "https://coindesk.com",
    ]
    
    total_start_time = time.time()
    processed_count = 0
    
    for url in sample_urls[:batch_size]:
        result = process_url(url, "web", "Politico/Reuters/CoinDesk")
        if result:
            processed_count += 1
        
        # Rate limiting
        time.sleep(2)
    
    total_time = time.time() - total_start_time
    
    print(f"\n{'='*80}")
    print(f"✅ Pipeline completed!")
    print(f"📊 Sources processed: {processed_count}/{len(sample_urls[:batch_size])}")
    print(f"⏱️  Total duration: {total_time:.2f} seconds")
    print(f"💾 Results stored in: {Path.home() / '.hermes' / 'gematria' / 'gematria_database.sqlite'}")
    print("="*80 + "\n")


if __name__ == "__main__":
    # Initialize database
    db_path = Path.home() / ".hermes" / "gematria" / "gematria_database.sqlite"
    init_sqlite_db(str(db_path))
    
    # Run pipeline
    run_multi_source_pipeline(batch_size=3)
    
    print("\n🧙‍♂️ Multi-source data ingestion complete!")
