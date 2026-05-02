#!/usr/bin/env python3
"""
Arbitrator / Judge - Decision Arbiter Layer

This script acts as the decision arbiter that:
1. Receives arguments from all advocates (Layer 2)
2. Receives challenges from the falsification engine/opponent (Layer 3)
3. Applies Domain Laws to evaluate evidence quality
4. Makes Bayesian-updated judgments about hypothesis strength
5. Reports results with appropriate heat-scale visualization

Core Principles:
- Never claims absolute certainty (always probabilistic)
- Separates meta-analysis from specific claims (avoids self-reference paradoxes)
- Uses Domain Laws as formal axioms for arbitration
- Tracks cumulative evidence with Bayesian-style updating

Domain Law Axioms (Formal):
1. Conservation Hypothesis: All claims must have explainable origin/transformation rules
2. Simplicity Hypothesis: Prefer explanations with fewer assumptions (Occam's Razor)  
3. Consistency Hypothesis: Same symbols must behave consistently across contexts

Visualization: Uses ASCII heat scale encoding (░ ▒ ▓ █ . O) for status reports
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import random


@dataclass 
class ArgumentRecord:
    """Records an advocate's argument with metadata."""
    hypothesis_name: str
    confidence: float
    key_points: List[str]
    evidence_strength: float
    domain_law_compliance: List[Dict]
    
    def to_dict(self):
        return self.__dict__


@dataclass
class OpponentChallenge:
    """Records an opponent's challenge from meta-level."""
    hypothesis_name: str
    law_violated: str
    evidence_summary: str
    confidence: float
    counter_hypothesis: Optional[str] = None
    
    def to_dict(self):
        return self.__dict__


@dataclass
class ArbitrationResult:
    """Records the arbitration decision and reasoning."""
    hypothesis_name: str
    advocacy_score: float
    opposition_score: float  
    net_strength: float
    domain_law_status: Dict[str, str]
    evidence_quality: str
    confidence_estimate: float
    recommendation: str  # "accept", "tentatively_accept", "reject", "needs_more_evidence"
    reasoning_summary: str
    
    def to_dict(self):
        return self.__dict__


class DomainLawAxioms:
    """
    Formal axioms that govern all arbitration decisions.
    
    These are the "Domain Laws" - immutable principles that 
    hypotheses must satisfy or face scrutiny.
    """
    
    Axioms = {
        "conservation": {
            "name": "Law of Conservation",
            "formal_statement": "Every claim about a symbol/value must have an explainable origin and transformation rules.",
            "transformation_rules": [
                "No creation from nothing or disappearance into void",
                "Value chains must be reversible where natural", 
                "Every manifestation connects to causal context",
                "Reduction/construction operations must follow defined patterns"
            ],
            "violation_indicators": [
                "Claims appearing without clear origin story",
                "Numbers transforming arbitrarily between contexts",
                "Manifestations disconnected from underlying system",
                "Asymmetric transformations (A→B but not B→A) without explanation"
            ]
        },
        "simplicity": {
            "name": "Law of Simplicity (Occam's Razor)", 
            "formal_statement": "Prefer explanations with fewer assumptions and simpler operations.",
            "preference_principles": [
                "Each domain should resolve to core primitives when decomposed",
                "Avoid unnecessary complexity in transformation rules",
                "Multi-step explanations require multiple pieces of evidence",
                "Special cases must be clearly marked as exceptions"
            ],
            "violation_indicators": [
                "Overly complex multi-stage explanations for simple phenomena",
                "Unnecessary intermediate concepts between primitives and claims",
                "Same effect explained by multiple different 'special' mechanisms",
                "Lack of reduction to fundamental operations"
            ]
        },
        "consistency": {
            "name": "Law of Consistency", 
            "formal_statement": "The same symbols must behave consistently across contexts.",
            "consistency_requirements": [
                "Identical symbols should produce predictable results",
                "Domain-specific exceptions must be clearly marked and bounded",
                "No contradictory claims within the same scope or level",
                "Boundary conditions must be explicitly stated when rules change"
            ],
            "violation_indicators": [
                "Same symbol behaving differently without explained context shift",
                "Contradictory definitions for the same value",
                "Unbounded special cases that undermine general principles",
                "Inconsistent transformation rules applied to similar inputs"
            ]
        }
    }
    
    @classmethod
    def check_compliance(cls, hypothesis: str, evidence: str) -> Dict[str, str]:
        """Check a hypothesis/evidence pair against all domain laws."""
        results = {}
        
        for law_name, law_specs in cls.Axioms.items():
            compliance = cls._check_single_law(law_specs, hypothesis, evidence)
            results[law_name] = compliance["status"]  # "compliant", "questionable", "violated"
            
        return results
    
    @classmethod
    def _check_single_law(cls, law_specs: Dict, hypothesis: str, evidence: str) -> Dict[str, any]:
        """Check against a single domain law."""
        hypothesis_lower = hypothesis.lower()
        evidence_lower = evidence.lower()
        
        # Check for violation indicators in evidence
        violations = [ind for ind in law_specs["violation_indicators"] 
                     if ind.lower() in evidence_lower]
        
        # Check for compliance patterns in evidence (use appropriate key based on which has the rules)
        rule_key = law_specs.get("preference_principles") or law_specs.get("transformation_rules", [])
        if not rule_key and isinstance(rule_key, list):
            rule_key = []  # Default empty list if no rules defined
        compliances = [rule for rule in rule_key 
                      if any(keyword in evidence_lower for keyword in str(rule).lower().split())]
        
        if violations:
            return {"status": "questionable", "reason": f"Potential {violations[0]} detected"}
        elif compliances:
            return {"status": "compliant", "reason": f"Supports {compliances[0]}"}
        else:
            return {"status": "neutral", "reason": "No clear compliance or violation indicators found"}


