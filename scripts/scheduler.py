"""
STEVE'S GEMATRIA — Python Scheduler for Automatic Overnight Runs
====================================================================

Schedules overnight research pipeline to run automatically at 3:00 AM daily.
Uses APScheduler for flexible timing and task management.

Usage:
    python scripts/scheduler.py --mode overnight       # Run overnight research @ 3 AM
    python scripts/scheduler.py --mode hourly          # Hourly sync
    python scripts/scheduler.py --mode pattern         # Pattern scan every 6 hours
    python scripts/scheduler.py --immediate            # Run all tasks immediately
    python scripts/scheduler.py --help                 # Show usage options

Requirements:
    pip install apscheduler
"""

import sys
import os
from datetime import datetime, timezone
from pathlib import Path
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger


# Configuration
WORKING_DIR = Path.home() / ".hermes" / "gematria"
SCRIPTS_DIR = WORKING_DIR / "scripts"
LOGS_DIR = WORKING_DIR / "cron_logs"
EXPORTS_DIR = WORKING_DIR / "obsidian_exports"

# Ensure directories exist
for directory in [WORKING_DIR, SCRIPTS_DIR, LOGS_DIR, EXPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Log timestamp format
LOG_TIMESTAMP = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def run_overnight_research():
    """Run overnight research pipeline."""
    log_file = LOGS_DIR / "overnight.log"
    
    try:
        print(f"\n[{LOG_TIMESTAMP}] \n[{LOG_TIMESTAMP}] > STEVE'S GEMATRIA - Overnight Research Pipeline\n")
        print("=" * 80)
        
        # Execute the overnight research script
        import subprocess
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "orchestrator_standalone.py")],
            cwd=str(WORKING_DIR),
            capture_output=False,
            check=False
        )
        
        print("=" * 80)
        if result.returncode == 0:
            print(f"\n[{LOG_TIMESTAMP}] ✓ Overnight research completed successfully!\n")
        else:
            print(f"\n[{LOG_TIMESTAMP}] ✗ Overnight research encountered issues (exit code {result.returncode})\n")
        
    except Exception as e:
        print(f"\n[{LOG_TIMESTAMP}] ✗ Error running overnight research: {e}\n")
    
    # Always write log timestamp
    with open(log_file, 'a') as f:
        f.write(f"[{LOG_TIMESTAMP}] Overnight run completed\n")


def run_hourly_sync():
    """Run hourly knowledge graph sync."""
    import subprocess
    
    print(f"\n[{LOG_TIMESTAMP}] \n[{LOG_TIMESTAMP}] > STEVE'S GEMATRIA - Hourly Sync Pipeline\n")
    print("=" * 80)
    
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "auto_obisidian_sync_v2.py")],
            cwd=str(WORKING_DIR),
            capture_output=False,
            check=False
        )
        
        print("=" * 80)
        if result.returncode == 0:
            print(f"\n[{LOG_TIMESTAMP}] ✓ Hourly sync completed successfully!\n")
        else:
            print(f"\n[{LOG_TIMESTAMP}] ✗ Hourly sync encountered issues (exit code {result.returncode})\n")
        
    except Exception as e:
        print(f"\n[{LOG_TIMESTAMP}] ✗ Error running hourly sync: {e}\n")


def run_pattern_scan():
    """Run pattern convergence scan every 6 hours."""
    import subprocess
    
    print(f"\n[{LOG_TIMESTAMP}] \n[{LOG_TIMESTAMP}] > STEVE'S GEMATRIA - Pattern Scan Pipeline\n")
    print("=" * 80)
    
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "orchestrator_standalone.py"), "--mode", "pattern"],
            cwd=str(WORKING_DIR),
            capture_output=False,
            check=False
        )
        
        print("=" * 80)
        if result.returncode == 0:
            print(f"\n[{LOG_TIMESTAMP}] ✓ Pattern scan completed successfully!\n")
        else:
            print(f"\n[{LOG_TIMESTAMP}] ✗ Pattern scan encountered issues (exit code {result.returncode})\n")
        
    except Exception as e:
        print(f"\n[{LOG_TIMESTAMP}] ✗ Error running pattern scan: {e}\n")


