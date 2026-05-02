#!/usr/bin/env python3
"""
Steve's Gematria Self-Sustaining Opponent System
===================================================

Purpose: Actively search for counter-evidence, edge cases, and falsification attempts
         to challenge current gematria hypothesis strength.

Features:
- Edge Case Finder — Identifies apparent contradictions
- Boundary Condition Tester — Tests limits where hypothesis fails  
- Alternative Explanation Generator — Proposes competing theories
- Counter-Example Generator — Constructs concrete counter-examples
- Domain Consistency Checker — Tests against domain laws

Architecture: Avoids self-reference paradoxes through hierarchical separation.
              The opponent operates at meta-level, challenging interpretations,
              not the underlying symbols themselves.
"""

import os, json, datetime, re, sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import yaml


# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Opponent system configuration"""
    
    # Paths
    GEMATRIA_WORKSPACE = os.getenv("GEMATRIA_WORKSPACE", str(Path.home() / ".hermes" / "gematria"))
    DATABASE_FILE = os.path.join(GEMATRIA_WORKSPACE, "gematria_database.json")
    VISUAL_ARCHIVE = os.path.join(GEMATRIA_WORKSPACE, "visual_archive")
    SYMBOLS_DIR = os.path.join(VISUAL_ARCHIVE, "symbols")
    PATTERN_TRAILS_DIR = os.path.join(VISUAL_ARCHIVE, "pattern_trails")
    
    # Debate settings
    ATTACK_INTENSITY = 2  # Low=1, Medium=2, High=3 (how aggressively to attack)
    ATTACK_VECTORS = [
        "edge_cases",           # Find edge cases that break correlations
        "boundary_conditions",   # Test limit cases  
        "alternative_explanations",  # Propose competing theories
        "reduction_challenges",  # Question claimed reduction pathways
        "spurious_correlation"    # Challenge correlation strength claims
    ]
    
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
# UTILITY FUNCTIONS
# ============================================================================

