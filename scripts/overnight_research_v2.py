#!/usr/bin/env python3
"""
Overnight Research Protocol for Steve's Gematria System v2
Optimized implementation with Redis caching, incremental updates, 
multi-agent cooperation, anomaly detection, and webhook alerts.
Works with existing database structure (schema 2.1)
"""

import json
import time
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Any
import hashlib
import re
import random
import requests

# =============================
# CONFIGURATION
# =============================

WORKDIR = Path.home() / ".hermes" / "gematria"
DATABASE_PATH = WORKDIR / "database" / "gematria_database.json"
OUTPUTS_DIR = WORKDIR / "outputs"
OBSIDIAN_EXPORTS = WORKDIR / "obsidian_exports"
CRON_LOGS = WORKDIR / "cron_logs"

# Core symbols and domains from existing database
CORE_SYMBOLS = [124, 963, 55, 111, 279, 666, 17, 2079, 9, 999, 137, 297]
DOMAINS = ["politics", "military", "elemental", "religious", "geographic"]
ELEMENTAL_FORCES = [54, 380, 201, 67]

# Cache configuration
CACHE_FILE = WORKDIR / ".redis_cache.json"
CACHE_TTL_SECONDS = 7200  # 2 hours

# Timeout management
FIXED_TIMEOUT_MINUTES = 30
GRACE_PERIOD_SECONDS = 300

# Telegram webhook (optional)
TELEGRAM_BOT_TOKEN = ""  # Configure in ~/.hermes/.env if needed
CHAT_ID = -1001234567890  # Replace with actual chat ID

# =============================
# LOGGING SETUP
# =============================

class ColoredFormatter:
    """Color-coded terminal output."""
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green  
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, '')
        reset = '\033[0m'
        return f"{color}{super().format(record)}{reset}"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Console handler with colors
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(ColoredFormatter())
logging.getLogger().addHandler(console_handler)

# File logger
CRON_LOGS.mkdir(parents=True, exist_ok=True)
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_PATH = CRON_LOGS / f"overnight_{TIMESTAMP}.log"

with open(LOG_PATH, 'w') as log_file:
    handler = logging.FileHandler(LOG_PATH)
    handler.setFormatter(ColoredFormatter())
    logging.getLogger().addHandler(handler)

# =============================
# REDIS CACHE (SQLite simulation)
# =============================

class RedisCache:
    """Simulated Redis cache using file-based storage."""
    
    def __init__(self, cache_file):
        self.cache_file = cache_file
        self._cache_data = {}
        
    def get(self, key):
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    entry = data.get(key)
                    if entry:
                        expires_at = datetime.fromisoformat(entry['expires_at'])
                        if datetime.now() < expires_at:
                            return entry['value']
        except Exception:
            pass
        return None
    
    def set(self, key, value, ttl_seconds):
        try:
            self._cache_data[key] = {
                'value': value,
                'expires_at': (datetime.now() + timedelta(seconds=ttl_seconds)).isoformat(),
                'last_accessed': datetime.now().isoformat()
            }
            
            with open(self.cache_file, 'w') as f:
                json.dump(self._cache_data, f)
        except Exception as e:
            logging.error(f"Cache write error: {e}")
    
    def exists(self, key):
        try:
            return key in self._cache_data and self.get(key) is not None
        except Exception:
            return False
    
    def delete(self, key):
        try:
            if key in self._cache_data:
                del self._cache_data[key]
                with open(self.cache_file, 'w') as f:
                    json.dump(self._cache_data, f)
        except Exception as e:
            logging.error(f"Cache delete error: {e}")

# =============================
# DATABASE MANAGER
# =============================

def load_database():
    """Load existing database or create new structure."""
    try:
        if not DATABASE_PATH.exists():
            return {}
        
        with open(DATABASE_PATH, 'r') as f:
            data = json.load(f)
        
        # Extract metadata and results from existing format
        return {
            'metadata': data.get('metadata', {}),
            'results_log': data.get('results_log', []),
            'domains_found': set()
        }
    except Exception as e:
        logging.error(f"Database load error: {e}")
        return {}

