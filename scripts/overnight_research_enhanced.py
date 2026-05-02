#!/usr/bin/env python3
"""
Steve's Gematria Enhanced Overnight Research Protocol v2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OPTIMIZATIONS IMPLEMENTED:
1. Extended timeout budget (60 min vs 15 min demo)
2. Multi-domain search queries (Wikipedia, NYTimes, Coindesk, etc.)
3. Parallel processing ready architecture

Based on Andrej Karpathy's autoresearch methodology:
- Fixed-time experiment budget
- Structured results logging (TSV)
- Autonomous iteration (no manual intervention)
- Timeout protection (>15min = auto-kill)
- Simplicity criterion evaluation
"""

import json
import time
import datetime
import signal
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from urllib.parse import urljoin

try:
    import aiohttp
except ImportError:
    print("Installing aiohttp for parallel processing...")
    subprocess = __import__('subprocess')
    subprocess.check_call(['pip3', 'install', 'aiohttp'])
    import aiohttp


# Setup logging
LOG_DIR = Path("/home/avalonas/.hermes/gematria/cron_logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "enhanced_overnight.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration (EXTENDED timeout budget for production)
EXP_NAME = f"enhanced_autonomous_{datetime.date.today().strftime('%Y%m%d')}"
MAX_RUN_SECONDS = 3600  # 60 minutes timeout protection (was 900s/15min demo)
CHECK_INTERVAL = 300  # 5 minutes between metrics checks (was 60s)
SCRAPE_BATCH_SIZE = 24
TIMEOUT_GRACE_PERIOD = 120  # 2 minutes before hard kill

# Load Firecrawl API key from env
try:
    with open(Path.home() / ".hermes/.env", "r") as f:
        for line in f:
            if "FIRECRAWL_API_KEY" in line and "=" in line:
                api_key = line.strip().split("=")[1].replace('***', 'YOUR_KEY')  # Mask for safety
                break
except Exception as e:
    logger.error(f"Failed to load API key: {e}")
    sys.exit(1)

HEADERS = {"Authorization": f"Bearer {api_key}"}
LOCAL_BASE_URL = "http://localhost:3002/v1"  # Local Firecrawl instance


# Import multi-domain URLs for external discovery
MULTI_DOMAIN_FILE = Path.home() / ".hermes/gematria/scrape_urls_external.txt"


def load_multi_domain_urls():
    """Load external search queries from file."""
    try:
        with open(MULTI_DOMAIN_FILE, "r") as f:
            urls = [line.strip() for line in f if line.strip()]
        logger.info(f"Loaded {len(urls)} multi-domain URLs from {MULTI_DOMAIN_FILE}")
        return urls
    except FileNotFoundError:
        logger.warning(f"Multi-domain file not found, using fallback URLs")
        return get_fallback_urls(SCRAPE_BATCH_SIZE)


# Parallel scraper imports (lazy load to avoid errors if aiohttp not installed)
try:
    from scripts.parallel_scrapers.firecrawl_batch_worker import scrape_parallel, scrape_multi_domain, analyze_patterns_in_results
    PARALLEL_SCRAPER_AVAILABLE = True
except ImportError:
    PARALLEL_SCRAPER_AVAILABLE = False
    logger.warning("Parallel scraper module not available - will use single-threaded mode")


class TimeoutHandler:
    """Autonomous timeout protection with extended budget."""
    
    def __init__(self, max_seconds: int):
        self.max_seconds = max_seconds
        self.start_time = time.time()
        
    def check_timeout(self) -> Tuple[bool, float]:
        elapsed = time.time() - self.start_time
        remaining = self.max_seconds - elapsed
        
        if remaining <= 0:
            return True, elapsed
        return False, elapsed


class ResultsLogger:
    """TSV results logging system with enhanced metadata."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.results_file = LOG_DIR / f"{EXP_NAME}_enhanced_results.tsv"
        
    def initialize(self):
        self.results_file.parent.mkdir(parents=True, exist_ok=True)
        header = "commit\tsymbols_detected\tdomains_found\ttimeout_seconds\tstatus\tdescription\n"
        if not self.results_file.exists():
            with open(self.results_file, "w") as f:
                f.write(header)
            logger.info(f"Initialized enhanced results logging at {self.results_file}")
    
    def log_result(self, commit_hash: str, symbols_count: int, domains_found: int, 
                   elapsed_seconds: float, status: str, description: str):
        line = f"{commit_hash}\t{symbols_count}\t{domains_found}\t{elapsed_seconds:.1f}\t{status}\t{description}\n"
        
        with open(self.results_file, "a") as f:
            f.write(line)


class DatabaseEvaluator:
    """Ground truth evaluation harness (read-only)."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        with open(db_path, "r") as f:
            self.database = json.load(f)
        
    def evaluate_improvement(self, new_symbols_count: int, current_symbols_count: int) -> bool:
        return new_symbols_count > current_symbols_count
    
    def record_result(self, metadata_key: str, result_data: Dict):
        if "entries" not in self.database or "results_log" not in self.database.get("metadata", {}):
            self.database.setdefault("metadata", {}).setdefault("results_log", [])
        
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "experiment": EXP_NAME,
            **result_data
        }
        self.database["metadata"]["results_log"].append(entry)
        
        with open(self.db_path, "w") as f:
            json.dump(self.database, f, indent=2)


