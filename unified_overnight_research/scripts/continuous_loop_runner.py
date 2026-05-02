#!/usr/bin/env python3
"""
Steve's Gematria Unified Overnight Research Pipeline - Continuous Loop Runner v4.0
===============================================================================
Runs in LOOP mode with continuous execution (repeat 9999 for unlimited iterations)
Processes ~30 items per cycle with git version tracking, symbol-keying strategies,
hidden layering detection, and domain correlation analysis.

Core Symbols: 124, 666, 963, 55, 111, 279, 17
Domains: Political, Religious, Economic, Military, Elemental
"""

import sys
import os
import json
import time
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
import shutil

# Add parent to path for imports
sys.path.insert(0, str(Path.home() / ".hermes"))

BASE_DIR = Path.home() / ".hermes" / "gematria"
UNIFIED_OUR_DIR = BASE_DIR / "unified_overnight_research"
DATABASE_PATH = UNIFIED_OUR_DIR / "database" / "gematria_database.json"
OBSIDIAN_EXPORTS = UNIFIED_OUR_DIR / "obsidian_exports"
REPORTS_DIR = UNIFIED_OUR_DIR / "reports"
LOGS_DIR = UNIFIED_OUR_DIR / "logs"
RESEARCH_LOGS_DIR = UNIFIED_OUR_DIR / "research_logs"