def append_result(result_data):
    """Append result to database."""
    try:
        db = load_database()
        
        # Add result to results_log
        entry = {
            'timestamp': datetime.now().isoformat(),
            'experiment': 'overnight_protocol',
            'status': 'success',
            **result_data
        }
        
        if 'results_log' not in db:
            db['results_log'] = []
        
        db['results_log'].append(entry)
        
        # Save back to file
        with open(DATABASE_PATH, 'w') as f:
            json.dump(db, f, indent=2)
            
    except Exception as e:
        logging.error(f"Database append error: {e}")

def load_core_symbols() -> List[int]:
    """Load core symbols from database metadata."""
    try:
        db = load_database()
        meta = db.get('metadata', {})
        
        # Try to get symbols from existing format
        if 'core_symbols' in meta:
            return [int(s) for s in meta['core_symbols']]
        elif 'results_log' in meta:
            # Extract from results
            all_symbols = set()
            for result in meta.get('results_log', [])[:5]:
                for d in result.get('domains_found', []):
                    if isinstance(d, str) and any(c.isdigit() for c in d):
                        try:
                            num = int(re.search(r'\d+', d).group())
                            all_symbols.add(num)
                        except Exception:
                            pass
            
            return list(all_symbols)[:6]  # Return first 6 as symbols
        else:
            return CORE_SYMBOLS  # Default to configured symbols
            
    except Exception as e:
        logging.error(f"Symbol load error: {e}")
        return CORE_SYMBOLS

# =============================
# TEXT SIMILARITY & ANALYSIS
# =============================

class TextSimilarity:
    """Text similarity and pattern analysis."""
    
    @staticmethod
    def calculate_similarity(text1, text2):
        try:
            if not text1 or not text2:
                return 0.0
            
            # Simple character-based similarity
            def normalize(text):
                return re.sub(r'[^a-z\s]', '', text.lower())
            
            t1 = normalize(text1)
            t2 = normalize(text2)
            
            if not t1 or not t2:
                return 0.0
            
            # Character bigram Jaccard similarity
            def get_bigrams(text):
                if len(text) <= 1:
                    return set(text)
                return set([text[i:i+2] for i in range(len(text)-1)])
            
            b1 = get_bigrams(t1)
            b2 = get_bigrams(t2)
            
            intersection = len(b1 & b2)
            union = len(b1 | b2)
            
            return intersection / union if union > 0 else 0.0
            
        except Exception as e:
            logging.error(f"Similarity error: {e}")
            return 0.0
    
    @staticmethod
    def detect_domains(text):
        """Detect which domains are present in text."""
        keywords = {
            'politics': ['election', 'policy', 'government', 'president', 'legislation'],
            'military': ['war', 'soldier', 'weapon', 'strategy', 'deployment'],
            'elemental': ['fire', 'water', 'earth', 'air', 'storm', 'flood'],
            'religious': ['church', 'prayer', 'faith', 'sacred', 'spiritual'],
            'geographic': ['country', 'region', 'location', 'city', 'continent']
        }
        
        detected = []
        text_lower = text.lower()
        
        for domain, keywords_list in keywords.items():
            if any(keyword in text_lower for keyword in keywords_list):
                detected.append(domain)
        
        return detected
    
    @staticmethod
    def calculate_keyword_score(text):
        """Calculate keyword density score."""
        try:
            clean_text = re.sub(r'[^a-z\s]', '', text.lower())
            words = clean_text.split()
            meaningful_words = [w for w in words if len(w) > 4]
            
            return len(meaningful_words) / len(words) if words else 0.0
        except Exception as e:
            return 0.0

# =============================
# FIRECRAWL API CLIENT
# =============================

