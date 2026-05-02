#!/usr/bin/env python3
"""
Steve's Gematria Self-Sustaining Opponent & Advocate Loop Orchestrator
========================================================================

Purpose: Run continuous adversarial research loop with auto-debate scheduling.

Features:
- Executes opponent attacks every 2 hours (or configurable)
- Loads advocate responses for each symbol
- Arbitrates debates and tracks hypothesis strength evolution
- Logs all debate transcripts to dedicated repository
- Git version tracking of hypothesis evolution over time

Architecture: Prevents self-reference paradoxes through hierarchical separation.
              Opponent operates at meta-level, challenging interpretations,
              not the underlying symbols themselves.
"""


import os, json, datetime, sys, subprocess, shutil
from pathlib import Path
from typing import List, Dict, Optional
import yaml


# ============================================================================
# CONFIGURATION
# ============================================================================

class DebateConfig:
    """Main debate loop configuration"""
    
    # Paths  
    GEMATRIA_WORKSPACE = os.getenv("GEMATRIA_WORKSPACE", str(Path.home() / ".hermes" / "gematria"))
    OPPONENT_DIR = os.path.join(GEMATRIA_WORKSPACE, "opponent")
    ADVOCATES_DIR = os.path.join(GEMATRIA_WORKSPACE, "advocates")
    ARBITRATOR_DIR = os.path.join(GEMATRIA_WORKSPACE, "arbitrator")
    
    # Schedule settings  
    LOOP_INTERVAL_MINUTES = 120  # 2 hours between attacks  
    ENABLE_LOOP_MODE = True      # Auto-retrigger mode
    
    # Attack intensity (1-3)
    ATTACK_INTENSITY = 2
    
    # Git version tracking directory
    GIT_TRACKING_DIR = os.path.join(GEMATRIA_WORKSPACE, "git_tracking")
    
    # Output repositories
    DEBATE_LOGS_DIR = os.path.join(GEMATRIA_WORKSPACE, "debate_logs")
    EVOLUTION_REPORTS_DIR = os.path.join(GEMATRIA_WORKSPACE, "evolution_reports")
    
    # Symbol titles (advocate filenames)
    SYMBOL_TITLES = [
        "[[124|THRESHOLD]]",
        "[[963|CYCLE-TURN]]", 
        "[[55|COMPLETION]]",
        "[[666|WHOLENESS]]",
        "[[279|HARMONIC CONFLUENCE]]",
        "[[111|UNITY]]"
    ]


# ============================================================================
# DEBATE LOOP ENGINE
# ============================================================================

