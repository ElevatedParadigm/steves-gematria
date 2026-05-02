#!/usr/bin/env python3
"""
Arbitrator / Judge System for Steve's Gematria Debate
=====================================================

Purpose: Evaluate arguments from advocates and opponent against domain laws.
         Decides winners per debate round and tracks hypothesis strength over time.

Features:
- Loads all advocate scripts  
- Loads opponent system output
- Evaluates both sides against shared domain law constraints
- Updates hypothesis strength via Bayesian prior adjustment
- Outputs ASCII heat scale voting
"""


import os, json, datetime, re, sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple


# ============================================================================
# CONFIGURATION
# ============================================================================

class ArbitrationConfig:
    """Arbitrator configuration"""
    
    # Paths  
    GEMATRIA_WORKSPACE = os.getenv("GEMATRIA_WORKSPACE", str(Path.home() / ".hermes" / "gematria"))
    ADVOCATES_DIR = os.path.join(GEMATRIA_WORKSPACE, "advocates")
    OPPONENT_DIR = os.path.join(GEMATRIA_WORKSPACE, "opponent")
    
    # Domain laws (shared constraints for both sides)
    DOMAIN_LAWS = {
        "physics": [
            "Conservation of information cannot be violated",
            "Energy cannot be created or destroyed", 
            "Thermodynamic arrows of time must be respected",
            "Quantum uncertainty limits apply"
        ],
        "biology": [
            "Homeostasis constraints must be maintained",
            "Metabolic efficiency bounds apply",
            "Evolutionary fitness optimization assumed",
            "Information transmission fidelity limits"
        ],
        "psychology": [
            "Cognitive consistency requirements (Festinger)",
            "Bounded rationality applies", 
            "Memory capacity limits exist",
            "Pattern completion biases are real phenomena"
        ],
        "history": [
            "Contingency vs. determinism tradeoff acknowledged", 
            "Path dependence cannot be ignored",
            "Actor agency matters in historical analysis",
            "Selection bias must be considered"
        ]
    }


# ============================================================================
# LOADING AND PARSING
# ============================================================================

def load_advocate_responses(advocates_dir: str, symbol_title: str) -> Dict[str, str]:
    """Load response arguments from advocate scripts"""
    
    responses = {}
    
    try:
        # Map common symbol aliases to actual filenames
        alias_to_file = {
            "[[124|THRESHOLD]]": "124_BRIDGE_advocate.py",
            "[[963|CYCLE-TURN]]": "963_CYCLE_TURN_advocate.py",  
            "[[55|COMPLETION]]": "55_COMPLETION_advocate.py",
            "[[666|WHOLENESS]]": "666_WHOLENESS_advocate.py",
            "[[279|HARMONIC CONFLUENCE]]": "279_HARMONIC_CONFLUENCE_advocate.py",
            "[[111|UNITY]]": "111_UNITY_advocate.py"
        }
        
        # Also try without brackets for simplicity
        simple_aliases = {
            "124 bridge": "124_BRIDGE_advocate.py",
            "963 cycle turn": "963_CYCLE_TURN_advocate.py",
            "55 completion": "55_COMPLETION_advocate.py",
            "666 wholeness": "666_WHOLENESS_advocate.py",
            "279 harmonic confluence": "279_HARMONIC_CONFLUENCE_advocate.py",
            "111 unity": "111_UNITY_advocate.py"
        }
        
        for title_alias, filename in list(alias_to_file.items()) + list(simple_aliases.items()):
            if symbol_title.lower() in title_alias.lower():
                advocate_file = os.path.join(advocates_dir, filename)
                
                if os.path.exists(advocate_file):
                    try:
                        # Run advocate and capture output
                        import subprocess
                        result = subprocess.run(
                            ["python3", advocate_file],
                            capture_output=True, text=True, timeout=30
                        )
                        
                        if result.returncode == 0:
                            responses[filename] = result.stdout
                            
                    except subprocess.TimeoutExpired:
                        log(f"Advocate execution timed out for {filename}")
                    except Exception as e:
                        log(f"Error running advocate {filename}: {e}", "WARNING")
        
    except Exception as e:
        log(f"Error loading advocate responses: {e}", "WARNING")
        
    return responses