class Arbitrator:
    """
    Main arbitrator that evaluates hypotheses against domain laws.
    
    Operates at decision-making layer, receiving arguments from advocates
    and challenges from opponent, then applying Domain Law axioms to 
    make Bayesian-updated judgments.
    """
    
    def __init__(self):
        self.argument_history: List[ArgumentRecord] = []
        self.challenge_history: List[OpponentChallenge] = []
        self.arbitration_results: List[ArbitrationResult] = []
        
    async def receive_argument(self, hypothesis_name: str, argument_data: Dict[str, any]) -> ArgumentRecord:
        """Receive and record an advocate's argument."""
        record = ArgumentRecord(
            hypothesis_name=hypothesis_name,
            confidence=argument_data.get("confidence_estimate", 0.7),
            key_points=argument_data.get("key_points", []),
            evidence_strength=argument_data.get("evidence_strength", 0.5),
            domain_law_compliance=argument_data.get("domain_law_compliance", [])
        )
        
        self.argument_history.append(record)
        print(f"✓ Argument received for {hypothesis_name}: confidence={record.confidence:.2%}")
        
        return record
    
    async def receive_challenge(self, hypothesis_name: str, challenge_data: Dict[str, any]) -> OpponentChallenge:
        """Receive and record an opponent's meta-level challenge."""
        record = OpponentChallenge(
            hypothesis_name=hypothesis_name,
            law_violated=challenge_data.get("law_violated", "unknown"),
            evidence_summary=challenge_data.get("evidence_summary", ""),
            confidence=challenge_data.get("confidence_estimate", 0.6),
            counter_hypothesis=challenge_data.get("counter_hypothesis")
        )
        
        self.challenge_history.append(record)
        print(f"⚠️  Challenge received for {hypothesis_name}: law_violated={record.law_violated}")
        
        return record
    
    def make_arbitration_decision(self, hypothesis_name: str) -> ArbitrationResult:
        """
        Make arbitration decision based on all accumulated evidence.
        
        Uses Bayesian-style updating with Domain Law axioms as constraints.
        Never claims certainty - only estimates probability-based strength.
        """
        # Get arguments and challenges for this hypothesis
        hypothesis_arguments = [a for a in self.argument_history if a.hypothesis_name == hypothesis_name]
        hypothesis_challenges = [c for c in self.challenge_history if c.hypothesis_name == hypothesis_name]
        
        # Calculate scores
        advocacy_score = sum(a.confidence * a.evidence_strength 
                           for a in hypothesis_arguments) / max(1, len(hypothesis_arguments))
        opposition_score = sum(c.confidence for c in hypothesis_challenges) / max(1, len(hypothesis_challenges))
        
        # Net strength with heat-scale visualization
        if advocacy_score > 0 and opposition_score == 0:
            net_strength = advocacy_score * 0.95
            net_heat = "██"
        elif advocacy_score <= 0:
            net_strength = -min(1.0, opposition_score / 2)
            net_heat = "░░"
        else:
            ratio = (advocacy_score - opposition_score) / max(1, advocacy_score + opposition_score)
            net_strength = min(1.0, max(-1.0, ratio))
            
            if net_strength > 0.7:
                net_heat = "██"
            elif net_strength > 0.4:
                net_heat = "▓█"  
            elif net_strength > 0.2:
                net_heat = "░▓"
            elif net_strength > -0.3:
                net_heat = "░░"
            else:
                net_heat = ".O"
        
        # Check domain law compliance for each axiom
        law_status = {}
        for argument in hypothesis_arguments:
            if argument.domain_law_compliance:
                for compliance in argument.domain_law_compliance:
                    law_name = compliance.get("law", "unknown")
                    status = compliance.get("status", "unknown")
                    if law_name not in law_status:
                        law_status[law_name] = []
                    law_status[law_name].append(status)
        
        # Determine overall domain law status  
        if all(status == "compliant" for statuses in law_status.values() for status in statuses):
            domain_law_status = "full_compliance"
        elif any("questionable" in statuses for statuses in law_status.values()):
            domain_law_status = "partial_compliance" 
        else:
            domain_law_status = "non_compliant"
        
        # Calculate evidence quality rating
        total_arguments = len(hypothesis_arguments)
        total_challenges = len(hypothesis_challenges)
        
        if total_arguments == 0:
            evidence_quality = "untested"
        elif total_challenges == 0:
            evidence_quality = "advocacy_only" 
        elif total_challenges > total_arguments * 2:
            evidence_quality = "heavily_scorched"
        elif total_challenges > total_arguments:
            evidence_quality = "moderately_scrutinized"
        else:
            evidence_quality = "well_tested"
        
        # Estimate confidence (never certainty!)
        base_confidence = abs(net_strength) * 0.85
        if evidence_quality == "untested":
            base_confidence *= 0.5
        elif evidence_quality == "advocacy_only":
            base_confidence *= 0.75
        
        confidence_estimate = min(0.92, max(0.35, base_confidence))
        
        # Determine recommendation
        if net_strength > 0.6:
            recommendation = "accept"
        elif net_strength > 0.4:
            recommendation = "tentatively_accept" 
        elif net_strength < -0.4:
            recommendation = "reject"
        else:
            recommendation = "needs_more_evidence"
        
        # Generate reasoning summary with heat scale
        advocacy_str = f"{int(advocacy_score * 100)}%"
        opposition_str = f"{int(opposition_score * 100)}%"
        
        reasoning = (
            f"[{net_heat}] {hypothesis_name}: Advocacy [{advocacy_str}] vs Opposition [{opposition_str}]\n"
            f"→ Domain Law Status: {domain_law_status.replace('_', ' ').title()}\n" 
            f"→ Evidence Quality: {evidence_quality.replace('_', ' ').title()}\n"
            f"→ Confidence Estimate: {confidence_estimate:.1%} (never 100%)\n"
            f"→ Recommendation: {recommendation.replace('_', ' ').title()}"
        )
        
        result = ArbitrationResult(
            hypothesis_name=hypothesis_name,
            advocacy_score=advocacy_score,
            opposition_score=opposition_score, 
            net_strength=net_strength,
            domain_law_status=domain_law_status,
            evidence_quality=evidence_quality,
            confidence_estimate=confidence_estimate,
            recommendation=recommendation,
            reasoning_summary=reasoning
        )
        
        self.arbitration_results.append(result)
        return result
    
    async def periodic_review(self) -> Dict[str, any]:
        """Periodically review all arbitration results for pattern detection."""
        # Group results by hypothesis
        hypothesis_stats = {}
        for result in self.arbitration_results:
            if result.hypothesis_name not in hypothesis_stats:
                hypothesis_stats[result.hypothesis_name] = {
                    "total_arbitrations": 0,
                    "accepts": 0,
                    "tentative_accepts": 0,
                    "rejects": 0, 
                    "needs_more_evidence": 0,
                    "net_strengths": []
                }
            
            stats = hypothesis_stats[result.hypothesis_name]
            stats["total_arbitrations"] += 1
            
            if result.recommendation == "accept":
                stats["accepts"] += 1
            elif result.recommendation == "tentatively_accept":
                stats["tentative_accepts"] += 1 
            elif result.recommendation == "reject":
                stats["rejects"] += 1
            else:
                stats["needs_more_evidence"] += 1
            
            stats["net_strengths"].append(result.net_strength)
        
        # Calculate success rates
        review_results = []
        for name, stats in hypothesis_stats.items():
            total = stats["total_arbitrations"]
            if total == 0:
                continue
                
            accept_rate = (stats["accepts"] + 0.3 * stats["tentative_accepts"]) / total
            rejection_rate = (stats["rejects"] + 0.5 * stats["needs_more_evidence"]) / total
            
            review_results.append({
                "hypothesis": name,
                "total_reviews": total,
                "accept_rate": accept_rate,
                "rejection_rate": rejection_rate,
                "avg_net_strength": sum(stats["net_strengths"]) / len(stats["net_strengths"]) if stats["net_strengths"] else 0,
                "status": self._get_status_class(accept_rate, rejection_rate)
            })
        
        # Sort by most significant findings
        review_results.sort(key=lambda x: abs(x["avg_net_strength"]), reverse=True)
        
        return {
            "review_complete": True,
            "hypotheses_reviewed": len(review_results),
            "findings": review_results[:10],  # Top 10 most significant
            "patterns_detected": self._detect_patterns(review_results)
        }
    
    def _get_status_class(self, accept_rate: float, rejection_rate: float) -> str:
        """Get status class based on rates."""
        if accept_rate > 0.8 and rejection_rate < 0.2:
            return "strong_support"
        elif accept_rate > 0.5 and rejection_rate < 0.3:
            return "moderate_support" 
        elif reject_rate > 0.6 or (accept_rate < 0.2 and reject_rate > 0.1):
            return "strong_suspicion"
        else:
            return "indeterminate"
    
    def _detect_patterns(self, results: List[Dict]) -> List[str]:
        """Detect interesting patterns in arbitration history."""
        patterns = []
        
        # Check for clustering by domain law violations
        if len(results) > 3:
            dominant_law = None
            max_violations = 0
            
            for result in results:
                stats = hypothesis_stats.get(result["hypothesis"], {})
                violations = stats.get("rejects", 0) + stats.get("needs_more_evidence", 0)
                
                if violations > max_violations:
                    dominant_law = None  # Would track which law caused issues
                    max_violations = violations
            
            if max_violations > len(results) * 0.4 and len(results) > 3:
                patterns.append(f"High violation rate detected ({max_violations}/{len(results)}), review domain laws")
        
        return patterns


