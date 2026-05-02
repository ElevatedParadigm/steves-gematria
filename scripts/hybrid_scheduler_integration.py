#!/usr/bin/env python3
"""
🔄 Hybrid Scheduler Integration Module
=========================================================

Provides multi-phase elasticity monitoring for overnight research loops.
Integrates with hybrid_scheduler.py for baseline/speed_up/slow_down/intensify phases.

Usage:
    python3 hybrid_scheduler_integration.py [--once] [--domain DOMAIN_NAME]
    
Or import and use programmatically in loop_runner_enhanced.py
"""

import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path.home()))

class HybridSchedulerIntegration:
    """Integration module for hybrid scheduler with phase rotation"""
    
    def __init__(self):
        self.gematria_dir = Path.home() / ".hermes" / "gematria"
        self.hybrid_scheduler_path = self.gematria_dir / "scripts" / "hybrid_scheduler.py"
        self.config_path = self.gematria_dir / "config.yaml"
        self.state_file = self.gematria_dir / "elasticity_state.json"
        
    def load_config(self):
        """Load elasticity configuration from config.yaml"""
        
        if not self.config_path.exists():
            return {
                "elasticity_rules": {},
                "domains": {
                    "Military History": {
                        "current_phase": "baseline",
                        "phase_rotation_schedule": {
                            "speed_up_observer": "Europe/EEST",
                            "slow_down_observer": "America/EST",
                            "intensify_observer": "Asia/Shanghai"
                        }
                    },
                    "Space Exploration": {
                        "current_phase": "baseline",
                        "phase_rotation_schedule": {
                            "speed_up_observer": "Asia/Tokyo",
                            "slow_down_observer": "Australia/Sydney",
                            "intensify_observer": "America/Pacific"
                        }
                    },
                    "Climate Science": {
                        "current_phase": "baseline",
                        "phase_rotation_schedule": {
                            "speed_up_observer": "Europe/EEST",
                            "slow_down_observer": None,
                            "intensify_observer": "Asia/Shanghai"
                        }
                    }
                },
                "phases": {
                    "baseline": {"name": "Baseline (Default)", "description": "Standard operations"},
                    "speed_up": {"name": "Speed Up (+20%)", "description": "Faster info gathering"},
                    "slow_down": {"name": "Slow Down (-15%)", "description": "Focused verification mode"},
                    "intensify": {"name": "Intensify", "description": "Deep analysis with parallel depth"}
                }
            }
        
        # Parse config.yaml for phase assignments
        domains = {
            "Military History": None,
            "Space Exploration": None,
            "Climate Science": None
        }
        
        current_config = {}
        
        in_section = False
        current_domain = None
        
        try:
            with open(self.config_path, 'r') as f:
                content = f.read()
            
            for line in content.split('\n'):
                stripped = line.strip()
                
                if ': elasticity_enabled:' in stripped or current_domain is None:
                    # Look for domain section header
                    parts = stripped.split(': ')
                    if len(parts) >= 2:
                        domain_name = parts[0].strip().rstrip('/')
                        if 'current_phase' in stripped and domain_name in domains:
                            phase_str = stripped.split('"')[1] if '"' in stripped else "baseline"
                            domains[domain_name] = phase_str
        except Exception as e:
            pass
        
        return {"domains": domains}
    
    def get_current_phase(self) -> str:
        """Get current elasticity phase based on time and timezone"""
        
        from datetime import datetime
        
        now = datetime.utcnow()
        
        # Get observer times
        eest_time = now.astimezone('Europe/EEST')
        est_time = now.astimezone('America/EST')
        shanghai_time = now.astimezone('Asia/Shanghai')
        
        eest_hour = eest_time.hour
        est_hour = est_time.hour
        shanghai_hour = shanghai_time.hour
        
        # Determine phase based on time windows
        phase = "baseline"
        
        # Speed up: Europe/EEST observer hours (8-18)
        if eest_hour in range(8, 18):
            phase = "speed_up"
        
        # Slow down: America/EST observer hours (4-12)
        elif est_hour in range(4, 12):
            phase = "slow_down"
        
        # Intensify: Asia/Shanghai midday (8-14)
        elif shanghai_hour in range(8, 14):
            phase = "intensify"
        
        return phase
    
    def print_status(self):
        """Print current elasticity phase with status markers"""
        
        phase = self.get_current_phase()
        
        # Load state
        if not self.state_file.exists():
            state = {"current_phase": phase}
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        
        else:
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                # Update current phase
                state["current_phase"] = phase
                state["last_change"] = datetime.now().isoformat()
                with open(self.state_file, 'w') as f:
                    json.dump(state, f, indent=2)
            except:
                state = {"current_phase": phase}
        
        # Determine emoji and description
        phase_info = {
            "baseline": ("⏱️", "BASELINE - Standard operations at normal pace"),
            "speed_up": ("🚀", "SPEED UP - +20% faster, larger batches enabled"),
            "slow_down": ("🐢", "SLOW DOWN - -15% slower, focused verification mode"),
            "intensify": ("⚡", "INTENSIFY - Deep analysis with parallel depth")
        }
        
        emoji, description = phase_info.get(phase, ("📊", f"PHASE: {phase}"))
        
        print(f"\n{'='*50}")
        print("🔄 HYBRID SCHEDULER STATUS")
        print(f"{'='*50}")
        print(f"\nCurrent Elasticity Phase: [{emoji}] {phase.upper()}")
        print(f"\n{description}")
        
        now_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        print(f"\nTimestamp: {now_str}")
        
        print(f"\n{'='*50}\n")
    
    def get_phase_info(self) -> dict:
        """Get detailed phase information for logging"""
        
        phase = self.get_current_phase()
        
        phase_details = {
            "phase": phase,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rules": {}
        }
        
        # Get rules based on phase
        if phase == "speed_up":
            phase_details["rules"] = {
                "timing_adjustment": "+20%",
                "batch_multiplier": 9,
                "subtask_increase": "+50%"
            }
        elif phase == "slow_down":
            phase_details["rules"] = {
                "timing_adjustment": "-15%",
                "batch_multiplier": 1,
                "verification_mode": "checkpoints between each step"
            }
        elif phase == "intensify":
            phase_details["rules"] = {
                "timing_adjustment": "unchanged",
                "subtask_increase": "+30%",
                "analysis_depth": "deep + cross-check queries"
            }
        
        return phase_details


def main():
    """Main entry point for standalone execution"""
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Hybrid Scheduler Integration Module"
    )
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--domain', type=str, default=None, 
                       help='Specific domain name (Military History, Space Exploration, Climate Science)')
    
    args = parser.parse_args()
    
    integration = HybridSchedulerIntegration()
    
    if args.json:
        phase_info = integration.get_phase_info()
        print(json.dumps(phase_info, indent=2))
    else:
        if args.once or not getattr(sys, '_is_cron_job', True):
            integration.print_status()
        else:
            # For cron jobs running continuously
            print("✅ Hybrid scheduler integration ready")
            print(f"   Current phase: {integration.get_current_phase().upper()}")


if __name__ == "__main__":
    main()