class ContinuousLoopRunner:
    """Main continuous loop runner for overnight research with all parallel tasks."""
    
    def __init__(
        self, 
        repeat_count: int = 9999, 
        interval_seconds: int = 600,
        enable_image_seed: bool = False,
        enable_symbol_keying: bool = False,
        enable_git_versioning: bool = False,
        enable_hidden_layering: bool = False,
        enable_domain_correlation: bool = False,
        database_path: Path = DATABASE_PATH,
        image_vault_path: Path = None,
        obsidian_exports: Path = OBSIDIAN_EXPORTS
    ):
        self.repeat_count = repeat_count  # 9999 = continuous/unlimited
        self.interval_seconds = interval_seconds  # Default 10 minutes for loop mode
        self.cycle_count = 0
        self.start_time = datetime.now(timezone.utc)
        self.running = True
        self.processes: Dict[str, subprocess.Popen] = {}
        
        # Feature flags
        self.enable_image_seed = enable_image_seed
        self.enable_symbol_keying = enable_symbol_keying
        self.enable_git_versioning = enable_git_versioning
        self.enable_hidden_layering = enable_hidden_layering
        self.enable_domain_correlation = enable_domain_correlation
        
        # Override paths if provided
        if image_vault_path:
            self.image_vault_path = Path(image_vault_path)
        else:
            self.image_vault_path = Path.home() / "Pictures/Steves gematria/"
        
        if obsidian_exports:
            self.obsidian_exports = Path(obsidian_exports)
        
    def _get_current_utc(self) -> str:
        """Get current UTC timestamp."""
        now = datetime.now(timezone.utc)
        return now.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    def log(self, message: str, level: str = "INFO"):
        """Log with timestamp to console and file."""
        timestamp = self._get_current_utc()
        print(f"[{timestamp}] [{level}] {message}")
        
        # Append to research logs
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        log_path = LOGS_DIR / f"continuous_loop_{self.start_time.strftime('%Y%m%d_%H%M%S')}.log"
        with open(log_path, 'a') as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")
    
    def commit_git_version(self, description: str):
        """Commit database and exports for version tracking."""
        RESEARCH_LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        try:
            # Add changes
            subprocess.run(
                ["git", "-C", str(UNIFIED_OUR_DIR), "add", "."],
                check=True, capture_output=True
            )
            
            # Commit with timestamp and description
            commit_msg = f"[{self._get_current_utc()}] Cycle {self.cycle_count}: {description}"
            subprocess.run(
                ["git", "-C", str(UNIFIED_OUR_DIR), "commit", "-m", commit_msg],
                check=True, capture_output=True
            )
            
            # Log commit hash
            result = subprocess.run(
                ["git", "-C", str(UNIFIED_OUR_DIR), "log", "-1", "--format=%H %s"],
                capture_output=True, text=True
            )
            commit_info = result.stdout.strip() if result.stdout else "N/A"
            
            self.log(f"✅ Git commit: {commit_info}", "COMMIT")
            return commit_info
            
        except subprocess.CalledProcessError as e:
            self.log(f"⚠️  Git commit skipped or failed (git not initialized?): {e}", "WARNING")
        except Exception as e:
            self.log(f"⚠️  Git version tracking error: {str(e)}", "WARNING")
    
    def run_overnight_research_task(self) -> Dict[str, Any]:
        """Run the core overnight research protocol."""
        self.log("=" * 60, "HEADER")
        self.log(f"🌙 STARTING OVERNIGHT RESEARCH CYCLE #{self.cycle_count + 1}", "INFO")
        
        cycle_start = time.time()
        
        try:
            # Create fresh database file if it doesn't exist
            if not DATABASE_PATH.exists():
                DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
                with open(DATABASE_PATH, 'w') as f:
                    json.dump({
                        "version": "4.0",
                        "initialized": True,
                        "analysis_cycles": 0,
                        "symbols_tracked": [],
                        "relationships_tracked": []
                    }, f, indent=2)
            
            # Run overnight research with all features enabled
            self.log("🔍 Running overnight research protocol (web scraping + cross-symbol analysis)...")
            
            result = subprocess.run(
                [sys.executable, str(UNIFIED_OUR_DIR / "unified_engine.py")],
                capture_output=True, text=True, timeout=3600
            )
            
            cycle_duration = time.time() - cycle_start
            
            # Parse output for cycle summary
            output_lines = result.stdout.split('\n') if result.stdout else []
            lines_found = sum(1 for line in output_lines if 'CYCLE COMPLETE' in line or 'COMPLETE' in line)
            
            self.log(f"📊 Cycle duration: {cycle_duration:.2f}s, Files generated: {lines_found}", "INFO")
            
            # Update database with cycle count
            try:
                with open(DATABASE_PATH, 'r') as f:
                    db = json.load(f)
                
                if "analysis_cycles" in db:
                    db["analysis_cycles"] += 1
                    db["last_updated"] = self._get_current_utc()
                    db["symbols_tracked"] = list(set(db.get("symbols_tracked", []) + [124, 666, 963, 55, 111, 279]))
                    with open(DATABASE_PATH, 'w') as f:
                        json.dump(db, f, indent=2)
                else:
                    self.log("⚠️ Database not initialized for cycle counting", "WARNING")
                    
                self.log("💾 Database updated with cycle results", "INFO")
            except Exception as e:
                self.log(f"⚠️ Could not update database: {e}", "ERROR")
                
            return {
                "success": True,
                "duration": cycle_duration,
                "cycle_count": self.cycle_count + 1,
                "files_generated": lines_found
            }
            
        except subprocess.TimeoutExpired:
            self.log("⏰ Overnight research task timed out (>30min), continuing...", "WARNING")
            return {"success": False, "duration": cycle_start - time.time()}
        except Exception as e:
            self.log(f"❌ Overnight research error: {str(e)}", "ERROR")
            return {"success": False, "error": str(e)}
    
    def run_hidden_layering_detection(self) -> Dict[str, Any]:
        """Run hidden layering detection across all symbols."""
        self.log("=" * 60, "SECTION")
        self.log("🔮 PHASE: HIDDEN LAYERING DETECTION", "INFO")
        
        try:
            result = subprocess.run(
                [sys.executable, str(UNIFIED_OUR_DIR / "run_hidden_layering_cycle.py"), "--continuous-loop"],
                capture_output=True, text=True, timeout=600
            )
            
            output_lines = result.stdout.split('\n') if result.stdout else []
            connections_found = sum(1 for line in output_lines if 'connection' in line.lower() or 'layering' in line.lower())
            
            self.log(f"🔗 Hidden layering detection complete. Connections identified: {connections_found}", "INFO")
            return {"success": True, "connections_found": connections_found}
        except subprocess.TimeoutExpired:
            self.log("⏰ Hidden layering task timed out", "WARNING")
            return {"success": False, "timed_out": True}
        except Exception as e:
            self.log(f"❌ Hidden layering error: {str(e)}", "ERROR")
            return {"success": False, "error": str(e)}
    
    def run_domain_correlation_analysis(self) -> Dict[str, Any]:
        """Run domain correlation matrix analysis."""
        self.log("=" * 60, "SECTION")
        self.log("🔬 PHASE: DOMAIN CORRELATION ANALYSIS", "INFO")
        
        try:
            # Create correlation matrix for all symbols and domains
            result = subprocess.run(
                [sys.executable, str(UNIFIED_OUR_DIR / "create_correlation_matrix.py"), "--all-symbols", "--all-domains"],
                capture_output=True, text=True, timeout=1800
            )
            
            output_lines = result.stdout.split('\n') if result.stdout else []
            matrices_created = sum(1 for line in output_lines if 'matrix' in line.lower() or 'created' in line.lower())
            
            self.log(f"📊 Domain correlation matrices created: {matrices_created}", "INFO")
            return {"success": True, "matrices_created": matrices_created}
        except subprocess.TimeoutExpired:
            self.log("⏰ Correlation analysis timed out", "WARNING")
            return {"success": False, "timed_out": True}
        except Exception as e:
            self.log(f"❌ Correlation analysis error: {str(e)}", "ERROR")
            return {"success": False, "error": str(e)}
    
    def run_image_seed_analysis(self) -> Dict[str, Any]:
        """Run image-seed bootstrapping from vault."""
        self.log("=" * 60, "SECTION")
        self.log("🖼️  PHASE: IMAGE-SEED ANALYSIS", "INFO")
        
        try:
            # Check if image vault has files
            # Use correct path for image vault (handles space in directory name)
            image_vault = Path.home() / "Pictures" / "Steves gematria"
            
            if image_vault.exists():
                images = list(image_vault.glob("*.*"))
                self.log(f"📂 Image seed analysis bootstrapping from {len(images)} images...", "INFO")
                
                result = subprocess.run(
                    [sys.executable, str(UNIFIED_OUR_DIR / "image_seed_analyzer.py"), "--continuous-mode"],
                    capture_output=True, text=True, timeout=600
                )
                
                return {"success": True, "image_count": len(images)}
            else:
                self.log("🖼️  Image vault not found - skipping image seed analysis", "INFO")
                return {"success": True, "image_count": 0}
        except Exception as e:
            self.log(f"❌ Image seed error: {str(e)}", "ERROR")
            return {"success": False, "error": str(e)}
    
    def run_push_components(self) -> Dict[str, Any]:
        """Push components to Tolaria vault."""
        self.log("=" * 60, "SECTION")
        self.log("📤 PHASE: PUSH COMPONENTS TO TOLARIA", "INFO")
        
        try:
            result = subprocess.run(
                [sys.executable, str(UNIFIED_OUR_DIR / "push_components.py"), "--continuous-loop"],
                capture_output=True, text=True, timeout=600
            )
            
            output_lines = result.stdout.split('\n') if result.stdout else []
            components_pushed = sum(1 for line in output_lines if 'push' in line.lower() or 'created' in line.lower())
            
            self.log(f"📦 Components pushed to Tolaria: {components_pushed}", "INFO")
            return {"success": True, "components_pushed": components_pushed}
        except subprocess.TimeoutExpired:
            self.log("⏰ Push components task timed out", "WARNING")
            return {"success": False, "timed_out": True}
        except Exception as e:
            self.log(f"❌ Push components error: {str(e)}", "ERROR")
            return {"success": False, "error": str(e)}
    
    def run_composer(self) -> Dict[str, Any]:
        """Run composer for domain integration synthesis."""
        self.log("=" * 60, "SECTION")
        self.log("🧩 PHASE: COMPOSER - DOMAIN INTEGRATION SYNTHESIS", "INFO")
        
        try:
            result = subprocess.run(
                [sys.executable, str(UNIFIED_OUR_DIR / "composer.py"), "--mode", "overnight_loop"],
                capture_output=True, text=True, timeout=600
            )
            
            output_lines = result.stdout.split('\n') if result.stdout else []
            integrations_created = sum(1 for line in output_lines if 'integration' in line.lower() or 'synthesis' in line.lower())
            
            self.log(f"🎨 Domain integrations synthesized: {integrations_created}", "INFO")
            return {"success": True, "integrations_created": integrations_created}
        except subprocess.TimeoutExpired:
            self.log("⏰ Composer task timed out", "WARNING")
            return {"success": False, "timed_out": True}
        except Exception as e:
            self.log(f"❌ Composer error: {str(e)}", "ERROR")
            return {"success": False, "error": str(e)}
    
    def run_advanced_overnight_loop(self) -> Dict[str, Any]:
        """Run advanced overnight loop with all features."""
        self.log("=" * 60, "SECTION")
        self.log("🚀 PHASE: ADVANCED OVERNIGHT LOOP", "INFO")
        
        try:
            result = subprocess.run(
                [sys.executable, str(UNIFIED_OUR_DIR / "advanced_overnight_loop.py"), "--continuous-loop"],
                capture_output=True, text=True, timeout=1800
            )
            
            output_lines = result.stdout.split('\n') if result.stdout else []
            research_cycles = sum(1 for line in output_lines if 'cycle' in line.lower() and ('complete' in line.lower() or 'completed' in line.lower()))
            
            self.log(f"🔬 Advanced loop completed cycles: {research_cycles}", "INFO")
            return {"success": True, "cycles_completed": research_cycles}
        except subprocess.TimeoutExpired:
            self.log("⏰ Advanced overnight loop timed out", "WARNING")
            return {"success": False, "timed_out": True}
        except Exception as e:
            self.log(f"❌ Advanced overnight loop error: {str(e)}", "ERROR")
            return {"success": False, "error": str(e)}
    
    def run_loop_cycle(self) -> Dict[str, Any]:
        """Run a single complete cycle with all parallel tasks."""
        self.log("=" * 80, "HEADER")
        self.log(f"🔄 OVERNIGHT RESEARCH PIPELINE - CYCLE #{self.cycle_count + 1}", "INFO")
        self.log("=" * 80)
        
        cycle_start = time.time()
        cycle_tasks: List[Dict[str, Any]] = []
        
        # Run core overnight research (main task)
        our_result = self.run_overnight_research_task()
        cycle_tasks.append({"task": "Overnight Research", "result": our_result})
        
        # Run hidden layering detection (parallel)
        hl_result = self.run_hidden_layering_detection()
        cycle_tasks.append({"task": "Hidden Layering Detection", "result": hl_result})
        
        # Run domain correlation analysis (parallel)
        ca_result = self.run_domain_correlation_analysis()
        cycle_tasks.append({"task": "Domain Correlation Analysis", "result": ca_result})
        
        # Run image seed analysis (parallel)
        isa_result = self.run_image_seed_analysis()
        cycle_tasks.append({"task": "Image-Seed Analysis", "result": isa_result})
        
        # Run push components (parallel)
        pc_result = self.run_push_components()
        cycle_tasks.append({"task": "Push Components to Tolaria", "result": pc_result})
        
        # Run composer synthesis (parallel)
        comp_result = self.run_composer()
        cycle_tasks.append({"task": "Composer Synthesis", "result": comp_result})
        
        # Run advanced overnight loop (parallel)
        aol_result = self.run_advanced_overnight_loop()
        cycle_tasks.append({"task": "Advanced Overnight Loop", "result": aol_result})
        
        # Git version tracking after each cycle
        if any(r.get("success") for r in [our_result, ca_result]):
            self.commit_git_version(f"Cycle {self.cycle_count + 1}: Web research + hidden layering detection")
        
        cycle_duration = time.time() - cycle_start
        
        # Summary - handle both dict and string return values for success counting
        successful_count = 0
        for t in cycle_tasks:
            result = t["result"]
            if isinstance(result, dict):
                if result.get("success"):
                    successful_count += 1
            else:
                # String result is not a success
                pass
        
        successful_tasks = successful_count
        self.log(f"\n📊 CYCLE #{self.cycle_count + 1} SUMMARY", "INFO")
        self.log(f"✅ Successful tasks: {successful_tasks}/{len(cycle_tasks)}", "INFO")
        self.log(f"⏱️  Cycle duration: {cycle_duration:.2f}s", "INFO")
        
        # Print task results - handle both dict and string return values
        for task_name, result in cycle_tasks:
            # Ensure we have a proper dictionary
            if isinstance(result, str):
                status = "⚠️"
                details = result[:60] if result else ""
                self.log(f"   {status} {task_name}: {details}", "INFO")
            else:
                status = "✅" if result.get("success") else "⚠️ "
                connections = result.get('connections_found', 0) if 'connections_found' in result else ''
                details = f"({connections} connections)" if connections else ""
                self.log(f"   {status} {task_name}{details}", "INFO")
        
        return {"cycle_duration": cycle_duration, "successful_tasks": successful_tasks}
    
    def run_continuous_loop(self):
        """Main loop for continuous overnight research execution."""
        print("\n" + "=" * 80)
        print("🌉 STEVE'S GEMATRIA UNIFIED OVERNIGHT RESEARCH PIPELINE")
        print("=" * 80)
        print(f"Mode: CONTINUOUS LOOP (repeat={self.repeat_count} times)")
        print(f"Interval: {self.interval_seconds/3600:.1f} hours between cycles")
        print(f"Start Time: {self._get_current_utc()}")
        print("=" * 80 + "\n")
        
        while self.running and (self.repeat_count == 9999 or self.cycle_count < self.repeat_count):
            try:
                self.cycle_count += 1
                self.run_loop_cycle()
                
                if self.repeat_count != 9999 and self.cycle_count >= self.repeat_count:
                    self.log(f"🏁 Loop completed after {self.cycle_count} cycles", "INFO")
                    break
                    
            except KeyboardInterrupt:
                self.log("⚠️  Manual interrupt received - stopping loop", "WARNING")
                break
            
            if self.repeat_count != 9999 and self.cycle_count >= self.repeat_count:
                break
                
        print("\n" + "=" * 80)
        print(f"🏁 STEVE'S GEMATRIA OVERNIGHT RESEARCH PIPELINE COMPLETE")
        print("=" * 80)


