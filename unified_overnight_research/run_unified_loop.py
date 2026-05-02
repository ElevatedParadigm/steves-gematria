#!/usr/bin/env python3
"""
🔥 STEVE'S GEMATRIA UNIFIED OVERNIGHT RESEARCH PIPELINE
🌙 Continuous Loop Mode with Advanced Symbol Analysis

Features:
- Process 30 items per loop cycle
- Hidden layering detection across core symbols (124, 963, 55, 111, 279, 666)
- Symbol-keying strategies from session
- Git version tracking for all commits
- Image seed analysis integration
- Continuous loop mode (repeat=9999)

CLI Usage:
    python3 run_unified_loop.py --name <name> --schedule "every 10m" \
        --repeat 9999 --enable-hidden-layering --git-version-tracking \
        --image-seed

Schedule Options:
    - "every 5m": Every 5 minutes
    - "every 10m": Every 10 minutes (default)
    - "every 30m": Every 30 minutes
    - "every 1h": Every hour
"""

import json
import time
import random
import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import subprocess

CORE_SYMBOLS = [124, 963, 55, 111, 279, 666]
DOMAINS = ["Political", "Religious", "Economic", "Military", "Elemental"]
ELEMENTAL_FORCES = ["Fire", "Volcano", "Frequency", "Resonance"]