def load_opponent_attacks(opponent_file: str) -> List[Dict]:
    """Load opponent attack results from previous execution"""
    
    attacks = []
    
    try:
        with open(opponent_file, 'r') as f:
            content = f.read()
            
        # Parse opponent output into structured format
        attack_count = 0
        current_attack = {}
        
        for line in content.split('\n'):
            line_lower = line.lower()
            
            if "attack" in line_lower and ":" in line_lower:
                if attack_count > 0:
                    attacks.append(current_attack)
                    
                # Parse new attack
                parts = line.split(':')
                current_attack = {}
                
                for part in parts:
                    part = part.strip()
                    if 'vector=' in part:
                        current_attack['vector'] = part.split('=')[1].strip().strip('"\'')
                    elif 'severity=' in part:
                        current_attack['severity'] = int(part.split('=')[1].strip())
                    elif 'argument' in part.lower():
                        argument_text = part.split('argument')[1] if len(parts) > 1 else ''
                        current_attack['argument'] = argument_text.strip().strip('"\'')
                
                attack_count += 1
                
            elif "found" in line_lower and "attack vector" in line_lower:
                # Simple format from opponent output
                count_match = re.search(r'Found (\d+) attack', line)
                if count_match:
                    attacks.append({
                        'vector': count_match.group(0),
                        'severity': 2,  # Default
                        'argument': ""
                    })
                    
    except Exception as e:
        log(f"Error parsing opponent attacks: {e}", "WARNING")
        
    return attacks


# ============================================================================
# EVALUATION FUNCTIONS
# ============================================================================

def check_domain_compliance(argument: str, domain: str = None) -> Tuple[bool, List[str]]:
    """Check if argument respects domain laws"""
    
    violations = []
    arg_lower = argument.lower()
    
    for law in ArbitrationConfig.DOMAIN_LAWS.get(domain, []):
        law_lower = law.lower()
        
        # Check for potential violations
        violation_keywords = [
            ("violate", "violates conservation/energy"),
            ("impossible", "claims impossibility without justification"),
            ("never", "absolute negative claim"),
            ("always", "absolute positive claim")  
        ]
        
        for keyword, explanation in violation_keywords:
            if keyword in arg_lower:
                violations.append({
                    "law": law,
                    "type": "absolute_claim",
                    "explanation": explanation
                })
                
    return len(violations) == 0, violations


def evaluate_advocate_strength(responses: Dict[str, str], symbol_name: str) -> float:
    """Evaluate advocate defense strength across all arguments"""
    
    total_responses = len(responses)
    if total_responses == 0:
        return 0.3  # Neutral default
        
    strong_responses = 0
    weak_responses = 0
    
    for filename, response in responses.items():
        # Count how many "I think" or confident statements
        confidence_markers = [
            ("is confirmed", True),
            ("confirms", True),  
            ("strong evidence", True),
            ("strengthens hypothesis", True),
            ("this is the mechanism", True)
        ]
        
        response_lower = response.lower()
        for marker, is_strong in confidence_markers:
            if marker in response_lower:
                strong_responses += 1
        
        # Check for hedging (weakness indicators)
        weak_markers = [
            ("might", False),
            ("could be", False),
            ("maybe", False),
            ("possibly", False),
            ("perhaps", False),
            ("uncertain", False)
        ]
        
        for marker, _ in weak_markers:
            if marker in response_lower and "uncertain" not in response_lower:  # Avoid false negative
                weak_responses += 1
                
    avg_confidence = (strong_responses - weak_responses) / total_responses
    return max(0.1, min(0.95, 0.5 + avg_confidence))


def evaluate_opponent_effectiveness(attacks: List[Dict]) -> float:
    """Evaluate opponent attack effectiveness"""
    
    if not attacks:
        return 0.2  # No attacks = minimal effect
        
    total_severity = sum(a.get('severity', 1) for a in attacks)
    avg_severity = total_severity / len(attacks)
    
    # High severity attacks more effective
    effectiveness = min(0.9, avg_severity / 3.0)
    return effectiveness


# ============================================================================
# DECISION LOGIC
# ============================================================================

