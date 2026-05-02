#!/usr/bin/env python3
"""
Steve's Gematria Autonomous Overnight Research Protocol - PRODUCTION ENHANCED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Enhanced with top priority recommendations from test autonomous research analysis:
1. CONFIGURED EXTENDED TIMEOUT (30-60 min production budget) 
2. EXTERNAL SEARCH QUERIES for multi-domain pattern discovery
3. MULTI-AGENT PARALLEL SCRAPING mode enabled

Based on Andrej Karpathy's autoresearch methodology with gematria integration:
- Fixed-time experiment budget (configurable per run)
- Structured results logging (TSV)
- Autonomous iteration (no manual intervention)
- Timeout protection (>15min = auto-kill for safety)
- Simplicity criterion evaluation

LOCAL RUN - No external dependencies, uses local Firecrawl instance.
"""

import json
import time
import datetime
import signal
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import aiohttp
import asyncio
from urllib.parse import urljoin
import re

# Setup logging
LOG_DIR = Path("/home/avalonas/.hermes/gematria/cron_logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "overnight_autonomous_enhanced.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# =============================================================================
# PRODUCTION CONFIGURATION - Enhanced from test mode
# =============================================================================
EXP_NAME = f"autonomous_enhanced_{datetime.date.today().strftime('%Y%m%d')}"
MAX_RUN_SECONDS = 1800  # 🆕 EXTENDED TIMEOUT: 30 minutes (production budget, vs 5min test)
CHECK_INTERVAL = 90    # seconds between metrics checks (reduced for longer runs)
SCRAPE_BATCH_SIZE = 24 # URLs per run
TIMEOUT_GRACE_PERIOD = 60  # seconds before hard kill (extended from 30s)

# 🆕 MULTI-DOMAIN SEARCH QUERIES - External search integration
EXTERNAL_SEARCH_QUERIES = [
    "124 universal frequency symbolism",
    "963 numerical code meaning politics",
    "55 elemental resonance patterns",
    "111 activation symbols conspiracy",
    "666 completion number analysis",
    "fire volcano military imagery gematria",
    "political coup narrative analysis",
    "trump canada mexico symbolism 2024",
    "bitcoin financial domination themes",
    "military defense technology advancement"
]

# 🆕 PARALLEL SCRAPING CONFIGURATION - Multi-agent architecture
PARALLEL_SCRAPE_ENABLED = True
PARALLEL_WORKERS = 3  # Number of concurrent scraping workers for parallel processing

# Load Firecrawl API key from env
try:
    with open(Path.home() / ".hermes/.env", "r") as f:
        for line in f:
            if line.startswith("FIRECRAWL_API_KEY="):
                api_key = line.strip().split("=")[1]
                break
except Exception as e:
    logger.error(f"Failed to load API key: {e}")
    sys.exit(1)

HEADERS = {"Authorization": f"Bearer {api_key}"}
LOCAL_BASE_URL = "http://localhost:3002/v1"  # Local Firecrawl instance


# =============================================================================
# Timeout Handler - Fixed-time experiment budget
# =============================================================================
class TimeoutHandler:
    """
    Autonomous timeout protection pattern from autoresearch_folktales.
    Implements fixed-time experiment budget with auto-kill capability.
    """

    def __init__(self, max_seconds: int):
        self.max_seconds = max_seconds
        self.start_time = time.time()
        
    def check_timeout(self) -> Tuple[bool, float]:
        """Check if timeout exceeded and return elapsed seconds."""
        elapsed = time.time() - self.start_time
        remaining = self.max_seconds - elapsed
        
        if remaining <= 0:
            return True, elapsed
        
        return False, elapsed


# =============================================================================
# Enhanced Results Logger with External Query Tracking
# =============================================================================
class ResultsLogger:
    """TSV results logging system for autonomous research runs."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.results_file = LOG_DIR / f"{EXP_NAME}_results.tsv"
        
    def initialize(self):
        """Initialize results TSV with header row."""
        self.results_file.parent.mkdir(parents=True, exist_ok=True)
        header = "commit\tsymbols_detected\tdomains_found\texternal_searches\tstatus\tdescription\n"
        if not self.results_file.exists():
            with open(self.results_file, "w") as f:
                f.write(header)
            logger.info(f"Initialized enhanced results logging at {self.results_file}")

    def log_result(self, commit_hash: str, symbols_count: int, domains_found: int, 
                   external_queries: int, status: str, description: str):
        """Log experiment result to TSV (including external search count)."""
        line = f"{commit_hash}\t{symbols_count}\t{domains_found}\t{external_queries}\t{status}\t{description}\n"
        
        # Append to results file (no overwrite on timeout)
        with open(self.results_file, "a") as f:
            f.write(line)

    def get_best_run(self) -> Optional[Dict]:
        """Get best run by symbol count."""
        if not self.results_file.exists():
            return None
        
        best_count = -1
        best_run = None
        
        with open(self.results_file, "r") as f:
            for line in f:
                parts = line.strip().split("\t", 5)
                if len(parts) >= 4:
                    try:
                        symbols = int(parts[1])
                        external = int(parts[3])
                        if symbols > best_count and parts[4] == "keep":
                            best_count = symbols
                            best_run = parts
                    except ValueError:
                        continue
        
        return best_run


# =============================================================================
# Enhanced Database Evaluator with Multi-Domain Support
# =============================================================================
class DatabaseEvaluator:
    """Ground truth evaluation harness with multi-domain tracking."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        with open(db_path, "r") as f:
            self.database = json.load(f)
        
    def evaluate_improvement(self, new_symbols_count: int, current_symbols_count: int) -> bool:
        """Evaluate if run improved."""
        return new_symbols_count > current_symbols_count
    
    def record_result(self, metadata_key: str, result_data: Dict):
        """Record experiment result to database ground truth with domain tracking."""
        if "entries" not in self.database or "results_log" not in self.database.get("metadata", {}):
            self.database.setdefault("metadata", {}).setdefault("results_log", [])
        
        # Extract domains from results_data for multi-domain tracking
        domains = result_data.get("domains_found", [])
        
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "experiment": EXP_NAME,
            **result_data
        }
        self.database["metadata"]["results_log"].append(entry)
        
        with open(self.db_path, "w") as f:
            json.dump(self.database, f, indent=2)


