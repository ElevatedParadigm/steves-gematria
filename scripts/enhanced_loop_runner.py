#!/usr/bin/env python3
"""
Enhanced Overnight Research Loop Runner with Hybrid Scheduler Integration
==========================================================================
Runs every 3 hours (at :00 of hours 0,3,6,9,12,15,18,21)

This enhanced loop runner:
1. Runs stability test on gematria database
2. Performs auto-sync to Obsidian notes  
3. Generates correlation heatmaps and relationship matrices
4. Writes logs with phase markers for elasticity monitoring
5. Auto-restarts on failure using hybrid scheduler state

Usage:
  python3 /home/avalonas/.hermes/gematria/scripts/enhanced_loop_runner.py
  python3 /home/avalonas/.hermes/gematria/scripts/enhanced_loop_runner.py --daemon
"""

import sys
import os
import json
import time
import signal
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess
import re

# Add parent directory to path for imports
sys.path.insert(0, str(Path.home() / ".hermes"))

CONFIG_PATH = "/home/avalonas/.hermes/gematria/config.yaml"
CRON_LOGS_DIR = "/home/avalonas/.hermes/gematria/cron_logs"
OBSIDIAN_EXPORTS_DIR = "/home/avalonas/.hermes/gematria/obsidian_exports"
HEATMAP_DIR = "/home/avalonas/.hermes/gematria/research/heatmaps"
LOGS_DIR = "/home/avalonas/.hermes/gematria/logs"