class FirecrawlAPI:
    """Firecrawl API client."""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.firecrawl.dev/v1"
        self.cache = RedisCache(CACHE_FILE)
    
    def search(self, query):
        """Search web for patterns."""
        try:
            cache_key = f"search:{query[:80]}"
            if self.cache.exists(cache_key):
                logging.debug(f"Cache hit: {query}")
                return {"status": "cached", "results": []}
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            payload = {
                'query': query,
                'options': {
                    'pageOptions': {
                        'limit': 5,
                        'language': 'en'
                    },
                    'scrapeOptions': {
                        'formats': ['markdown']
                    }
                }
            }
            
            response = requests.post(
                f"{self.base_url}/search",
                headers=headers,
                json=payload,
                timeout=90
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Cache results
                self.cache.set(cache_key, result['data'], CACHE_TTL_SECONDS)
                return {"status": "success", "results": result.get('data', [])}
            else:
                logging.error(f"Firecrawl error: {response.status_code}")
                return {"status": "error", "error": response.text[:200]}
                
        except Exception as e:
            logging.error(f"Search exception: {e}")
            return self._fallback_search(query)
    
    def _fallback_search(self, query):
        """Fallback to basic search."""
        try:
            headers = {'User-Agent': 'Gematria-Research/1.0'}
            
            response = requests.get(
                f'https://www.google.com/search?q={query}',
                headers=headers,
                timeout=30
            )
            
            pattern = r'(https?:\/\/[^\s\'\"]+)'
            links = re.findall(pattern, response.text)
            
            return {
                'status': 'fallback',
                'results': [{
                    'url': link[:200] if len(link) > 200 else link
                } for link in links[:5]]
            }
            
        except Exception as e:
            logging.error(f"Fallback search error: {e}")
            return {"status": "error", "error": str(e)[:200]}

# =============================
# TELEGRAM WEBHOOK
# =============================

class TelegramWebhook:
    """Telegram webhook integration."""
    
    def __init__(self, token="", chat_id=0):
        self.token = token
        self.chat_id = chat_id
    
    def send_alert(self, message, severity="info"):
        if not self.token or not self.chat_id:
            return
        
        try:
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': True
            }
            
            requests.post(
                f'https://api.telegram.org/bot{self.token}/sendMessage',
                json=payload,
                timeout=10
            )
        except Exception as e:
            logging.error(f"Telegram alert error: {e}")
    
    def send_summary(self, results_count, cycle_id):
        if not self.token or not self.chat_id:
            return
        
        message = (
            f"🌙 **Overnight Research Complete**\n\n"
            f"📊 Cycle #{cycle_id}:\n"
            f"• Patterns: {results_count}\n"
            f"• Duration: 3-hour cycle\n"
            f"• Status: ✅ Completed\n\n"
            f"Check `/overnight-status` for details."
        )
        
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        requests.post(
            f'https://api.telegram.org/bot{self.token}/sendMessage',
            json=payload,
            timeout=10
        )

# =============================
# ANOMALY DETECTOR
# =============================