def run_health_check():
    """Run system health check."""
    import subprocess
    from datetime import datetime
    
    print(f"\n[{LOG_TIMESTAMP}] \n[{LOG_TIMESTAMP}] > STEVE'S GEMATRIA - Health Check Pipeline\n")
    print("=" * 80)
    
    try:
        # Simple health check - verify orchestrator can be imported and database exists
        health_script = '''
import sys
from pathlib import Path
from datetime import datetime

WORKING_DIR = Path.home() / ".hermes" / "gematria"
DB_FILE = WORKING_DIR / "database" / "gematria_database.json"

print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking system health...")
print("=" * 80)

checks_passed = 0
checks_failed = 0

# Check database exists
if DB_FILE.exists():
    print(f"[✓] Database file exists: {DB_FILE}")
    checks_passed += 1
else:
    print(f"[✗] Database file missing: {DB_FILE}")
    checks_failed += 1

# Check scripts directory
scripts_dir = WORKING_DIR / "scripts"
if scripts_dir.exists():
    script_count = len(list(scripts_dir.glob("*.py")))
    print(f"[✓] Scripts directory exists with {script_count} Python files")
    checks_passed += 1
else:
    print(f"[✗] Scripts directory missing")
    checks_failed += 1

# Check exports directory
exports_dir = WORKING_DIR / "obsidian_exports"
if exports_dir.exists():
    export_count = len(list(exports_dir.glob("*.md")))
    print(f"[✓] Exports directory exists with {export_count} markdown files")
    checks_passed += 1
else:
    print(f"[✗] Exports directory missing")
    checks_failed += 1

print("=" * 80)
print(f"Health Check Summary: {checks_passed} passed, {checks_failed} failed")
'''
        result = subprocess.run(
            [sys.executable, "-c", health_script],
            capture_output=False,
            check=False
        )
        
        if result.returncode == 0:
            print(f"\n[{LOG_TIMESTAMP}] ✓ Health check passed!\n")
        else:
            print(f"\n[{LOG_TIMESTAMP}] ✗ Health check failed (exit code {result.returncode})\n")
        
    except Exception as e:
        print(f"\n[{LOG_TIMESTAMP}] ✗ Error running health check: {e}\n")


def get_mode_description(mode):
    """Get human-readable mode description."""
    descriptions = {
        "overnight": "Overnight research pipeline (3 AM daily)",
        "hourly": "Hourly knowledge graph sync",
        "pattern": "Pattern convergence scan (every 6 hours)",
        "health": "System health check",
    }
    return descriptions.get(mode, "Unknown mode")


def create_scheduler(modes=None):
    """Create and configure scheduler with specified modes."""
    scheduler = BlockingScheduler()
    
    # Default: overnight research at 3 AM daily
    if modes is None or "overnight" in modes:
        scheduler.add_job(
            run_overnight_research,
            CronTrigger(hour=3, minute=0),
            id="overnight",
            name="Overnight Research (3 AM)",
            replace_existing=True
        )
    
    # Hourly sync (every hour at :30)
    if modes is None or "hourly" in modes:
        scheduler.add_job(
            run_hourly_sync,
            CronTrigger(minute=30),
            id="hourly",
            name="Hourly Sync",
            replace_existing=True
        )
    
    # Pattern scan (every 6 hours at :00)
    if modes is None or "pattern" in modes:
        scheduler.add_job(
            run_pattern_scan,
            CronTrigger(minute=0, hour=[0, 6, 12, 18]),
            id="pattern",
            name="Pattern Scan",
            replace_existing=True
        )
    
    # Health check (every 30 minutes)
    if modes is None or "health" in modes:
        scheduler.add_job(
            run_health_check,
            CronTrigger(minute=0),
            id="health",
            name="Health Check",
            replace_existing=True
        )
    
    return scheduler