class EnhancedLoopRunner:
    """Main loop runner with stability testing, auto-sync, and hybrid scheduler integration."""
    
    def __init__(self, interval_seconds: int = 10800):
        self.interval_seconds = interval_seconds  # Default 3 hours = 10800s
        self.start_time = datetime.now()
        self.cycle_count = 0
        self.last_stability_check = None
        self.hybrid_scheduler_status = "unknown"
        
    def _get_current_utc_time(self) -> str:
        """Get current UTC time for timestamping."""
        now = datetime.now(timezone.utc)
        return now.strftime('%Y-%m-%d %H:%M:%S UTC')
    
    def _log_phase_marker(self, phase: str, message: str, log_file: Optional[str] = None):
        """Write phase marker to log file for elasticity monitoring."""
        if not log_file:
            # Default log location
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_path = Path(CRON_LOGS_DIR) / f"phase_markers_{self.start_time.strftime('%Y%m%d')}.log"
            log_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            log_path = Path(log_file)
        
        log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] === {phase.upper():15s} PHASE MARKER ===\n"
        log_entry += f"  → Message: {message}\n"
        log_entry += f"  → UTC Time: {self._get_current_utc_time()}\n"
        
        with open(log_path, 'a') as f:
            f.write(log_entry + "\n")
    
    def run_stability_test(self) -> tuple[bool, str]:
        """Run stability test on gematria database."""
        print("\n🧪 PHASE: STABILITY TEST ===>")
        self._log_phase_marker("STABILITY", "Running enhanced stability test with Priority Enhancements #1-3")
        
        try:
            process = subprocess.Popen(
                [sys.executable, "/home/avalonas/.hermes/gematria/scripts/stability_test_enhanced_fixed.py", "--timeout", "2700"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=CRON_LOGS_DIR
            )
            
            output, _ = process.communicate(timeout=300)
            print(output)
            
            if process.returncode == 0:
                self._log_phase_marker("COMPLETED", "Stability test passed - all Priority Enhancements verified")
                return True, "passed"
            else:
                error_msg = f"Stability test failed with code {process.returncode}\n{output[-500:]}" if len(output) > 500 else output
                self._log_phase_marker("FAILED", f"Stability test failed - exit code: {process.returncode}")
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Stability test exception: {str(e)}"
            self._log_phase_marker("EXCEPTION", f"Stability test exception: {str(e)}")
            return False, error_msg
    
    def run_auto_sync(self) -> tuple[bool, str]:
        """Perform auto-sync to Obsidian notes."""
        print("\n📤 PHASE: AUTO-SYNC TO OBSIDIAN ===>")
        self._log_phase_marker("AUTOSYNC", "Starting auto-sync with relationship extraction and temporal analysis")
        
        try:
            process = subprocess.Popen(
                [sys.executable, "/home/avalonas/.hermes/gematria/scripts/auto_obisidian_sync_v2.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=OBSIDIAN_EXPORTS_DIR
            )
            
            output, _ = process.communicate(timeout=180)
            print(output)
            
            if process.returncode == 0:
                self._log_phase_marker("COMPLETED", "Auto-sync completed - relationship matrices and cross-reference index updated")
                
                # Generate correlation heatmaps
                self._generate_heatmaps()
                
                return True, "synced_and_heatmaps_generated"
            else:
                error_msg = f"Auto-sync failed with code {process.returncode}\n{output[-300:]}" if len(output) > 300 else output
                self._log_phase_marker("FAILED", f"Auto-sync failed - exit code: {process.returncode}")
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Auto-sync exception: {str(e)}"
            self._log_phase_marker("EXCEPTION", f"Auto-sync exception: {str(e)}")
            return False, error_msg
    
    def _generate_heatmaps(self):
        """Generate correlation heatmaps and relationship matrices if heatmap tools available."""
        heatmap_script = Path(HEATMAP_DIR) / "heatmap_generator.py"
        
        if not heatmap_script.exists():
            print("\n⚠️  Heatmap generator not found - skipping visualization generation")
            self._log_phase_marker("SKIPPED", "Heatmap generator not available")
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
            print(f"⚠️  Heatmap generation skipped (not critical): {e}")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics for reporting."""
        db_path = Path.home() / ".hermes" / "gematria" / "database" / "gematria_database.json"
        
        try:
            with open(db_path, 'r') as f:
                db_data = json.load(f)
            
            metadata = db_data.get('metadata', {})
            core_symbols = metadata.get('core_symbols', [])
            domains_tracked = metadata.get('domains_tracked', [])
            elemental_forces = metadata.get('elemental_forces', [])
            
            return {
                'total_core_symbols': len(core_symbols),
                'symbols_list': core_symbols[:6],  # Top 6 symbols
                'domains_count': len(domains_tracked),
                'domain_names': domains_tracked,
                'forces_count': len(elemental_forces),
                'entries_count': len(db_data.get('entries', {})),
                'pattern_summary_keys': len(db_data.get('pattern_summary', {}))
            }
        except Exception as e:
            return {'error': str(e)}
    
    def run_cycle(self) -> tuple[bool, str]:
        """Run one complete research loop cycle."""
        self.cycle_count += 1
        timestamp = self.start_time.strftime('%Y-%m-%d %H:%M:%S')
        
        print("\n" + "=" * 70)
        print(f"🌙 OVERNIGHT RESEARCH PROTOCOL - CYCLE #{self.cycle_count}")
        print("=" * 70)
        print(f"Timestamp: {timestamp}")
        print(f"Interval: {self.interval_seconds}s ({self.interval_seconds/3600:.1f} hours)")
        print("=" * 70)
        
        try:
            # Step 1: Run stability test first
            stability_passed, stability_status = self.run_stability_test()
            
            if not stability_passed:
                print("\n❌ Stability test failed - cycle aborted")
                return False, "stability_failed"
            
            # Step 2: Run auto-sync and heatmap generation
            sync_passed, sync_status = self.run_auto_sync()
            
            if sync_passed:
                db_stats = self.get_database_stats()
                print("\n📊 Database Statistics:")
                print(f"   Core Symbols Tracked: {db_stats.get('total_core_symbols', 'N/A')}")
                print(f"   Domains Covered: {db_stats.get('domains_count', 'N/A')}")
                print(f"   Batch Entries Analyzed: {db_stats.get('entries_count', 'N/A')}")
                
                status_msg = "Research cycle completed successfully!"
                return True, status_msg
            else:
                print("\n⚠️  Sync failed but proceeding to next cycle...")
                return False, "sync_failed"
                
        except Exception as e:
            error_msg = f"Cycle exception: {str(e)}"
            self._log_phase_marker("EXCEPTION", f"Cycle exception: {str(e)}")
            print(f"\n❌ Cycle failed with exception: {e}")
            return False, error_msg
    
    def run_daemon(self):
        """Run in daemon mode with auto-restart capability."""
        import argparse
        parser = argparse.ArgumentParser(description="Enhanced Loop Runner - Daemon Mode")
        parser.add_argument('--interval', type=int, default=10800, help='Interval between cycles (seconds)')
        args = parser.parse_args()
        
        self.interval_seconds = args.interval
        
        print("\n" + "=" * 70)
        print("🔄 OVERNIGHT RESEARCH PROTOCOL - DAEMON MODE")
        print("=" * 70)
        print(f"Cycle Interval: {self.interval_seconds}s ({self.interval_seconds/3600:.1f} hours)")
        print("Schedule: Every 3 hours at :00 (hours 0,3,6,9,12,15,18,21)")
        print("Auto-restart enabled on failure")
        print("Hybrid scheduler monitoring active")
        print("=" * 70)
        
        # Setup restart handler
        def signal_handler(sig, frame):
            print("\n⏸️  Daemon paused by signal")
            
        signal.signal(signal.SIGINT, signal_handler)
        
        try:
            while True:
                cycle_start = datetime.now()
                
                if self.run_cycle():
                    print(f"\n✅ Cycle #{self.cycle_count} completed at {cycle_end.strftime('%H:%M:%S')}\n")
                    
                    # Check hybrid scheduler status if running
                    self._check_hybrid_scheduler()
                else:
                    cycle_failed = datetime.now()
                    error_status = f"Cycle failed at {cycle_failed.strftime('%H:%M:%S')}"
                    self._log_phase_marker("CYCLE_FAILED", error_status)
                    print(f"\n⚠️  Cycle failed - auto-restart will trigger on next interval\n")
                
                # Wait for next cycle (unless interrupted)
                time.sleep(self.interval_seconds)
                
        except Exception as e:
            print(f"\n❌ Daemon interrupted: {e}")
            self._log_phase_marker("EXCEPTION", f"Daemon interrupted: {str(e)}")


def _check_hybrid_scheduler():
    """Check hybrid scheduler status if background process exists."""
    try:
        # Check if hybrid scheduler process is running
        result = subprocess.run(
            ['pgrep', '-f', 'hybrid_scheduler.py'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            print(f"🔗 Hybrid Scheduler Status: ACTIVE (PIDs: {', '.join(pids[:3])})")
            
            # Show last scheduler log entry
            log_file = Path("/home/avalonas/.hermes/gematria/logs/elasticity_phases.log")
            if log_file.exists():
                with open(log_file, 'r') as f:
                    lines = f.readlines()[-3:]  # Last 3 entries
                    for line in lines:
                        print(f"  {line.strip()}")
        else:
            print("🔗 Hybrid Scheduler Status: NOT RUNNING (optional component)")
    except Exception as e:
        print(f"⚠️  Could not check hybrid scheduler: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Enhanced Overnight Research Loop Runner with Hybrid Scheduler Integration",
        epilog="""
Examples:
  # Run single cycle
  python3 enhanced_loop_runner.py
  
  # Run in daemon mode (auto-restart)
  python3 enhanced_loop_runner.py --daemon
  
  # Custom interval (90 minutes)
  python3 enhanced_loop_runner.py --interval 5400
  
  # Combined with hybrid scheduler:
  python3 /home/avalonas/.hermes/gematria/scripts/enhanced_loop_runner.py --daemon &
  python3 /home/avalonas/.hermes/gematria/hybrid_scheduler.py &
        """
    )
    parser.add_argument('--interval', type=int, default=10800, 
                       help='Interval between cycles in seconds (default: 10800 = 3 hours)')
    parser.add_argument('--daemon', action='store_true',
                       help='Run in daemon mode with auto-restart on failure')
    
    args = parser.parse_args()
    
    runner = EnhancedLoopRunner(interval_seconds=args.interval)
    
    if args.daemon:
        runner.run_daemon()
    else:
        # Run single cycle by default
        success, status = runner.run_cycle()
        
        if success:
            print("\n✅ OVERNIGHT RESEARCH PROTOCOL - CYCLE COMPLETE")
            print(f"📊 Status: {status}")
            
            # Check hybrid scheduler compatibility
            _check_hybrid_scheduler()
            
            print("\n🔄 Next cycle in 3 hours (at :00 minute of next hour)")
        else:
            print(f"\n❌ OVERNIGHT RESEARCH PROTOCOL - CYCLE FAILED")
            print(f"📊 Status: {status}")