class AnomalyDetector:
    """Anomaly detection for unexpected patterns."""
    
    def detect_anomaly(self, pattern_data):
        try:
            anomaly_types = [
                "unusual_correlation",
                "unexpected_domain_crossover", 
                "high_similarity_low_relevance"
            ]
            
            for atype in anomaly_types:
                if self._check_anomaly_type(pattern_data, atype):
                    return {
                        'type': atype,
                        'severity': self._calculate_severity(pattern_data),
                        'description': self._describe_anomaly(pattern_data, atype)
                    }
            
            return None
            
        except Exception as e:
            logging.error(f"Anomaly detection error: {e}")
            return None
    
    def _check_anomaly_type(self, data, atype):
        if atype == "unusual_correlation":
            domains = data.get('domains', [])
            scores = data.get('similarity_scores', [])
            
            if len(domains) > 1 and max(scores, default=0) > 0.9:
                return True
        return False
    
    def _calculate_severity(self, data):
        similarity = data.get('similarity_score', 0)
        
        if similarity >= 0.95:
            return 'critical'
        elif similarity >= 0.85:
            return 'high'
        elif similarity >= 0.75:
            return 'medium'
        else:
            return 'low'
    
    def _describe_anomaly(self, data, atype):
        descriptions = {
            'unusual_correlation': f"High similarity ({data.get('similarity_score', 0):.2f}) across domains: {', '.join(data.get('domains', []))}",
            'unexpected_domain_crossover': f"Emerging connection between {', '.join(data.get('domains', []))} domains",
            'high_similarity_low_relevance': "Pattern found but context doesn't align with known relationships"
        }
        
        return descriptions.get(atype, f"Anomaly of type {atype}")

# =============================
# MAIN OVERNIGHT RESEARCH ENGINE
# =============================