def main():
    """Main entry point for continuous loop runner."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Steve's Gematria Unified Overnight Research Pipeline - Continuous Loop Mode"
    )
    parser.add_argument("--repeat", type=int, default=9999, help="Number of iterations (9999=continuous)")
    parser.add_argument("--interval", type=str, default="10m", help="Interval between cycles (e.g., '10m', '3h')")
    parser.add_argument("--image-seed", action="store_true", help="Enable image-seed bootstrapping from vault")
    parser.add_argument("--symbol-keying-strategies", action="store_true", help="Apply discovered symbol-keying strategies")
    parser.add_argument("--git-version-tracking", action="store_true", help="Enable git version tracking for crash recovery")
    parser.add_argument("--hidden-layering-detection", action="store_true", help="Detect hidden connections across symbols")
    parser.add_argument("--domain-correlation", action="store_true", help="Track domain correlations in analysis")
    parser.add_argument("--base-dir", type=str, default=str(BASE_DIR), help="Base working directory")
    parser.add_argument("--database", type=str, default=str(DATABASE_PATH), help="Database file path")
    parser.add_argument("--image-vault", type=str, default=str(Path.home() / "Pictures/Steves gematria/"), help="Image vault path")
    parser.add_argument("--obsidian-export", type=str, default=str(OBSIDIAN_EXPORTS), help="Obsidian exports directory")
    
    args = parser.parse_args()
    
    # Parse interval to seconds
    interval_str = args.interval.lower().replace("h", " hours").replace("m", " minutes").replace("s", " seconds")
    try:
        if " hour" in interval_str:
            interval_seconds = int(float(interval_str.replace(" hour", "")) * 3600)
        elif " minute" in interval_str:
            interval_seconds = int(float(interval_str.replace(" minute", "")) * 60)
        elif " second" in interval_str:
            interval_seconds = int(float(interval_str.replace(" second", "")))
        else:
            # Try to parse as hours by default
            interval_seconds = int(float(interval_str.replace(" hours", "").replace(" hour", "")) * 3600)
    except ValueError:
        interval_seconds = 600  # Default 10 minutes for continuous loop
    
    runner = ContinuousLoopRunner(
        repeat_count=args.repeat,
        interval_seconds=interval_seconds
    )
    
    # Set configuration based on flags
    runner.enable_image_seed = args.image_seed
    runner.enable_symbol_keying = args.symbol_keying_strategies
    runner.enable_git_versioning = args.git_version_tracking
    runner.enable_hidden_layering = args.hidden_layering_detection
    runner.enable_domain_correlation = args.domain_correlation
    
    # Override paths if provided
    if args.database:
        runner.database_path = Path(args.database)
    if args.image_vault:
        runner.image_vault_path = Path(args.image_vault)
    if args.obsidian_export:
        runner.obsidian_exports = Path(args.obsidian_export)
    
    print(f"🌙 STEVE'S GEMATRIA OVERNIGHT RESEARCH PIPELINE - LOOP MODE")
    print("=" * 70)
    print(f"🔁 Repeat count: {args.repeat}")
    print(f"⏱️ Interval: {interval_seconds/60:.1f} minutes per cycle")
    if args.image_seed:
        print("⭐ Image-seed bootstrapping: ENABLED")
    if args.symbol_keying_strategies:
        print("🔑 Symbol-keying strategies: ENABLED")
    if args.git_version_tracking:
        print("💾 Git version tracking: ENABLED")
    if args.hidden_layering_detection:
        print("🔗 Hidden layering detection: ENABLED")
    if args.domain_correlation:
        print("📊 Domain correlation tracking: ENABLED")
    print("=" * 70)
    print("Press Ctrl+C to stop the loop\n")
    
    runner.run_continuous_loop()


if __name__ == "__main__":
    main()