def log(message: str, level: str = "INFO") -> None:
    """Log message with timestamp"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


def extract_symbol_data_from_md(md_file: Path) -> Dict:
    """Extract YAML frontmatter and content from symbol MD file"""
    try:
        with open(md_file) as f:
            content = f.read()
            
        # Parse YAML frontmatter
        frontmatter_end = content.find("---\n")
        if frontmatter_end > 0:
            yaml_content = content[7:content.find('\n---')]
        else:
            yaml_content = ""
            
        # Simple parser for frontmatter (no external deps)
        data = {}
        lines = yaml_content.strip().split('\n') if yaml_content else []
        for line in lines:
            if ':' in line:
                key, _, value = line.partition(':')
                key = key.strip().lower()
                # Remove brackets and quotes
                value = value.strip().strip('[]{}').strip('"\'')
                data[key] = value
                
        return {
            "file": str(md_file),
            "title": data.get("aliases", "")[:20] if data.get("aliases") else "Unknown",
            "tags": data.get("tags", []) if isinstance(data.get("tags"), list) else [data.get("tags", "")],
            "wikilinks": data.get("wikilinks_inbound", ""),
            "correlation_strengths": {},  # Will be extracted from content
            "category": data.get("category", "Unknown")
        }
        
    except Exception as e:
        log(f"Warning: Error reading {md_file}: {e}", "WARNING")
        return {}


def extract_correlations_from_content(content: str) -> Dict[str, float]:
    """Extract correlation matrix data from MD content"""
    correlations = {}
    
    # Pattern for heat scale representations like ████████░ (HIGH)
    strength_patterns = {
        "Very High": 0.95,
        "High": 0.80,
        "High-Medium": 0.70,
        "Medium": 0.50,
        "Medium-Low": 0.30,
        "Low": 0.15,
    }
    
    # Look for correlation declarations in content
    correlation_keywords = ["correlation", "correlate", "connection"]
    
    for line in content.split('\n'):
        line_lower = line.lower()
        for keyword in correlation_keywords:
            if keyword in line_lower:
                # Find heat scale patterns on same or next few lines
                context_lines = line + "\n".join(content.split('\n')[content.split('\n').index(line):content.split('\n').index(line)+3])
                
                for pattern, strength in strength_patterns.items():
                    if pattern in context_lines:
                        # Extract which symbol this relates to
                        match = re.search(r'\[\[([^\]]+)\]\]', context_lines)
                        if match:
                            symbol = match.group(1).replace('-', '').lower()
                            correlations[symbol] = strength
                            
    return correlations


# ============================================================================
# OPPONENT MODULES
# ============================================================================

class EdgeCaseFinder:
    """Module 1: Identifies apparent contradictions and edge cases"""
    
    def find_edge_cases(self, symbol_data: Dict) -> List[Dict]:
        """Find edge cases where correlation might fail"""
        edge_cases = []
        
        # Example edge cases based on symbol properties
        if "666" in str(symbol_data.get("title", "")) or "wholeness" in symbol_data.get("tags", ""):
            edge_cases.append({
                "case_type": "boundary_condition",
                "description": "What happens during incomplete transitions? Does [[666]] only apply to completed cycles?",
                "severity": Config.ATTACK_INTENSITY,
                "category": "completeness_requirements"
            })
            
        if any(x in str(symbol_data.get("tags", "")) for x in ["124", "bridge", "threshold"]):
            edge_cases.append({
                "case_type": "threshold_violation", 
                "description": "Are there threshold-crossing events where bridge correlation breaks down?",
                "severity": Config.ATTACK_INTENSITY,
                "category": "universal_vs_contextual"
            })
            
        return edge_cases


class BoundaryConditionTester:
    """Module 2: Tests limits where hypothesis might fail"""
    
    def test_boundaries(self, symbol_data: Dict) -> List[Dict]:
        """Test boundary conditions that could falsify correlation claims"""
        boundaries = []
        
        # Reduction pathway limits
        if "reduction" in str(symbol_data.get("wikilinks", "")).lower():
            boundaries.append({
                "boundary_type": "reduction_limit",
                "question": "Does every 3-symbol pathway actually reduce? What about non-reducible cycles?",
                "test_case": "Try finding examples of symbol chains that don't reduce to harmony"
            })
            
        # Domain-specific boundaries
        for domain, laws in Config.DOMAIN_LAWS.items():
            boundaries.append({
                "boundary_type": f"{domain}_violation",
                "question": f"What happens when {domain.capitalize()} domain law is violated?",
                "severity": 2,
                "domain_laws": laws
            })
            
        return boundaries


class AlternativeExplanationGenerator:
    """Module 3: Proposes competing theories"""
    
    def generate_alternatives(self, symbol_data: Dict) -> List[Dict]:
        """Generate alternative explanations for observed correlations"""
        alternatives = []
        
        # Spurious correlation arguments
        alternatives.append({
            "hypothesis_type": "post_hoc_fitting",
            "alternative_explanation": "Correlation identified after data collection (HARKing: Hypothesizing After Results Known)",
            "counter_argument": "Could represent confirmation bias rather than predictive relationship"
        })
        
        # Common cause explanations  
        alternatives.append({
            "hypothesis_type": "common_cause",
            "alternative_explanation": "Both symbols correlate with third variable (latent confounder)",
            "counter_argument": "Need to control for confounding variables before claiming direct relationship"
        })
        
        # Overfitting concerns
        alternatives.append({
            "hypothesis_type": "data_snooping",
            "alternative_explanation": "High correlations could emerge from searching large hypothesis space without correction",
            "counter_argument": "Need multiple testing corrections (Bonferroni, FDR) before claiming significance"
        })
        
        return alternatives


class ReductionMechanismChallenger:
    """Module 4: Questions claimed reduction pathways"""
    
    def challenge_reduction(self, symbol_data: Dict) -> List[Dict]:
        """Challenge the validity of claimed reduction mechanisms"""
        challenges = []
        
        # Question the reduction claims
        if "reduction" in str(symbol_data.get("wikilinks", "")).lower() or \
           any(x in str(symbol_data.get("tags", "")) for x in ["55", "111"]):
            
            challenges.append({
                "challenge_type": "mechanism_opaque",
                "argument": "How exactly does 6+6+6=18→9 reduction work physically? What's the transformation mechanism?",
                "evidence_required": "Physical/mathematical derivation of reduction operation, not just arithmetic"
            })
            
        challenges.append({
            "challenge_type": "pathway_uniqueness",
            "argument": "Could multiple pathways achieve same end state? Is reduction path unique or one of many?",
            "implication": "If not unique, correlation strength claims need recalibration"
        })
        
        return challenges


class DomainConsistencyChecker:
    """Module 5: Tests arguments against domain laws"""
    
    def check_domain_consistency(self, argument: str) -> Tuple[bool, List[str]]:
        """Check if argument respects domain-specific laws"""
        violations = []
        
        # Extract implied domain from argument
        domain_keywords = {
            "physics": ["quantum", "energy", "wave", "particle", "field", "entropy"],
            "biology": ["cell", "organism", "evolution", "metabolism", "homeostasis", "cycle"],
            "psychology": ["consciousness", "cognition", "memory", "learning", "belief"],
            "history": ["coups", "conflict", "political", "social", "epoch"]
        }
        
        arg_lower = argument.lower()
        for domain, keywords in domain_keywords.items():
            if any(kw in arg_lower for kw in keywords):
                # Check against that domain's laws
                for law in Config.DOMAIN_LAWS.get(domain, []):
                    law_lower = law.lower()
                    if law_lower not in arg_lower and 'violate' not in arg_lower:
                        violations.append({
                            "domain": domain,
                            "law": law,
                            "potential_violation": f"Argument may not fully respect {law}"
                        })
        
        return len(violations) == 0, violations


# ============================================================================
# MAIN OPPONENT ENGINE
# ============================================================================

class FalsificationEngine:
    """Main opponent engine that orchestrates all attack modules"""
    
    def __init__(self):
        self.edge_case_finder = EdgeCaseFinder()
        self.boundary_tester = BoundaryConditionTester()
        self.alternative_generator = AlternativeExplanationGenerator()
        self.reduction_challenger = ReductionMechanismChaller()
        self.consistency_checker = DomainConsistencyChecker()
        
    def scan_for_hypotheses(self) -> List[Dict]:
        """Scan existing symbol pages for hypotheses to attack"""
        hypotheses = []
        
        if not os.path.exists(self.SYMBOLS_DIR):
            log(f"Symbols directory not found: {self.SYMBOLS_DIR}", "WARNING")
            return hypotheses
            
        md_files = list(Path(self.SYMBOLS_DIR).glob("*.md"))
        
        for md_file in md_files[:10]:  # Limit to first 10 for efficiency
            symbol_data = extract_symbol_data_from_md(md_file)
            
            if not symbol_data:
                continue
                
            content_type = "symbol_definition" if "definition" in symbol_data.get("tags", []) else "correlation_claim"
            
            hypotheses.append({
                "id": md_file.stem,
                "symbol_title": symbol_data.get("title", "Unknown"),
                "type": content_type,
                "wikilinks": symbol_data.get("wikilinks", ""),
                "file_path": str(md_file)
            })
            
        return hypotheses
    
    def launch_attack(self, hypothesis: Dict) -> List[AttackResult]:
        """Launch coordinated attack on given hypothesis"""
        
        # Load the actual content for analysis
        try:
            with open(hypothesis["file_path"]) as f:
                content = f.read()
            
            # Extract correlation data if present
            correlations = extract_correlations_from_content(content)
            symbol_data = {
                "title": hypothesis["symbol_title"],
                "tags": [t.lower() for t in hypothesis.get("wikilinks", "").split()[:3]],
                "wikilinks": hypothesis["wikilinks"],
                "correlation_strengths": correlations,
                "category": "correlation_claim"
            }
            
        except Exception as e:
            log(f"Error loading hypothesis {hypothesis['file_path']}: {e}", "WARNING")
            return []
        
        # Attack with all modules
        attack_results = []
        
        for vector_name, finder in [
            ("edge_cases", self.edge_case_finder),
            ("boundaries", self.boundary_tester),
            ("alternatives", self.alternative_generator),
            ("reduction", self.reduction_challenger)
        ]:
            
            try:
                results = finder.find_edge_cases(symbol_data) if hasattr(finder, 'find_edge_cases') else \
                           finder.test_boundaries(symbol_data) if hasattr(finder, 'test_boundaries') else \
                           finder.generate_alternatives(symbol_data) if hasattr(finder, 'generate_alternatives') else \
                           finder.challenge_reduction(symbol_data) if hasattr(finder, 'challenge_reduction') else []
                
                for result in results:
                    attack_results.append(AttackResult(
                        vector=vector_name,
                        counter_argument=result.get("description") or result.get("question"),
                        severity=result.get("severity", 2),
                        category=result.get("category") or "general"
                    ))
                    
            except Exception as e:
                log(f"Error in attack vector {vector_name}: {e}", "WARNING")
                
        return attack_results


class AttackResult:
    """Structure for an attack result"""
    
    def __init__(self, vector: str, counter_argument: str, severity: int, category: str):
        self.vector = vector
        self.counter_argument = counter_argument
        self.severity = severity
        self.category = category
        
    def to_dict(self) -> Dict:
        return {
            "vector": self.vector,
            "argument": self.counter_argument,
            "severity": self.severity,
            "category": self.category
        }


def generate_debate_log(advocates_responses: List[Dict], attacks: List[AttackResult]) -> Dict:
    """Generate structured debate log"""
    
    timestamp = datetime.datetime.now().isoformat()
    
    # Create heat scale summary
    attack_count = len(attacks)
    severity_sum = sum(a.severity for a in attacks)
    avg_severity = severity_sum / max(attack_count, 1)
    
    if avg_severity >= 3.0:
        overall_strength = "████░░░░ (LOW)"
    elif avg_severity >= 2.5:
        overall_strength = "▒▓████░░ (MEDIUM-LOW)"  
    elif avg_severity >= 2.0:
        overall_strength = "░░██████░ (MEDIUM-HIGH)"
    else:
        overall_strength = "░░░░█████ (HIGH)"
        
    log_result = {
        "timestamp": timestamp,
        "attack_count": attack_count,
        "severity_summary": avg_severity,
        "overall_hypothesis_strength": overall_strength,
        "attacks": [a.to_dict() for a in attacks],
        "advocate_responses": advocates_responses
    }
    
    return log_result


# ============================================================================
# ENTRY POINT
# ============================================================================

async def main():
    """Main entry point for opponent system"""
    
    log("=" * 60, "INFO")
    log("⚔️  STEVE'S GEMATRIA OPPONENT SYSTEM ACTIVATED", "INFO")  
    log("=" * 60, "INFO")
    log(f"Attack Intensity: {Config.ATTACK_INTENSITY}/3", "INFO")
    log(f"Domain Laws Loaded: {len(Config.DOMAIN_LAWS)} domains", "INFO")
    
    # Initialize engine
    engine = FalsificationEngine()
    
    # Scan for hypotheses to attack
    log("\n🔍 SCANNING FOR HYPOTHESES TO ATTACK...", "INFO")
    hypotheses = engine.scan_for_hypotheses()
    
    if not hypotheses:
        log("No hypotheses found to attack. Exiting.", "WARNING")
        return
        
    log(f"Found {len(hypotheses)} active hypotheses", "INFO")
    
    # Launch attacks on each hypothesis
    all_attacks = []
    for i, hypothesis in enumerate(hypotheses, 1):
        log(f"\n🎯 Attack #{i}: [{hypothesis['symbol_title']}] ...", "INFO")
        
        attacks = engine.launch_attack(hypothesis)
        all_attacks.extend(attacks)
        
        if attacks:
            log(f"   Found {len(attacks)} attack vectors (severity: {max(a.severity for a in attacks)})")
    
    # Generate debate log
    if all_attacks:
        log("\n📊 GENERATING DEBATE LOG...", "INFO")
        
        # Placeholder: In real system, would also get advocate responses
        debates = generate_debate_log([], all_attacks)
        
        # Save to file
        log_file = Path(Config.PATTERN_TRAILS_DIR) / f"opponent_report_{datetime.datetime.now().strftime('%Y%m%d')}.md"
        
        with open(log_file, 'w') as f:
            f.write(f"# Opponent Report — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"\n## Summary\n- Attacks launched: {debates['attack_count']}\n")
            f.write(f"- Overall hypothesis strength: {debates['overall_hypothesis_strength']}\n\n")
            
            # Write attacks
            for attack in all_attacks:
                f.write(f"### [{attack.severity}/3] {attack.category}\n")
                f.write(f"**Vector:** {attack.vector}\n\n")
                f.write(f"{attack.counter_argument}\n\n")
                
        log(f"Debate log saved to: {log_file}", "INFO")
        log("⚔️  Opponent system cycle complete", "INFO")


# ============================================================================
# STANDALONE EXECUTION (for cron/call via terminal)
# ============================================================================

if __name__ == "__main__":
    import asyncio
    
    try:
        result = asyncio.run(main())
        print(f"Opponent engine completed with status: {result}")
    except KeyboardInterrupt:
        log("Opponent system interrupted by user", "INFO")
        sys.exit(0)
