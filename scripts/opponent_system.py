#!/usr/bin/env python3
"""
Self-Sustaining Opponent System Orchestrator (Debate Loop)

This script coordinates the adversarial research system:
1. Initializes all advocates for core symbols  
2. Runs falsification engine periodically
3. Arbitrates debates between advocates and opponent
4. Updates hypothesis strength with Bayesian-like updating
5. Reports status with ASCII heat-scale visualization

Architecture Layers:
- Layer 2 (Domain): Specific symbol/hypothesis claims (advocates)
- Layer 3 (Meta)  : Opponent tests framework integrity (falsification engine)
- Layer 4 (Arbitration): Judge evaluates and updates hypothesis strength

Core Features:
- Automatic debate loop with configurable intervals  
- Self-sustaining: runs continuously until interrupted
- Scientific rigor enforced via Domain Law axioms
- Visualization: ASCII heat scale encoding (░ ▒ ▓ █ . O)
- Paradox avoidance: Opponent operates at meta-level (Layer 3) vs hypothesis claims (Layer 2)

Domain Law Axioms (Formal):
1. Conservation Hypothesis: Explainable origin/transformation for all claims
2. Simplicity Hypothesis: Occam's Razor - prefer fewer assumptions
3. Consistency Hypothesis: Same symbols behave consistently across contexts
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass 
class SystemState:
    """Tracks the current state of all hypotheses."""
    hypotheses: Dict[str, Dict[str, any]] = field(default_factory=dict)
    
    def get_hypothesis(self, name: str) -> Optional[Dict]:
        return self.hypotheses.get(name)
        
    def set_hypothesis(self, name: str, data: Dict):
        self.hypotheses[name] = data


@dataclass
class DebateRound:
    """Records a single debate round."""
    round_number: int
    timestamp: str
    hypothesis_name: str
    advocate_confidence: float
    opponent_confidence: float
    arbitrator_decision: Dict[str, any]
    
    def to_dict(self):
        return self.__dict__


class DebateLoopOrchestrator:
    """
    Main orchestrator for the adversarial research system.
    
    Coordinates advocates and opponent in an automated debate loop that 
    continuously tests hypotheses against counter-evidence while enforcing 
    Domain Law axioms to maintain scientific integrity.
    """
    
    def __init__(self, state_file: Optional[str] = None):
        self.state = SystemState()
        self.state_file = state_file
        
        # Initialize advocates for all 6 core symbols
        self.advocates: Dict[str, Any] = {}
        
        # Initialize falsification engine (opponent)
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from opponents.falsification_engine import FalsificationEngine
            self.opponent = FalsificationEngine()
            if hasattr(self.opponent, 'initialize'):
                self.opponent.initialize()  # Initialize synchronously in __init__
        except ImportError as e:
            print(f"⚠️  Could not load opponent module: {e}")
            self.opponent = None
        
        # Initialize arbitrator
        from arbitrator.judge import Arbitrator
        self.arbitrator = Arbitrator()
        
        # Load or initialize state
        self._load_state()
        
    def _load_state(self):
        """Load state from file if exists, otherwise start fresh."""
        if self.state_file and os.path.exists(self.state_file):
            try:
                with open(self.state_file) as f:
                    saved = json.load(f)
                for name, data in saved.get("hypotheses", {}).items():
                    self.state.hypotheses[name] = data
                print(f"✓ Loaded state from {self.state_file}")
            except Exception as e:
                print(f"⚠️  Could not load state file: {e}")
        else:
            print("ℹ️  Starting with fresh state (no previous data)")
            
    def _save_state(self):
        """Save state to file if path provided."""
        if self.state_file:
            try:
                with open(self.state_file, 'w') as f:
                    json.dump({
                        "hypotheses": {k: v for k, v in self.state.hypotheses.items()}
                    }, f, indent=2)
                print(f"✓ Saved state to {self.state_file}")
            except Exception as e:
                print(f"⚠️  Could not save state: {e}")
                
    async def initialize_advocates(self):
        """Load all advocate modules."""
        advocates_dir = Path(__file__).parent / "advocates"
        
        for script in advocates_dir.glob("symbol_*.py"):
            try:
                module_name = script.stem  # e.g., "symbol_124"
                
                # Import the advocate class dynamically
                module = __import__(f"advocates.{module_name}", fromlist=[""])
                
                # The class is named SymbolXXXAdvocate (e.g., Symbol124Advocate)
                # Extract the numeric part and reconstruct the full class name
                if module_name.startswith("symbol_"):
                    num_part = module_name.replace("symbol_", "")
                    class_name = f"Symbol{num_part}Advocate"
                else:
                    class_name = f"Symbol{module_name}Advocate"
                
                advocate_class = getattr(module, class_name)
            except Exception as e:
                print(f"⚠️  Could not load advocate {script}: {e}")
                continue
                
            # Instantiate and store
            try:
                self.advocates[module_name] = advocate_class()
                print(f"✓ Loaded advocate: {module_name.replace('symbol_', '')}")
            except Exception as e:
                print(f"⚠️  Could not instantiate advocate {script}: {e}")
        
        if not self.advocates:
            raise RuntimeError("No advocates loaded!")
        
        # Build reverse mapping from hypothesis name to advocate instance
        self.hypothesis_to_advocate = {}
        for mod_name, advocate in self.advocates.items():
            hypothesis_name = advocate.hypothesis.get("name", "")
            if hypothesis_name:
                self.hypothesis_to_advocate[hypothesis_name] = advocate
            
    async def run_single_round(self, hypothesis_name: str) -> DebateRound:
        """Run a single debate round for one hypothesis."""
        print(f"\n{'='*60}")
        print(f"🔊 DEBATE ROUND FOR: {hypothesis_name.replace('_', ' ').title()}")
        print(f"{'='*60}\n")
        
        # Round 1: Advocate presents argument
        print("🗣️  PHASE 1 - ADVOCATE ARGUMENT:")
        
        # Get advocate from mapping
        advocate = self.hypothesis_to_advocate.get(hypothesis_name)
        
        if not advocate:
            raise ValueError(f"No advocate loaded for {hypothesis_name}")
            
        argument = await advocate.make_argument()
        
        # Update state with current advocacy strength
        current_state = self.state.get_hypothesis(hypothesis_name) or {}
        current_state["advocacy_confidence"] = argument.get("confidence_estimate", 0.7)
        current_state["evidence_strength"] = argument.get("evidence_strength", 0.5)
        current_state["last_argument"] = datetime.utcnow().isoformat()
        
        self.state.set_hypothesis(hypothesis_name, current_state)
        
        # Store in arbitrator
        await self.arbitrator.receive_argument(hypothesis_name, argument)
        
        print(f"   → Advocate confidence: {argument.get('confidence_estimate', 0):.1%}")
        print(f"   → Evidence strength avg: {argument.get('evidence_strength', 0):.2%}")
        print(f"   → Domain Laws Compliance:")
        for law in argument.get("domain_law_compliance", []):
            heat = "██" if law["status"] == "compliant" else "░░"
            print(f"      [{heat}] {law['law']}: {law['note']}")
        
        # Round 2: Opponent issues challenge  
        print("\n⚠️  PHASE 2 - OPPONENT CHALLENGE:")
        if self.opponent:
            counter_hypothesis = await self.opponent.generate_counter_hypothesis(
                hypothesis_name, 
                "conservation"
            )
            
            challenge_data = {
                "hypothesis_name": hypothesis_name,
                "law_violated": "conservation",
                "evidence_summary": f"Hypothesis needs stronger evidence against {counter_hypothesis or 'alternative explanations'}",
                "confidence_estimate": 0.6 + random.uniform(-0.1, 0.2),
                "counter_hypothesis": counter_hypothesis
            }
            
            await self.arbitrator.receive_challenge(hypothesis_name, challenge_data)
            print(f"   → Challenge: {challenge_data['evidence_summary'][:80]}...")
        else:
            challenge_data = {
                "hypothesis_name": hypothesis_name,
                "law_violated": None,
                "evidence_summary": "No opponent available",
                "confidence_estimate": 0.3
            }
            await self.arbitrator.receive_challenge(hypothesis_name, challenge_data)
            
        # Round 3: Arbitration decision
        print("\n⚖️  PHASE 3 - ARBITRATION DECISION:")
        result = self.arbitrator.make_arbitration_decision(hypothesis_name)
        
        current_state["arbitration_result"] = result.to_dict()
        self.state.set_hypothesis(hypothesis_name, current_state)
        
        # Visualize status - use to_dict() attributes which should be consistent
        result_dict = result.to_dict()
        net_strength = result_dict.get("net_strength", 0)
        net_heat = result_dict.get("net_heat", "░░")
        advocacy_score = result_dict.get("advocacy_score", 0)
        opposition_score = result_dict.get("opposition_score", 0)
        domain_law_status = result_dict.get("domain_law_status", "INDETERMINATE")
        evidence_quality = result_dict.get("evidence_quality", "UNKNOWN")
        recommendation = result_dict.get("recommendation", "No change recommended")
        
        net_str = f"Net: [{net_heat}] {int(net_strength * 100):3d}%"
        print(f"   [█] Advocacy Score:  {int(advocacy_score * 100)}%")
        print(f"   [░] Opposition Score: {int(opposition_score * 100)}%")
        print(f"   [{net_str}]")
        print(f"   Domain Law Status: {domain_law_status.replace('_', ' ').title()}")
        print(f"   Evidence Quality:  {evidence_quality.replace('_', ' ').title()}")
        print(f"   → Recommendation:  {recommendation.replace('_', ' ').title()}")
        print()
        
        return DebateRound(
            round_number=1,
            timestamp=datetime.utcnow().isoformat(),
            hypothesis_name=hypothesis_name,
            advocate_confidence=argument.get("confidence_estimate", 0.7),
            opponent_confidence=challenge_data.get("confidence_estimate", 0.3),
            arbitrator_decision=result.to_dict()
        )
        
    async def run_all_hypotheses(self):
        """Run debate round for all hypotheses."""
        if not self.state.hypotheses and not self.hypothesis_to_advocate:
            # Auto-initialize with all core symbols
            self._initialize_core_hypotheses()
        
        # If we have a hypothesis-to-advocate mapping, iterate over that
        if self.hypothesis_to_advocate:
            for hypothesis_name in list(self.hypothesis_to_advocate.keys()):
                await self.run_single_round(hypothesis_name)
        else:
            # Fall back to iterating state keys (for initialization runs)
            hypothesis_names = list(self.state.hypotheses.keys())
            for name in hypothesis_names:
                await self.run_single_round(name)
            
    def _initialize_core_hypotheses(self):
        """Initialize state with all 6 core symbols."""
        core_symbols = {
            "124": {"name": "Universal Threshold", "alias": "Bridge"},
            "666": {"name": "Completion / Wholeness", "alias": "Cycle Finisher"}, 
            "963": {"name": "Cycle Turning Variants", "alias": "Harmony Bridge"},
            "55": {"name": "Vessel / Holds The Fire", "alias": "Fire Container"},
            "17": {"name": "Harmony Integration", "alias": "Balance Point"},
            "279": {"name": "Cycle Turning Variants", "alias": "Resolution Variant"}
        }
        
        for key, info in core_symbols.items():
            self.state.hypotheses[key] = {
                "name": info["name"],
                "alias": info["alias"],
                "advocacy_confidence": 0.75,
                "evidence_strength": 0.6,
                "arbitration_result": None,
                "init_timestamp": datetime.utcnow().isoformat()
            }
            
        print(f"✓ Initialized {len(core_symbols)} core hypotheses")
        
    async def run_periodic_opponent_check(self):
        """Run opponent's periodic self-test."""
        if self.opponent:
            try:
                result = await self.opponent.periodic_self_test()
                if result.get("self_test_complete"):
                    print(f"\n🔍 OPPONENT SELF-TEST COMPLETE:")
                    print(f"   Suspicious patterns detected: {result.get('suspicious_patterns', []) or 'None'}")
            except Exception as e:
                print(f"⚠️  Opponent self-test failed: {e}")
                
    async def display_system_status(self):
        """Display current state of all hypotheses with heat-scale visualization."""
        print("\n" + "="*60)
        print("📊 SYSTEM STATUS OVERVIEW")  
        print("="*60)
        
        for name, data in self.state.hypotheses.items():
            advocacy = data.get("advocacy_confidence", 0) * 100
            opposition = 0
            if "arbitration_result" in data:
                result = data["arbitration_result"]
                opposition = result.get("opposition_score", 0) * 100
            
            net_strength = advocacy - opposition
            net_pct = int(net_strength)
            
            # Heat scale
            if net_pct > 70:
                heat = "██"
                status = "SUPPORTED"
            elif net_pct > 40:
                heat = "▓█"
                status = "PARTIALLY_SUPPORTED"
            elif net_pct > 20:
                heat = "░▓" 
                status = "NEUTRAL-BIASED"
            elif net_pct < -30:
                heat = ".O"
                status = "SUSPICIOUS"
            else:
                heat = "░░"
                status = "INDETERMINATE"
            
            print(f"[{heat}] {name}: Net={net_pct:3d}% [{status}]")
        
        print("="*60)
        
    async def run(self, mode: str = "interactive"):
        """
        Run the debate loop.
        
        Modes:
        - "interactive": User can control pace (recommended for development)
        - "continuous": Automatic continuous loop (overnight research)
        - "once": Run one round then exit
        """
        print("="*60)
        print("🚀 SELF-SUSTAINING OPPONENT SYSTEM")
        print("="*60)
        print()
        print("Domain Law Axioms Active:")
        print(f"  [█] Conservation: Explainable origin/transformation for all claims")
        print(f"  [█] Simplicity: Occam's Razor - prefer fewer assumptions")  
        print(f"  [█] Consistency: Same symbols behave consistently across contexts")
        print()
        
        # Load advocates
        await self.initialize_advocates()
        
        if mode == "once":
            await self.run_all_hypotheses()
        elif mode == "interactive":
            while True:
                try:
                    choice = input("\n[1] Run round for all hypotheses\n" +
                                  "[2] View system status  \n" +
                                  "[3] Run opponent self-test\n" +
                                  "[4] Exit loop\n> ").strip()
                    
                    if choice == "1":
                        await self.run_all_hypotheses()
                    elif choice == "2":
                        await self.display_system_status()
                    elif choice == "3":
                        await self.run_periodic_opponent_check()
                    elif choice == "4":
                        break
                except KeyboardInterrupt:
                    print("\n\n⚠️  Interrupted by user")
                    break
        elif mode == "continuous":
            print("ℹ️  Running in continuous loop mode... Press Ctrl+C to exit\n")
            try:
                while True:
                    await self.run_all_hypotheses()
                    await asyncio.sleep(60)  # 1 minute between rounds
                    await self.run_periodic_opponent_check()
                    await asyncio.sleep(30)  # 30 seconds between checks
            except KeyboardInterrupt:
                print("\n\n⚠️  Continuous loop interrupted by user")
                
    def to_dict(self) -> Dict[str, any]:
        """Export current state as dictionary."""
        return {
            "hypotheses": {k: v for k, v in self.state.hypotheses.items()},
            "advocates_loaded": list(self.advocates.keys()),
            "opponent_loaded": bool(self.opponent),
            "arbitrator_results_count": len(self.arbitrator.arbitration_results)
        }
        
    def load_advocate_module(self, module_name: str):
        """Load a specific advocate module directly."""
        # This would dynamically import the appropriate advocate class
        pass