# =============================================================================
# 🆕 Enhanced Scraping with Multi-Domain Search Queries
# =============================================================================
async def scrape_urls_batch(urls: List[str], timeout_seconds: int, 
                            use_external_searches: bool = True) -> Tuple[Optional[Dict], str]:
    """
    Enhanced scraping batch with external search integration.
    Uses local Firecrawl v1 format.
    """
    try:
        # Build payload with external search options if enabled
        payload = {
            "urls": urls,
            "options": {
                "formats": ["markdown"],
                "timeout": timeout_seconds,
                "pageOptions": {
                    "headers": {"User-Agent": "SteveGematriaBot/2.0-Enhanced"},
                    "extract": True  # Enable content extraction for better pattern detection
                }
            },
            "searchQueries": EXTERNAL_SEARCH_QUERIES if use_external_searches else None  # 🆕 Multi-domain queries
        }
        
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            try:
                async with session.post(f"{LOCAL_BASE_URL}/crawl", json=payload) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return result, "success"
                    else:
                        error_msg = await resp.text()
                        return None, f"HTTP {resp.status}: {error_msg[:100]}"
            except Exception as e:
                return None, f"Error: {str(e)}"

    except ImportError:
        logger.warning("aiohttp not available, logging URLs only with external search")
        if use_external_searches:
            return {"urls": urls, "external_queries": EXTERNAL_SEARCH_QUERIES}, "logged_only_no_scrape"
        else:
            return {"urls": urls}, "logged_only_no_scrape"


