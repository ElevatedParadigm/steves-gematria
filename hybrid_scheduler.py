#!/usr/bin/env python3
"""
🔀 Hybrid Scheduler for Multi-Phase Elasticity Monitoring
==========================================================

Coordinates multi-phase execution (speed up/slow down/intensify) across timezones.
Integrates with overnight research loop at 0,3,6,9,12,15,18,21 hour slots.

Phase rotation strategy:
- Slot 0 (00:00): Slow + Light weight operations
- Slot 3 (03:00): Normal intensity
- Slot 6 (06:00): Speed up - lighter operations
- Slot 9 (09:00): Intensify - full analysis
- Slot 12 (12:00): Speed up + partial processing
- Slot 15 (15:00): Normal intensity
- Slot 18 (18:00): Speed up - optimized operations  
- Slot 21 (21:00): Slow wrap-up phase

Hybrid approach: Combines time-based scheduling with adaptive intensity.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple

# Configuration
HERE = Path(__file__).resolve().parent.parent.parent  # /home/avalonas
GEMATRIA_DIR = HERE / ".hermes" / "gematria"
LOGS_DIR = GEMATRIA_DIR / "logs"
STATUS_FILE = GEMATRIA_DIR / "hybrid_scheduler_status.json"


class HybridScheduler:
    """Multi-phase elasticity monitoring scheduler"""
    
    # Phase definitions for each 3-hour slot
    SLOTS = {
        0: {"name": "midnight_slow", "intensity": 0.5, "type": "light"},
        3: {"name": "early_morning_normal", "intensity": 1.0, "type": "normal"},
        6: {"name": "morning_speed_up", "intensity": 1.5, "type": "optimized"},
        9: {"name": "business_start_intensify", "intensity": 1.8, "type": "full"},
        12: {"name": "noon_speed_up", "intensity": 1.3, "type": "optimized"},
        15: {"name": "afternoon_normal", "intensity": 1.0, "type": "normal"},
        18: {"name": "evening_speed_up", "intensity": 1.4, "type": "optimized"},
        21: {"name": "night_wrapup_slow", "intensity": 0.7, "type": "light"}
    }
    
    def __init__(self):
        self.log_dir = LOGS_DIR
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize state
        self._load_state()
        
        # Current execution state
        self.current_slot: Optional[int] = None
        self.intensity_multiplier: float = 1.0
        self.phase_type: str = "normal"
    
    def _load_state(self):
        """Load scheduler state from status file"""
        if STATUS_FILE.exists():
            try:
                with open(STATUS_FILE, 'r') as f:
                    state = json.load(f)
                
                # Extract intensity info
                self.intensity_multiplier = state.get("intensity", 1.0)
                self.phase_type = state.get("phase_type", "normal")
                self.current_slot = state.get("current_hour", None)
            except Exception as e:
                print(f"⚠️ State load error (non-fatal): {e}")
        
        # Auto-detect current hour for phase alignment
        now_utc = datetime.now(timezone.utc)
        self.last_run_slot = int(now_utc.hour // 3) * 3
        self.current_slot = self.last_run_slot if self.last_run_slot in self.SLOTS else 0
    
    def get_current_phase_config(self) -> Dict:
        """Get current phase configuration"""
        slot = self.SLOTS.get(self.current_slot, self.SLOTS[0])
        
        return {
            "slot_hour": self.current_slot,
            "phase_name": slot["name"],
            "intensity_multiplier": slot["intensity"] * self.intensity_multiplier,
            "operation_type": slot["type"],
            "effective_intensity": round(slot["intensity"] * self.intensity_multiplier, 2)
        }
    
    def run_with_elasticity(self, operation: callable, 
                           operation_name: str = "operation") -> Tuple[bool, any]:
        """Execute operation with current phase elasticity applied"""
        
        config = self.get_current_phase_config()
        intensity = config["effective_intensity"]
        op_type = config["operation_type"]
        
        # Log phase start for monitoring
        self._log(f"PHASE_START", 
                  f"{op_type.upper()} mode ({intensity}x intensity) - {operation_name}",
                  "RUNNING")
        
        try:
            # Adjust operation execution based on phase type
            result = self._execute_with_elasticity(operation, intensity, op_type)
            
            self._log(f"PHASE_COMPLETE", 
                     f"{op_type.upper()} mode completed successfully",
                     "COMPLETED")
            
            return True, result
            
        except Exception as e:
            error_msg = str(e)
            self._log("PHASE_FAILURE", 
                      f"{op_type.upper()} mode failed: {error_msg}",
                      "FAILED")
            
            # Attempt restart (auto-restart on failure)
            if int(self.intensity_multiplier) > 0:
                try:
                    self.restart_operation(operation, operation_name)
                    return True, result
                except Exception as restart_error:
                    print(f"❌ Restart failed: {restart_error}")
            
            return False, error_msg
    
    def _execute_with_elasticity(self, operation: callable, 
                                 intensity: float, op_type: str) -> any:
        """Execute operation with elasticity-adjusted parameters"""
        
        # Log execution details for phase monitoring
        print(f"🕐 Elasticity Phase: {self.current_slot}:00 | Mode: {op_type.upper()}")
        print(f"  Intensity: {intensity}x | Duration multiplier: 1/{intensity:.2f}")
        
        # Adjust operation parameters based on phase
        if op_type == "light":
            # Light mode: reduce timeouts, batch smaller operations
            config = operation.__code__.co_names if hasattr(operation, '__code__') else None
            pass  # Would apply light-weight adjustments here
        
        elif op_type == "optimized":
            # Optimized mode: balance speed and thoroughness
            pass
        
        elif op_type == "full":
            # Full intensity: comprehensive processing
            pass
        
        # Execute the actual operation
        return operation()
    
    def restart_operation(self, operation: callable, name: str):
        """Restart failed operation with exponential backoff"""
        
        import signal
        
        attempts = 0
        max_attempts = 3
        base_delay = 10
        
        while attempts < max_attempts:
            delay = base_delay * (2 ** attempts)
            print(f"\n🔧 Restarting {name} (Attempt {attempts + 1}/{max_attempts})...")
            
            try:
                # Wait before retry
                import time
                time.sleep(delay)
                
                # Clear temporary state
                self._clear_temp_state()
                
                # Re-execute with adjusted intensity
                operation()
                
                print(f"✅ {name} restarted successfully")
                return True
                
            except Exception as e:
                attempts += 1
                if attempts < max_attempts:
                    print(f"⚠️ Restart attempt failed ({attempts}/{max_attempts}): {str(e)[:100]}")
                else:
                    print(f"❌ All restart attempts failed for {name}")
        
        raise Exception(f"All restart attempts failed for {name}")
    
    def _clear_temp_state(self):
        """Clear temporary state files"""
        
        temp_files = [
            "/tmp/overnight_stability_*.json",
            "/tmp/overnight_analysis_*",
            str(STATUS_FILE.with_suffix(".tmp"))
        ]
        
        for pattern in temp_files:
            try:
                import glob
                for path in glob.glob(pattern):
                    os.remove(path)
            except Exception as e:
                pass  # Ignore cleanup errors
    
    def _log(self, phase: str, message: str, status: str = "RUNNING"):
        """Log to both console and file"""
        
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        log_line = f"[{timestamp}] === PHASE: {phase} ==="
        print(log_line)
        log_line += f"\n📝 {message}"
        print(log_line)
        log_line += f"\n   Status: {status}"
        print(log_line)
        
        # Write to log file
        try:
            with open(self.log_dir / "hybrid_scheduler.log", 'a', encoding='utf-8') as f:
                f.write(log_line + "\n")
        except Exception as e:
            pass
    
    def update_status_file(self):
        """Update scheduler status for monitoring"""
        
        config = self.get_current_phase_config()
        
        status_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "current_slot": self.current_slot,
            "phase_type": config["operation_type"],
            "intensity_multiplier": config["effective_intensity"],
            "last_run_hour": self.last_run_slot,
            "next_slot": (self.last_run_slot + 3) % 24 if self.last_run_slot != 21 else None,
            "status": "ACTIVE" if self.current_slot is not None else "INITIALIZING"
        }
        
        try:
            with open(STATUS_FILE, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, indent=2)
            
            # Create compact status for quick monitoring
            compact_status = {
                "slot": self.current_slot,
                "mode": config["operation_type"].upper(),
                "intensity": config["effective_intensity"],
                "phase": config["phase_name"]
            }
            
            status_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_dir / "scheduler_compact.json", 'w') as f:
                json.dump(compact_status, f)
            
        except Exception as e:
            print(f"⚠️  Status file update error: {e}")
    
    def check_next_slot(self) -> Optional[int]:
        """Determine if we should advance to next slot"""
        
        now_utc = datetime.now(timezone.utc)
        current_hour = int(now_utc.hour // 3) * 3
        
        # If hour changed significantly (≥2 hours), advance to new slot
        if abs(current_hour - self.last_run_slot) >= 2:
            next_slot = (current_hour + 3) % 24 if current_hour < 21 else None
            return next_slot
        
        return None
    
    def run_health_check(self) -> Dict:
        """Run health check for scheduler status"""
        
        try:
            with open(STATUS_FILE, 'r') as f:
                status = json.load(f)
            
            return {
                "healthy": True,
                "current_slot": self.current_slot,
                "phase_type": status.get("phase_type", "unknown"),
                "intensity": status.get("intensity_multiplier", 1.0),
                "timestamp": status.get("timestamp")
            }
        
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }


def main():
    """Main entry point for scheduler CLI"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="🔀 Hybrid Scheduler - Multi-Phase Elasticity")
    parser.add_argument("--status", action="store_true", help="Show current scheduler status")
    parser.add_argument("--slot", type=int, default=None, help="Manually set slot hour")
    parser.add_argument("--check-health", action="store_true", help="Run health check")
    
    args = parser.parse_args()
    
    # Initialize scheduler
    scheduler = HybridScheduler()
    
    if args.status:
        config = scheduler.get_current_phase_config()
        print("\n🔀 HYBRID SCHEDULER STATUS")
        print("=" * 60)
        print(f"Current Slot: {config['slot_hour']:02d}:00 UTC")
        print(f"Phase Name:   {config['phase_name']}")
        print(f"Operation Type: {config['operation_type'].upper()}")
        print(f"Intensity:     {config['effective_intensity']}x")
        print("=" * 60)
        
        return 0
    
    elif args.check_health:
        health = scheduler.run_health_check()
        if health["healthy"]:
            print("✅ Scheduler is healthy and running normally")
            return 0
        else:
            print(f"❌ Scheduler health check failed: {health.get('error', 'Unknown error')}")
            return 1
    
    # Normal operation: Check and update slot
    next_slot = scheduler.check_next_slot()
    
    if next_slot is not None:
        scheduler.current_slot = next_slot
        print(f"\n🔀 Advancing to slot {next_slot}:00")
        
        # Update status file
        scheduler.update_status_file()
    
    else:
        config = scheduler.get_current_phase_config()
        print(f"\n🔀 Current phase active: {config['phase_name']}")
        print(f"   Intensity: {config['effective_intensity']}x mode")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
