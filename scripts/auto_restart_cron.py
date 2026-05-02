#!/usr/bin/env python3
"""
🔄 Auto-Restart Script for Gematria Cron Jobs
=========================================================

Monitors cron job logs for failures and automatically restarts failed jobs.
Supports auto-restart on expiration or failure with exponential backoff.

Usage:
    python3 auto_restart_cron.py [--interval N] [--max-retries N]
    
Default interval: 600 seconds (10 minutes)
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path
import re
import subprocess

sys.path.insert(0, str(Path.home()))

class CronJobMonitor:
    """Monitor and auto-restart failed cron jobs"""
    
    def __init__(self):
        self.gematria_dir = Path.home() / ".hermes" / "gematria"
        self.logs_dir = self.gematria_dir / "cron_logs"
        self.main_log_file = self.logs_dir / "cron_job.log"
        self.restart_script = self.gematria_dir / "scripts" / "restart_cron.py"
        self.retry_config_path = self.gematria_dir / "cron_restart_config.json"
        
        # Default configuration
        self.config = {
            "check_interval": 300,  # Check every 5 minutes (300s)
            "max_retries": 3,
            "backoff_multiplier": 2,  # Exponential backoff
            "restart_delay": 30,
            "phases": ["stability", "auto_sync", "heatmap"]
        }
        
    def load_config(self):
        """Load restart configuration"""
        if self.retry_config_path.exists():
            try:
                with open(self.retry_config_path, 'r') as f:
                    user_config = json.load(f)
                    # Merge with defaults
                    for key in self.config:
                        if key not in user_config:
                            user_config[key] = self.config[key]
                    return user_config
            except Exception as e:
                print(f"⚠️ Warning: Could not load config: {e}")
        
        return self.config
    
    def save_config(self, config):
        """Save configuration to file"""
        self.retry_config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.retry_config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def parse_log_errors(self):
        """Parse main log for error patterns and failure markers"""
        
        errors_found = []
        
        if not self.main_log_file.exists():
            return errors_found
        
        with open(self.main_log_file, 'r') as f:
            lines = f.readlines()
        
        # Look for failure markers
        for i, line in enumerate(lines):
            # Error patterns
            error_patterns = [
                (r'❌|EXCEPTION|Traceback|CRITICAL|FATAL', 'CRITICAL_ERROR'),
                (r'STDIN EOF|TIMEOUT|TIMED OUT', 'TIMEOUT'),
                (r'Return code: 1|EXIT STATUS: 1', 'NON_ZERO_EXIT'),
                (r'WARNING.*FAILED|ERROR.*COMPLETED', 'OPERATION_WARNING'),
            ]
            
            for pattern, error_type in error_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    errors_found.append({
                        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
                        "type": error_type,
                        "line": line.strip()[:200],
                        "severity": "HIGH" if error_type in ["CRITICAL_ERROR", "TIMEOUT"] else "MEDIUM"
                    })
        
        return errors
    
    def get_restart_command(self):
        """Get the restart command for the cron job"""
        
        base_cmd = (
            'cd /home/avalonas/.hermes/gematria && '
            'python scripts/loop_runner_enhanced.py >> cron_logs/cron_job.log 2>&1'
        )
        
        return base_cmd
    
    def execute_restart(self):
        """Execute restart command"""
        
        print("🔄 Attempting to restart cron job...")
        self.config_log(f"=== PHASE: AUTO_RESTART ===", "Action: Restarting failed cron job")
        
        command = self.get_restart_command()
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=180  # Max 3 minutes for restart
            )
            
            print(f"✅ Restart completed (exit code: {result.returncode})")
            self.config_log(f"=== PHASE: AUTO_RESTART_RESULT ===", 
                           f"Exit code: {result.returncode}")
            
            if result.stdout:
                first_lines = result.stdout.strip().split('\n')[:3]
                for line in first_lines:
                    print(line)
            
            return True, result.returncode
        
        except subprocess.TimeoutExpired:
            print("❌ Restart timed out")
            self.config_log("=== PHASE: AUTO_RESTART_TIMEOUT ===", "Exceeded 180s timeout")
            return False, -1
        
        except Exception as e:
            print(f"❌ Restart failed: {e}")
            self.config_log(f"=== PHASE: AUTO_RESTART_ERROR ===", str(e)[:100])
            return False, -1
    
    def run_monitor(self, interval=None):
        """Start monitoring and auto-restart loop"""
        
        if interval is None:
            interval = self.config.get('check_interval', 300)
        
        print(f"\n📋 Cron Job Auto-Restart Monitor")
        print("=" * 60)
        print(f"Check interval: {interval}s")
        print(f"Max retries: {self.config.get('max_retries', 3)}")
        print(f"Restart delay: {self.config.get('restart_delay', 30)}s")
        print("=" * 60)
        
        try:
            while True:
                self.config_log("=== MONITORING CYCLE START ===", f"Cycle started at {datetime.now().strftime('%H:%M:%S')}")
                
                # Parse for errors
                errors = self.parse_log_errors()
                
                if errors:
                    for error in errors:
                        print(f"\n⚠️ Error detected: {error['type']}")
                        print(f"   Timestamp: {error['timestamp']}")
                        print(f"   Message: {error['line']}")
                        
                        # Check retry count
                        last_retry_file = self.logs_dir / f"last_restart_{datetime.now().strftime('%Y%m%d')}.json"
                        
                        if last_retry_file.exists():
                            with open(last_retry_file, 'r') as f:
                                last_state = json.load(f)
                                retry_count = last_state.get('retry_count', 0)
                                
                                max_retries = self.config.get('max_retries', 3)
                                
                                if retry_count >= max_retries:
                                    print(f"   ⚠️ Max retries ({max_retries}) reached - skipping restart")
                                    continue
                                
                        # Attempt restart
                        success, exit_code = self.execute_restart()
                        
                        if success and exit_code == 0:
                            print("✅ Restart successful")
                            
                            # Update retry state
                            state = {
                                "retry_count": retry_count + 1,
                                "last_restart": datetime.now().isoformat(),
                                "exit_code": exit_code
                            }
                            
                            self.logs_dir.mkdir(parents=True, exist_ok=True)
                            with open(last_retry_file, 'w') as f:
                                json.dump(state, f, indent=2)
                        
                        # Wait before checking again (exponential backoff)
                        delay = min(
                            self.config.get('restart_delay', 30),
                            interval
                        )
                        time.sleep(delay)
                
                else:
                    print("✅ No errors detected")
                    self.config_log("=== NO_ERRORS_DETECTED ===", "Checking for new errors...")
                
                # Wait next cycle
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n👋 Monitor stopped by user")


def main():
    """Main entry point"""
    
    import argparse
    import json
    
    parser = argparse.ArgumentParser(
        description="Auto-restart script for Gematria cron jobs"
    )
    parser.add_argument('--interval', type=int, default=None,
                       help='Check interval in seconds')
    parser.add_argument('--once', action='store_true',
                       help='Run single check and exit')
    
    args = parser.parse_args()
    
    monitor = CronJobMonitor()
    config = monitor.load_config()
    
    if args.once:
        # Single check mode
        errors = monitor.parse_log_errors()
        
        if errors:
            print("⚠️ Errors found in cron job logs:")
            for error in errors:
                print(f"  - {error['type']}: {error['line'][:100]}")
            
            if args.interval is None:
                interval = config.get('check_interval', 300)
                # Wait before auto-restart
                time.sleep(config.get('restart_delay', 30))
            
            success, exit_code = monitor.execute_restart()
        
        else:
            print("✅ No errors found")
    else:
        # Continuous monitoring mode
        monitor.run_monitor(interval=args.interval)


if __name__ == "__main__":
    main()