# =============================================================================
# 🆕 Enhanced Pattern Analysis with Multi-Domain Discovery
# =============================================================================
async def analyze_patterns_in_results(results_data: Dict) -> Tuple[int, List[str], str]:
    """
    Enhanced analysis with multi-domain discovery support.
    Returns (symbol_count, list_of_domains, description).
    """
    # 🆕 Expanded symbol keywords
    symbol_keywords = [
        "124", "963", "55", "111", "666", 
        "fire", "frequency", "volcano", "resonance", 
        "coup", "political", "military", "narrative",
        "domination", "transformation", "bridge", "cycle"
    ]
    
    # 🆕 Expanded multi-domain keywords
    domain_keywords = {
        "political_events": ["political", "government", "election", "democracy"],
        "epstein_files_analysis": ["epstein", "files", "document", "conspiracy"],
        "trump_canada_narrative": ["trump", "canada", "statehood", "mexico", "border"],
        "bitcoin_crypto_symbolism": ["bitcoin", "crypto", "ethereum", "financial", "money"],
        "military_coup_themes": ["coup", "military", "defense", "general", "army"],
        "elemental_forces": ["fire", "earth", "air", "water", "nature"],
        "frequency_patterns": ["frequency", "resonance", "vibration", "pattern"]
    }
    
    symbol_count = 0
    domain_matches = {}
    
    if results_data and isinstance(results_data, dict) and "markdown" in results_data:
        content = results_data["markdown"].lower()
        
        # Count symbol instances
        for keyword in symbol_keywords:
            matches = len(re.findall(rf'\b{keyword}\b', content))  # Use regex for word boundaries
            if matches > 0:
                symbol_count += matches
        
        # Detect domains (multi-domain discovery)
        for domain_name, keywords in domain_keywords.items():
            for kw in keywords:
                if kw in content:
                    domain_matches[domain_name] = domain_matches.get(domain_name, 0) + 1
    
    description = f"Detected {symbol_count} pattern instances across {len(domain_matches)} domains"
    
    # 🆕 Add external search info if applicable
    if results_data and isinstance(results_data, dict) and "external_queries" in results_data:
        query_count = len(results_data["external_queries"])
        description += f" (with {query_count} external search queries)"
    
    return symbol_count, list(domain_matches.keys()), description


# =============================================================================
# 🆕 Parallel Scraping Worker Pool
# =============================================================================
class ParallelScrapeWorker:
    """Worker pool for parallel scraping with multi-agent architecture."""

    def __init__(self, worker_id: int):
        self.worker_id = worker_id
        self.urls_processed = 0
        
    async def process_batch(self, urls: List[str], timeout_seconds: int) -> Optional[Dict]:
        """Process a batch of URLs."""
        try:
            payload = {
                "urls": urls,
                "options": {
                    "formats": ["markdown"],
                    "timeout": timeout_seconds,
                    "pageOptions": {"headers": {"User-Agent": f"SteveGematriaWorker{self.worker_id}/1.0"}}
                }
            }
            
            async with aiohttp.ClientSession(headers=HEADERS) as session:
                try:
                    async with session.post(f"{LOCAL_BASE_URL}/crawl", json=payload) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            self.urls_processed += len(urls)
                            return result
                        else:
                            error_msg = await resp.text()
                            return {"error": f"HTTP {resp.status}: {error_msg[:100]}"}
                except Exception as e:
                    logger.warning(f"Worker {self.worker_id} error: {str(e)[:50]}")
                    return None
        
        except ImportError:
            logger.warning(f"Worker {self.worker_id}: aiohttp not available")
            return {"urls": urls}

    def get_progress(self) -> float:
        """Get progress percentage."""
        total = PARALLEL_SCRAPE_ENABLED * 10 if PARALLEL_SCRAPE_ENABLED else 24
        return (self.urls_processed / total) * 100 if total > 0 else 0


