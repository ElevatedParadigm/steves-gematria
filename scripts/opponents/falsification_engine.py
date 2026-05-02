#!/usr/bin/env python3
"""
Falsification Engine - Main Adversarial Opponent (Layer 3: Meta-Level)

This script implements the adversarial opponent system for Steve's Gematria research.
The opponent operates at a meta-level, never directly attacking specific hypothesis claims,
but rather testing the framework against domain laws and counter-evidence patterns.

Architecture:
- Layer 2 (Domain): Specific symbol/hypothesis claims
- Layer 3 (Meta)   : Opponent tests framework integrity vs Domain Laws
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
import random

# Import from parent gematria module (adjust path as needed)
try:
    from gematria.database import get_db  # type: ignore
except ImportError:
    get_db = None


@dataclass
class FalsificationEvent:
    """Records a falsification attempt and outcome."""
    timestamp: str
    hypothesis_name: str
    domain_law_violated: str
    evidence_summary: str
    confidence: float
    action_taken: str  # "reject", "modify", "suspend"
    
    def to_dict(self):
        return self.__dict__


@dataclass  
class FalsificationLog:
    """Accumulates falsification attempts over time."""
    events: List[FalsificationEvent] = field(default_factory=list)
    
    def record(self, event: FalsificationEvent):
        self.events.append(event)
        
    def count_violations(self, domain_law: str) -> int:
        return sum(1 for e in self.events if e.domain_law_violated == domain_law)
        
    def total_confidence(self) -> float:
        """Return average confidence of all falsification attempts."""
        if not self.events:
            return 0.0
        return sum(e.confidence for e in self.events) / len(self.events)


class FalsificationEngine:
    """
    Main opponent that tests gematria hypotheses against Domain Laws.
    
    Operates at meta-level (Layer 3), never directly attacking specific claims,
    but testing the framework's structural integrity.
    
    Core Principles:
    - Never claim a hypothesis is "true" definitively
    - Always ask "what would falsify this?" before acceptance
    - Track cumulative evidence, not single instances
    - Report confidence as probability, not certainty
    """
    
    # Domain Laws that all hypotheses must respect
    DOMAIN_LAWS = {
        "conservation": [
            "Hypotheses must have explainable origin and transformation rules",
            "No creation from nothing or disappearance into void",
            "Value chains must be reversible where natural"
        ],
        "simplicity": [
            "Occam's Razor: prefer explanations with fewer assumptions",
            "Each domain should resolve to core primitives when decomposed",
            "Avoid unnecessary complexity in transformation rules"
        ],
        "consistency": [
            "Same symbols must behave consistently across contexts",
            "Domain-specific exceptions must be clearly marked",
            "No contradictory claims within the same scope"
        ]
    }
    
    def __init__(self, db_path: Optional[str] = None):
        self.log = FalsificationLog()
        self.db = get_db(db_path) if get_db else None
        self._initialized = False
        
    async def initialize(self):
        """Initialize the engine with database and state."""
        if not self._initialized:
            # Load recent falsifications from DB if available
            if self.db:
                try:
                    cursor = await self.db.cursor()
                    await cursor.execute("SELECT * FROM falsification_events ORDER BY timestamp DESC LIMIT 100")
                    rows = await cursor.fetchall()
                    for row in rows:
                        event_data = dict(row)
                        # Convert ISO strings back to datetime if needed
                        event = FalsificationEvent(
                            timestamp=event_data['timestamp'],
                            hypothesis_name=event_data['hypothesis_name'],
                            domain_law_violated=event_data['domain_law_violated'],
                            evidence_summary=event_data['evidence_summary'],
                            confidence=float(event_data['confidence']),
                            action_taken=event_data['action_taken']
                        )
                        self.log.record(event)
                except Exception as e:
                    pass  # Graceful fallback if DB not available
                
            self._initialized = True
            
    async def test_against_law(
        self, 
        hypothesis_name: str, 
        domain_law_violated: str,
        evidence: str, 
        confidence: float
    ) -> Optional[FalsificationEvent]:
        """
        Test a specific claim against a domain law.
        
        Returns FalsificationEvent if law was violated, None otherwise.
        Never definitively rejects - only raises flags for scrutiny.
        """
        if not self._initialized:
            await self.initialize()
            
        # Validate confidence is reasonable (0-1 range)
        confidence = max(0.0, min(1.0, confidence))
        
        # Check against relevant domain laws
        relevant_laws = [law for law in self.DOMAIN_LAWS.values()]
        if domain_law_violated.lower() in [l.lower() for l in relevant_laws]:
            event = FalsificationEvent(
                timestamp=datetime.utcnow().isoformat(),
                hypothesis_name=hypothesis_name,
                domain_law_violated=domain_law_violated,
                evidence_summary=evidence[:500],  # Limit size
                confidence=confidence,
                action_taken="pending_review"
            )
            
            self.log.record(event)
            
            return event
            
        return None
    
    async def generate_counter_hypothesis(
        self, 
        hypothesis_name: str,
        domain_law: str
    ) -> Optional[str]:
        """
        Generate counter-hypotheses based on domain laws.
        
        Operates at meta-level - doesn't attack the claim directly,
        but considers what alternative frameworks would handle this case.
        """
        if not self._initialized:
            await self.initialize()
            
        # Meta-level analysis: consider different explanatory frameworks
        counter_frameworks = {
            "conservation": [
                f"Consider energy/information entropy model for {hypothesis_name}",
                f"What if {hypothesis_name} involves hidden variables?",
                f"Can this be expressed through reversible transformations?"
            ],
            "simplicity": [
                f"Does {hypothesis_name} reduce to primitive operations?",
                f"Are there multiple simpler explanations for same observations?",
                f"What's the minimal sufficient assumption set?"
            ],
            "consistency": [
                f"How does {hypothesis_name} handle edge cases?",
                f"Is this a special case or general pattern?",
                f"Does this contradict similar hypotheses in adjacent domains?"
            ]
        }
        
        framework = counter_frameworks.get(domain_law.lower(), [])
        if framework:
            return random.choice(framework)
            
        return None
    
    async def assess_evidence_strength(self, hypothesis_name: str) -> Dict[str, any]:
        """
        Assess total evidence for/against a hypothesis.
        
        Returns Bayesian-style evidence strength (not certainty).
        Uses log-likelihood ratios implicitly.
        """
        if not self._initialized:
            await self.initialize()
            
        violations = self.log.count_violations(hypothesis_name)
        total_events = len([e for e in self.log.events if e.hypothesis_name == hypothesis_name])
        
        return {
            "hypothesis": hypothesis_name,
            "total_observations": total_events,
            "violations": violations,
            "support_ratio": total_events / max(1, violations),  # Simplified LR proxy
            "evidence_strength": min(3.0, max(-3.0, violations - total_events)),  # Rough score
            "status": self._get_status(total_events, violations)
        }
    
    def _get_status(self, observations: int, violations: int) -> str:
        """Return human-readable status based on evidence."""
        if observations == 0:
            return "untested"
        elif violations > observations * 0.5:
            return "highly_suspicious"
        elif violations > 0:
            return "needs_scrutiny"
        else:
            return "tentatively_supported"
    
    async def periodic_self_test(self):
        """Run automated self-consistency checks periodically."""
        if not self._initialized:
            await self.initialize()
            
        # Check for pattern of suspicious behavior in specific domains
        law_stats = {}
        for law_name, laws in self.DOMAIN_LAWS.items():
            violations = sum(e.confidence for e in self.log.events 
                           if law_name in e.domain_law_violated.lower())
            law_stats[law_name] = {
                "total_tests": len([e for e in self.log.events if law_name in e.domain_law_violated.lower()]),
                "violations": violations,
                "avg_confidence": violations / max(1, len([e for e in self.log.events if law_name in e.domain_law_violated.lower()]))
            }
            
        # Flag laws with high violation rates
        suspicious_laws = [k for k, v in law_stats.items() 
                          if v['total_tests'] > 0 and v['violations'] / v['total_tests'] > 0.3]
                          
        return {"self_test_complete": True, "suspicious_patterns": suspicious_laws}


def main():
    """CLI entry point for the falsification engine."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Falsification Engine CLI")
    parser.add_argument("--hypothesis", type=str, help="Hypothesis name to test")
    parser.add_argument("--domain-law", type=str, help="Domain law to check against")
    parser.add_argument("--evidence", type=str, help="Evidence description")
    parser.add_argument("--confidence", type=float, default=0.7, help="Confidence level (0-1)")
    parser.add_argument("--self-test", action="store_true", help="Run self-consistency check")
    
    args = parser.parse_args()
    
    async def run():
        engine = FalsificationEngine()
        await engine.initialize()
        
        if args.self_test:
            result = await engine.periodic_self_test()
            print(json.dumps(result, indent=2))
        elif args.hypothesis and args.domain_law:
            event = await engine.test_against_law(
                args.hypothesis,
                args.domain_law,
                args.evidence,
                args.confidence
            )
            if event:
                print(json.dumps(event.to_dict(), indent=2))
                print(f"→ Action: {event.action_taken}")
                print(f"→ Log now contains {len(engine.log.events)} falsification events")
            else:
                print("No law violation detected")
        else:
            # Show current state
            stats = {}
            for law_name, laws in engine.DOMAIN_LAWS.items():
                violations = engine.log.count_violations(law_name)
                total_tests = len([e for e in engine.log.events if law_name in e.domain_law_violated.lower()])
                stats[law_name] = {
                    "total_tests": total_tests,
                    "violations": violations
                }
            
            print("=== Falsification Engine Status ===")
            for law_name, data in stats.items():
                heat = "░░░░" if not data['total_tests'] else (
                    "██░░" if data['total_tests'] > 0 and data['violations'] / max(1, data['total_tests']) < 0.3 else
                    "▓█░░" if data['total_tests'] > 0 and data['violations'] / max(1, data['total_tests']) <= 0.4 else
                    "█▓░░" if data['total_tests'] > 0 and data['violations'] / max(1, data['total_tests']) <= 0.6 else
                    "██"
                )
                print(f"{law_name.upper()}: {data['violations']}/{data['total_tests']} violations [{heat}]")
                
            print(f"\nTotal falsification events logged: {len(engine.log.events)}")
            
    asyncio.run(run())


if __name__ == "__main__":
    main()