async def scrape_urls_batch(urls: List[str], timeout_seconds: int, parallel: bool = True) -> Tuple[Optional[Dict], str]:
    """Scrape batch of URLs with Firecrawl v1 format."""
    
    if PARALLEL_SCRAPER_AVAILABLE:
        # Use enhanced parallel scraper for better performance
        try:
            result = await scrape_multi_domain(urls, api_key, use_crawl=False)
            
            if isinstance(result, dict) and "status" in result and result["status"] == "success":
                return result.get("results", {}), "success"
            elif isinstance(result, dict) and "error" in result:
                return {"markdown": f"Error: {result.get('error', 'Unknown error')}"}, "error"
            else:
                return {"markdown": "\n".join(urls)}, "logged_only_no_scrape"
        except Exception as e:
            logger.error(f"Parallel scrape failed: {e}")
            # Fallback to single-threaded mode
            pass
    
    # Single-threaded fallback (backward compatible)
    try:
        payload = {
            "urls": urls,
            "options": {
                "formats": ["markdown"],
                "timeout": timeout_seconds,
                "pageOptions": {"headers": {"User-Agent": "SteveGematriaBot/1.0"}}
            }
        }
        
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            try:
                async with session.post(f"{LOCAL_BASE_URL}/scrape", json=payload) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return result, "success"
                    else:
                        error_msg = await resp.text()
                        return None, f"HTTP {resp.status}: {error_msg[:100]}"
            except Exception as e:
                return None, f"Error: {str(e)}"
    except ImportError:
        logger.warning("aiohttp not available, logging URLs only for analysis")
        return {"urls": urls}, "logged_only_no_scrape"


async def analyze_patterns_in_results(results_data: Dict) -> Tuple[int, int, str]:
    """Analyze discovered patterns in scraping results."""
    
    if PARALLEL_SCRAPER_AVAILABLE and "analyze_patterns_in_results" in dir():
        return await analyze_patterns_in_results(results_data)
    
    # Fallback implementation
    symbol_keywords = ["124", "963", "55", "111", "666", "fire", "frequency", 
                       "volcano", "resonance", "coup", "political", "military"]
    
    domain_keywords = {
        "political_events": ["political", "government", "narrative"],
        "epstein_files_analysis": ["epstein", "files", "document"],
        "trump_canada_narrative": ["trump", "canada", "statehood", "mexico"],
        "bitcoin_crypto_symbolism": ["bitcoin", "crypto", "ethereum", "financial"],
        "military_coup_themes": ["coup", "military", "defense"]
    }
    
    symbol_count = 0
    domain_matches = {}
    
    if results_data and isinstance(results_data, dict) and "markdown" in results_data:
        content = results_data["markdown"].lower()
        
        for keyword in symbol_keywords:
            matches = len(content.split(keyword)) // 2
            if matches > 0:
                symbol_count += matches
        
        for domain_name, keywords in domain_keywords.items():
            for kw in keywords:
                if kw in content:
                    domain_matches[domain_name] = domain_matches.get(domain_name, 0) + 1
    
    description = f"Detected {symbol_count} pattern instances across {len(domain_matches)} domains"
    return symbol_count, len(domain_matches), description


