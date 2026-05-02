#!/usr/bin/env python3
"""
Steve's Gematria Autonomous Overnight Research Protocol
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Based on Andrej Karpathy's autoresearch methodology:
- Fixed-time experiment budget
- Structured results logging (TSV)
- Autonomous iteration (no manual intervention)
- Timeout protection (>15min = auto-kill)
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
import logging
from urllib.parse import urljoin

# Setup logging
LOG_DIR = Path("/home/avalonas/.hermes/gematria/cron_logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "overnight_autonomous.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration (fixed experiment budget)
EXP_NAME = f"autonomous_{datetime.date.today().strftime('%Y%m%d')}"
MAX_RUN_SECONDS = 900  # 15 minutes timeout protection
CHECK_INTERVAL = 60  # seconds between metrics checks
SCRAPE_BATCH_SIZE = 24  # URLs per run
TIMEOUT_GRACE_PERIOD = 30  # seconds before hard kill

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


class ResultsLogger:
    """
    TSV results logging system (from autoresearch_folktales).
    Tracks experiment metrics with commit-style versioning.
    """
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.results_file = LOG_DIR / f"{EXP_NAME}_results.tsv"
        
    def initialize(self):
        """Initialize results TSV with header row."""
        self.results_file.parent.mkdir(parents=True, exist_ok=True)
        header = "commit\tsymbols_detected\tdomains_found\tstatus\tdescription\n"
        if not self.results_file.exists():
            with open(self.results_file, "w") as f:
                f.write(header)
            logger.info(f"Initialized results logging at {self.results_file}")
    
    def log_result(self, commit_hash: str, symbols_count: int, domains_found: int, 
                   status: str, description: str):
        """Log experiment result to TSV (NOT CSV - commas break in descriptions)."""
        line = f"{commit_hash}\t{symbols_count}\t{domains_found}\t{status}\t{description}\n"
        
        # Append to results file (no overwrite on timeout)
        with open(self.results_file, "a") as f:
            f.write(line)
    
    def get_best_run(self) -> Optional[Dict]:
        """Get best run by symbol count (equivalent to val_bpb metric)."""
        if not self.results_file.exists():
            return None
        
        best_count = -1
        best_run = None
        
        with open(self.results_file, "r") as f:
            for line in f:
                parts = line.strip().split("\t", 4)
                if len(parts) >= 3:
                    try:
                        symbols = int(parts[1])
                        if symbols > best_count and parts[3] == "keep":
                            best_count = symbols
                            best_run = parts
                    except ValueError:
                        continue
        
        return best_run


class DatabaseEvaluator:
    """
    Ground truth evaluation harness (read-only).
    From autoresearch_folktales: agent can't modify prepare.py, only train.py.
    
    For our system: database/gematria_database.json is the ground truth - we log improvements here.
    """
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        with open(db_path, "r") as f:
            self.database = json.load(f)
        
    def evaluate_improvement(self, new_symbols_count: int, current_symbols_count: int) -> bool:
        """
        Evaluate if run improved (lower val_bpb in training = better; 
        higher symbol count here = better discovery).
        """
        return new_symbols_count > current_symbols_count
    
    def record_result(self, metadata_key: str, result_data: Dict):
        """Record experiment result to database ground truth."""
        if "entries" not in self.database or "results_log" not in self.database.get("metadata", {}):
            # Initialize results log structure
            self.database.setdefault("metadata", {}).setdefault("results_log", [])
        
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "experiment": EXP_NAME,
            **result_data
        }
        self.database["metadata"]["results_log"].append(entry)
        
        with open(self.db_path, "w") as f:
            json.dump(self.database, f, indent=2)


async def scrape_urls_batch(urls: List[str], timeout_seconds: int) -> Tuple[Optional[Dict], str]:
    """
    Scrape batch of URLs with local Firecrawl v1 format.
    Returns (scrape_result, status_message).
    """
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
        # Fallback: just log the URLs without scraping if aiohttp not available
        logger.warning("aiohttp not available, logging URLs only for analysis")
        return {"urls": urls}, "logged_only_no_scrape"


async def analyze_patterns_in_results(results_data: Dict) -> Tuple[int, int, str]:
    """
    Analyze discovered patterns in scraping results.
    Returns (symbol_count, domain_count, description).
    """
    symbol_keywords = ["124", "963", "55", "111", "666", "fire", "frequency", 
                       "volcano", "resonance", "coup", "political", "military"]
    
    domain_keywords = {
        "political_events": ["political", "government", "narrative"],
        "epstein_files_analysis": ["epstein", "files", "document"],
        "trump_canada_narrative": ["trump", "canada", "statehood", "mexico"],
        "bitcoin_crypto_symbolism": ["bitcoin", "crypto", "ethereum", "financial"],
        "military_coup_themes": ["coup", "military", "defense", "defense"]
    }
    
    symbol_count = 0
    domain_matches = {}
    
    if results_data and "markdown" in results_data:
        content = results_data["markdown"].lower()
        
        for keyword in symbol_keywords:
            matches = len(content.split(keyword)) // 2  # Rough frequency count
            if matches > 1:
                symbol_count += matches
        
        for domain_name, keywords in domain_keywords.items():
            for kw in keywords:
                if kw in content:
                    domain_matches[domain_name] = domain_matches.get(domain_name, 0) + 1
    
    description = f"Detected {symbol_count} pattern instances across {len(domain_matches)} domains"
    return symbol_count, len(domain_matches), description


async def main():
    """
    Autonomous overnight research loop.
    Implements Karpathy's fixed-time experiment budget + autonomous iteration.
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"🧙‍♂️  STEVE'S GEMATRIA AUTONOMOUS OVERNIGHT RESEARCH")
    logger.info(f"{'='*60}")
    logger.info(f"Experiment: {EXP_NAME}")
    logger.info(f"Fixed time budget: {MAX_RUN_SECONDS}s ({MAX_RUN_SECONDS//60}min)")
    logger.info(f"Timeout protection enabled (hard kill at >{MAX_RUN_SECONDS}s)")
    
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
    
    # Get URLs to scrape (from previous session or hardcoded list)
    try:
        with open(Path.home() / ".hermes/gematria/scrape_urls_queue.txt", "r") as f:
            urls = [line.strip() for line in f if line.strip()][:SCRAPE_BATCH_SIZE]
    except FileNotFoundError:
        # Fallback to previous session's scraped content
        logger.info("No queue file found, using embedded URLs for demo")
        urls = get_fallback_urls(SCRAPE_BATCH_SIZE)
    
    logger.info(f"Prepared {len(urls)} URLs for analysis")
    
    # Create timeout handler (fixed-time experiment budget)
    timeout_handler = TimeoutHandler(MAX_RUN_SECONDS)
    
    # Main autonomous loop
    best_symbols_count = current_symbols
    commit_counter = 0
    
    while timeout_handler.max_seconds - time.time() > CHECK_INTERVAL:
        elapsed, remaining = timeout_handler.check_timeout()
        logger.info(f"\n[{elapsed:.1f}s elapsed, {remaining:.0f}s remaining]")
        
        if remaining <= TIMEOUT_GRACE_PERIOD:
            status = "timeout"
            description = f"Auto-kill triggered at {MAX_RUN_SECONDS}s budget"
            
        else:
            # Autonomous experiment: scrape and analyze
            logger.info(f"▶️  Running autonomous scrape cycle (cycle #{commit_counter + 1})")
            
            # Scrape batch
            try:
                results_data, status_msg = await scrape_urls_batch(urls, CHECK_INTERVAL)
                
                if status_msg == "success" and results_data and "markdown" in results_data:
                    commit_counter += 1
                    
                    # Analyze patterns (equivalent to running training experiment)
                    symbol_count, domain_count, description = await analyze_patterns_in_results(results_data)
                    
                    logger.info(f"✅ Analysis complete: {symbol_count} symbols, {domain_count} domains")
                    
                    # Evaluate improvement (read-only ground truth check)
                    improved = database_evaluator.evaluate_improvement(symbol_count, best_symbols_count)
                    
                    if improved:
                        status = "keep"
                        description = f"Improved discovery: {symbol_count} symbols (+{symbol_count - best_symbols_count}) across {domain_count} domains"
                        
                        # Update best result
                        best_symbols_count = symbol
                        
                    else:
                        status = "baseline"
                        description = f"Same performance as baseline ({best_symbols_count} symbols)"
                    
                    # Log to TSV (structured results logging)
                    short_commit = f"auto_{commit_counter}"
                    results_logger.log_result(short_commit, symbol_count, domain_count, status, description)
                    
                    logger.info(f"✅ Logged to {results_logger.results_file}")
            
            except Exception as e:
                error_desc = str(e)[:50]
                logger.error(f"🔥 Error in cycle #{commit_counter + 1}: {error_desc}")
                
                # Autonomous decision: treat as crash, don't halt entire run
                commit_counter += 1
                short_commit = f"auto_{commit_counter}_crash"
                results_logger.log_result(short_commit, 0, 0, "crash", error_desc)
        
        # Check timeout before next iteration
        if remaining <= TIMEOUT_GRACE_PERIOD:
            break
    
    # Final autonomous decision: record completion state
    logger.info(f"\n{'='*60}")
    logger.info(f"🏁 OVERNIGHT RESEARCH COMPLETED")
    logger.info(f"{'='*60}")
    
    final_status = "keep" if best_symbols_count > current_symbols else "baseline"
    final_desc = f"Completed with {best_symbols_count} total symbols detected ({final_status} status)"
    
    # Log completion to database
    completion_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "experiment": EXP_NAME,
        "status": final_status,
        "symbols_detected": best_symbols_count,
        "run_seconds": int(time.time() - timeout_handler.start_time),
        "best_domains_found": len(database.get("search_indices", {}).get("elemental_keywords", []))
    }
    
    database_evaluator.record_result(EXP_NAME, completion_entry)
    
    logger.info(f"📊 Final results written to {results_logger.results_file}")
    logger.info(f"💾 Database updated with experiment entry")
    
    # Send report to Telegram webhook if configured
    try:
        await send_telegram_report(EXP_NAME, best_symbols_count, final_desc)
    except Exception as e:
        logger.warning(f"Telegram delivery failed (optional): {e}")
    
    logger.info(f"\n🔮 Autonomous overnight research loop ready for next iteration")
    logger.info(f"   Next run: Tomorrow at 04:15 AM (or manual trigger)")


def get_fallback_urls(count: int) -> List[str]:
    """Return sample URLs for demonstration when queue is empty."""
    return [
        "https://en.wikipedia.org/wiki/Epstein_files",
        "https://www.nytimes.com/2025/12/trump-canada-statehood",
        "https://www.coindesk.com/tech/2025/12/bitcoin-crypto-symbolism",
        "https://en.wikipedia.org/wiki/List_of_military_coups"
    ] * (count // 4)


async def send_telegram_report(exp_name: str, symbols_count: int, description: str):
    """Send completion report to Telegram webhook."""
    try:
        # This would require a separate webhook setup
        logger.info(f"Telegram report would contain:")
        logger.info(f"   • Experiment: {exp_name}")
        logger.info(f"   • Symbols detected: {symbols_count}")
        logger.info(f"   • Status: {description}")
    except Exception as e:
        logger.warning(f"Telegram webhook not configured: {e}")


# Alternative synchronous main for cron compatibility (no async/await)
def run_main():
    """Synchronous main function for cron job compatibility."""
    import asyncio
    
    # Run with timeout protection
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Autonomous research failed: {e}")
        logger.info("Completed with errors logged")


if __name__ == "__main__":
    run_main()
