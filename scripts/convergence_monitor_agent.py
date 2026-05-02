#!/usr/bin/env python3
"""
Convergence Monitor Agent
==========================

Specialized agent for monitoring elemental forces, cycle convergence,
and pattern transformation dynamics.

Capabilities:
- Elemental force intensity tracking
- Transformation cycle detection
- Convergence threshold monitoring
- Cross-elemental crossover alerts
- Domain-specific elemental preferences mapping
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
from pydantic import BaseModel, Field

# Add parent to path for imports
sys.path.insert(0, str(Path.home()))
sys.path.insert(0, str(Path.home() / ".hermes"))
sys.path.insert(0, str(Path.home() / ".hermes/gematria/scripts"))

class ElementalPattern(BaseModel):
    """Represents an elemental pattern occurrence"""
    force: str  # "fire", "air", "water", "earth"
    symbols: List[int]
    intensity_score: float
    domains: List[str]
    timestamp: str
    context: Optional[str] = None

class TransformationCycle(BaseModel):
    """Represents a transformation cycle"""
    from_force: str
    to_force: str
    symbols_involved: List[int]
    occurrences: int
    strength: float

class ConvergenceMonitorAgent:
    """
    Agent responsible for elemental/cycle convergence monitoring.
    
    Routes:
    • Elemental tracking → Force intensity analysis
    • Cycle detection → Transformation mapping
    • Crossover alerts → Threshold monitoring
    
    Dependencies:
    • Core symbols configuration (124, 963, 55, 111, 279, 666)
    • Elemental force definitions
    • Convergence threshold parameters
    """
    
    def __init__(self):
        self.agent_id = "convergence-monitor"
        self.agent_type = "monitoring"
        self.name = f"[{self.agent_id}] Convergence Monitor Agent"
        
        # Elemental force definitions
        self.elemental_forces = {
            "fire": ["55", "124"],
            "air": ["963", "124"],
            "water": ["111", "279"],
            "earth": ["666", "55"]
        }
        
        self.force_intensity_threshold = 3.0
        self.convergence_threshold = 0.75
        
        self.current_patterns: List[ElementalPattern] = []
        self.transformation_cycles: List[TransformationCycle] = []
        self.alerts: List[Dict] = []
        
    async def initialize(self):
        """Initialize elemental tracking from database"""
        self.log("INFO", "Initializing convergence monitor")
        
        try:
            db_path = Path.home() / ".hermes/gematria/database.json"
            
            if db_path.exists():
                with open(db_path, 'r') as f:
                    db = json.load(f)
                
                # Extract elemental force information
                for symbol_data in db.get("symbols", []):
                    number = symbol_data.get("number")
                    forces = symbol_data.get("elemental_forces", [])
                    
                    if forces:
                        for force in forces:
                            existing = next(
                                (p for p in self.current_patterns 
                                 if p.force.lower() == force.lower()),
                                None
                            )
                            
                            if not existing:
                                self.current_patterns.append(ElementalPattern(
                                    force=force,
                                    symbols=[number],
                                    intensity_score=1.0,
                                    domains=[],
                                    timestamp=datetime.now().isoformat()
                                ))
                                
                self.log("INFO", f"Loaded {len(self.current_patterns)} elemental patterns")
            
        except Exception as e:
            self.log("WARN", f"Could not load elemental data: {str(e)}")
        
    async def execute_task(self, task_payload: Dict) -> Dict:
        """Execute specific monitoring task"""
        task_name = task_payload.get("type", "unknown")
        
        if task_name == "track_elemental":
            return await self.track_elemental_forces()
        elif task_name == "detect_cycles":
            return await self.detect_transformation_cycles()
        elif task_name == "monitor_thresholds":
            return await self.monitor_convergence_thresholds()
        else:
            return {"error": f"Unknown task type: {task_name}"}
            
    async def execute_workflow(self) -> Dict:
        """Run daily convergence monitoring workflow"""
        self.log("INFO", "Starting convergence monitoring workflow")
        
        # Import get_database directly
        from overnight_research import get_database
        
        db = await get_database()
        
        # Run all monitoring tasks
        results = await self.track_elemental_forces(db)
        
        if results.get("success"):
            cycle_results = await self.detect_transformation_cycles(db)
            threshold_results = await self.monitor_convergence_thresholds()
            
            summary = {
                "workflow_completed": True,
                "timestamp": datetime.now().isoformat(),
                "monitoring": {
                    "elemental_patterns_tracked": len(self.current_patterns),
                    "transformation_cycles_detected": len(self.transformation_cycles),
                    "alerts_triggered": len([a for a in self.alerts if a.get("severity") == "high"])
                },
                "elemental_summary": results,
                "cycles": cycle_results,
                "thresholds": threshold_results
            }
            
            # Print top findings
            cycles = cycle_results.get("cycles", [])
            if cycles:
                strongest = max(cycles, key=lambda x: x.get("strength", 0))
                self.log("INFO", f"Strongest transformation: {strongest['from_force']}→{strongest['to_force']} (score: {strongest['strength']:.2f})")
            
            # Print alerts if any
            high_alerts = [a for a in self.alerts if a.get("severity") == "high"]
            if high_alerts:
                self.log("ALERT", f"⚠️  {len(high_alerts)} high-severity convergence events detected")
            
        return summary

    async def track_elemental_forces(self, db) -> Dict:
        """Track elemental force intensity and patterns"""
        
        # Track each elemental force
        force_tracking = {}
        
        for symbol_data in db.get("symbols", []):
            number = symbol_data.get("number")
            elemental_forces = symbol_data.get("elemental_forces", [])
            
            if not elemental_forces:
                continue
                
            # Calculate intensity based on occurrences
            occurrences = symbol_data.get("occurrences", {})
            total_occurrences = sum(
                d.get("count", 0) 
                for d in occurrences.values()
            )
            
            intensity = min(1.0, total_occurrences / 50)  # Normalize to 0-1
            
            for force in elemental_forces:
                existing = next(
                    (p for p in self.current_patterns 
                     if p.force.lower() == force.lower()),
                    None
                )
                
                if not existing:
                    self.current_patterns.append(ElementalPattern(
                        force=force,
                        symbols=[number],
                        intensity_score=intensity,
                        domains=list(occurrences.keys())[:5],  # Top 5 domains
                        timestamp=datetime.now().isoformat()
                    ))
                else:
                    # Update existing pattern
                    existing.symbols.append(number)
                    existing.intensity_score = max(existing.intensity_score, intensity)
                    
                    existing.domains.extend(occurrences.keys())
            
            force_tracking[f"symbol_{number}"] = {
                "elemental_forces": elemental_forces,
                "total_occurrences": total_occurrences,
                "intensity": round(intensity, 3)
            }
        
        # Summary by force
        force_summary = {}
        for pattern in self.current_patterns:
            force = pattern.force.lower()
            
            if force not in force_summary:
                force_summary[force] = {
                    "patterns": 0,
                    "total_intensity": 0.0,
                    "symbols": []
                }
            
            force_summary[force]["patterns"] += 1
            force_summary[force]["total_intensity"] += pattern.intensity_score
            
            if number not in force_summary[force]["symbols"]:
                force_summary[force]["symbols"].append(number)
        
        # Calculate average intensity per force
        for force, data in force_summary.items():
            data["avg_intensity"] = round(
                data["total_intensity"] / data["patterns"], 3
            ) if data["patterns"] > 0 else 0
        
        return {
            "success": True,
            "forces_tracked": len(force_summary),
            "force_summary": force_summary,
            "pattern_count": len(self.current_patterns)
        }

    async def detect_transformation_cycles(self, db) -> Dict:
        """Detect elemental transformation cycles"""
        
        cycles_detected = []
        
        # Check for common transformation patterns
        transformations = [
            ("fire", "air", ["55", "963", "124"]),  # Fire releases into air
            ("air", "water", ["963", "111", "124"]),  # Air condenses to water
            ("water", "earth", ["111", "666", "279"]),  # Water deposits as earth
            ("earth", "fire", ["666", "55"])  # Earth generates fire
        ]
        
        for from_force, to_force, core_symbols in transformations:
            try:
                # Count occurrences across symbols in the transformation
                occurrences_count = 0
                
                for symbol_data in db.get("symbols", []):
                    number = symbol_data.get("number")
                    elemental_forces = symbol_data.get("elemental_forces", [])
                    
                    if from_force.lower() in [f.lower() for f in elemental_forces]:
                        occurrences_count += 1
                
                if occurrences_count > 0:
                    strength = min(1.0, occurrences_count / 4) * 100
                    
                    cycle = TransformationCycle(
                        from_force=from_force,
                        to_force=to_force,
                        symbols_involved=[int(s) for s in core_symbols if s.isdigit()],
                        occurrences=occurrences_count,
                        strength=round(strength, 2)
                    )
                    
                    cycles_detected.append(cycle)
                    
            except Exception as e:
                self.log("WARN", f"Cycle detection failed for {from_force}→{to_force}: {str(e)}")
        
        # Sort by strength and take top cycles
        sorted_cycles = sorted(
            cycles_detected,
            key=lambda x: x.strength,
            reverse=True
        )[:10]  # Top 10 cycles
        
        return {
            "cycles_detected": len(sorted_cycles),
            "top_cycles": [
                {
                    "from_force": c.from_force,
                    "to_force": c.to_force,
                    "symbols": c.symbols_involved,
                    "occurrences": c.occurrences,
                    "strength": round(c.strength, 2)
                }
                for c in sorted_cycles
            ],
            "workflow_completed": True
        }

    async def monitor_convergence_thresholds(self) -> Dict:
        """Monitor convergence thresholds and generate alerts"""
        
        alerts = []
        
        # Check for high-convergence events
        high_intensity_patterns = [
            p for p in self.current_patterns
            if p.intensity_score >= 0.8
        ]
        
        if len(high_intensity_patterns) > 5:
            alert = {
                "type": "high_intensity",
                "message": f"High elemental intensity detected in {len(high_intensity_patterns)} patterns",
                "severity": "medium",
                "timestamp": datetime.now().isoformat()
            }
            alerts.append(alert)
            
        # Check for unusual elemental co-occurrence
        unusual_combinations = await self._find_unusual_elemental_combinations(db)
        
        if unusual_combinations:
            alert = {
                "type": "unusual_combination",
                "message": f"Unusual elemental combination detected: {' × '.join(unusual_combinations[:5])}",
                "severity": "high" if len(unusual_combinations) > 3 else "medium",
                "timestamp": datetime.now().isoformat()
            }
            alerts.append(alert)
        
        # Check for fire element intensity spikes
        fire_intensity = sum(p.intensity_score for p in self.current_patterns if p.force.lower() == "fire")
        if fire_intensity > 3.0 and len(self.current_patterns) < 10:
            alert = {
                "type": "low_elemental_diversity",
                "message": f"Fire elemental patterns ({len([p for p in self.current_patterns if p.force.lower() == 'fire'])}) dominate with total intensity {fire_intensity:.2f}",
                "severity": "medium",
                "timestamp": datetime.now().isoformat()
            }
            alerts.append(alert)
        
        # Update global alerts list
        self.alerts = alerts
        
        return {
            "alerts_generated": len(alerts),
            "high_severity_alerts": len([a for a in alerts if a.get("severity") == "high"]),
            "medium_severity_alerts": len([a for a in alerts if a.get("severity") == "medium"]),
            "low_severity_alerts": len([a for a in alerts if a.get("severity") == "low"]),
            "alerts": alerts
        }

    async def _find_unusual_elemental_combinations(self, db) -> List[str]:
        """Find unusual elemental combinations"""
        
        unusual = []
        
        # Analyze co-occurrence patterns
        for symbol_data in db.get("symbols", []):
            number = symbol_data.get("number")
            elemental_forces = symbol_data.get("elemental_forces", [])
            
            if len(elemental_forces) >= 2:
                force_names = [f.capitalize() for f in elemental_forces]
                unusual.append(f"{number}({' × '.join(force_names)})")
        
        return unusual[:10]

    def log(self, level: str, message: str):
        print(f"[{self.name}] [{level}] {message}")
