#!/usr/bin/env python3
"""
Steve's Gematria - RSS Feed Aggregator
Collects content from specialized political/financial/cryptocurrency feeds

Version: 2.0.0
Date: April 26, 2026
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
import feedparser
import json
from pathlib import Path

# Core symbols configuration
CORE_SYMBOLS = {
    "124": {"name": "Universal Bridge", "elemental": "water"},
    "963": {"name": "Frequency/Air", "elemental": "air"},
    "55": {"name": "Elemental Fire", "elemental": "fire"},
    "111": {"name": "Activation/Spirit", "elemental": "spirit"},
    "279": {"name": "Military Coup/Volcano", "elemental": "earth"},
    "666": {"name": "Completion/Wholeness", "elemental": "fire"}
}


class RSSAggregator:
    """RSS Feed Aggregation System"""
    
    def __init__(self, config_file: str = None):
        self.rss_feeds = {}
        self.config_file = config_file
        
        # Load configuration
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)
        
        self.processed_items = set()
    
    def load_config(self, config_path: str):
        """Load RSS feed configurations from file"""
        try:
            with open(config_path, 'r') as f:
                feeds = json.load(f)
                
            for key, feed_data in feeds.items():
                if "url" in feed_data:
                    self.rss_feeds[key] = {
                        "name": feed_data.get("name", key),
                        "url": feed_data["url"],
                        "category": feed_data.get("category", "general"),
                        "keywords": feed_data.get("keywords", []),
                        "enabled": feed_data.get("enabled", True)
                    }
            
            print(f"✅ Loaded {len(self.rss_feeds)} RSS feeds from {config_path}")
            
        except Exception as e:
            print(f"⚠️  Could not load config: {str(e)}")
    
    def add_feed(self, name: str, url: str, category: str = "general"):
        """Add a new RSS feed"""
        self.rss_feeds[name] = {
            "name": name,
            "url": url,
            "category": category,
            "keywords": [],
            "enabled": True
        }
    
    def fetch_all_feeds(self) -> List[Dict[str, Any]]:
        """Fetch content from all enabled RSS feeds"""
        
        all_articles = []
        
        for feed_key, feed_config in self.rss_feeds.items():
            if not feed_config.get("enabled", True):
                continue
            
            print(f"\n📡 Fetching RSS feed: {feed_config['name']}")
            
            try:
                response = requests.get(feed_config["url"], timeout=15)
                
                if response.status_code == 200:
                    parser = feedparser.parse(response.text)
                    
                    for entry in parser.entries[:5]:  # Limit to 5 items per feed
                        article = self.create_article_entry(entry, feed_config)
                        
                        # Check for duplicates
                        unique_key = f"{article['title'][:20]}-{article.get('link', '')[:50]}"
                        
                        if unique_key not in self.processed_items:
                            all_articles.append(article)
                            self.processed_items.add(unique_key)
                            
                    print(f"  ✅ Fetched {len(parser.entries)} items")
                    
                else:
                    print(f"  ❌ HTTP error: {response.status_code}")
                    
            except Exception as e:
                print(f"  ⚠️  Error fetching feed: {str(e)}")
        
        return all_articles
    
    def create_article_entry(self, entry: Dict, feed_config: Dict) -> Dict[str, Any]:
        """Convert feedparser entry to structured article format"""
        
        pub_date = entry.get("published_parsed", None)
        formatted_date = datetime.utcnow().isoformat() if pub_date else datetime.utcnow().isoformat()
        
        return {
            "title": entry.title or "",
            "link": entry.link or "",
            "description": entry.get("summary") or entry.get("content", ""),
            "pubDate": formatted_date,
            "source": feed_config["name"],
            "category": feed_config.get("category", "general"),
            "keywords": feed_config.get("keywords", []),
            "guid": entry.get("id", "")
        }


def check_for_gematria_patterns(text: str) -> List[Tuple[str, float]]:
    """Check text for gematria patterns"""
    
    import re
    
    patterns_found = []
    
    for symbol, info in CORE_SYMBOLS.items():
        keywords = [symbol.lower()]
        
        if symbol == "124":
            keywords.extend(["km³", "bridge", "universal"])
        elif symbol == "963":
            keywords.extend(["frequency", "vei", "vibration"])
        elif symbol == "279":
            keywords.extend(["volcano", "military coup", "earth", "grounding"])
        
        for keyword in keywords:
            pattern = re.compile(keyword, re.IGNORECASE)
            if pattern.search(text):
                relevance = 0.85 + (text.lower().count(keyword.lower()) * 0.05)
                relevance = min(1.0, relevance)
                patterns_found.append((symbol, relevance))
    
    return patterns_found


def fetch_expanded_news_sources() -> List[Dict[str, Any]]:
    """Fetch from expanded news sources including web scraping"""
    
    import requests
    
    # Expanded political news sources
    political_sources = [
        "https://www.politico.com/",
        "https://www.reuters.com/world/us",
        "https://www.axios.com/",
        "https://www.nytimes.com/section/politics"
    ]
    
    # Financial/business sources  
    financial_sources = [
        "https://www.bloomberg.com/news/politics",
        "https://www.wsj.com/articles/business-government",
        "https://www.reuters.com/business",
        "https://finance.yahoo.com/"
    ]
    
    # Cryptocurrency sources
    crypto_sources = [
        "https://www.coindesk.com/",
        "https://cointelegraph.com/",
        "https://decrypt.co/"
    ]
    
    all_articles = []
    
    for i, url in enumerate((political_sources + financial_sources + crypto_sources)[:3], 1):
        print(f"\n🔍 Scanning source {i}: {url[:60]}...")
        
        try:
            # Use firecrawl or simple HTTP fetch for content
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                text = response.text[:2000]  # First 2000 chars
                
                patterns = check_for_gematria_patterns(text)
                
                if patterns:
                    articles.append({
                        "source": url,
                        "text": text[:1000],
                        "patterns": patterns,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
        except Exception as e:
            print(f"  ⚠️  Error: {str(e)}")
    
    return all_articles


def create_rss_config_file(config_path: str = None):
    """Create comprehensive RSS feed configuration file"""
    
    if config_path is None:
        config_path = Path.home() / ".hermes" / "gematria" / "rss_feeds.json"
    
    rss_feeds = {
        "political_news": [
            {
                "name": "Politico Politics",
                "url": "https://www.politico.com/rss/politics.xml",
                "keywords": ["politics", "government", "policy"],
                "enabled": True
            },
            {
                "name": "Reuters US Politics",
                "url": "http://rss.reuters.com/world/rss/us.xml",
                "keywords": ["us politics", "economy", "elections"],
                "enabled": True
            },
            {
                "name": "Axios Politics",
                "url": "https://www.axios.com/politics/",
                "keywords": ["policy", "congress", "white house"],
                "enabled": True
            }
        ],
        
        "financial_news": [
            {
                "name": "Bloomberg Business",
                "url": "http://feeds.bloomberg.com/rss/home/markets.xml",
                "keywords": ["business", "markets", "economy"],
                "enabled": True
            },
            {
                "name": "Wall Street Journal Politics",
                "url": "https://www.wsj.com/section/politics/",
                "keywords": ["business policy", "government spending"],
                "enabled": True
            },
            {
                "name": "Financial Times Business",
                "url": "http://content.ft.com/rss/frontpage.html",
                "keywords": ["markets", "global economy"],
                "enabled": True
            }
        ],
        
        "cryptocurrency_news": [
            {
                "name": "CoinDesk News",
                "url": "https://www.coindesk.com/rss.xml",
                "keywords": ["bitcoin", "blockchain", "crypto"],
                "enabled": True
            },
            {
                "name": "Cointelegraph",
                "url": "http://cointelegraph.com/feed/all",
                "keywords": ["cryptocurrency", "defi", "nft"],
                "enabled": True
            },
            {
                "name": "Decrypt News",
                "url": "https://decrypt.co/feed/",
                "keywords": ["web3", "metaverse", "blockchain"],
                "enabled": True
            }
        ],
        
        "technology_news": [
            {
                "name": "TechCrunch Politics",
                "url": "https://techcrunch.com/category/politics/",
                "keywords": ["tech policy", "regulation"],
                "enabled": True
            },
            {
                "name": "Ars Technica Policy",
                "url": "http://feeds.arstechnica.com/arstechnica/tech-policy",
                "keywords": ["technology law", "privacy"],
                "enabled": True
            }
        ]
    }
    
    with open(config_path, 'w') as f:
        json.dump(rss_feeds, f, indent=2)
    
    print(f"✅ Created RSS configuration file: {config_path}")


def run_rss_aggregation():
    """Run complete RSS aggregation workflow"""
    
    import requests
    
    config_file = Path.home() / ".hermes" / "gematria" / "rss_feeds.json"
    
    # Create RSS config if not exists
    if not config_file.exists():
        create_rss_config_file(str(config_path))
    
    aggregator = RSSAggregator(str(config_file))
    
    print("\n📡 STEVE'S GEMATRIA - RSS FEED AGGREGATOR")
    print("="*80)
    print(f"🎯 Aggregating from {len(aggregator.rss_feeds)} RSS feeds...")
    
    # Fetch all feeds
    articles = aggregator.fetch_all_feeds()
    
    # Check for gematria patterns in articles
    pattern_analysis = []
    for article in articles:
        text = article.get("description", article.get("title", ""))[:2000]
        patterns = check_for_gematria_patterns(text)
        
        if patterns:
            pattern_analysis.append({
                "title": article["title"][:100],
                "source": article["source"],
                "patterns": [(p[0], p[1]) for p in patterns]
            })
    
    # Display results
    print(f"\n{'='*80}")
    print(f"📊 Results:")
    print(f"  Total articles fetched: {len(articles)}")
    print(f"  Articles with gematria patterns: {len(pattern_analysis)}")
    
    if pattern_analysis:
        print(f"\n  🔮 Patterns found in news sources:")
        for item in pattern_analysis[:5]:
            print(f"\n    📰 {item['title'][:80]}...")
            print(f"       Source: {item['source']}")
            for symbol, relevance in item['patterns']:
                elemental = CORE_SYMBOLS[symbol].get("elemental", "unknown")
                print(f"         → Symbol [{symbol}]: {relevance:.2f} ({elemental})")


if __name__ == "__main__":
    run_rss_aggregation()