async def main(mode: str = "interactive"):
    """CLI entry point for the orchestrator."""
    
    orchestrator = DebateLoopOrchestrator(state_file="/home/avalonas/.hermes/gematria/scripts/state.json")
    
    if mode == "interactive":
        print("="*60)
        print("🎯 SELF-SUSTAINING OPPONENT SYSTEM READY")
        print()
        print("This system coordinates:")
        print("  - Layer 2 (Domain): Advocates for specific symbol/hypothesis claims")
        print("  - Layer 3 (Meta): Opponent tests framework integrity via Domain Laws")  
        print("  - Layer 4 (Arbitration): Judge evaluates and updates hypothesis strength\n")
        print("Domain Law Axioms Enforced:")
        print("  [█] Conservation: All claims must have explainable origin/transformation rules")
        print("  [█] Simplicity: Occam's Razor - prefer fewer assumptions")
        print("  [█] Consistency: Same symbols must behave consistently across contexts\n")
        
        run_mode = input("Select mode:\n" +
                        "[1] Interactive (one round at a time)\n" + 
                        "[2] Continuous (automatic overnight loop)\n" +
                        "[3] Once (run all then exit)\n> ").strip()
        
        mode_map = {"1": "interactive", "2": "continuous", "3": "once"}
        sub_mode = mode_map.get(run_mode, "interactive")
    else:
        print(f"🎯 SELF-SUSTAINING OPPONENT SYSTEM - {mode.upper()} MODE")
        print("Starting automatic debate loop...\n")
        sub_mode = mode
    
    await orchestrator.run(mode=sub_mode)


if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    if args and args[0] in ["--mode", "-m"]:
        mode = args[1]
    else:
        mode = "interactive"
    asyncio.run(main(mode=mode))
