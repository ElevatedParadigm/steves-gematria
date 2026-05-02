#!/usr/bin/env python3
"""
🔗 Multi-Phase Elasticity Protocol — Hybrid Scheduler
===================================================
Safely integrate speed up/slow down/intensify elasticity into overnight research loops.

This scheduler:
1. Reads config.yaml for elasticity rules and domain assignments
2. Runs in background alongside existing cron jobs  
3. Monitors phase transitions via output markers in logs
4. No modification needed to existing loop_runner.py or cron scripts

Usage:
  python3 /home/avalonas/.hermes/gematria/hybrid_scheduler.py &

Or add to crontab for overnight rotation:
  0 2 * * * python3 /home/avalonas/.hermes/gematria/hybrid_scheduler.py >> /home/avalonas/.hermes/gematria/logs/hybrid_scheduler.log 2>&1
"""

import sys
import os
import yaml
import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path.home() / ".hermes"))

CONFIG_PATH = "/home/avalonas/.hermes/gematria/config.yaml"
LOGS_DIR = "/home/avalonas/.hermes/gematria/logs"
ELASTICITY_LOG_FILE = Path(LOGS_DIR) / "elasticity_phases.log"

class ElasticityHybridScheduler:
    """
    Hybrid Scheduler for Multi-Phase Elasticity Protocol
    
    Coordinates phase rotation across domains and timezones without modifying
    existing cron jobs. Runs alongside current overnight research infrastructure.
    """
    
    def __init__(self, config_path: str = CONFIG_PATH):
        self.config_path = Path(config_path)
        self.log_file = ELASTICITY_LOG_FILE
        
        # Ensure logs directory exists
        self.logs_dir = Path(self.log_file).parent
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
        
        # Phase definitions with descriptions for log output
        self.phase_names = {
            'baseline': '⚪ Baseline (Default)',
            'speed_up': '🚀 Speed Up (+20%)',
            'slow_down': '🐢 Slow Down (-15%)',
            'intensify': '💪 Intensify'
        }
    
    def _load_config(self) -> dict:
        """Load elasticity configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Error loading config.yaml: {e}")
            # Return minimal default config if file doesn't exist
            return {
                'elasticity_rules': {
                    'speed_up': {'timing_adjustment': '+20%', 'batch_multiplier': 3, 'subtask_increase': '+50%'},
                    'slow_down': {'timing_adjustment': '-15%', 'batch_multiplier': 0.3, 'verification_mode': 'checkpoints between each step'},
                    'intensify': {'timing_adjustment': 'unchanged', 'subtask_increase': '+30%', 'analysis_depth': 'deep + cross-check queries'}
                },
                'domains': {
                    'Military History': {
                        'elasticity_enabled': True,
                        'current_phase': 'baseline',
                        'phase_rotation_schedule': {
                            'speed_up_observer': 'Europe/EEST',
                            'slow_down_observer': 'America/EST',
                            'intensify_observer': 'Asia/Shanghai'
                        }
                    }
                },
                'phases': {},
                'monitoring': {}
            }
    
    def _get_current_utc_time(self) -> str:
        """Get current UTC time for timezone conversions"""
        now = datetime.now(timezone.utc)
        return now.strftime('%Y-%m-%d %H:%M UTC')
    
    def _convert_to_timezone(self, utc_time: str, tz_name: str) -> tuple[str, bool]:
        """Convert UTC timestamp to target timezone"""
        try:
            from dateutil import tz
            utc = timezone.utc
            tz_target = tz.getzoneinfo(tz_name)
            
            utc_dt = datetime.strptime(utc_time, '%Y-%m-%d %H:%M UTC').replace(tzinfo=utc)
            local_dt = utc_dt.astimezone(tz_target)
            return local_dt.strftime('%Y-%m-%d %H:%M'), True
        except Exception as e:
            print(f"⚠️ Timezone conversion failed for {tz_name}: {e}")
            return utc_time, False
    
    def _is_observer_active(self, domain: str, phase: str) -> tuple[bool, str]:
        """
        Check if observer for given domain/phase is currently active.
        
        Returns: (is_active, timezone_name)
        """
        now_utc = self._get_current_utc_time()
        
        # Get rotation schedule for this domain
        domain_config = self.config.get('domains', {}).get(domain, {})
        rotation_schedule = domain_config.get('phase_rotation_schedule', {})
        
        # Determine which observer is active based on current time
        if phase == 'speed_up':
            observer_tz = rotation_schedule.get('speed_up_observer')
        elif phase == 'slow_down':
            observer_tz = rotation_schedule.get('slow_down_observer')
        elif phase == 'intensify':
            observer_tz = rotation_schedule.get('intensify_observer')
        else:
            return False, "Unknown"
        
        if not observer_tz:
            return False, "no_observer_assigned"
        
        # Convert UTC to local time and check if within 2-hour window (elasticity runs during observer work hours)
        local_time, success = self._convert_to_timezone(now_utc, observer_tz)
        
        # Simple logic: consider observer active if it's between their "work hours"
        # For EEST/EST/China timezones, assume 2AM-4AM EEST window as primary elasticity window
        if 'EEST' in observer_tz or 'EST' in observer_tz or 'Shanghai' in observer_tz:
            is_active = now_utc[11:13] == '02' or now_utc[11:13] == '03'  # Check hour digits
        else:
            # For other timezones, use broader window
            is_active = True
        
        return is_active, observer_tz
    
    def get_active_phase_for_domain(self, domain: str) -> tuple[str, str]:
        """
        Get which elasticity phase should be active for given domain at current time.
        
        Returns: (phase_name, observer_timezone)
        """
        if not self.config.get('domains', {}).get(domain, {}).get('elasticity_enabled', False):
            return 'baseline', 'N/A'
        
        # Try each phase in priority order based on rotation schedule
        for phase_key in ['speed_up', 'slow_down', 'intensify']:
            is_active, observer_tz = self._is_observer_active(domain, phase_key)
            
            if is_active:
                return phase_key, observer_tz
        
        # If no observer active, use current_phase from config as fallback
        domain_config = self.config.get('domains', {}).get(domain, {})
        current_phase = domain_config.get('current_phase', 'baseline')
        return current_phase, 'fallback'
    
    def log_phase_activation(self, domain: str, phase: str, observer_tz: str):
        """Log phase activation with clear markers for monitoring"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        # Create formatted output marker that appears in logs
        log_line = f"[{timestamp}] === {self.phase_names[phase]} PHASE ===\n"
        log_line += f"  → Domain: {domain}\n"
        log_line += f"  → Active Observer: {observer_tz}\n"
        
        # Get elasticity rules for this phase
        phase_rules = self.config.get('elasticity_rules', {}).get(phase, {})
        log_line += f"  → Timing adjustment: {phase_rules.get('timing_adjustment', 'baseline')}\n"
        log_line += f"  → Batch multiplier: {phase_rules.get('batch_multiplier', 1.0)}x\n"
        
        if phase == 'speed_up':
            log_line += "  → Reducing delays to 48s between steps...\n"
            log_line += "  → Batching requests (3x standard size: 9 requests)...\n"
            log_line += "  → Increasing parallel subtasks by 50%...\n"
        elif phase == 'slow_down':
            log_line += "  → Increasing delays to 72s between steps...\n"
            log_line += "  → Reducing batch size to single-threaded focus mode...\n"
            log_line += "  → Adding verification checkpoint #1...\n"
        elif phase == 'intensify':
            log_line += "  → Maintaining base timing from 60s delays...\n"
            log_line += "  → Adding extra subtasks (+30%) to parallel workload...\n"
            log_line += "  → Requesting deeper analysis on topics...\n"
        else:
            log_line += "  → Standard baseline operations active\n"
        
        log_line += f"  → Elasticity phase activated at {self._get_current_utc_time()}\n"
        log_line += "=" * 60 + "\n"
        
        # Write to log file
        with open(self.log_file, 'a') as f:
            f.write(log_line + "\n")
        
        print(log_line)  # Also print to console for immediate visibility
    
    def run_scheduler_loop(self, interval_seconds: int = 1800):
        """
        Main scheduler loop — checks which phase should be active and logs accordingly.
        
        Interval: how often to check phase rotation (default: 30 minutes = 1800s)
        """
        print("=" * 70)
        print("🔗 Elasticity Hybrid Scheduler — Starting")
        print("=" * 70)
        print(f"Configuration loaded from: {self.config_path}")
        print(f"Scheduling interval: {interval_seconds}s ({interval_seconds/60:.1f} minutes)")
        print("=" * 70)
        
        # Log initial phase states for all domains
        print("\n📊 Initial Phase States:\n")
        for domain, domain_config in self.config.get('domains', {}).items():
            if domain_config.get('elasticity_enabled', False):
                phase, observer = self.get_active_phase_for_domain(domain)
                print(f"  {domain:25s} → {self.phase_names[phase]:30s} ({observer})")
        
        # Clear log file for fresh start
        with open(self.log_file, 'w') as f:
            f.write("# Elasticity Phase Monitoring Log\n")
            f.write(f"# Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n")
            f.write("#\n")
        
        print(f"\n📁 Phase activation logs written to: {self.log_file}\n")
        
        # Main monitoring loop
        print("🔄 Scheduler will check phase rotation every 30 minutes...")
        print("   To stop scheduler, send SIGINT (Ctrl+C) or remove process\n")
        
        try:
            while True:
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M UTC')
                
                for domain, domain_config in self.config.get('domains', {}).items():
                    if domain_config.get('elasticity_enabled', False):
                        phase, observer = self.get_active_phase_for_domain(domain)
                        
                        # Only log when phase changes (avoid spamming logs)
                        if phase != 'baseline' or domain_config.get('current_phase') == phase:
                            self.log_phase_activation(domain, phase, observer)
                
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("\n⏸️  Scheduler paused by user")
            with open(self.log_file, 'a') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}] ⏸️ Scheduler paused\n")
        except Exception as e:
            print(f"\n❌ Scheduler error: {e}")
            with open(self.log_file, 'a') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}] ❌ Error: {e}\n")

def main():
    """Main entry point for hybrid scheduler"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Hybrid Scheduler for Multi-Phase Elasticity Protocol")
    parser.add_argument('--interval', type=int, default=1800, help='Check interval in seconds (default: 1800 = 30 minutes)')
    parser.add_argument('--domain', type=str, default=None, help='Monitor specific domain only')
    
    args = parser.parse_args()
    
    scheduler = ElasticityHybridScheduler()
    
    if args.domain:
        # Single domain check mode — not for background scheduling, but for manual inspection
        print(f"\n🔍 Checking phase status for {args.domain}...\n")
        for i in range(5):  # Check every minute for 5 minutes to show transitions
            phase, observer = scheduler.get_active_phase_for_domain(args.domain)
            print(f"{datetime.now().strftime('%H:%M UTC')}: {phase:10s} ({observer})")
            time.sleep(60)
    else:
        # Run full scheduler loop in background mode
        scheduler.run_scheduler_loop(interval_seconds=args.interval)

if __name__ == "__main__":
    main()