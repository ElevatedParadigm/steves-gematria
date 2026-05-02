#!/usr/bin/env python3
"""
Cross-Domain Analysis Agent
============================

Specialized agent for analyzing and correlating patterns across
multiple domains (politics, crypto, military, etc.).

Capabilities:
- Cross-domain convergence detection
- Pattern correlation analysis  
- Domain-specific preference mapping
- Convergence scoring and ranking
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json
import re
from pydantic import BaseModel, Field

# Add parent to path for imports
sys.path.insert(0, str(Path.home()))
sys.path.insert(0, str(Path.home() / ".hermes"))
sys.path.insert(0, str(Path.home() / ".hermes/gematria/scripts"))

class ConvergenceOccurrence(BaseModel):
    """Represents a cross-domain convergence"""
    symbols: List[int]
    domains: List[str]
    convergence_score: float
    context_links: Dict[str, str]
    timestamp: str
    elemental_forces: Optional[List[str]] = None

class CrossDomainAnalysisAgent:
    """
    Agent responsible for cross-domain pattern correlation and analysis.
    
    Routes:
    • Convergence detection → Domain intersection analysis
    • Pattern correlation → Symbol co-occurrence mapping  
    • Domain preferences → Historical analysis
    
    Dependencies:
    • Core symbols configuration (124, 963, 55, 111, 279, 666)
    • Domain metadata from database
    """
    
    def __init__(self):
        self.agent_id = "cross-domain-analysis"
        self.agent_type = "analysis" 
        self.name = f"[{self.agent_id}] Cross-Domain Analysis Agent"
        self.core_symbols = [124, 963, 55, 111, 279, 666]
        self.domains_metadata: Dict[str, Dict] = {}
        self.domain_preferences: Dict[int, List[str]] = {
            124: ["politics", "military"],
            963: ["crypto", "technology"],
            55: ["religious", "cultural"],
            111: ["political", "spiritual"],
            279: ["military", "historical"],
            666: ["mythological", "entertainment"]
        }
        self.convergences_found: List[ConvergenceOccurrence] = []
        
    async def initialize(self):
        """Load domain metadata and preferences"""
        try:
            db_path = Path.home() / ".hermes/gematria/database.json"
            
            if db_path.exists():
                with open(db_path, 'r') as f:
                    db = json.load(f)
                    
                # Extract domains metadata
                for domain_data in db.get("domains", []):
                    self.domains_metadata[domain_data.get("name")] = {
                        "type": domain_data.get("type", "unknown"),
                        "preferences": domain_data.get("preferred_symbols", []),
                        "associated_forces": domain_data.get("associated_forces", [])
                    }
                    
            self.log("INFO", f"Loaded metadata for {len(self.domains_metadata)} domains")
            
        except Exception as e:
            self.log("WARN", f"Could not load domain metadata: {str(e)}")
        
    async def execute_task(self, task_payload: Dict) -> Dict:
        """Execute specific analysis task"""
        task_name = task_payload.get("type", "unknown")
        
        if task_name == "correlate":
            return await self.correlate_patterns(task_payload.get("symbols", self.core_symbols))
        elif task_name == "find_convergences":
            return await self.find_domain_convergences()
        elif task_name == "domain_preferences":
            return await self.analyze_domain_preferences()
        else:
            return {"error": f"Unknown task type: {task_name}"}
            
    async def execute_workflow(self) -> Dict:
        """Run daily cross-domain analysis workflow"""
        self.log("INFO", "Starting cross-domain analysis workflow")
        
        # Import functions directly from overnight_research
        from overnight_research import get_database
        
        db = await get_database()
        
        results = {
            "correlations": await self.correlate_patterns(self.core_symbols, db),
            "convergences": await self.find_domain_convergences(db),
            "preferences": await self.analyze_domain_preferences(db)
        }
        
        # Summary
        total_correlations = results["correlations"].get("total_pairs", 0)
        convergence_count = len(results["convergences"].get("convergences", []))
        
        summary = {
            "workflow_completed": True,
            "timestamp": datetime.now().isoformat(),
            "analyses": {
                "correlations_analyzed": total_correlations,
                "convergences_found": convergence_count,
                "domains_analyzed": len(self.domains_metadata)
            },
            "top_convergence": results["convergences"].get("top_convergence", None),
            "key_findings": [
                f"Analyzed {total_correlations} symbol pairs for cross-domain patterns",
                f"Found {convergence_count} domain convergences",
                f"Mapped preferences across {len(self.domains_metadata)} domains"
            ]
        }
        
        self.log("INFO", f"Analysis complete: found {convergence_count} convergences")
        
        return summary

    async def correlate_patterns(self, symbols: List[int], db) -> Dict:
        """Analyze correlations between symbol pairs across domains"""
        
        correlation_pairs = []
        total_correlations = 0
        
        # Analyze each pair of core symbols
        for i, sym1 in enumerate(symbols):
            for sym2 in symbols[i+1:]:
                try:
                    # Calculate correlation based on shared domains
                    doms1 = self._get_symbol_domains(sym1, db)
                    doms2 = self._get_symbol_domains(sym2, db)
                    
                    # Correlation coefficient
                    shared = len(doms1.intersection(doms2))
                    max_possible = min(len(doms1), len(doms2))
                    correlation_score = (shared / max_possible) * 100 if max_possible > 0 else 0
                    
                    pair_info = {
                        "symbols": [sym1, sym2],
                        "correlation_coefficient": round(correlation_score, 2),
                        "shared_domains": list(doms1.intersection(doms2)),
                        "dom_count_sym1": len(doms1),
                        "dom_count_sym2": len(doms2)
                    }
                    
                    correlation_pairs.append(pair_info)
                    total_correlations += 1
                    
                except Exception as e:
                    self.log("WARN", f"Correlation analysis for {sym1}×{sym2} failed: {str(e)}")
        
        return {
            "total_pairs_analyzed": len(correlation_pairs),
            "pairs": correlation_pairs[:20],  # Top 20 pairs
            "analysis_depth": f"{len(self.core_symbols)} symbols × {len(self.core_symbols)-1} combinations"
        }

    async def find_domain_convergences(self, db) -> Dict:
        """Find patterns converging across multiple domains"""
        
        convergences = []
        
        # Check each group of 3+ symbols for domain convergence
        if len(self.core_symbols) >= 3:
            symbol_combinations = [
                self.core_symbols[:3],
                self.core_symbols[1:] + [self.core_symbols[0]],
                self.core_symbols[-2:],
                self.core_symbols[-1] + self.core_symbols[:-1]
            ]
            
            for combo in symbol_combinations:
                try:
                    # Find shared domains across symbols in combination
                    all_domains = set()
                    for sym in combo:
                        doms = self._get_symbol_domains(sym, db)
                        all_domains.update(doms)
                    
                    convergence_score = min(100, len(all_domains) * 8)  # Weighted score
                    
                    if len(combo) >= 3:
                        convergence = ConvergenceOccurrence(
                            symbols=combo,
                            domains=list(all_domains)[:5],  # Top 5
                            convergence_score=round(convergence_score, 2),
                            context_links={},
                            timestamp=datetime.now().isoformat()
                        )
                        
                        convergences.append(convergence)
                        
                except Exception as e:
                    self.log("WARN", f"Convergence analysis for {combo} failed: {str(e)}")
        
        # Sort by convergence score
        sorted_convergences = sorted(
            convergences,
            key=lambda x: x.convergence_score,
            reverse=True
        )
        
        top = sorted_convergences[0] if sorted_convergences else None
        
        return {
            "convergences": [
                {
                    "symbols": list(c.symbols),
                    "domains": c.domains,
                    "score": c.convergence_score,
                    "context_links": c.context_links
                }
                for c in sorted_convergences[:10]  # Top 10
            ],
            "top_convergence": {
                "symbols": list(top.symbols) if top else [],
                "domains": top.domains if top else [],
                "score": round(top.convergence_score, 2) if top else 0
            } if top else None,
            "total_found": len(convergences)
        }

    async def analyze_domain_preferences(self, db) -> Dict:
        """Analyze domain preferences for each core symbol"""
        
        analysis = {}
        
        for symbol in self.core_symbols:
            key = f"symbol_{symbol}"
            
            # Get domains from database
            try:
                symbol_data = next(
                    (item for item in db.get("symbols", []) if item["number"] == symbol),
                    None
                )
                
                if symbol_data:
                    domains_with_occurrences = symbol_data.get("occurrences", {}).get("by_domain", {})
                    
                    analysis[key] = {
                        "symbol": symbol,
                        "total_domains": len(domains_with_occurrences),
                        "primary_domains": list(domains_with_occurrences.keys())[:5],
                        "elemental_forces": symbol_data.get("elemental_forces", []),
                        "domain_preferences": self.domain_preferences.get(symbol, [])
                    }
                else:
                    analysis[key] = {
                        "symbol": symbol,
                        "total_domains": 0,
                        "primary_domains": [],
                        "elemental_forces": [],
                        "domain_preferences": self.domain_preferences.get(symbol, [])
                    }
                    
            except Exception as e:
                self.log("WARN", f"Domain preference analysis for {symbol} failed: {str(e)}")
                analysis[key] = {
                    "symbol": symbol,
                    "error": str(e)
                }
        
        return {
            "analysis_completed": True,
            "symbol_preferences": analysis,
            "summary": [
                f"{len(self.core_symbols)} symbols analyzed",
                "Domain preferences mapped for each core symbol",
                "Elemental force associations tracked"
            ]
        }

    def _get_symbol_domains(self, symbol: int, db) -> set:
        """Extract domains where symbol appears"""
        
        symbol_data = next(
            (item for item in db.get("symbols", []) if item["number"] == symbol),
            None
        )
        
        if not symbol_data:
            return set()
            
        by_domain = symbol_data.get("occurrences", {}).get("by_domain", {})
        return {domain for domain in by_domain.keys()}

    def log(self, level: str, message: str):
        print(f"[{self.name}] [{level}] {message}")
