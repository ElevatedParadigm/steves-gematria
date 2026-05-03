#!/usr/bin/env python3
"""
Continuous Loop Mode Wrapper for Steve's Gematria Overnight Research Pipeline
==============================================================================
Runs the enhanced_loop_runner.py continuously in loop mode until manually stopped.
Monitors completion markers and phase transitions in logs.
Each cycle runs every 3 hours (10800 seconds).
9999 iterations = continuous until stopped.
"""

import sys
import os
import json
import time
from datetime import datetime, timezone
from pathlib import Path

# Working directories
WORKING_DIR = Path.home() / ".hermes" / "gematria" / "unified_overnight_research"
SCRIPTS_DIR = WORKING_DIR / "scripts"
DB_PATH = WORKING_DIR.parent / "database" / "gematria_database.json"
OBSIDIAN_EXPORTS = WORKING_DIR / "obsidian_exports"
LOGS_DIR = WORKING_DIR.parent / "logs"
CRON_LOGS_DIR = WORKING_DIR.parent / "cron_logs"

class ContinuousLoopRunner:
    """Runs overnight research pipeline in continuous loop mode."""
    
    def __init__(self, max_iterations: int = 9999):
        self.max_iterations = max_iterations  # 9999 iterations = continuous
        self.iteration_count = 0
        self.start_time = datetime.now()
        self.cycle_interval = 10800  # 3 hours in seconds
        
        # Ensure directories exist
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        CRON_LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
    def run_stability_test(self) -> tuple[bool, str]:
        """Run stability test on gematria database."""
        print("\n🧪 PHASE: STABILITY TEST ===>")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        log_entry = (
            f"[{timestamp}] === STABILITY TEST ====\n"
            f"  → Running enhanced stability test with Priority Enhancements\n"
            f"  → UTC Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        )
        log_path = CRON_LOGS_DIR / "stability_test.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_path, 'a') as f:
            f.write(log_entry + "\n")
        
        try:
            process = subprocess.Popen(
                [sys.executable, str(DB_PATH), "stability"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=str(CRON_LOGS_DIR)
            )
            
            output, _ = process.communicate(timeout=300)
            print(output[:2000])  # Limit output
            
            if process.returncode == 0:
                return True, "passed"
            else:
                return False, f"Stability test failed with code {process.returncode}"
                
        except Exception as e:
            return False, f"Exception during stability test: {str(e)}"
    
    def run_auto_sync(self) -> tuple[bool, str]:
        """Perform auto-sync to Obsidian notes."""
        print("\n📤 PHASE: AUTO-SYNC TO OBSIDIAN ===>")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        log_entry = (
            f"[{timestamp}] === AUTO-SYNC PHASE ====\n"
            f"  → Starting auto-sync with relationship extraction\n"
            f"  → UTC Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        )
        log_path = CRON_LOGS_DIR / "autosync.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_path, 'a') as f:
            f.write(log_entry + "\n")
        
        try:
            process = subprocess.Popen(
                [sys.executable, str(SCRIPTS_DIR / "auto_obisidian_sync_v2.py")],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=str(OBSIDIAN_EXPORTS)
            )
            
            output, _ = process.communicate(timeout=180)
            print(output[:2500])
            
            if process.returncode == 0:
                status_msg = (
                    f"[{datetime.now().strftime('%H:%M:%S')}] === AUTOSYNC COMPLETED ====\n"
                    f"  → Auto-sync completed - relationship matrices and cross-reference index updated\n"
                    f"  → UTC Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
                )
                with open(log_path, 'a') as f:
                    f.write(status_msg + "\n")
                
                # Generate correlation heatmaps if available
                self._generate_heatmaps()
                
                return True, "synced_and_heatmaps_generated"
            else:
                error = (
                    f"[{datetime.now().strftime('%H:%M:%S')}] === AUTOSYNC FAILED ====\n"
                    f"  → Exit code: {process.returncode}\n"
                    f"  → UTC Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
                )
                with open(log_path, 'a') as f:
                    f.write(error + "\n")
                
                return False, "sync_failed"
                
        except Exception as e:
            error = (
                f"[{datetime.now().strftime('%H:%M:%S')}] === AUTOSYNC EXCEPTION ====\n"
                f"  → Exception: {str(e)}\n"
                f"  → UTC Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            )
            log_path = CRON_LOGS_DIR / "autosync.log"
            with open(log_path, 'a') as f:
                f.write(error + "\n")
            return False, f"Exception: {str(e)}"
    
    def _generate_heatmaps(self):
        """Generate correlation heatmaps and relationship matrices."""
        heatmap_script = SCRIPTS_DIR / "heatmap_generator.py"
        
        if not heatmap_script.exists():
            print("\n⚠️  Heatmap generator not found - skipping visualization generation")
            return
        
        try:
            process = subprocess.Popen(
                [sys.executable, str(heatmap_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            output, _ = process.communicate(timeout=60)
            if output:
                print(output[:500] + "..." if len(output) > 500 else output)
                
        except Exception as e:
            print(f"\n⚠️  Heatmap generation skipped (not critical): {e}")
    
    def run_cycle(self) -> tuple[bool, str]:
        """Run one complete research loop cycle."""
        self.iteration_count += 1
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print("\n" + "=" * 70)
        print(f"🌙 OVERNIGHT RESEARCH PROTOCOL - CYCLE #{self.iteration_count}")
        print("=" * 70)
        print(f"Timestamp: {timestamp}")
        print(f"Iteration Counter: {self.iteration_count}/{self.max_iterations}")
        print(f"Interval: {self.cycle_interval}s (3 hours)")
        print("=" * 70)
        
        cycle_log = CRON_LOGS_DIR / f"cycle_{self.iteration_count}.log"
        
        try:
            # Step 1: Run stability test first
            stability_passed, stability_status = self.run_stability_test()
            
            if not stability_passed:
                print("\n❌ Stability test failed - cycle aborted")
                return False, "stability_failed"
            
            # Step 2: Run auto-sync and heatmap generation
            sync_passed, sync_status = self.run_auto_sync()
            
            if sync_passed:
                status_msg = "Research cycle completed successfully!"
                
                # Log success
                log_entry = (
                    f"[{datetime.now().strftime('%H:%M:%S')}] === CYCLE #{self.iteration_count} COMPLETED ====\n"
                    f"  → Status: {status_msg}\n"
                    f"  → Iteration: {self.iteration_count}/{self.max_iterations}\n"
                    f"  → UTC Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
                )
                with open(cycle_log, 'a') as f:
                    f.write(log_entry + "\n")
                
                return True, status_msg
            else:
                print("\n⚠️  Sync failed but proceeding to next cycle...")
                log_entry = (
                    f"[{datetime.now().strftime('%H:%M:%S')}] === CYCLE #{self.iteration_count} PARTIAL ====\n"
                    f"  → Status: Sync failed\n"
                    f"  → Iteration: {self.iteration_count}/{self.max_iterations}\n"
                    f"  → UTC Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
                )
                with open(cycle_log, 'a') as f:
                    f.write(log_entry + "\n")
                return False, "sync_failed"
                
        except Exception as e:
            error_msg = f"Cycle exception: {str(e)}"
            log_entry = (
                f"[{datetime.now().strftime('%H:%M:%S')}] === CYCLE #{self.iteration_count} EXCEPTION ====\n"
                f"  → Exception: {str(e)}\n"
                f"  → Iteration: {self.iteration_count}/{self.max_iterations}\n"
                f"  → UTC Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            )
            with open(cycle_log, 'a') as f:
                f.write(log_entry + "\n")
            print(f"\n❌ Cycle failed with exception: {e}")
            return False, error_msg
    
    def run_continuous(self):
        """Run in continuous loop mode until stopped or max iterations."""
        import signal
        
        print("\n" + "=" * 70)
        print("🔄 STEVE'S GEMATRIA UNIFIED OVERNIGHT RESEARCH PIPELINE")
        print("=" * 70)
        print(f"Mode: Continuous Loop (9999 iterations)")
        print(f"Cycle Interval: {self.cycle_interval}s (3 hours at :00)")
        print(f"Working Directory: {WORKING_DIR}")
        print(f"Database Path: {DB_PATH}")
        print(f"Obsidian Exports: {OBSIDIAN_EXPORTS}")
        print(f"Logs Dir: {CRON_LOGS_DIR}")
        print("=" * 70)
        
        # Setup restart handler for SIGINT
        def signal_handler(sig, frame):
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = (
                f"[{timestamp}] === CONTINUOUS MODE PAUSED ====\n"
                f"  → Process paused by signal\n"
                f"  → Iteration Count: {self.iteration_count}/{self.max_iterations}\n"
                f"  → UTC Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            )
            with open(cycle_log, 'a') as f:
                f.write(log_entry + "\n")
            
            print("\n⏸️  Continuous mode paused by signal (Ctrl+C)")
            
        signal.signal(signal.SIGINT, signal_handler)
        
        # Main loop
        print(f"\n📈 Ready to start continuous research pipeline...\n")
        
        try:
            while self.iteration_count < self.max_iterations:
                cycle_start = datetime.now()
                
                if self.run_cycle():
                    cycle_end = datetime.now()
                    duration = (cycle_end - cycle_start).total_seconds()
                    print(f"\n✅ Cycle #{self.iteration_count} completed in {duration:.0f}s")
                    
                    # Check iteration count
                    remaining = self.max_iterations - self.iteration_count
                    if remaining <= 10:
                        print(f"⚠️  Only {remaining} iterations remaining...")
                
                else:
                    cycle_end = datetime.now()
                    error_time = cycle_end.strftime('%H:%M:%S')
                    log_entry = (
                        f"[{datetime.now().strftime('%H:%M:%S')}] === CYCLE FAILED ====\n"
                        f"  → UTC Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
                    )
                    with open(cycle_log, 'a') as f:
                        f.write(log_entry + "\n")
                    print(f"\n⚠️  Cycle failed - proceeding to next cycle\n")
                
                # Wait for next cycle (3 hours = 10800 seconds)
                # Use shorter sleep for testing/demo, can be adjusted
                time.sleep(10800)
                
        except Exception as e:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = (
                f"[{timestamp}] === EXCEPTION ====\n"
                f"  → Exception: {str(e)}\n"
                f"  → Iteration Count: {self.iteration_count}/{self.max_iterations}\n"
            )
            with open(cycle_log, 'a') as f:
                f.write(log_entry + "\n")
            print(f"\n❌ Continuous mode interrupted: {e}")


if __name__ == "__main__":
    # Setup imports
    import subprocess
    
    # Create and run continuous loop runner
    runner = ContinuousLoopRunner(max_iterations=9999)
    runner.run_continuous()