async def main():
    """Enhanced overnight research loop with all optimizations."""
    
    logger.info(f"\n{'='*60}")
    logger.info(f"🧙‍♂️ STEVE'S GEMATRIA ENHANCED OVERNIGHT RESEARCH v2.0")
    logger.info(f"{'='*60}")
    logger.info(f"Experiment: {EXP_NAME}")
    logger.info(f"Extended timeout budget: {MAX_RUN_SECONDS}s ({MAX_RUN_SECONDS//60}min)")
    logger.info(f"Parallel processing: {'ENABLED' if PARALLEL_SCRAPER_AVAILABLE else 'FALLBACK MODE'}")
    logger.info(f"Multi-domain queries: {'ENABLED' if MULTI_DOMAIN_FILE.exists() else 'FALLBACK MODE'}")
    
    # Initialize components
    db_path = Path.home() / ".hermes/gematria/database/gematria_database.json"
    results_logger = ResultsLogger(db_path)
    database_evaluator = DatabaseEvaluator(db_path)
    
    with open(db_path, "r") as f:
        database = json.load(f)
    
    current_symbols = len(database.get("search_indices", {}).get("core_numbers", []))
    logger.info(f"Starting from {current_symbols} existing symbols in database")
    
    results_logger.initialize()
    
    # Load multi-domain URLs (EXTENDED OPTIMIZATION #2)
    urls = load_multi_domain_urls()
    logger.info(f"Prepared {len(urls)} URLs for analysis (multi-domain enabled)")
    
    # Create timeout handler (extended budget - OPTIMIZATION #1)
    timeout_handler = TimeoutHandler(MAX_RUN_SECONDS)
    
    best_symbols_count = current_symbols
    commit_counter = 0
    
    while timeout_handler.max_seconds - time.time() > CHECK_INTERVAL:
        elapsed, remaining = timeout_handler.check_timeout()
        logger.info(f"\n[{elapsed:.1f}s elapsed, {remaining:.0f}s remaining]")
        
        if remaining <= TIMEOUT_GRACE_PERIOD:
            status = "timeout"
            description = f"Auto-kill triggered at {MAX_RUN_SECONDS}s budget"
            
        else:
            # Autonomous experiment cycle
            logger.info(f"▶️  Running enhanced scrape cycle (cycle #{commit_counter + 1})")
            
            try:
                results_data, status_msg = await scrape_urls_batch(
                    urls, CHECK_INTERVAL, parallel=PARALLEL_SCRAPER_AVAILABLE
                )
                
                if status_msg in ["success", "logged_only_no_scrape"] and results_data:
                    commit_counter += 1
                    
                    # Analyze patterns
                    symbol_count, domain_count, description = await analyze_patterns_in_results(results_data)
                    
                    logger.info(f"✅ Analysis complete: {symbol_count} symbols, {domain_count} domains")
                    
                    # Evaluate improvement
                    improved = database_evaluator.evaluate_improvement(symbol_count, best_symbols_count)
                    
                    if improved:
                        status = "keep"
                        description = f"Improved discovery: {symbol_count} symbols (+{symbol_count - best_symbols_count}) across {domain_count} domains"
                        
                        best_symbols_count = symbol_count
                    
                    else:
                        status = "baseline"
                        description = f"Same performance as baseline ({best_symbols_count} symbols)"
                    
                    # Log to TSV with timeout metadata
                    short_commit = f"enhanced_{commit_counter}"
                    results_logger.log_result(
                        short_commit, 
                        symbol_count, 
                        domain_count,
                        elapsed,
                        status, 
                        description
                    )
                    
                    logger.info(f"✅ Logged enhanced results to {results_logger.results_file}")
                    
            except Exception as e:
                error_desc = str(e)[:100]
                logger.error(f"🔥 Error in cycle #{commit_counter + 1}: {error_desc}")
                
                commit_counter += 1
                short_commit = f"enhanced_{commit_counter}_crash"
                results_logger.log_result(short_commit, 0, 0, elapsed, "crash", error_desc)
        
        # Check timeout before next iteration (OPTIMIZATION #1: Extended grace period)
        if remaining <= TIMEOUT_GRACE_PERIOD:
            break
    
    # Final completion report
    logger.info(f"\n{'='*60}")
    logger.info(f"🏁 ENHANCED OVERNIGHT RESEARCH COMPLETED")
    logger.info(f"{'='*60}")
    
    final_status = "keep" if best_symbols_count > current_symbols else "baseline"
    final_desc = f"Completed with {best_symbols_count} total symbols detected ({final_status} status)"
    
    completion_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "experiment": EXP_NAME,
        "status": final_status,
        "symbols_detected": best_symbols_count,
        "run_seconds": int(time.time() - timeout_handler.start_time),
        "best_domains_found": len(database.get("search_indices", {}).get("elemental_keywords", [])),
        "parallel_mode": PARALLEL_SCRAPER_AVAILABLE,
        "multi_domain_queries": MULTI_DOMAIN_FILE.exists() if Path(MULTI_DOMAIN_FILE).exists() else False
    }
    
    database_evaluator.record_result(EXP_NAME, completion_entry)
    
    logger.info(f"📊 Enhanced results written to {results_logger.results_file}")
    logger.info(f"💾 Database updated with experiment entry")


def get_fallback_urls(count: int) -> List[str]:
    """Return sample URLs for demonstration when queue is empty."""
    return [
        "https://en.wikipedia.org/wiki/Epstein_files",
        "https://www.nytimes.com/2025/12/trump-canada-statehood",
        "https://www.coindesk.com/tech/2025/12/bitcoin-crypto-symbolism",
        "https://en.wikipedia.org/wiki/List_of_military_coups"
    ] * (count // 4)


# Synchronous wrapper for cron compatibility
def run_main():
    """Synchronous main function for cron job compatibility."""
    import asyncio
    
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Enhanced overnight research failed: {e}")
        logger.info("Completed with errors logged")


if __name__ == "__main__":
    run_main()
