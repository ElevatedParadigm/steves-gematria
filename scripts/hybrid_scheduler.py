#!/usr/bin/env python3
"""
🔄 Hybrid Scheduler - Elasticity Phase Monitoring System
========================================================

Multi-phase elasticity monitoring for gematria research system.
Manages baseline/speed_up/slow_down/intensify phases across timezones.

Integrates with overnight research loop for dynamic scheduling.

Usage:
    python3 hybrid_scheduler.py [--phase PHASE] [--debug]

Elasticity Phases (from config.yaml):
- baseline: Standard operations at normal pace
- speed_up: +20% faster, larger batches enabled
- slow_down: -15% slower, focused verification mode
- intensify: Same pace but deeper analysis with parallel depth

Phase rotation across timezones per config rules.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import random

# Auto-detect gematria directory
HERE = Path(__file__).resolve().parent.parent
GEMATRIA_DIR = HERE


class HybridScheduler:
    """Hybrid scheduler for multi-phase elasticity monitoring"""
    
    def __init__(self):
        self.config_file = GEMATRIA_DIR / "config.yaml"
        self.state_file = GEMATRIA_DIR / ".hybrid_scheduler_state.json"
        
        # Phase definitions with timing rules
        self.phase_rules = {
            "baseline": {
                "description": "Standard operations at normal pace",
                "speed_multiplier": 1.0,
                "batch_size": 3,
                "timeout_mult": 1.0,
                "parallel_depth": 1
            },
            "speed_up": {
                "description": "+20% faster, larger batches enabled",
                "speed_multiplier": 1.2,
                "batch_size": 9,
                "timeout_mult": 0.8,
                "parallel_depth": 1
            },
            "slow_down": {
                "description": "-15% slower, focused verification mode",
                "speed_multiplier": 0.85,
                "batch_size": 3,
                "timeout_mult": 1.15,
                "parallel_depth": 1
            },
            "intensify": {
                "description": "Same pace but deeper analysis with parallel depth",
                "speed_multiplier": 1.0,
                "batch_size": 3,
                "timeout_mult": 1.0,
                "parallel_depth": 4
            }
        }
        
        # Phase transition rules based on timezones/hours
        self.transition_rules = {
            "UTC": {
                "speed_up_hours": (8, 18),      # Business hours
                "slow_down_hours": (4, 12),     # Early morning
                "baseline_hours": (0, 4) + (18, 24),  # Off-hours
                "intensify_windows": [          # Deep work sessions
                    {"start": 2, "end": 3},     # Pre-business prep
                    {"start": 22, "end": 4}     # Late night deep analysis
                ]
            }
        }
        
        self.current_phase = self.load_current_phase()
    
    def load_current_phase(self) -> str:
        """Load current phase from state file or determine by timezone"""
        
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                
                current = state.get("current_phase", "baseline")
                return current
        
        except (json.JSONDecodeError, Exception):
            pass
        
        # Default to baseline if no state found
        self.current_phase = "baseline"
        
        return self.current_phase
    
    def save_current_phase(self, phase: str) -> None:
        """Save current phase to state file"""
        
        state = {
            "current_phase": phase,
            "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "phase_history": self.get_phase_history()
        }
        
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving state: {e}")
    
    def get_phase_history(self, max_entries: int = 100) -> list:
        """Get phase transition history"""
        
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                
                history = state.get("phase_history", [])
                return history[-max_entries:]
        except (json.JSONDecodeError, Exception):
            pass
        
        return []
    
    def determine_phase(self, timezone_name: str = "UTC") -> tuple:
        """Determine current phase based on rules and time"""
        
        now_utc = datetime.now(timezone.utc)
        hour = now_utc.hour
        day = now_utc.strftime("%Y-%m-%d")
        
        # Check intensify windows first
        for window in self.transition_rules["UTC"]["intensify_windows"]:
            if (window["start"] <= hour < window["end"]) or \
               (window["end"] > 24 and hour >= window["start"]):
                phase = "intensify"
                break
        else:
            # Check other windows
            if self.transition_rules["UTC"]["speed_up_hours"][0] <= hour < self.transition_rules["UTC"]["speed_up_hours"][1]:
                phase = "speed_up"
            elif self.transition_rules["UTC"]["slow_down_hours"][0] <= hour < self.transition_rules["UTC"]["slow_down_hours"][1]:
                phase = "slow_down"
            else:
                phase = "baseline"
        
        return (phase, f"{day}T{hour:02d}:00Z")
    
    def load_config(self) -> Dict[str, Any]:
        """Load elasticity configuration"""
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    content = f.read()
                
                config = parse_yaml_simple(content)
                
                # Merge with defaults if sections exist
                for key in self.phase_rules.keys():
                    if key not in config.get("elasticity_phases", {}):
                        config["elasticity_phases"][key] = self.phase_rules[key]
                
                return config
                
            except Exception as e:
                print(f"⚠️ Error loading config.yaml: {e}")
        
        # Return defaults if no config found
        return {"elasticity_phases": self.phase_rules}
    
    def transition_phase(self, new_phase: str) -> bool:
        """Transition to a new phase"""
        
        if new_phase not in self.phase_rules:
            print(f"❌ Invalid phase: {new_phase}")
            return False
        
        old_phase = self.current_phase
        self.current_phase = new_phase
        self.save_current_phase(new_phase)
        
        # Log transition
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        history_entry = {
            "from": old_phase,
            "to": new_phase,
            "timestamp": timestamp
        }
        
        current_state = {}
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    current_state = json.load(f)
            except:
                pass
        
        history = current_state.get("phase_history", [])
        history.append(history_entry)
        
        try:
            if self.state_file.exists():
                with open(self.state_file, 'w') as f:
                    json.dump({
                        "current_phase": new_phase,
                        "timestamp": timestamp,
                        "phase_history": history
                    }, f, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving state: {e}")
        
        return True
    
    def run(self, phase: Optional[str] = None, debug: bool = False) -> Dict[str, Any]:
        """Run hybrid scheduler initialization"""
        
        print("=" * 60)
        print("🔄 HYBRID SCHEDULER INITIALIZATION")
        print("=" * 60)
        
        # Load config
        config = self.load_config()
        
        if phase:
            success = self.transition_phase(phase)
            if not success:
                return {"success": False, "error": f"Failed to transition to {phase}"}
        
        else:
            # Auto-determine phase based on current time
            (auto_phase, timestamp) = self.determine_phase()
            
            # Check if we should stay in current phase or transition
            if auto_phase != self.current_phase:
                print(f"\n⏰ Time-based phase check ({timestamp}):")
                print(f"   → Current phase: {self.current_phase}")
                print(f"   → Recommended phase: {auto_phase}")
                
                # Auto-transition on first run or significant time difference
                if self.current_phase == "baseline":  # Default to auto on first run
                    success = self.transition_phase(auto_phase)
                    if success:
                        print(f"   → ✅ Transitioned to: {auto_phase}")
            else:
                print(f"\n✅ Phase check complete:")
                print(f"   → Current phase: {self.current_phase.upper()}")
        
        # Display current phase info
        phase_info = self.phase_rules.get(self.current_phase, {})
        
        print("\n📊 CURRENT ELASTICITY PHASE INFORMATION:")
        print(f"   Phase Name:    [{self.current_phase.upper()}]")
        print(f"   Description:   {phase_info.get('description', 'N/A')}")
        print(f"   Speed Multiplier: {phase_info.get('speed_multiplier', 1.0)}x")
        print(f"   Batch Size:     {phase_info.get('batch_size', 3)}")
        
        # Phase emoji display
        phase_emoji = {"baseline": "⏱️", "speed_up": "🚀", "slow_down": "🐢", "intensify": "⚡"}[self.current_phase]
        print(f"   → {phase_info.get('description', '')}")
        
        # Display phase rotation schedule
        print("\n📅 PHASE ROTATION SCHEDULE (UTC):")
        
        for rule_name, rule in self.transition_rules["UTC"].items():
            if isinstance(rule, tuple) and len(rule) == 2:
                start, end = rule
                period_str = f"{start:02d}:00 - {min(end, 24):02d}:00"
                print(f"   • {rule_name.title()}:    UTC {period_str}")
            elif isinstance(rule, list):
                periods = []
                for item in rule:
                    if isinstance(item, tuple):
                        periods.append(f"{item[0]:02d}:00 - {min(item[1], 24):02d}:00")
                    else:
                        periods.append(str(item))
                print(f"   • {rule_name.title()}:    UTC {', '.join(periods)}")
            elif isinstance(rule, list) and len(rule) > 0 and isinstance(rule[0], dict):
                # Window format
                windows = rule
                window_strs = []
                for w in windows:
                    start_h = w.get("start", 0)
                    end_h = w.get("end", 24)
                    if start_h < end_h:
                        window_strs.append(f"{start_h:02d}:00 - {end_h:02d}:00")
                    else:
                        window_strs.append(f"{start_h:02d}:00 - 24:00, 00:00 - {end_h:02d}:00")
                print(f"   • {rule_name.title()}:    UTC {', '.join(window_strs)}")
        
        # Display phase definitions
        print("\n📚 AVAILABLE ELASTICITY PHASES:")
        for name, info in sorted(self.phase_rules.items()):
            emoji = {"baseline": "⏱️", "speed_up": "🚀", "slow_down": "🐢", "intensify": "⚡"}.get(name, "•")
            print(f"\n  {emoji} [{name.upper()}]")
            print(f"     Description: {info.get('description', '')}")
            print(f"     Speed:       {info.get('speed_multiplier', 1.0)}x normal pace")
            print(f"     Batch Size:  {info.get('batch_size', 3)} requests/batch")
            if name == "intensify":
                print(f"     Parallel Depth: {info.get('parallel_depth', 4)} parallel streams")
        
        return {
            "success": True,
            "current_phase": self.current_phase,
            "phase_info": phase_info,
            "config_loaded": bool(self.config_file.exists())
        }
        
        # Output phase info for loop_runner extraction (always print)
        print(f"\nCurrent Elasticity Phase: [{self.current_phase.upper()}]")


# YAML handling (without PyYAML dependency)
def parse_yaml_simple(content):
    """Simple YAML parser for basic key: value format without PyYAML"""
    result = {}
    current_section = {}
    
    lines = content.split('\n')
    for line in lines:
        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith('#'):
            continue
        
        # Check indentation level (simple section detection)
        indent = len(line) - len(line.lstrip())
        
        # Top-level keys (indent 0)
        if indent == 0:
            current_section = {}
            if ':' in line:
                key, _, val = line.partition(':')
                key = key.strip()
                val = val.strip().strip('"\'').strip('- ')
                result[key] = parse_value(val, is_list=False)
        # Nested keys (indent > 0)
        elif indent > 0:
            if '---' in line or ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    val = parts[1].strip().strip('"\'').strip('- ')
                    current_section[key] = parse_value(val, is_list=is_in_list_mode(key))
    
    return result


def parse_value(val_str, is_list=False):
    """Parse a YAML value"""
    if not val_str:
        return None
    
    # List indicators
    if val_str.startswith('-'):
        return []
    
    # Quote handling
    val_str = val_str.strip('"\'')
    
    # Boolean
    if val_str.lower() in ('true', 'yes', 'on'):
        return True
    if val_str.lower() in ('false', 'no', 'off'):
        return False
    
    # Null
    if val_str.lower() in ('null', '~', ''):
        return None
    
    # Number
    try:
        if '.' in val_str:
            return float(val_str)
        return int(val_str)
    except ValueError:
        pass
    
    return val_str


def is_in_list_mode(key):
    """Check if key should store list values"""
    list_keys = ['domains', 'aliases', 'characteristics', 'complements', 'tags']
    return key in list_keys


def main():
    """Main entry point"""
    
    phase_override = None
    debug_mode = False
    
    # Parse arguments
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg.startswith("--phase"):
                try:
                    phase_override = arg.split("=")[1]
                    print(f"Phase override set to: {phase_override}")
                except (ValueError, IndexError):
                    pass
            
            elif arg == "--debug":
                debug_mode = True
    
    # Run scheduler
    scheduler = HybridScheduler()
    result = scheduler.run(phase=phase_override, debug=debug_mode)
    
    if result.get("success"):
        print("\n" + "=" * 60)
        print("✅ HYBRID SCHEDULER INITIALIZED SUCCESSFULLY")
        print("=" * 60)
        print(f"Current Elasticity Phase: [{scheduler.current_phase.upper()}]")
        
        if debug_mode:
            phase_state = {
                "current_phase": scheduler.current_phase,
                "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                "phase_rules": scheduler.phase_rules
            }
            print(f"\nDebug state saved to: {scheduler.state_file}")
        
        return 0
    
    else:
        print("\n" + "=" * 60)
        print("❌ HYBRID SCHEDULER INITIALIZATION FAILED")
        print("=" * 60)
        if "error" in result:
            print(f"Error: {result['error']}")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