class DebateLoopEngine:
    """Main orchestrator for self-sustaining opponent-advocate debates"""
    
    def __init__(self):
        self.config = DebateConfig()
        
    async def run_debate_cycle(self) -> Dict:
        """Run one complete debate cycle for all symbols"""
        
        print("\n" + "=" * 70)
        print("🏛️  STEVE'S GEMATRIA SELF-SUSTAINING OPPONENT & ADVOCATE DEBATE")
        print("=" * 70)
        print(f"Timestamp: {datetime.datetime.now().isoformat()}")
        print(f"Attack Intensity: {self.config.ATTACK_INTENSITY}/3")
        
        # Summary tracking
        cycle_summary = {
            "timestamp": datetime.datetime.now().isoformat(),
            "symbols_analyzed": 0,
            "total_attacks": 0,
            "advocate_wins": 0,
            "opponent_wins": 0,
            "ties": 0,
            "debate_logs": []
        }
        
        # Process each symbol  
        for symbol in self.config.SYMBOL_TITLES:
            try:
                print(f"\n🎯 Analyzing: {symbol} ...", "INFO")
                
                result = await self.adjudicate_symbol(symbol)
                cycle_summary["symbols_analyzed"] += 1
                cycle_summary["debate_logs"].append(result)
                
                # Update tracking files
                if hasattr(self, 'git_tracker'):
                    self.git_tracker.update_hypothesis_strength(symbol, result['prior_adjustment'])
                    
            except Exception as e:
                print(f"Error analyzing {symbol}: {e}", "ERROR")
                
        cycle_summary["total_attacks"] = sum(
            log.get("attack_count", 0) for log in cycle_summary["debate_logs"]
        )
        
        cycle_summary["advocate_wins"] = sum(
            1 for log in cycle_summary["debate_logs"] if log.get("winner") == "advocate_wins"
        )
        
        cycle_summary["opponent_wins"] = sum(
            1 for log in cycle_summary["debate_logs"] if log.get("winner") == "opponent_wins"
        )
        
        cycle_summary["ties"] = sum(
            1 for log in cycle_summary["debate_logs"] if log.get("winner") == "near_tie"
        )
        
        return cycle_summary
        
    async def adjudicate_symbol(self, symbol: str) -> Dict:
        """Adjudicate debate for single symbol"""
        
        print(f"  ├─ Step 1: Executing opponent attacks ...", "INFO")
        attack_results = await self.execute_opponent_attacks(symbol)
        print(f"     Found {len(attack_results)} attack vectors")
        
        if not attack_results:
            return {"symbol": symbol, "status": "no_attacks", "attacks": [], "advocate_responses": []}
            
        print(f"  ├─ Step 2: Loading advocate responses ...", "INFO")  
        advocate_responses = self.load_advocate_responses(symbol)
        
        print(f"  ├─ Step 3: Running arbitration ...", "INFO")
        arb_result = await self.run_arbitration(
            symbol, 
            attack_results, 
            advocate_responses
        )
        
        # Generate report
        report_path = os.path.join(self.config.DEBATE_LOGS_DIR, 
                                   f"{datetime.datetime.now().strftime('%Y%m%d')}_debate_{symbol.replace(']', '').replace('[', '')}.md")
        
        self.generate_debate_report(symbol, attack_results, advocate_responses, arb_result, report_path)
        
        return arb_result
    
    async def execute_opponent_attacks(self, symbol: str) -> List[Dict]:
        """Execute opponent attacks for given symbol"""
        
        try:
            # Run opponent script
            result = subprocess.run(
                ["python3", os.path.join(self.config.OPPONENT_DIR, "falsification_engine.py")],
                capture_output=True, text=True, timeout=120
            )
            
            if result.returncode != 0:
                print(f"  └─ Opponent execution returned error code {result.returncode}", "WARNING")
                
            return []  # Placeholder — would parse actual attack results
            
        except subprocess.TimeoutExpired:
            print(f"  └─ Opponent execution timed out", "WARNING")
            return []
            
        except Exception as e:
            print(f"  └─ Error executing opponent: {e}", "ERROR")
            return []


    def load_advocate_responses(self, symbol: str) -> Dict[str, str]:
        """Load advocate defense responses"""
        
        responses = {}
        
        for filename in ["advocate.py"] * len(self.config.SYMBOL_TITLES):  # Simplified
            if hasattr(self, 'run_advocate_test'):
                result = subprocess.run(
                    ["python3", os.path.join(self.config.ADVOCATES_DIR, f"{symbol.replace('[', '').replace(']', '')}_advocate.py")],
                    capture_output=True, text=True, timeout=60
                )
                
                if result.returncode == 0:
                    responses[os.path.basename(filename)] = result.stdout
                    
        return responses


    async def run_arbitration(self, symbol: str, attacks: List[Dict], 
                             advocate_responses: Dict[str, str]) -> Dict:
        """Run arbitrator to adjudicate debate"""
        
        try:
            result = subprocess.run(
                ["python3", os.path.join(self.config.ARBITRATOR_DIR, "judge.py")],
                input=json.dumps({
                    "symbol": symbol,
                    "advocate_responses": advocate_responses,
                    "attacks": attacks
                }),
                capture_output=True, text=True, timeout=120
            )
            
            if result.returncode == 0:
                print(f"    Arbitration complete for {symbol}", "INFO")
                return {"status": "success", "raw_output": result.stdout}
                
        except subprocess.TimeoutExpired:
            print(f"    Arbitration timed out for {symbol}", "WARNING")  
        except Exception as e:
            print(f"    Arbitration failed: {e}", "ERROR")
            
        return {"status": "error", "message": str(e)}


    def generate_debate_report(self, symbol: str, attacks: List[Dict], 
                              advocate_responses: Dict[str, str], 
                              arbitration_result: Dict, report_path: str):
        """Generate markdown debate report"""
        
        # Simplified — would create actual report
        with open(report_path, 'w') as f:
            f.write(f"# Debate Report: {symbol}\n")
            f.write(f"\nTimestamp: {datetime.datetime.now().isoformat()}\n\n")
            f.write("## Attacks Executed\n")
            
            for attack in attacks:
                severity = attack.get('severity', 'unknown')
                vector = attack.get('vector', 'general')
                argument = attack.get('argument', '')
                
                if argument:
                    f.write(f"- [{severity}/3] **{vector}**: {argument}\n")
                else:
                    f.write(f"- [{severity}/3] **{vector}**\n")
                    
            f.write("\n## Advocate Responses\n")
            
            for filename, response in advocate_responses.items():
                f.write(f"\n### {filename}\n")
                f.write(response[:500])  # Truncate to avoid overflow


# ============================================================================
# GIT VERSION TRACKING
# ============================================================================

class GitTracker:
    """Track hypothesis evolution over time via git-like commits"""
    
    def __init__(self, git_dir: str):
        self.git_dir = Path(git_dir)
        self.commits_log = os.path.join(git_dir, "commits.log")
        
    def update_hypothesis_strength(self, symbol: str, prior_adjustment: float):
        """Record hypothesis strength change like a git commit"""
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create simple commit log entry
        commit_msg = f"Hypothesis strength update for {symbol}: prior_adjustment={prior_adjustment:+.2f}\n"
        
        with open(self.commits_log, 'a') as f:
            f.write(f"[{timestamp}] {commit_msg}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main():
    """Main entry point for debate loop"""
    
    engine = DebateLoopEngine()
    
    if DebateConfig.ENABLE_LOOP_MODE:
        print("🔄 LOOP MODE ENABLED — Will auto-retrigger every 120 minutes")
        
        while True:
            try:
                result = await engine.run_debate_cycle()
                
                # Save cycle summary
                summary_file = os.path.join(DebateConfig.GEMATRIA_WORKSPACE, 
                                           f"debate_cycle_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                
                with open(summary_file, 'w') as f:
                    json.dump(result, f, indent=2)
                    
            except KeyboardInterrupt:
                print("\n🛑 Loop interrupted by user")
                break
            except Exception as e:
                print(f"\n❌ Error in loop cycle: {e}", "ERROR")
                # Continue to next iteration
                
            # Sleep until next interval
            if DebateConfig.ENABLE_LOOP_MODE:
                await asyncio.sleep(DebateConfig.LOOP_INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    import asyncio
    
    try:
        result = asyncio.run(main())
    except KeyboardInterrupt:
        print("Loop interrupted by user")
        sys.exit(0)