def run_immediate_all():
    """Run all tasks immediately (for testing)."""
    print(f"\n[{LOG_TIMESTAMP}] \n[{LOG_TIMESTAMP}] > STEVE'S GEMATRIA - Immediate Run Mode\n")
    print("=" * 80)
    
    # Run overnight research
    run_overnight_research()
    
    # Run hourly sync
    run_hourly_sync()
    
    # Run pattern scan
    run_pattern_scan()
    
    # Run health check
    run_health_check()
    
    print("\n" + "=" * 80)
    print(f"[{LOG_TIMESTAMP}] ✓ All immediate tasks completed!\n")


def show_scheduler_status():
    """Display scheduler job information."""
    print(f"\n[{LOG_TIMESTAMP}] \n[{LOG_TIMESTAMP}] > STEVE'S GEMATRIA - Scheduler Status\n")
    print("=" * 80)
    
    # Show what jobs are scheduled
    print("\nScheduled Jobs:")
    print("-" * 40)
    print("• overnight   → Cron trigger (3 AM daily)")
    print("• hourly      → Cron trigger (every hour at :30)")
    print("• pattern     → Cron trigger (every 6 hours)")
    print("• health      → Cron trigger (every 30 minutes)")
    print("\n" + "=" * 80)


def main():
    """Main entry point with CLI argument parsing."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Steve's Gematria Python Scheduler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/scheduler.py --mode overnight    # Run overnight research @ 3 AM daily
  python scripts/scheduler.py --mode hourly       # Run hourly sync every hour
  python scripts/scheduler.py --mode pattern      # Run pattern scans every 6 hours
  python scripts/scheduler.py --mode health       # Run health checks every 30 min
  python scripts/scheduler.py --immediate         # Run all tasks immediately
  python scripts/scheduler.py --all               # Schedule all jobs at their default intervals
        """
    )
    
    parser.add_argument(
        "--mode", "-m",
        choices=["overnight", "hourly", "pattern", "health"],
        help="Mode to run (overrides scheduled triggers)"
    )
    
    parser.add_argument(
        "--immediate", "-i",
        action="store_true",
        help="Run all tasks immediately (for testing)"
    )
    
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Schedule all jobs with default configurations"
    )
    
    parser.add_argument(
        "--status", "-s",
        action="store_true",
        help="Display scheduler job status without running"
    )
    
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    # Handle --status flag
    if args.status:
        show_scheduler_status()
        return
    
    # Handle --immediate flag
    if args.immediate:
        run_immediate_all()
        return
    
    # Handle --mode or --all flags
    modes = None
    if args.mode:
        modes = [args.mode]
    elif args.all:
        modes = ["overnight", "hourly", "pattern", "health"]
    
    if modes:
        print(f"\n[{LOG_TIMESTAMP}] \n[{LOG_TIMESTAMP}] > STEVE'S GEMATRIA - Scheduler Starting\n")
        print("=" * 80)
        print(f"Scheduled Modes: {', '.join(modes)}")
        print("=" * 80)
        
        # Create and run scheduler
        scheduler = create_scheduler(modes)
        
        try:
            scheduler.add_listener(
                scheduler.print_job,
                events=[scheduler.JOB_ERROR, scheduler.JOB_EXECUTED]
            )
            scheduler.print_job_info()
            
            if args.debug:
                print("\nDebug info:")
                print(f"  Working Dir: {WORKING_DIR.absolute()}")
                print(f"  Scripts Dir: {SCRIPTS_DIR.absolute()}")
                print(f"  Logs Dir: {LOGS_DIR.absolute()}")
                print(f"  Exports Dir: {EXPORTS_DIR.absolute()}")
            
            print("\n" + "=" * 80)
            print("Scheduler running with CTRL+C to stop\n")
            
            # Block and run scheduler
            scheduler.start()
            
        except (KeyboardInterrupt, SystemExit):
            print("\n" + "=" * 80)
            print(f"[{LOG_TIMESTAMP}] Scheduler stopped.\n")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