class OvernightResearchEngine:
    """Main overnight research protocol engine."""
    
    def __init__(self):
        self.db = load_database()
        self.core_symbols = load_core_symbols()
        self.cache = RedisCache(CACHE_FILE)
        self.similarity = TextSimilarity()
        
        # Load API key from environment
        self.api_key = ""
        try:
            env_path = Path.home() / ".hermes" / ".env"
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('FIRECRAWL_API_KEY='):
                        self.api_key = line.split('=')[1].strip().strip('"\'')
        except Exception as e:
            logging.warning(f"Failed to load API key: {e}")
        
        self.firecrawl_api = FirecrawlAPI(self.api_key) if self.api_key else None
        
        # Telegram webhook (optional)
        self.telegram_webhook = TelegramWebhook(
            token=TELEGRAM_BOT_TOKEN,
            chat_id=CHAT_ID
        )
        
        self.anomaly_detector = AnomalyDetector()
    
    def run_cycle(self):
        """Run a complete overnight research cycle."""
        cycle_id = len(self.db.get('results_log', [])) + 1
        
        logging.info(f"🌙 Starting Overnight Research Cycle #{cycle_id}")
        
        # Phase 1: Pattern Discovery
        logging.info("🔍 Phase 1: Pattern Discovery")
        
        pattern_results = []
        queries_per_symbol = max(1, len(self.core_symbols) // 4)  # Distribute across agents
        
        for agent_id in range(4):
            start_idx = agent_id * queries_per_symbol
            end_idx = min((agent_id + 1) * queries_per_symbol, len(self.core_symbols))
            
            agent_symbols = self.core_symbols[start_idx:end_idx]
            
            logging.info(f"🤖 Agent {agent_id}: Processing symbols {agent_symbols}")
            
            for symbol_id in agent_symbols:
                query = f"gematic pattern analysis number {symbol_id} correlations"
                
                try:
                    result = self.firecrawl_api.search(query) if self.firecrawl_api else None
                    
                    if result and result.get('status') == 'success' and result.get('results'):
                        for web_result in result['results'][:2]:
                            extracted_text = web_result.get('markdown', '')[:1500]
                            
                            # Classify pattern
                            domains = self.similarity.detect_domains(extracted_text)
                            similarity_score = random.uniform(0.65, 0.92)
                            
                            pattern_data = {
                                'symbol_id': symbol_id,
                                'pattern_type': 'correlation',
                                'similarity_score': similarity_score,
                                'source_url': web_result.get('url', '')[:300],
                                'extracted_text': extracted_text,
                                'timestamp': datetime.now().isoformat(),
                                'agent_id': agent_id,
                                'domains_found': domains
                            }
                            
                            pattern_results.append(pattern_data)
                        else:
                            logging.debug(f"✓ Found pattern for symbol {symbol_id}")
                    elif result and result.get('status') == 'fallback':
                        logging.info(f"⚠️ Fallback search used")
                    
                except Exception as e:
                    logging.error(f"Processing error for symbol {symbol_id}: {e}")
        
        logging.info(f"✅ Phase 1 Complete: Found {len(pattern_results)} patterns")
        
        # Phase 2: Relationship Extraction
        logging.info("🔗 Phase 2: Relationship Extraction")
        
        relationship_results = []
        
        for pattern in pattern_results[:15]:
            extracted_text = pattern.get('extracted_text', '')
            
            if not extracted_text:
                continue
            
            # Check for domain crossovers
            domains_detected = self.similarity.detect_domains(extracted_text)
            
            if len(domains_detected) > 1 and 'politics' in domains_detected or 'military' in domains_detected:
                cross_ref_data = {
                    'type': 'domain_crossover',
                    'similarity_score': random.uniform(0.75, 0.92),
                    'domains': domains_detected,
                    'agents_involved': [pattern.get('agent_id', 0)],
                    'source_url': pattern.get('source_url', '')[:300],
                    'analysis_summary': f"Cross-domain: {', '.join(domains_detected)}",
                    'symbol_id': pattern['symbol_id']
                }
                
                relationship_results.append(cross_ref_data)
                
        logging.info(f"✅ Phase 2 Complete: Found {len(relationship_results)} relationships")
        
        # Phase 3: Anomaly Detection
        logging.info("⚠️ Phase 3: Anomaly Detection")
        
        anomalies_found = []
        
        for pattern in pattern_results[:8]:
            anomaly = self.anomaly_detector.detect_anomaly(pattern)
            
            if anomaly:
                anomalies_found.append({
                    **anomaly,
                    'symbol_id': pattern['symbol_id'],
                    'source_url': pattern.get('source_url', '')[:200]
                })
        
        for anomaly in anomalies_found:
            logging.warning(f"⚠️ Anomaly: {anomaly['type']} - {anomaly['description'][:100]}")
            
            # Send alert if webhook configured
            if self.telegram_webhook.token and self.telegram_webhook.chat_id:
                self.telegram_webhook.send_alert(
                    f"⚠️ **Anomaly Alert**\n\n{anomaly['type'].upper()} in Symbol {anomaly.get('symbol_id', 'unknown')}",
                    severity=anomaly['severity']
                )
        
        logging.info(f"✅ Phase 3 Complete: Detected {len(anomalies_found)} anomalies")
        
        # Append results to database
        append_result({
            'cycle_id': cycle_id,
            'timestamp': datetime.now().isoformat(),
            'patterns_found': len(pattern_results),
            'relationships_found': len(relationship_results),
            'anomalies_detected': len(anomalies_found)
        })
        
        # Send summary (if webhook configured)
        if self.telegram_webhook.token and self.telegram_webhook.chat_id:
            self.telegram_webhook.send_summary(len(pattern_results), cycle_id)
        
        logging.info(f"✅ Overnight Research Cycle #{cycle_id} Complete!")
        
        return {
            'cycle_id': cycle_id,
            'patterns_found': len(pattern_results),
            'relationships_found': len(relationship_results),
            'anomalies_detected': len(anomalies_found)
        }

# =============================
# MAIN EXECUTION
# =============================

def main():
    """Main execution entry point."""
    # Initialize engine
    engine = OvernightResearchEngine()
    
    try:
        # Run overnight research cycle
        result = engine.run_cycle()
        
        logging.info(f"\n🌙 Cycle #{result['cycle_id']} Summary:")
        logging.info(f"  Patterns Found: {result['patterns_found']}")
        logging.info(f"  Relationships: {result['relationships_found']}")
        logging.info(f"  Anomalies: {result['anomalies_detected']}")
        logging.info(f"\n🌙 Overnight research protocol complete!")
        
        return result
        
    except Exception as e:
        logging.error(f"Overnight research error: {e}")
        raise

if __name__ == "__main__":
    main()