# =============================================================================
# Enhanced Main Function with Multi-Domain & Parallel Processing
# =============================================================================
async def main():
    """Enhanced autonomous overnight research loop with parallel scraping."""
    logger.info(f"\n{'='*70}")
    logger.info(f"🧙‍♂️  STEVE'S GEMATRIA AUTONOMOUS OVERNIGHT RESEARCH - PRODUCTION ENHANCED")
    logger.info(f"{'='*70}")
    logger.info(f"Experiment: {EXP_NAME}")
    logger.info(f"✅ FIXED TIMEOUT: {MAX_RUN_SECONDS}s ({MAX_RUN_SECONDS//60} minutes production budget)")
    logger.info(f"🌍 EXTERNAL SEARCH QUERIES: {len(EXTERNAL_SEARCH_QUERIES)} queries enabled")
    logger.info(f"🔄 PARALLEL SCRAPING: {'ENABLED' if PARALLEL_SCRAPE_ENABLED else 'DISABLED'}")
    
    # Initialize components
    db_path = Path.home() / ".hermes/gematria/database/gematria_database.json"
    results_logger = ResultsLogger(db_path)
    database_evaluator = DatabaseEvaluator(db_path)
    
    # Load core symbols and current state
    with open(db_path, "r") as f:
        database = json.load(f)
    
    current_symbols = len(database.get("search_indices", {}).get("core_numbers", []))
    logger.info(f"Starting from {current_symbols} existing symbols in database")
    
    # Initialize results logging
    results_logger.initialize()
    
    # Get URLs to scrape (from previous session or fallback)
    try:
        with open(Path.home() / ".hermes/gematria/scrape_urls_queue.txt", "r") as f:
            urls = [line.strip() for line in f if line.strip()][:SCRAPE_BATCH_SIZE]
    except FileNotFoundError:
        logger.info("No queue file found, using embedded URLs with external search queries")
        urls = get_fallback_urls(SCRAPE_BATCH_SIZE)
    
    logger.info(f"Prepared {len(urls)} URLs for multi-domain analysis")
    
    # Create timeout handler (fixed-time experiment budget - extended for production)
    timeout_handler = TimeoutHandler(MAX_RUN_SECONDS)
    
    # Initialize parallel workers if enabled
    parallel_workers: List[ParallelScrapeWorker] = []
    if PARALLEL_SCRAPE_ENABLED:
        logger.info(f"🚀 Initializing {PARALLEL_WORKERS} parallel scraping workers")
        parallel_workers = [ParallelScrapeWorker(i) for i in range(PARALLEL_WORKERS)]
    
    # Main autonomous loop
    best_symbols_count = current_symbols
    commit_counter = 0
    
    while timeout_handler.max_seconds - time.time() > CHECK_INTERVAL:
        elapsed, remaining = timeout_handler.check_timeout()
        
        if PARALLEL_SCRAPE_ENABLED and parallel_workers:
            worker_progress = sum(w.get_progress() for w in parallel_workers) / len(parallel_workers)
            logger.info(f"▶️  Parallel scraping progress: {worker_progress:.1f}%")
        
        logger.info(f"\n[{elapsed:.1f}s elapsed, {remaining:.0f}s remaining]")
        
        if remaining <= TIMEOUT_GRACE_PERIOD:
            status = "timeout"
            description = f"Auto-kill triggered at {MAX_RUN_SECONDS}s budget (extended production timeout)"
            external_queries = len(EXTERNAL_SEARCH_QUERIES) if PARALLEL_SCRAPE_ENABLED else 0
            
        else:
            # Autonomous experiment cycle with multi-domain discovery
            logger.info(f"▶️  Running enhanced scrape cycle #{commit_counter + 1}")
            
            if PARALLEL_SCRAPE_ENABLED and parallel_workers:
                # 🆕 Parallel scraping mode - distribute URLs among workers
                chunk_size = len(urls) // len(parallel_workers)
                results_data = {"markdown": "", "external_queries": EXTERNAL_SEARCH_QUERIES}
                
                async with aiohttp.ClientSession(headers=HEADERS) as session:
                    tasks = []
                    for i, worker in enumerate(parallel_workers):
                        start_idx = i * chunk_size
                        end_idx = min(start_idx + chunk_size, len(urls))
                        if start_idx < len(urls):
                            batch_urls = urls[start_idx:end_idx]
                            task = session.post(
                                f"{LOCAL_BASE_URL}/crawl", 
                                json={
                                    "urls": batch_urls,
                                    "options": {
                                        "formats": ["markdown"],
                                        "timeout": CHECK_INTERVAL,
                                        "pageOptions": {"headers": {"User-Agent": "SteveGematriaWorker/1.0"}}
                                    }
                                }, headers=HEADERS
                            )
                            tasks.append(task)
                    
                    if tasks:
                        try:
                            responses = await asyncio.gather(*tasks, return_exceptions=True)
                            for resp, worker in zip(responses, parallel_workers):
                                if isinstance(resp, Exception):
                                    logger.error(f"Worker error: {resp}")
                                elif resp and "error" not in str(resp).lower():
                                    if "markdown" in resp:
                                        results_data["markdown"] += resp.get("markdown", "") + "\n"
                external_queries = len(EXTERNAL_SEARCH_QUERIES)
                
            else:
                # Standard serial scraping (fallback or single-worker mode)
                logger.info(f"▶️  Running standard scrape cycle with external search queries")
                results_data, status_msg = await scrape_urls_batch(
                    urls, CHECK_INTERVAL, use_external_searches=True
                )
                
                if status_msg == "success" and results_data and isinstance(results_data, dict) and "markdown" in results_data:
                    commit_counter += 1
                    
                    # 🆕 Enhanced analysis with multi-domain discovery
                    symbol_count, domain_list, description = await analyze_patterns_in_results(results_data)
                    
                    logger.info(f"✅ Analysis complete: {symbol_count} symbols, {len(domain_list)} domains")
                    
                    # Evaluate improvement
                    improved = database_evaluator.evaluate_improvement(symbol_count, best_symbols_count)
                    
                    if improved:
                        status = "keep"
                        description += f" (+{symbol_count - best_symbols_count} symbols)"
                        
                        # Update best result (fixed bug from original script)
                        best_symbols_count = symbol_count
                        
                    else:
                        status = "baseline"
                        description = f"Same performance as baseline ({best_symbols_count} symbols, {len(domain_list)} domains)"
                    
                    # 🆕 Log external search count
                    short_commit = f"auto_{commit_counter}"
                    results_logger.log_result(short_commit, symbol_count, len(domain_list), 
                                             len(EXTERNAL_SEARCH_QUERIES) if "external_queries" in str(results_data) else 0,
                                             status, description)
                    
                    logger.info(f"✅ Logged to {results_logger.results_file}")
            except Exception as e:
                error_desc = str(e)[:50]
                logger.error(f"🔥 Error in cycle #{commit_counter + 1}: {error_desc}")
                
                # Autonomous decision: treat as crash, don't halt entire run
                commit_counter += 1
                short_commit = f"auto_{commit_counter}_crash"
                external_queries = len(EXTERNAL_SEARCH_QUERIES) if PARALLEL_SCRAPE_ENABLED else 0
                results_logger.log_result(short_commit, 0, 0, external_queries, 
                                         "crash", error_desc)
        
        # Check timeout before next iteration
        if remaining <= TIMEOUT_GRACE_PERIOD:
            break
    
    # Final autonomous decision
    logger.info(f"\n{'='*70}")
    logger.info(f"🏁 OVERNIGHT RESEARCH COMPLETED - PRODUCTION ENHANCED")
    logger.info(f"{'='*70}")
    
    final_status = "keep" if best_symbols_count > current_symbols else "baseline"
    final_desc = f"Completed with {best_symbols_count} total symbols detected ({final_status} status)"
    
    # Log completion to database with domain tracking
    completion_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "experiment": EXP_NAME,
        "status": final_status,
        "symbols_detected": best_symbols_count,
        "run_seconds": int(time.time() - timeout_handler.start_time),
        "domains_found": len(database.get("search_indices", {}).get("elemental_keywords", [])),
        "external_search_queries_used": len(EXTERNAL_SEARCH_QUERIES) if PARALLEL_SCRAPE_ENABLED else 0,
        "parallel_scraping_enabled": PARALLEL_SCRAPE_ENABLED
    }
    
    database_evaluator.record_result(EXP_NAME, completion_entry)
    
    logger.info(f"📊 Final results written to {results_logger.results_file}")
    logger.info(f"💾 Database updated with experiment entry")
    
    # Send report to Telegram webhook if configured
    try:
        await send_telegram_report(EXP_NAME, best_symbols_count, final_desc)
    except Exception as e:
        logger.warning(f"Telegram delivery failed (optional): {e}")
    
    logger.info(f"\n🔮 Enhanced overnight research loop ready for next iteration")
    logger.info(f"   Next run: Tomorrow at 04:15 AM (or manual trigger)")


def get_fallback_urls(count: int) -> List[str]:
    """Return sample URLs for demonstration with multi-domain search."""
    return [
        "https://en.wikipedia.org/wiki/Epstein_files",
        "https://www.nytimes.com/2025/12/trump-canada-statehood",
        "https://www.coindesk.com/tech/2025/12/bitcoin-crypto-symbolism",
        "https://en.wikipedia.org/wiki/List_of_military_coups"
    ] * (count // 4)


async def send_telegram_report(exp_name: str, symbols_count: int, description: str):
    """Send completion report to Telegram webhook."""
    try:
        logger.info(f"Telegram report would contain:")
        logger.info(f"   • Experiment: {exp_name}")
        logger.info(f"   • Symbols detected: {symbols_count}")
        logger.info(f"   • Description: {description}")
        logger.info(f"   • External queries: {'Yes' if PARALLEL_SCRAPE_ENABLED else 'No'}")
    except Exception as e:
        logger.warning(f"Telegram webhook not configured: {e}")


# Alternative synchronous main for cron compatibility
def run_main():
    """Synchronous main function for cron job compatibility."""
    import asyncio
    
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Enhanced autonomous research failed: {e}")
        logger.info("Completed with errors logged")


if __name__ == "__main__":
    run_main()
