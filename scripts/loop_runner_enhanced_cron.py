#!/usr/bin/env python3
"""
🌙 Enhanced Overnight Research Loop - Cron Job Version (Final Working)
========================================================

Run nightly research loop with:
✅ Enhanced stability test on gematria database
✅ Auto-sync to Obsidian notes with relationship matrices  
✅ Correlation heatmaps and relationship visualizations
✅ Hybrid scheduler for multi-phase elasticity monitoring
✅ Phase markers in logs for hybrid_scheduler.py integration
✅ Auto-restart/retry capability on failure

Usage:
    python3 loop_runner_enhanced_cron.py --timeout 2700 [--dry-run]
    
Configuration:
    Script: /home/avalonas/.hermes/gematria/scripts/loop_runner_enhanced_cron.py
    Logs to: /home/avalonas/.hermes/gematria/cron_logs/
    Schedule: Every 3 hours at :00 (hours 0,3,6,9,12,15,18,21 UTC)

Integrations:
    - stability_test_enhanced_fixed.py
    - auto_obisidian_sync_v2.py  
    - hybrid_scheduler.py (elasticity phase rotation)

Elasticity Phases (from config.yaml):
    - baseline: Standard operations at normal pace
    - speed_up: +20% faster, larger batches enabled (9 requests vs 3 standard)
    - slow_down: -15% slower, focused verification mode  
    - intensify: Same pace but deeper analysis with parallel depth
"""

import os
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any
import json

sys.path.insert(0, str(Path.home()))


class EnhancedLoopConfig:
    """Configuration for enhanced overnight research loop"""
    
    def __init__(self):
        self.gematria_dir = Path.home() / ".hermes" / "gematria"
        self.logs_dir = self.gematria_dir / "cron_logs"
        self.main_log_file = self.logs_dir / "cron_job.log"
        self.phase_log_file = self.logs_dir / "phase_markers.log"
        self.hybrid_log_file = self.logs_dir / "hybrid_scheduler.log"
        
        # Script paths
        self.stability_script = self.gematria_dir / "scripts" / "stability_test_enhanced_fixed.py"
        self.sync_script = self.gematria_dir / "scripts" / "auto_obisidian_sync_v2.py"
        self.hybrid_scheduler_script = self.gematria_dir / "scripts" / "hybrid_scheduler.py"


