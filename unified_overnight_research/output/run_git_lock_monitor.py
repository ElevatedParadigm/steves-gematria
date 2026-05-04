#!/usr/bin/env python3
"""
Git Lock Monitor - Main Entry Point for Visual Archive Export Monitoring

This script runs before each Visual Archive export job to check and clean
up stale .git/index.lock files that may be left by interrupted runs.

Exit codes:
  0 - No lock detected (clean)
  1 - Lock was detected and cleaned up
  2 - Error occurred during cleanup

Usage:
    python git_lock_monitor.py [output_dir] [--db PATH] [-n|--dry-run]
    
Or as part of a cron job:
    */5 * * * * /usr/bin/python3 /path/to/git_lock_monitor.py output >> /var/log/gematria/lock_monitor.log 2>&1
"""

import os
import sys
from datetime import datetime
from pathlib import Path


# Add the output directory to path so we can import our modules
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from git_lock_monitor import GitLockMonitor


def main():
    """Main entry point."""
    # Parse arguments manually for cron compatibility
    args = sys.argv[1:]
    
    output_dir = "output"  # Default
    db_path = None
    dry_run = False
    
    for arg in args:
        if arg.startswith(("-n", "--dry-run")):
            dry_run = True
        elif arg.startswith("--db="):
            db_path = arg.split("=", 1)[1]
        else:
            # Positional argument - output directory
            output_dir = arg
    
    # Create monitor instance
    monitor = GitLockMonitor(
        output_dir=output_dir,
        db_path=db_path
    )
    
    # Run monitor
    exit_code = monitor.run(dry_run=dry_run)
    
    # Output summary to stdout (for cron log capture)
    print(f"=== Git Lock Monitor ===", file=sys.stderr)
    print(f"Timestamp: {datetime.now().isoformat()}", file=sys.stderr)
    print(f"Output directory: {output_dir}", file=sys.stderr)
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}", file=sys.stderr)
    
    # Exit with appropriate code
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