def main():
    """CLI entry point for the arbitrator."""
    
    async def run():
        arbitrator = Arbitrator()
        
        print("=== ARBITRATOR / JUDGE ===\n")
        print("Domain Law Axioms Active:")
        print(f"  [█] Conservation: All claims must have explainable origin/transformation rules")
        print(f"  [█] Simplicity: Prefer explanations with fewer assumptions")  
        print(f"  [█] Consistency: Same symbols must behave consistently across contexts")
        print()
        
        # Example: Simulate receiving arguments from advocates
        advocate_args = [
            {
                "hypothesis_name": "Universal Threshold",
                "confidence_estimate": 0.82,
                "evidence_strength": 0.81,
                "key_points": ["124 appears as structural threshold", "Bidirectional reduction supported"],
                "domain_law_compliance": [
                    {"law": "conservation", "status": "compliant"},
                    {"law": "simplicity", "status": "compliant"}, 
                    {"law": "consistency", "status": "compliant"}
                ]
            }
        ]
        
        print("📥 Receiving arguments from advocates...")
        for arg in advocate_args:
            await arbitrator.receive_argument(arg["hypothesis_name"], arg)
            
        # Example: Simulate receiving challenges from opponent
        opponent_challenges = [
            {
                "hypothesis_name": "Universal Threshold",
                "law_violated": "conservation", 
                "evidence_summary": "124 appears without clear causal context in some instances",
                "confidence_estimate": 0.65,
                "counter_hypothesis": "Consider energy/information entropy model for 124"
            }
        ]
        
        print("📤 Receiving challenges from falsification engine...")
        for challenge in opponent_challenges:
            await arbitrator.receive_challenge(challenge["hypothesis_name"], challenge)
            
        # Make arbitration decision
        result = arbitrator.make_arbitration_decision(advocate_args[0]["hypothesis_name"])
        
        print(f"\n📊 Arbitration Decision for '{result.hypothesis_name}':")
        print(f"   Advocacy Score: {int(result.advocacy_score * 100)}%")
        print(f"   Opposition Score: {int(result.opposition_score * 100)}%")
        print(f"   Net Strength: [{result.net_heat}]")  
        print(f"   Domain Law Status: {result.domain_law_status.replace('_', ' ').title()}")
        print(f"   Evidence Quality: {result.evidence_quality.replace('_', ' ').title()}")
        print(f"   Confidence Estimate: {result.confidence_estimate:.1%} (never 100%)")
        print(f"   → Recommendation: {result.recommendation.replace('_', ' ').title()}")
        print()
        print("📝 Reasoning Summary:")
        print(result.reasoning_summary)
        
    import asyncio
    asyncio.run(run())


if __name__ == "__main__":
    main()