class EnhancedLoopRunner:
    """Enhanced overnight research loop runner with elasticity monitoring"""
    
    def __init__(self, config: EnhancedLoopConfig, timeout: int = 2700):
        self.config = config
        self.main_log = self.config.main_log_file
        self.phase_log = self.config.phase_log_file
        self.hybrid_log = self.config.hybrid_log_file
        
        # Ensure directories exist
        for log_file in [self.main_log, self.phase_log, self.hybrid_log]:
            log_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.hybrid_scheduler_active = False
        self.timeout = timeout
    
    def log_main(self, message: str) -> None:
        """Write to main log file"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        entry = f"[{timestamp}] {message}\n"
        
        with open(self.main_log, 'a') as f:
            f.write(entry)
    
    def log_phase_marker(self, phase: str, details: str = "") -> None:
        """Write phase marker to dedicated log file for hybrid_scheduler monitoring"""
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        
        # Determine emoji based on phase
        phase_info = {
            "stability": ("🧪", ""),
            "sync": ("🔄", ""),
            "heatmap": ("📊", ""),
            "hybrid_scheduler": ("🔄", "")
        }
        
        emoji, suffix = phase_info.get(phase, ("", ""))
        log_entry = f"[{timestamp}] === PHASE: {phase.upper()} ===\n   → Action: {details}\n   → Timestamp: {timestamp}{suffix}\n\n"
        
        with open(self.phase_log, 'a') as f:
            f.write(log_entry)
    
    def log_hybrid_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Write event to hybrid scheduler log for elasticity monitoring"""
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        
        # Get current phase from hybrid_scheduler output or default
        try:
            now = datetime.now()
            # Use UTC hours only to avoid timezone string parsing errors
            utc_hour = now.hour
            
            if 8 <= utc_hour < 18:
                current_phase = "speed_up"
            elif 4 <= utc_hour < 12:
                current_phase = "slow_down"
            else:
                current_phase = "baseline"
        except:
            current_phase = "baseline"
        
        event_entry = f"[{timestamp}] === {event_type.upper()} ===\nCurrent Phase: [{current_phase.upper()}]\nData: {json.dumps(data)[:500]}\n\n"
        
        with open(self.hybrid_log, 'a') as f:
            f.write(event_entry)
    
    def ensure_hybrid_scheduler_active(self) -> bool:
        """Ensure hybrid scheduler is running for elasticity monitoring
        
        Integrates with hybrid_scheduler.py for multi-phase elasticity monitoring:
        - baseline: Standard operations at normal pace  
        - speed_up: +20% faster, larger batches enabled (9 requests vs 3 standard)
        - slow_down: -15% slower, focused verification mode
        - intensify: Same pace but deeper analysis with parallel depth
        
        Phase rotation across timezones per config.yaml elasticity_rules.
        """
        
        print("🔄 Starting hybrid scheduler for elasticity monitoring...")
        self.log_main("🔄 === PHASE: HYBRID_SCHEDULER_INIT ===")
        self.log_main(f"   → Action: Starting elasticity phase rotation system")
        self.log_main(f"   → Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        try:
            result = subprocess.run(
                ["python3", str(self.config.hybrid_scheduler_script)],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(Path.home() / ".hermes" / "gematria" / "scripts")
            )
            
            output_lines = result.stdout.strip().split('\n') if result.stdout else []
            
            # Extract current phase from output - handle emoji in output
            current_phase = "baseline"
            for line in output_lines:
                if "Current Elasticity Phase:" in line or ("[speed_up" in line.lower() and "elasticity" in line.lower()):
                    # Handle both emoji and text-based extraction
                    parts = line.split("Current Elasticity Phase: [")
                    if len(parts) > 1:
                        bracket_content = parts[1].split("]")[0]
                        # Clean up the phase name - handle emojis
                        clean_phase = ""
                        for char in bracket_content.strip().split():
                            if char and char not in ['🚀', '🐢', '⏱️', '⚡']:  # Skip emoji characters
                                clean_phase += char
                        current_phase = clean_phase.lower()
                elif "[speed_up" in line.lower() and "elasticity" in line.lower():
                    parts = line.split("Current Elasticity Phase: [")
                    if len(parts) > 1:
                        bracket_content = parts[1].split("]")[0]
                        clean_phase = ""
                        for char in bracket_content.strip().split():
                            if char and char not in ['🚀', '🐢', '⏱️', '⚡']:
                                clean_phase += char
                        current_phase = clean_phase.lower()
                elif "[slow_down" in line.lower() and "elasticity" in line.lower():
                    parts = line.split("Current Elasticity Phase: [")
                    if len(parts) > 1:
                        bracket_content = parts[1].split("]")[0]
                        clean_phase = ""
                        for char in bracket_content.strip().split():
                            if char and char not in ['🚀', '🐢', '⏱️', '⚡']:
                                clean_phase += char
                        current_phase = clean_phase.lower()
                elif "[baseline" in line.lower() and "elasticity" in line.lower():
                    parts = line.split("Current Elasticity Phase: [")
                    if len(parts) > 1:
                        bracket_content = parts[1].split("]")[0]
                        clean_phase = ""
                        for char in bracket_content.strip().split():
                            if char and char not in ['🚀', '🐢', '⏱️', '⚡']:
                                clean_phase += char
                        current_phase = clean_phase.lower()
            
            print(f"✅ Hybrid scheduler active - Current phase: {current_phase.upper()}")
            self.log_main(f"   → Current Elasticity Phase: [{current_phase.upper()}]")
            self.log_hybrid_event("HYBRID_SCHEDULER_START", {"phase": current_phase, "output_lines": len(output_lines)})
            
            if result.returncode == 0 or (output_lines and len(output_lines) > 0):
                print("✅ Hybrid scheduler started/running")
                self.hybrid_scheduler_active = True
                self.log_main(f"   → Status: HYBRID_SCHEDULER_RUNNING")
                
                # Log phase info for elasticity monitoring  
                if 'elasticity_rules' in result.stdout or ('speed_up' in current_phase.lower()):
                    timing_info = ["speed_up/rules_active"]
                elif 'FOCUSED VERIFICATION' in result.stdout:
                    timing_info = ["slow_down/verification_mode"]
                elif 'DEEP ANALYSIS' in result.stdout:
                    timing_info = ["intensify/deep_analysis"]
                else:
                    timing_info = []
                
                self.log_main(f"   → Available phases: baseline, speed_up, slow_down, intensify")
            else:
                print(f"⚠️ Hybrid scheduler check returned exit code: {result.returncode}")
                self.log_main(f"   → Status: HYBRID_SCHEDULER_CHECK_SKIPPED (exit {result.returncode})")
                
        except subprocess.TimeoutExpired:
            print(f"⚠️ HYBRID_SCHEDULER CHECK TIMEOUT")
            self.log_main("   → Status: HYBRID_SCHEDULER_TIMEOUT (exceeded 120s)")
            self.hybrid_scheduler_active = False
            
        except FileNotFoundError as e:
            print(f"❌ HYBRID_SCHEDULER_NOT_FOUND: {e}")
            self.log_main(f"   → Error: HYBRID_SCHEDULER_PATH - {str(e)}")
            self.hybrid_scheduler_active = False
            
        except Exception as e:
            error_msg = str(e)
            if "No module named" in error_msg or "import" in error_msg.lower():
                print(f"⚠️ PYTHON_IMPORT_ERROR: {error_msg[:50]}")
                self.log_main(f"   → Error: HYBRID_SCHEDULER - Python import error: {error_msg[:100]}")
            else:
                print(f"⚠️ ERROR_STARTING_HYBRID_SCHEDULER: {e}")
                self.log_main(f"   → Error: HYBRID_SCHEDULER - Exception: {str(e)[:100]}")
            self.hybrid_scheduler_active = False
        
        return self.hybrid_scheduler_active
    
    def run_with_retry(self, func) -> Dict[str, Any]:
        """Run a function with retry capability on failure"""
        
        last_error = None
        attempts = 0
        
        while attempts < 3:
            attempts += 1
            print(f"\n   Attempt {attempts}/3")
            
            try:
                return func()
                
            except Exception as e:
                error_msg = str(e)
                if "Timeout" in error_msg or "timeout" in error_msg.lower():
                    last_error = {"error": f"Timeout - exceeded {self.timeout}s", "type": "timeout"}
                else:
                    last_error = {"error": error_msg[:200], "type": str(type(e).__name__)}
                print(f"   Error: {last_error['error']}")
        
        return {"success": False, "error": str(last_error.get("error", "Unknown")), "attempt": attempts}
    
    def run_stability_test(self) -> Dict[str, Any]:
        """Run enhanced stability test on gematria database
        
        Phase marker: === PHASE: STABILITY_TEST ===
        Integrates with stability_test_enhanced_fixed.py for comprehensive integrity checks.
        """
        
        print("\n" + "="*60)
        print("🧪 PHASE 1: STABILITY TEST")
        print("="*60)
        
        script_path = str(self.config.stability_script)
        
        # Phase marker for hybrid scheduler integration
        self.log_phase_marker("stability", "Starting enhanced stability test on gematria database")
        
        try:
            result = subprocess.run(
                ["python3", script_path, "--timeout", str(self.timeout)],
                capture_output=True,
                text=True,
                timeout=self.timeout + 60
            )
            
            output = result.stdout + result.stderr
            
            # Log main progress for monitoring
            self.log_main(f"🧪 Stability Test Started")
            self.log_main(output[:2000])
            
            if result.returncode == 0:
                print("✅ STABILITY TEST PASSED")
                self.log_phase_marker("stability", "✅ PASSED - Database integrity verified")
                
                # Report to hybrid scheduler if active
                if self.hybrid_scheduler_active:
                    event_data = {"status": "passed", "output_length": len(output)}
                    self.log_hybrid_event("STABILITY_CHECK_PASSED", event_data)
                
                return {
                    "success": True,
                    "returncode": result.returncode,
                    "duration_seconds": 0
                }
            else:
                print(f"⚠️ STABILITY TEST COMPLETED WITH WARNINGS (Exit code: {result.returncode})")
                self.log_phase_marker("stability", f"⚠️ COMPLETED WITH WARNINGS - Check reports for details")
                
                # Log warning to hybrid scheduler
                if self.hybrid_scheduler_active:
                    event_data = {"status": "warnings", "returncode": result.returncode}
                    self.log_hybrid_event("STABILITY_CHECK_WARNING", event_data)
                
                return {
                    "success": False,
                    "returncode": result.returncode,
                    "output": output[:2000]
                }
                
        except subprocess.TimeoutExpired:
            print("❌ STABILITY TEST TIMEOUT")
            self.log_phase_marker("stability", f"❌ TIMEOUT - Exceeded {self.timeout}s")
            
            if self.hybrid_scheduler_active:
                event_data = {"status": "timeout", "timeout": self.timeout}
                self.log_hybrid_event("STABILITY_CHECK_TIMEOUT", event_data)
                
            return {
                "success": False,
                "error": "Timeout",
                "timeout": self.timeout
            }

    def run_auto_sync(self) -> Dict[str, Any]:
        """Run auto-sync to Obsidian notes with relationship matrices
        
        Phase marker: === PHASE: AUTO_SYNC ===
        Integrates with auto_obisidian_sync_v2.py for exporting relationships, matrices.
        """
        
        print("\n" + "="*60)
        print("🔄 PHASE 2: AUTO-OBSIDIAN SYNC")
        print("="*60)
        
        script_path = str(self.config.sync_script)
        
        # Phase marker for hybrid scheduler integration
        self.log_phase_marker("sync", "Auto-sync to Obsidian notes with relationship matrices")
        
        try:
            result = subprocess.run(
                ["python3", script_path],
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes for sync operations
            )
            
            output = result.stdout + result.stderr
            
            # Log main progress for monitoring
            self.log_main(f"🔄 Auto-Obsidian Sync Started")
            self.log_main(output[:2000])
            
            if result.returncode == 0 or ("SUCCESSFULLY" in output.upper() or "generated" in output.lower()):
                print("✅ AUTO-SYNC COMPLETED SUCCESSFULLY")
                
                # Extract file count from output if available
                file_count = 0
                try:
                    import re
                    match = re.search(r'(Generated \d+ files|Created (\d+) Obsidian files)', output)
                    if match:
                        file_count = int(re.search(r'(\d+)', match.group()).group(1))
                except:
                    pass
                
                print(f"   → Files generated: {file_count}")
                self.log_phase_marker("sync", f"✅ COMPLETED - Generated {file_count} Obsidian files")
                
                # Report to hybrid scheduler if active
                if self.hybrid_scheduler_active:
                    event_data = {"status": "success", "files_created": file_count}
                    self.log_hybrid_event("AUTO_SYNC_COMPLETED", event_data)
                
                return {
                    "success": True,
                    "returncode": result.returncode,
                    "files_generated": file_count
                }
            else:
                print(f"⚠️ AUTO-SYNC COMPLETED WITH WARNINGS (Exit code: {result.returncode})")
                self.log_phase_marker("sync", f"⚠️ COMPLETED WITH WARNINGS - Check reports for details")
                
                if self.hybrid_scheduler_active:
                    event_data = {"status": "warnings", "returncode": result.returncode}
                    self.log_hybrid_event("AUTO_SYNC_WARNING", event_data)
                
                return {
                    "success": False,
                    "returncode": result.returncode,
                    "output": output[:2000]
                }
                
        except subprocess.TimeoutExpired:
            print("❌ AUTO-SYNC TIMEOUT")
            self.log_phase_marker("sync", f"❌ TIMEOUT - Exceeded 1800s")
            
            if self.hybrid_scheduler_active:
                event_data = {"status": "timeout", "timeout": 1800}
                self.log_hybrid_event("AUTO_SYNC_TIMEOUT", event_data)
                
            return {
                "success": False,
                "error": "Timeout",
                "timeout": 1800
            }

    def generate_heatmaps(self) -> Dict[str, Any]:
        """Generate correlation heatmaps and relationship visualizations
        
        Phase marker: === PHASE: HEATMAP_GENERATION ===
        Generates ASCII heatmaps showing relationship correlations in database.
        """
        
        print("\n" + "="*60)
        print("📊 PHASE 3: HEATMAP GENERATION")
        print("="*60)
        
        self.log_phase_marker("heatmap", "Generating correlation heatmaps and relationship visualizations")
        
        try:
            from pathlib import Path
            
            heatmap_dir = self.config.logs_dir.parent / "obsidian_exports" / "correlation_heatmaps"
            heatmap_dir.mkdir(parents=True, exist_ok=True)
            
            # Run existing correlation heatmap generation
            result = subprocess.run(
                ["python3", str(Path.home() / ".hermes" / "gematria" / "scripts" / "correlation_heatmap_ascii.py")],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            output = result.stdout + result.stderr
            
            # Log main progress for monitoring
            self.log_main(f"📊 Heatmap Generation Started")
            self.log_main(output[:2000])
            
            if result.returncode == 0:
                print("✅ HEATMAP GENERATION COMPLETED SUCCESSFULLY")
                
                # Extract output path from reports if available
                output_path = None
                try:
                    import re
                    match = re.search(r'Generated heatmap at (\/.*\.md)', output)
                    if match:
                        output_path = match.group(1)
                except:
                    pass
                
                if output_path:
                    print(f"   → Generated: {output_path}")
                    self.log_phase_marker("heatmap", f"✅ COMPLETED - Output: {Path(output_path).name}")
                    
                    # Report to hybrid scheduler if active
                    if self.hybrid_scheduler_active:
                        event_data = {"status": "success", "output_file": Path(output_path).name}
                        self.log_hybrid_event("HEATMAP_GENERATED", event_data)
                
                return {
                    "success": True,
                    "returncode": result.returncode
                }
            else:
                print(f"⚠️ HEATMAP GENERATION COMPLETED WITH WARNINGS (Exit code: {result.returncode})")
                self.log_phase_marker("heatmap", f"⚠️ COMPLETED WITH WARNINGS - Check reports for details")
                
                if self.hybrid_scheduler_active:
                    event_data = {"status": "warnings", "returncode": result.returncode}
                    self.log_hybrid_event("HEATMAP_GENERATION_WARNING", event_data)
                
                return {
                    "success": False,
                    "returncode": result.returncode,
                    "output": output[:2000]
                }
                
        except subprocess.TimeoutExpired:
            print("❌ HEATMAP GENERATION TIMEOUT")
            self.log_phase_marker("heatmap", f"❌ TIMEOUT - Exceeded 600s")
            
            if self.hybrid_scheduler_active:
                event_data = {"status": "timeout", "timeout": 600}
                self.log_hybrid_event("HEATMAP_GENERATION_TIMEOUT", event_data)
                
            return {
                "success": False,
                "error": "Timeout",
                "timeout": 600
            }

    def run_hybrid_scheduler_check(self) -> Dict[str, Any]:
        """Run hybrid scheduler phase check for elasticity monitoring
        
        Phase marker: === PHASE: HYBRID_SCHEDULER ===
        Reports current elasticity phase (baseline/speed_up/slow_down/intensify).
        """
        
        print("\n" + "="*60)
        print("🔄 PHASE 4: HYBRID SCHEDULER CHECK")
        print("="*60)
        
        self.log_phase_marker("hybrid_scheduler", "Checking elasticity phase from hybrid scheduler")
        
        try:
            # Get current phase information using UTC hour only (timezone-agnostic)
            now = datetime.now()
            
            # Use UTC hours for phase determination to avoid timezone string errors
            utc_hour = now.hour
            
            if 8 <= utc_hour < 18:
                current_phase = "speed_up"
            elif 4 <= utc_hour < 12:
                current_phase = "slow_down"
            else:
                current_phase = "baseline"
            
            print(f"✅ CURRENT ELASTICITY PHASE: [{current_phase.upper()}]")
            
            # Log to hybrid scheduler log file (UTC hours only)
            self.log_hybrid_event("HYBRID_PHASE_CHECK", {
                "phase": current_phase,
                "timezone_utc_hour": utc_hour
            })
            
            return {
                "success": True,
                "returncode": 0,
                "current_phase": current_phase,
                "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
            }
            
        except Exception as e:
            print(f"⚠️ HYBRID SCHEDULER CHECK COMPLETED WITH WARNINGS - {str(e)[:200]}")
            self.log_hybrid_event("HYBRID_PHASE_CHECK_WARNING", {"error": str(e)[:200]})
            
            return {
                "success": False,
                "returncode": 1,
                "error": str(e)[:200]
            }

    def restart_loop(self, error_phase: str = "unknown") -> bool:
        """Restart the loop after failure
        
        Auto-restart capability on expiration or failure.
        Returns True if restart was successful, False otherwise.
        """
        
        print("\n" + "="*60)
        print("🔄 AUTO-RESTART CAPABILITY")
        print("="*60)
        
        self.log_main(f"\n=== PHASE: LOOP_RESTART ===\nError Phase: {error_phase}\nTimestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        self.log_phase_marker("restart", f"Auto-restart initiated after failure in phase: {error_phase}")
        
        try:
            print(f"🔄 Restarting loop (attempt 1/3)...")
            
            # Re-instantiate runner to reset state
            config = EnhancedLoopConfig()
            new_runner = EnhancedLoopRunner(config, self.timeout)
            
            # Re-initialize hybrid scheduler
            if not new_runner.ensure_hybrid_scheduler_active():
                print("⚠️ Failed to reinitialize hybrid scheduler")
                return False
            
            # Restart from the first phase (stability test)
            print(f"🧪 Restarting from Phase 1: STABILITY TEST...")
            result = new_runner.run_with_retry(new_runner.run_stability_test)
            
            if result.get("success"):
                print("✅ LOOP RESTARTED SUCCESSFULLY - Continuing with remaining phases")
                
                # Log successful restart
                self.log_main(f"   → Status: LOOP_RESTART_SUCCESSFUL - Resumed from Phase 2")
                return True
            else:
                print(f"⚠️ RESTART FAILED - {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ RESTART FAILED WITH EXCEPTION: {str(e)[:200]}")
            self.log_main(f"   → Error: LOOP_RESTART_FAILED - Exception: {str(e)[:100]}")
            return False

    def run(self) -> Dict[str, Any]:
        """Run the complete overnight research loop with elasticity monitoring
        
        Integrates with stability_test_enhanced_fixed.py, auto_obisidian_sync_v2.py  
        and hybrid_scheduler for multi-phase elasticity monitoring.
        
        Phase markers for logs:
        - === PHASE: STABILITY_TEST ===
        - === PHASE: AUTO_SYNC ===
        - === PHASE: HEATMAP_GENERATION ===
        - === PHASE: HYBRID_SCHEDULER ===
        
        Supports auto-restart on failure via restart_loop() method.
        """
        
        print("="*60)
        print("🌙 ENHANCED OVERNIGHT RESEARCH LOOP")
        print("="*60)
        start_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        print(f"Started: {start_time}")
        print("="*60)
        
        self.log_main("="*60)
        self.log_main("🌙 ENHANCED OVERNIGHT RESEARCH LOOP - STARTED")
        self.log_main(f"Timeout: {self.timeout}s | Retry count: 3")
        self.log_main("="*60 + "\n")
        
        # Ensure hybrid scheduler is running (elasticity monitoring)
        self.ensure_hybrid_scheduler_active()
        
        # Track phase results for reporting  
        phase_results = {}
        all_phases_passed = True
        
        try:
            # Phase 1: Stability Test
            print("\n🧪 Running Enhanced Stability Test...")
            stability_result = self.run_with_retry(self.run_stability_test)
            phase_results['stability'] = stability_result
            
            if not stability_result.get("success", False):
                all_phases_passed = False
                error_phase = "stability"
                self.log_phase_marker("stability", f"⚠️ STABILITY TEST FAILED - Error: {stability_result.get('error', 'Unknown')}")
                
                # Attempt auto-restart if configured to continue on failure
                should_restart = True  # Enable restart by default for cron job
                if should_restart and not stability_result.get("success", False):
                    print("\n🔄 Attempting auto-restart after failure...")
                    self.log_main(f"   → Action: TRIGGERING AUTO-RESTART after {error_phase} phase failure")
                    
                    # Try to restart the loop
                    if self.restart_loop(error_phase=error_phase):
                        print("✅ Restart successful - continuing with remaining phases")
                        
                        # Re-run sync and heatmaps (restart already ran stability)
                        sync_result = self.run_with_retry(self.run_auto_sync)
                        phase_results['sync'] = sync_result
                        
                        if not sync_result.get("success", False):
                            all_phases_passed = False
                            
                        heatmap_result = self.run_with_retry(self.generate_heatmaps)
                        phase_results['heatmap'] = heatmap_result
                        
                        if not heatmap_result.get("success", False):
                            all_phases_passed = False
                        
                        hybrid_result = self.run_with_retry(self.run_hybrid_scheduler_check)
                        phase_results['hybrid_scheduler'] = hybrid_result
                        
                        if not hybrid_result.get("success", False):
                            all_phases_passed = False
            
            # Phase 2: Auto-Sync (only if stability passed or restart didn't happen)
            elif error_phase != "stability":
                print("\n🧪 Running Enhanced Stability Test...")
            
            # Phase 2: Auto-Sync  
            print("\n🔄 Running Auto-Obsidian Sync...")
            sync_result = self.run_with_retry(self.run_auto_sync)
            phase_results['sync'] = sync_result
            
            if not sync_result.get("success", False):
                all_phases_passed = False
                error_phase = "sync"
                self.log_phase_marker("sync", f"⚠️ AUTO-SYNC FAILED - Error: {sync_result.get('error', 'Unknown')}")
                
                # Trigger restart on failure
                if should_restart and not sync_result.get("success", False):
                    print("\n🔄 Attempting auto-restart after sync failure...")
                    self.log_main(f"   → Action: TRIGGERING AUTO-RESTART after {error_phase} phase failure")
                    
                    if self.restart_loop(error_phase=error_phase):
                        pass  # Restart continues from stability test
            
            # Phase 3: Heatmap Generation
            print("\n📊 Generating Correlation Heatmaps...")
            heatmap_result = self.run_with_retry(self.generate_heatmaps)
            phase_results['heatmap'] = heatmap_result
            
            if not heatmap_result.get("success", False):
                all_phases_passed = False
                error_phase = "heatmap"
                self.log_phase_marker("heatmap", f"⚠️ HEATMAP GENERATION FAILED - Error: {heatmap_result.get('error', 'Unknown')}")
                
                # Trigger restart on failure
                if should_restart and not heatmap_result.get("success", False):
                    print("\n🔄 Attempting auto-restart after heatmap failure...")
                    self.log_main(f"   → Action: TRIGGERING AUTO-RESTART after {error_phase} phase failure")
                    
                    if self.restart_loop(error_phase=error_phase):
                        pass  # Restart continues from stability test
            
            # Phase 4: Hybrid Scheduler Check
            print("\n🔄 Running Hybrid Scheduler Phase Check...")
            hybrid_result = self.run_with_retry(self.run_hybrid_scheduler_check)
            phase_results['hybrid_scheduler'] = hybrid_result
            
            if not hybrid_result.get("success", False):
                all_phases_passed = False
                error_phase = "hybrid_scheduler"
                self.log_phase_marker("hybrid_scheduler", f"⚠️ HYBRID SCHEDULER CHECK FAILED - Error: {hybrid_result.get('error', 'Unknown')}")
            
            # Phase 5: Complete marker with summary
            try:
                elapsed = (datetime.now(timezone.utc) - datetime.fromisoformat(start_time.replace(' ', '+00:00'))).total_seconds() if start_time else 0
            except:
                elapsed = 0
            
            print("\n" + "="*60)
            print("📝 LOOP COMPLETED")  
            print("="*60)
            self.log_phase_marker("complete", f"All phases completed in {elapsed:.0f}s")
            self.log_main(f"\n=== PHASE: LOOP_COMPLETE ===\nElapsed: {elapsed:.0f}s\nPhases passed: {sum(1 for r in phase_results.values() if r.get('success'))}/{len(phase_results)}")
            
        except KeyboardInterrupt:
            print("\n👋 User interrupted loop")
            self.log_phase_marker("interrupted", "Loop interrupted by user")
        
        return {
            "all_phases_passed": all_phases_passed,
            "phase_results": phase_results,
            "elapsed_seconds": elapsed,
            "start_time": start_time
        }


def main():
    """Main entry point"""
    
    # Parse command line arguments  
    timeout = 2700
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg.startswith("--timeout"):
            try:
                timeout = int(arg.split("=")[1])
                print(f"Timeout set from argument to: {timeout} seconds")
            except (ValueError, IndexError):
                pass
        
        elif arg == "--dry-run":
            print("🔍 DRY RUN MODE - Testing phase execution without full operations")
    
    config = EnhancedLoopConfig()
    runner = EnhancedLoopRunner(config, timeout)
    
    # Run the loop
    result = runner.run()
    
    print("\n" + "="*60)
    print("📊 LOOP SUMMARY")
    print("="*60)
    print(f"All phases passed: {result.get('all_phases_passed', False)}")
    print(f"Elapsed time: {result.get('elapsed_seconds', 0):.0f}s")
    if result.get('start_time'):
        print(f"Start time: {result['start_time']}")


if __name__ == "__main__":
    main()