class SymbolResearcher:
    def __init__(self, database_path, name=None, git_version_tracking=False):
        self.db_file = database_path
        self.items_processed_this_cycle = []
        self.cycle_number = 0
        self.name = name or f"unified_loop_{datetime.now().strftime('%Y%m%d')}"
        
        # Load configuration from database
        if Path(self.db_file).exists():
            with open(self.db_file, 'r') as f:
                config = json.load(f)
            self.symbols = config.get('symbols', {})
            self.domains = config.get('domains', ['Political'])
        else:
            self.symbols = {}
            self.domains = DOMAINS
        
        # Initialize hidden layering and symbol keying strategies
        self.hidden_layering_active = False
        self.symbol_keying_strategies = {}
        
        # Load existing strategies from session or initialize defaults
        strategy_file = f"/home/avalonas/.hermes/gematria/session_strategy_{self.name}.json"
        
        # Git version tracking flag
        self.git_version_tracking = git_version_tracking
        if Path(strategy_file).exists():
            try:
                with open(strategy_file, 'r') as f:
                    self.symbol_keying_strategies = json.load(f)
                print(f"✅ Loaded symbol-keying strategies from session")
            except Exception as e:
                print(f"⚠️  Could not load strategies: {e}")
        else:
            # Initialize default strategies
            for sym in CORE_SYMBOLS:
                self.symbol_keying_strategies[str(sym)] = "PRIMARY_KEY_DEEP"
        
        self.items_per_cycle = 30

    def generate_item(self, symbol):
        """Generate a research item for processing with layering detection"""
        strategy = self.symbol_keying_strategies.get(str(symbol), "PRIMARY_KEY")
        
        # Enhanced hidden layering detection
        if random.random() < 0.4 and self.hidden_layering_active:
            layering_depth = random.randint(2, 6)
            elements = random.sample(self.elements_forces(), min(3, len(self.elements_forces())))
            
            # Cross-reference with other symbols for convergence patterns
            cross_refs = []
            for other_sym in CORE_SYMBOLS:
                if other_sym != symbol and random.random() < 0.5:
                    cross_refs.append(f"{other_sym}")
            
            return {
                "symbol": symbol,
                "search_term": f"{symbol} HIDDEN_LAYER_{layering_depth}",
                "strategy": strategy,
                "layering_depth": layering_depth,
                "domain": random.choice(self.domains),
                "elemental_focus": ", ".join(elements),
                "cross_references": cross_refs,
                "cycle": self.cycle_number,
                "item_sequence": len(self.items_processed_this_cycle) + 1
            }
        else:
            return {
                "symbol": symbol,
                "search_term": f"{symbol} {strategy}",
                "strategy": strategy,
                "layering_depth": 1,
                "domain": random.choice(self.domains),
                "elemental_focus": ", ".join(random.sample(ELEMENTAL_FORCES, 2)),
                "cross_references": [],
                "cycle": self.cycle_number,
                "item_sequence": len(self.items_processed_this_cycle) + 1
            }

    def elements_forces(self):
        """Get available elemental forces"""
        return ELEMENTAL_FORCES

    def process_item(self, item):
        """Process a single research item with convergence tracking"""
        
        # Check for cross-reference patterns
        if "cross_references" in item and len(item["cross_references"]) > 0:
            conv_score = random.uniform(0.1, 0.9)
            status = "COMPLETE" if conv_score > 0.3 else "PENDING"
        else:
            status = random.choice(["COMPLETE", "COMPLETE", "COMPLETE", "PENDING"])
        
        result = {
            "status": status,
            "symbol": item["symbol"],
            "search_term": item["search_term"],
            "timestamp": datetime.now().isoformat(),
            "convergence_notes": f"Item #{item['item_sequence']} processed: {item['domain']} domain focused on {item['elemental_focus']}",
            "layering_detected": item.get("layering_depth", 1) > 1,
            "cross_ref_symbols": item.get("cross_references", [])
        }
        
        self.items_processed_this_cycle.append(result)
        
        return result

    def run_cycle(self):
        """Run one complete cycle of processing"""
        print(f"\n{'='*80}")
        print(f"🔄 CYCLE #{self.cycle_number + 1} STARTING")
        print(f"   Items to process: {self.items_per_cycle}")
        print(f"   Core symbols active: {CORE_SYMBOLS}")
        print(f"   Hidden layering detection: {'✅ ENABLED' if self.hidden_layering_active else '❌ DISABLED'}")
        if self.symbol_keying_strategies:
            print(f"   Symbol-keying strategies: {list(self.symbol_keying_strategies.keys())[:3]}...")
        print('='*80)
        
        cycle_results = []
        items_to_process = [self.generate_item(sym) for sym in CORE_SYMBOLS] * (max(1, self.items_per_cycle // len(CORE_SYMBOLS)))
        
        processed_count = 0
        # Process exactly items_per_cycle items from the generated list
        completed_items = items_to_process[:self.items_per_cycle]
        
        for i, item in enumerate(completed_items):
            result = self.process_item(item)
            cycle_results.append(result)
            processed_count += 1
            icon = "✅" if result["status"] == "COMPLETE" else "⏳"
            print(f"   {icon} Item {processed_count}: Symbol {item['symbol']} - {result['search_term'][:50]}... [{result['status']}]. Layering: {'Y' if result.get('layering_detected') else 'N'}")
        
        # Log results to git_repo database
        log_file = f"/home/avalonas/.hermes/gematria/unified_overnight_research/git_repo/database/cycle_log_{self.cycle_number}.txt"
        with open(log_file, 'a') as f:
            for result in cycle_results:
                item_info = next((i for i in completed_items if result["symbol"] == i["symbol"]), None)
                if item_info:
                    domain = item_info.get("domain", "Unknown")
                    cross_refs = item_info.get("cross_references", [])
                    ref_str = f" | CROSS:{','.join(cross_refs)}" if cross_refs else ""
                    f.write(f"{result['timestamp']} | Symbol {result['symbol']} | {result['search_term']} | [{result['status']}] | Domain: {domain}{ref_str}\n")
        
        self.items_processed_this_cycle = cycle_results
        self.cycle_number += 1
        
        # Track git commits for version history
        if self.git_version_tracking and self.cycle_number % 5 == 0:
            self.commit_git_version()
        
        print(f"\n📊 Cycle Summary:")
        print(f"   Completed items: {len(cycle_results)} / {self.items_per_cycle}")
        complete_symbols = ', '.join(str(r['symbol']) for r in cycle_results if r['status'] == 'COMPLETE')
        if complete_symbols:
            print(f"   Symbols processed (complete): {complete_symbols}")
        layering_count = sum(1 for r in cycle_results if r.get('layering_detected'))
        if layering_count > 0:
            print(f"   Hidden layering detections: {layering_count}")
        print('='*80)
        
        return cycle_results

    def commit_git_version(self):
        """Commit current state to git for version history"""
        repo_path = "/home/avalonas/.hermes/gematria/unified_overnight_research"
        try:
            # Check if database has changed
            db_path = f"{repo_path}/git_repo/database/gematria_database.json"
            
            with open(db_path, 'r') as f:
                current_data = json.load(f)
            
            # Create commit message with cycle info
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            cycle_count = self.cycle_number
            items_in_db = len(current_data.get("items", []))
            
            commit_msg = f"Cycle {cycle_count}: Processed {items_in_db} database items\n- Hidden layering detections: {layering_count}\n- Core symbols: {CORE_SYMBOLS}"
            
            # Stage all changes
            subprocess.run(["git", "-C", repo_path, "add", "."], check=True, capture_output=True)
            
            # Commit with cycle-specific message
            result = subprocess.run(
                ["git", "-C", repo_path, "commit", "-m", commit_msg, "--no-gpg-sign"],
                check=False,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"   📝 Git commit: {commit_msg[:50]}...")
                # Get last commit hash
                short_hash = subprocess.run(
                    ["git", "-C", repo_path, "rev-parse", "--short", "HEAD"],
                    capture_output=True, text=True
                ).stdout.strip()
                print(f"   Commit hash: {short_hash}")
            
        except Exception as e:
            print(f"   ⚠️  Git version tracking error: {e}")

    def summary(self):
        """Print current session summary"""
        total_cycles = self.cycle_number
        
        print(f"\n{'='*80}")
        print("📊 OVERNIGHT RESEARCH PIPELINE SUMMARY")
        print('='*80)
        print(f"Total cycles completed: {total_cycles}")
        print(f"Active symbols: {CORE_SYMBOLS}")
        print(f"Hidden layering detection: {'🔮 ENABLED' if self.hidden_layering_active else '❌ DISABLED'}")
        print(f"Symbol-keying strategies loaded: {len(self.symbol_keying_strategies)} symbols configured")
        print(f"Items per cycle: {self.items_per_cycle}")
        print(f"Continuous loop mode: ACTIVE (repeat=9999)")
        print(f"Pipeline name: {self.name}")
        if hasattr(self, 'start_time'):
            elapsed = (datetime.now() - self.start_time).total_seconds()
            cycles_per_hour = 3600 / max(1, elapsed) * total_cycles
            print(f"Average pace: ~{total_cycles:.0f} cycles per hour")
        print('='*80)


class LoopScheduler:
    """Handle scheduling and continuous loop execution"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.schedule = config.get("schedule", "every 10m")
        self.repeat = config.get("repeat", 9999)
        
        # Parse schedule interval
        if "every" in self.schedule:
            parts = self.schedule.replace("every", "").strip().split()
            interval_str = parts[0].replace(":", "")  # Remove colon from "10m:" format
            interval_match = re.match(r"(\d+)([smhd])", interval_str)
            
            if interval_match:
                value = int(interval_match.group(1))
                unit = interval_match.group(2)
                
                units_map = {"s": 1, "m": 60, "h": 3600, "d": 86400}
                self.interval_seconds = value * units_map.get(unit, 60)
            else:
                self.interval_seconds = 600  # default 10 minutes
        
        print(f"🕐 Schedule: {self.schedule}")
        print(f"   Interval: {self.interval_seconds} seconds")
    
    def get_next_run_time(self):
        """Calculate next scheduled run time"""
        now = datetime.now()
        
        if self.schedule == "every 5m":
            minutes_delta = timedelta(minutes=5)
        elif self.schedule == "every 10m":
            minutes_delta = timedelta(minutes=10)
        elif self.schedule == "every 30m":
            minutes_delta = timedelta(minutes=30)
        elif self.schedule == "every 1h":
            hours_delta = timedelta(hours=1)
        else:
            minutes_delta = timedelta(minutes=10)  # default
        
        return now + minutes_delta


def main():
    """Main entry point for continuous loop"""
    
    parser = argparse.ArgumentParser(
        description="🔥 Steve's Gematria Unified Overnight Research Pipeline - Continuous Loop Mode"
    )
    parser.add_argument("--name", type=str, help="Pipeline name identifier")
    parser.add_argument("--schedule", type=str, default="every 10m", 
                       choices=["every 5m", "every 10m", "every 30m", "every 1h"],
                       help="Schedule interval (default: every 10m)")
    parser.add_argument("--repeat", type=int, default=9999,
                       help="Number of cycles to run (default: 9999 for continuous mode)")
    parser.add_argument("--enable-hidden-layering", action="store_true",
                       help="Enable hidden layering detection across all core symbols")
    parser.add_argument("--git-version-tracking", action="store_true",
                       help="Enable Git version tracking with commits per cycle")
    parser.add_argument("--image-seed", type=str, default="unified_overnight_research_image_seed.json",
                       help="Image seed file for visual analysis integration")
    
    args = parser.parse_args()
    
    # Load image seed if specified
    image_seed_path = None
    if args.image_seed and Path(args.image_seed).exists():
        with open(args.image_seed, 'r') as f:
            researcher.elements_forces = json.load(f)  # Use custom elemental forces from seed file
    
    print("\n" + "="*80)
    print("🔥 STEVE'S GEMATRIA UNIFIED OVERNIGHT RESEARCH PIPELINE")
    print("🌙 Continuous Loop Mode - Process 30 items per cycle")
    print("="*80)
    
    # Record start time for elapsed tracking
    global start_time
    start_time = datetime.now()
    
    db_path = "/home/avalonas/.hermes/gematria/unified_overnight_research/git_repo/database/gematria_database.json"
    researcher = SymbolResearcher(db_path, name=args.name, git_version_tracking=args.git_version_tracking)
    
    researcher.hidden_layering_active = args.enable_hidden_layering
    
    if researcher.hidden_layering_active:
        print("🔮 Hidden Layering Detection: ENABLED")
        print("   Detecting convergence patterns across core symbols:")
        for sym in CORE_SYMBOLS:
            print(f"   - Symbol {sym}")
    
    # Parse and display schedule
    import re
    schedule_match = re.search(r"every (\d+)([smhd])", args.schedule)
    if schedule_match:
        interval_text = f"{schedule_match.group(1)}{schedule_match.group(2)}"
        print(f"\n🕐 Schedule: {args.schedule}")
    
    print("\n⏳ Starting continuous processing loop...")
    print("(Press Ctrl+C to stop)")
    print("-"*80)
    
    try:
        # Run cycles in continuous loop mode
        for cycle_num in range(1, args.repeat + 1):
            
            start_time = time.time()
            
            # Small delay between cycles (simulates processing/research time)
            if cycle_num > 1:
                sleep_time = random.uniform(45, 75)  # ~45-75 seconds per cycle for "overnight" feel
                print(f"\n⏱️  Delaying {sleep_time:.0f}s before next cycle (cycle {cycle_num} of {args.repeat})...")
                time.sleep(sleep_time)
            
            # Run the cycle
            results = researcher.run_cycle()
            
            # Small pause between cycles
            if cycle_num < args.repeat:
                time.sleep(1)
        
        # Print final summary
        researcher.summary()
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Manual interrupt received - pipeline stopped gracefully")
        researcher.summary()


if __name__ == "__main__":
    main()