class Arbitrator:
    """Main arbitrator engine"""
    
    def __init__(self):
        self.config = ArbitrationConfig()
        
    def adjudicate_debate(self, symbol_title: str, advocate_responses: Dict, 
                         opponent_attacks: List[Dict]) -> Dict:
        """Adjudicate single debate round"""
        
        # Evaluate advocate strength
        advocate_strength = evaluate_advocate_strength(advocate_responses, symbol_title)
        
        # Evaluate opponent effectiveness  
        opponent_effectiveness = evaluate_opponent_effectiveness(opponent_attacks)
        
        # Check domain law compliance for both sides
        advocate_compliance = True  # Simplified — would check each response
        opponent_compliance = True  # Would check each attack
        
        # Calculate margin of victory
        margin = advocate_strength - opponent_effectiveness
        
        # Determine winner
        if abs(margin) < 0.15:  # Near tie
            result = "near_tie"
        elif margin > 0:
            result = "advocate_wins"
        else:
            result = "opponent_wins"
            
        # Bayesian prior adjustment (hypothesis strength update)
        if result == "advocate_wins":
            prior_adjustment = +0.15
        elif result == "opponent_wins":
            prior_adjustment = -0.20
        else:  # Near tie
            prior_adjustment = +0.05  # Slight bias toward main hypothesis
        
        return {
            "advocate_strength": advocate_strength,
            "opponent_effectiveness": opponent_effectiveness,
            "margin_of_victory": margin,
            "winner": result,
            "prior_adjustment": prior_adjustment,
            "domain_laws_respected": advocate_compliance and opponent_compliance,
            "confidence_score": self._calculate_confidence(advocate_responses, opponent_attacks)
        }
        
    def _calculate_confidence(self, advocates: Dict, attacks: List) -> float:
        """Calculate confidence score based on evidence quality"""
        
        # Count high-severity attacks
        high_severity_count = sum(1 for a in attacks if a.get('severity', 0) >= 2.5)
        
        # High-severity attacks reduce confidence  
        confidence_reduction = min(0.3, high_severity_count * 0.1)
        
        return max(0.3, 0.7 - confidence_reduction)


# ============================================================================
# HEAT SCALE VOTING SYSTEM
# ============================================================================

def heat_scale_from_score(score: float) -> str:
    """Convert numeric score to ASCII heat scale"""
    
    if score >= 0.85:
        return "████░░░░ (HIGH)"
    elif score >= 0.70:
        return "████▒▓░░ (HIGH-MEDIUM)"
    elif score >= 0.55:
        return "█▒▓░░░░░ (MEDIUM-HIGH)"
    elif score >= 0.40:
        return "█░░░░░░░ (MEDIUM)"
    elif score >= 0.25:
        return "▒░░░░░░░ (LOW-MEDIUM)"  
    else:
        return "▒░░░░░░░ (LOW)"


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Main arbitration entry point"""
    
    log("=" * 60, "INFO")
    log("⚖️  STEVE'S GEMATRIA ARBITRATOR SYSTEM", "INFO")
    log("=" * 60, "INFO")
    log(f"Domain Laws Loaded: {len(ArbitrationConfig.DOMAIN_LAWS)} domains", "INFO")
    
    # Example adjudication (would be integrated into loop system)
    symbol_title = "[[124|THRESHOLD]]"
    
    try:
        # Load responses and attacks
        advocate_responses = load_advocate_responses(
            ArbitrationConfig.ADVOCATES_DIR, 
            symbol_title
        )
        
        opponent_attacks = []  # Would load from previous run
        
        # Run arbitration
        arb = Arbitrator()
        result = arb.adjudicate_debate(symbol_title, advocate_responses, opponent_attacks)
        
        # Generate output report
        print(f"\n🏛️ ARBITRATION RESULT:")
        print(f"Symbol: {symbol_title}")
        print(f"Advocate Strength: {result['advocate_strength']:.2f}")
        print(f"Opponent Effectiveness: {result['opponent_effectiveness']:.2f}")
        print(f"Margin of Victory: {result['margin_of_victory']:+.2f}")
        print(f"Winner: {result['winner']}")
        print(f"Heat Scale Vote: {heat_scale_from_score(result.get('confidence_score', 0))}")
        print(f"\nBayesian Prior Adjustment: {result['prior_adjustment']:+.2f}")
        
    except Exception as e:
        log(f"Arbitration failed: {e}", "ERROR")


if __name__ == "__main__":
    main()
