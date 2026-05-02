#!/usr/bin/env python3
"""
Cross-Symbol Translation Layer for Steve's Gematria System

Enables bidirectional interpretation across core symbols (124, 963, 55, 111, 279, 666)
with support for:
- Symbol-to-symbol relationships
- Pattern transformation between domains
- Usage tracking and refinement
- Translation confidence scores
- Multi-hop inference chains
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional, Tuple, Any
from collections import defaultdict
import hashlib
import math

# =============================
# CONFIGURATION
# =============================

WORKDIR = Path.home() / ".hermes" / "gematria"
TRANSLATION_DB_PATH = WORKDIR / "translation_layer.json"
USAGE_STATS_PATH = WORKDIR / "usage_stats.json"
RELATIONSHIP_MATRIX_PATH = WORKDIR / "relationship_matrix.json"
OBSIDIAN_EXPORTS = WORKDIR / "obsidian_exports"

# Core symbols with their semantic properties
CORE_SYMBOLS = {
    124: {"name": "Bridge", "domains": ["politics", "military"], "elemental": [54, 380], "role": "threshold"},
    963: {"name": "Elevation", "domains": ["religious", "geographic"], "elemental": [201], "role": "spiritual"},
    55: {"name": "Foundation", "domains": ["political", "military"], "elemental": [67], "role": "grounding"},
    111: {"name": "Alignment", "domains": ["politics", "religious"], "elemental": [], "role": "catalyst"},
    279: {"name": "Transformation", "domains": ["military", "geographic"], "elemental": [54, 67], "role": "change"},
    666: {"name": "Completion", "domains": ["religious", "political"], "elemental": [380], "role": "wholeness"}
}

# Element symbol mappings
ELEMENTAL_FORCES = {
    54: {"name": "Fire", "symbols": [124, 279]},
    67: {"name": "Earth", "symbols": [55, 279]},
    201: {"name": "Air", "symbols": [963]},
    380: {"name": "Water", "symbols": [124, 666]}
}

# =============================
# LOGGING
# =============================

CRON_LOGS = WORKDIR / "cron_logs"
CRON_LOGS.mkdir(parents=True, exist_ok=True)
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_PATH = CRON_LOGS / f"translation_layer_{TIMESTAMP}.log"

with open(LOG_PATH, 'w') as log_file:
    print(f"📝 Translation Layer Log initialized at {LOG_PATH}", file=log_file)

# =============================
# UTILITY FUNCTIONS
# =============================

def load_database() -> Dict:
    """Load existing database or return empty structure."""
    try:
        if not TRANSLATION_DB_PATH.exists():
            _initialize_translation_db()
        
        with open(TRANSLATION_DB_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading database: {e}")
        return {}

def save_database(data: Dict):
    """Save updated database."""
    try:
        with open(TRANSLATION_DB_PATH, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving database: {e}")

def _initialize_translation_db():
    """Initialize translation layer database structure."""
    db = {
        "metadata": {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        },
        "translations": {},  # symbol -> {symbol: {"rule": ..., "confidence": ...}}
        "usage_stats": {},  # translation pair -> count, last_used, effectiveness
        "relationships": [],  # multi-hop inference chains
        "domains_tracked": []  # cross-domain correlations
    }
    
    save_database(db)
    print("Initialized translation layer database")

# =============================
# SYMBOL DEFINITION MANAGEMENT
# =============================

class SymbolDefinitionManager:
    """Manage symbol definitions and relationships."""
    
    @staticmethod
    def define_symbol(symbol_id: int, properties: Dict):
        """Define a new symbol or update existing definition."""
        core_symbols = CORE_SYMBOLS.copy()
        core_symbols[symbol_id] = properties
        
        print(f"✓ Defined/Updated Symbol {symbol_id}: {properties.get('name', 'Unknown')}")
        return core_symbols
    
    @staticmethod
    def get_symbol_properties(symbol_id: int) -> Optional[Dict]:
        """Get properties for a symbol."""
        if symbol_id in CORE_SYMBOLS:
            return CORE_SYMBOLS[symbol_id]
        
        db = load_database()
        for sid, props in db.get("translations", {}).items():
            if "definition" in props and props["definition"].get("symbol_id") == symbol_id:
                return props["definition"]
        
        return None
    
    @staticmethod
    def get_all_symbols() -> Dict[int, Dict]:
        """Get all defined symbols."""
        return {sid: CORE_SYMBOLS.get(sid, db["translations"].get(sid, {}).get("definition", {})) 
                for sid in set(CORE_SYMBOLS.keys()) | set(db.get("translations", {}).keys())}

# =============================
# TRANSLATION RULE ENGINE
# =============================

class TranslationRuleEngine:
    """Manage and execute translation rules between symbols."""
    
    def __init__(self):
        self.rules = []
        self.db = load_database()
    
    def add_translation_rule(self, from_symbol: int, to_symbol: int, rule_type: str, 
                           conditions: Dict = None, weight: float = 1.0):
        """Add a translation rule with optional conditions."""
        
        rule = {
            "from": from_symbol,
            "to": to_symbol,
            "type": rule_type,
            "conditions": conditions or {},
            "weight": weight,
            "created_at": datetime.now().isoformat()
        }
        
        self.rules.append(rule)
        
        # Store in database
        if from_symbol not in self.db["translations"]:
            self.db["translations"][from_symbol] = {}
        
        self.db["translations"][from_symbol][to_symbol] = {
            "rule": rule,
            "confidence": 0.5,  # Will be refined with usage
            "usage_count": 0
        }
        
        save_database(self.db)
        print(f"✓ Rule: {from_symbol} → {to_symbol} ({rule_type})")
        return rule
    
    def execute_translation(self, from_symbol: int, input_pattern: str) -> List[Tuple[int, str]]:
        """Execute translation for given symbol and pattern."""
        
        translations = []
        
        if from_symbol not in self.db["translations"]:
            print(f"⚠️ No translations defined for symbol {from_symbol}")
            return translations
        
        # Find all target symbols with applicable rules
        target_symbols = list(self.db["translations"][from_symbol].keys())
        
        for to_symbol, translation_data in self.db["translations"][from_symbol].items():
            rule = translation_data["rule"]
            
            # Check conditions (simplified for this implementation)
            if rule.get("conditions"):
                condition_met = True  # Could add actual condition checking here
            
            # Apply translation with weight and confidence
            confidence = translation_data["confidence"] * rule["weight"]
            
            translations.append({
                "from": from_symbol,
                "to": to_symbol,
                "pattern": input_pattern,
                "confidence": confidence,
                "rule_type": rule["type"]
            })
        
        return translations
    
    def get_best_translation(self, from_symbol: int, input_pattern: str) -> Optional[Dict]:
        """Get the highest-confidence translation."""
        
        translations = self.execute_translation(from_symbol, input_pattern)
        
        if not translations:
            return None
        
        best = max(translations, key=lambda x: x["confidence"])
        return best

# =============================
# USAGE STATISTICS TRACKER
# =============================

class UsageStatsTracker:
    """Track and refine translation effectiveness over time."""
    
    def __init__(self):
        self.db = load_database()
        self._ensure_usage_stats_exists()
    
    def _ensure_usage_stats_exists(self):
        """Ensure usage stats structure exists."""
        if "usage_stats" not in self.db:
            self.db["usage_stats"] = {}
    
    def record_usage(self, from_symbol: int, to_symbol: int, 
                    input_pattern: str, result_quality: float, 
                    domain_context: str = None):
        """Record usage and update statistics."""
        
        key = f"{from_symbol}_{to_symbol}"
        
        if key not in self.db["usage_stats"]:
            self.db["usage_stats"][key] = {
                "total_usage": 0,
                "successful_translations": 0,
                "average_quality": 0.5,
                "domains_used": set(),
                "last_used": None
            }
        
        stats = self.db["usage_stats"][key]
        stats["total_usage"] += 1
        
        if result_quality >= 0.7:  # Threshold for successful translation
            stats["successful_translations"] += 1
        
        # Update average quality
        total = stats["total_usage"]
        new_avg = (stats["average_quality"] * (total - 1) + result_quality) / total
        stats["average_quality"] = new_avg
        
        if domain_context:
            stats["domains_used"].add(domain_context)
        
        stats["last_used"] = datetime.now().isoformat()
        
        save_database(self.db)
        
        # Update confidence based on usage
        self._update_confidence(from_symbol, to_symbol)
    
    def _update_confidence(self, from_symbol: int, to_symbol: int):
        """Update translation confidence based on usage statistics."""
        
        key = f"{from_symbol}_{to_symbol}"
        
        if key in self.db["usage_stats"]:
            stats = self.db["usage_stats"][key]
            
            # Confidence increases with successful usage
            success_rate = stats["successful_translations"] / max(stats["total_usage"], 1)
            usage_bonus = min(0.3, stats["total_usage"] * 0.05)
            
            current_confidence = self.db["translations"].get(from_symbol, {}).get(to_symbol, {}).get("confidence", 0.5)
            new_confidence = min(0.99, max(current_confidence + usage_bonus - (1 - success_rate) * 0.1, 0.3))
            
            if from_symbol in self.db["translations"] and to_symbol in self.db["translations"][from_symbol]:
                self.db["translations"][from_symbol][to_symbol]["confidence"] = new_confidence
            
            save_database(self.db)

# =============================
# RELATIONSHIP MATRIX MANAGER
# =============================

class RelationshipMatrixManager:
    """Manage multi-hop inference chains between symbols."""
    
    def __init__(self):
        self.db = load_database()
        self._ensure_relationships_exists()
    
    def _ensure_relationships_exists(self):
        """Ensure relationships structure exists."""
        if "relationships" not in self.db:
            self.db["relationships"] = []
    
    def add_relationship_chain(self, from_symbol: int, to_symbol: int, 
                              intermediate_symbols: List[int], 
                              chain_type: str, confidence: float):
        """Add a multi-hop relationship chain."""
        
        chain = {
            "from": from_symbol,
            "to": to_symbol,
            "intermediate": intermediate_symbols,
            "type": chain_type,
            "confidence": confidence,
            "created_at": datetime.now().isoformat()
        }
        
        self.db["relationships"].append(chain)
        save_database(self.db)
        print(f"✓ Relationship Chain: {from_symbol} → {to_symbol} (via {intermediate_symbols})")
    
    def find_relationships(self, from_symbol: int, to_symbol: int) -> List[Dict]:
        """Find all relationship chains between symbols."""
        
        relationships = []
        
        for chain in self.db["relationships"]:
            if chain["from"] == from_symbol and chain["to"] == to_symbol:
                relationships.append(chain)
        
        return relationships
    
    def find_direct_path(self, from_symbol: int, to_symbol: int) -> Optional[Dict]:
        """Find direct translation path (highest confidence)."""
        
        chains = self.find_relationships(from_symbol, to_symbol)
        
        if not chains:
            # Check if direct translation exists
            db = load_database()
            if from_symbol in db["translations"] and to_symbol in db["translations"][from_symbol]:
                return {
                    "from": from_symbol,
                    "to": to_symbol,
                    "intermediate": [],
                    "type": "direct",
                    "confidence": db["translations"][from_symbol][to_symbol].get("confidence", 0.5),
                    "created_at": None
                }
        
        if chains:
            return max(chains, key=lambda x: x.get("confidence", 0))
        
        return None

# =============================
# DOMAIN CROSS-REFERENCE LAYER
# =============================

class DomainCrossReferenceLayer:
    """Track cross-domain correlations between symbols."""
    
    def __init__(self):
        self.db = load_database()
        self._ensure_domains_tracked_exists()
    
    def _ensure_domains_tracked_exists(self):
        """Ensure domains structure exists."""
        if "domains_tracked" not in self.db:
            self.db["domains_tracked"] = []
    
    def register_domain_correlation(self, symbol_id: int, domain: str, 
                                   pattern_type: str, confidence: float):
        """Register a new domain correlation."""
        
        correlation = {
            "symbol": symbol_id,
            "domain": domain,
            "pattern_type": pattern_type,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }
        
        self.db["domains_tracked"].append(correlation)
        save_database(self.db)
        print(f"✓ Domain Correlation: Symbol {symbol_id} ↔ {domain}")
    
    def get_symbol_domains(self, symbol_id: int) -> List[Dict]:
        """Get all domains for a symbol."""
        
        domains = []
        for corr in self.db["domains_tracked"]:
            if corr["symbol"] == symbol_id:
                domains.append(corr)
        
        return domains
    
    def find_cross_domain_matches(self, symbol_id: int, target_domains: List[str]) -> List[Dict]:
        """Find symbols that appear in target domains."""
        
        matches = []
        
        for corr in self.db["domains_tracked"]:
            if corr["symbol"] != symbol_id and corr["domain"] in target_domains:
                matches.append({
                    "symbol": corr["symbol"],
                    "domain": corr["domain"],
                    "pattern_type": corr["pattern_type"]
                })
        
        return matches

# =============================
# MULTI-HOP INFERENCE ENGINE
# =============================

class MultiHopInferenceEngine:
    """Execute multi-hop inference across symbol relationships."""
    
    def __init__(self):
        self.rule_engine = TranslationRuleEngine()
        self.relationship_manager = RelationshipMatrixManager()
        self.usage_tracker = UsageStatsTracker()
    
    def infer(self, starting_symbol: int, target_domains: List[str], 
             max_hops: int = 2) -> Dict:
        """Execute multi-hop inference from starting symbol."""
        
        result = {
            "starting_symbol": starting_symbol,
            "target_domains": target_domains,
            "paths_found": [],
            "best_path": None,
            "confidence_scores": {}
        }
        
        # Phase 1: Direct translations
        print(f"🔍 Phase 1: Direct translations from {starting_symbol}")
        
        for domain in target_domains:
            direct_paths = self._find_direct_paths(starting_symbol, domain)
            
            if direct_paths:
                result["paths_found"].extend(direct_paths)
                
                # Record usage
                best_path = max(direct_paths, key=lambda x: x.get("confidence", 0))
                quality = best_path.get("confidence", 0.7)
                
                self.usage_tracker.record_usage(
                    from_symbol=best_path["from"],
                    to_symbol=best_path["to"],
                    input_pattern="inference_query",
                    result_quality=quality,
                    domain_context=domain
                )
        
        # Phase 2: Multi-hop inference if needed
        if max_hops > 1 and not result["paths_found"]:
            print(f"🔗 Phase 2: Multi-hop inference (max {max_hops} hops)")
            
            intermediate_symbols = list(CORE_SYMBOLS.keys())
            
            for hop in range(1, max_hops + 1):
                current_symbol = self._get_intermediate_at_hop(starting_symbol, hop)
                
                if current_symbol:
                    paths = self._find_direct_paths(current_symbol, target_domains)
                    
                    for path in paths:
                        path["hop"] = hop + 1
                        result["paths_found"].append(path)
                        
                        # Record usage for multi-hop
                        quality = path.get("confidence", 0.6) * (1 - hop * 0.1)
                        self.usage_tracker.record_usage(
                            from_symbol=path["from"],
                            to_symbol=path["to"],
                            input_pattern=f"multi_hop_{hop}",
                            result_quality=quality,
                            domain_context="inferred"
                        )
        
        # Find best path
        if result["paths_found"]:
            result["best_path"] = max(result["paths_found"], 
                                     key=lambda x: x.get("confidence", 0))
            
            # Update confidence scores
            for path in result["paths_found"]:
                key = f"{path['from']}_{path['to']}"
                result["confidence_scores"][key] = path.get("confidence", 0)
        
        return result
    
    def _find_direct_paths(self, from_symbol: int, target_domain: str) -> List[Dict]:
        """Find direct translation paths to domain."""
        
        paths = []
        
        # Get symbol properties for domain correlation
        domains_layer = DomainCrossReferenceLayer()
        symbol_domains = domains_layer.get_symbol_domains(from_symbol)
        
        for sd in symbol_domains:
            if sd["domain"] == target_domain:
                # Find translation to other symbols in same or related domain
                db = load_database()
                
                if from_symbol in db["translations"]:
                    for to_symbol, trans_data in db["translations"][from_symbol].items():
                        confidence = trans_data.get("confidence", 0.5)
                        
                        # Boost confidence if domains match
                        to_props = CORE_SYMBOLS.get(to_symbol, {})
                        if to_props:
                            to_domains = to_props.get("domains", [])
                            
                            if target_domain in to_domains or "geographic" in to_domains:
                                confidence = min(0.95, confidence + 0.2)
                        
                        paths.append({
                            "from": from_symbol,
                            "to": to_symbol,
                            "domain": target_domain,
                            "confidence": confidence,
                            "hop": 1
                        })
        
        return paths
    
    def _get_intermediate_at_hop(self, starting_symbol: int, hop: int) -> Optional[int]:
        """Get intermediate symbol at given hop."""
        
        # Simplified intermediate selection for demonstration
        intermediates = [sid for sid in CORE_SYMBOLS.keys() if sid != starting_symbol][:3]
        return intermediates[(hop - 1) % len(intermediates)]

# =============================
# OBSIDIAN EXPORT LAYER
# =============================

class ObsidianExportLayer:
    """Generate Obsidian-compatible markdown exports."""
    
    @staticmethod
    def generate_symbol_definitions() -> str:
        """Generate symbol definitions markdown."""
        
        lines = [
            "# 🔄 Symbol Definitions",
            "",
            "## Core Symbols",
            ""
        ]
        
        for sid, props in CORE_SYMBOLS.items():
            name = props.get("name", f"Symbol_{sid}")
            domains = ", ".join(props.get("domains", []))
            elemental = ", ".join(str(e) for e in props.get("elemental", [])[:2]) if props.get("elemental") else "None"
            role = props.get("role", "")
            
            lines.append(f"## {sid}: **{name}**")
            lines.append("")
            lines.append(f"- **Role**: {role}")
            lines.append(f"- **Domains**: {domains}")
            lines.append(f"- **Elemental**: {elemental}")
            lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_relationship_matrix() -> str:
        """Generate relationship matrix markdown."""
        
        db = load_database()
        translations = db.get("translations", {})
        
        lines = [
            "# 🔀 Relationship Matrix",
            "",
            "## Symbol-to-Symbol Relationships",
            ""
        ]
        
        for from_sid, targets in sorted(translations.items()):
            lines.append(f"### From {from_sid}")
            lines.append("")
            
            for to_sid, trans_data in sorted(targets.items()):
                confidence = trans_data.get("confidence", 0)
                rule = trans_data.get("rule", {})
                
                confidence_str = f"{confidence:.2f}🔮" if confidence > 0.8 else f"{confidence:.2f}"
                lines.append(f"- {to_sid}: `{rule.get('type', 'translation')}` @ {confidence_str}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_cross_reference_report() -> str:
        """Generate cross-domain correlation report."""
        
        layer = DomainCrossReferenceLayer()
        lines = [
            "# 🌉 Cross-Reference Index",
            "",
            "## Domain Correlations by Symbol",
            ""
        ]
        
        correlations = layer.db.get("domains_tracked", [])
        
        # Group by symbol
        by_symbol = defaultdict(list)
        for corr in correlations:
            by_symbol[corr["symbol"]].append(corr)
        
        for sid, corrs in sorted(by_symbol.items()):
            name = CORE_SYMBOLS.get(sid, {}).get("name", f"Symbol_{sid}")
            
            lines.append(f"## {sid}: **{name}**")
            lines.append("")
            lines.append("| Domain | Pattern Type | Confidence |")
            lines.append("|--------|--------------|------------|")
            
            for corr in corrs:
                lines.append(f"| {corr['domain']} | {corr['pattern_type']} | {corr['confidence']:.2f} |")
            
            lines.append("")
        
        return "\n".join(lines)

# =============================
# USAGE STATS MANAGER
# =============================

class UsageStatsManager:
    """Manage overall usage statistics and refinement."""
    
    def __init__(self):
        self.db = load_database()
        self._ensure_usage_stats_exists()
    
    def _ensure_usage_stats_exists(self):
        if "usage_stats" not in self.db:
            self.db["usage_stats"] = {}
    
    def get_statistics(self, symbol_id: int) -> Dict:
        """Get usage statistics for a symbol."""
        
        stats = {
            "total_translations": 0,
            "successful_translations": 0,
            "average_confidence": 0.5,
            "domains_used": [],
            "most_used_targets": []
        }
        
        # Collect stats for all translations from this symbol
        if symbol_id in self.db["translations"]:
            targets = self.db["translations"][symbol_id]
            
            for to_sid, trans_data in targets.items():
                key = f"{symbol_id}_{to_sid}"
                
                if key in self.db["usage_stats"]:
                    usage = self.db["usage_stats"][key]
                    
                    stats["total_translations"] += usage["total_usage"]
                    stats["successful_translations"] += usage["successful_translations"]
                    stats["average_confidence"] = max(
                        stats["average_confidence"],
                        trans_data.get("confidence", 0.5)
                    )
                    
                    if usage["domains_used"]:
                        for domain in usage["domains_used"]:
                            if domain not in stats["domains_used"]:
                                stats["domains_used"].append(domain)
        
        # Calculate success rate
        if stats["total_translations"] > 0:
            stats["success_rate"] = (
                stats["successful_translations"] / stats["total_translations"] * 100
            )
        
        return stats
    
    def get_best_translation_pairs(self, count: int = 10) -> List[Dict]:
        """Get top translation pairs by usage and confidence."""
        
        pairs = []
        
        for from_sid, targets in self.db["translations"].items():
            for to_sid, trans_data in targets.items():
                key = f"{from_sid}_{to_sid}"
                
                if key in self.db["usage_stats"]:
                    usage = self.db["usage_stats"][key]
                    
                    pairs.append({
                        "from": from_sid,
                        "to": to_sid,
                        "confidence": trans_data.get("confidence", 0.5),
                        "total_usage": usage["total_usage"],
                        "success_rate": (
                            usage["successful_translations"] / max(usage["total_usage"], 1) * 100
                        )
                    })
        
        # Sort by confidence and usage
        pairs.sort(key=lambda x: (x["confidence"], x["total_usage"]), reverse=True)
        
        return pairs[:count]

# =============================
# MAIN EXECUTION
# =============================

def main():
    """Main execution entry point for translation layer setup."""
    
    print("=" * 60)
    print("🔀 CROSS-SYMBOL TRANSLATION LAYER - Setup & Initialization")
    print("=" * 60)
    print()
    
    # Initialize layers
    rule_engine = TranslationRuleEngine()
    relationship_manager = RelationshipMatrixManager()
    domain_layer = DomainCrossReferenceLayer()
    usage_stats = UsageStatsManager()
    inference_engine = MultiHopInferenceEngine()
    
    # Define translation rules based on symbol properties
    print("📝 Defining core translation rules...")
    print()
    
    # Rule 1: Bridge (124) ↔ Foundation (55) - Political domain
    rule_engine.add_translation_rule(
        from_symbol=124, to_symbol=55, 
        rule_type="domain_correlation",
        conditions={"domains": ["politics"]},
        weight=1.5
    )
    
    # Rule 2: Elevation (963) ↔ Completion (666) - Religious domain  
    rule_engine.add_translation_rule(
        from_symbol=963, to_symbol=666,
        rule_type="domain_correlation",
        conditions={"domains": ["religious"]},
        weight=1.5
    )
    
    # Rule 3: Bridge (124) ↔ Transformation (279) - Elemental connection
    rule_engine.add_translation_rule(
        from_symbol=124, to_symbol=279,
        rule_type="elemental_bridge",
        conditions={"elemental": [54]},
        weight=1.3
    )
    
    # Rule 4: Foundation (55) ↔ Alignment (111) - Grounding connection
    rule_engine.add_translation_rule(
        from_symbol=55, to_symbol=111,
        rule_type="grounding_catalyst",
        conditions={},
        weight=1.2
    )
    
    # Rule 5: Transformation (279) ↔ Completion (666) - Water elemental
    rule_engine.add_translation_rule(
        from_symbol=279, to_symbol=666,
        rule_type="elemental_flow",
        conditions={"elemental": [380]},
        weight=1.4
    )
    
    # Rule 6: All symbols ↔ Bridge (124) - Universal threshold
    for sid in CORE_SYMBOLS.keys():
        if sid != 124:
            rule_engine.add_translation_rule(
                from_symbol=sid, to_symbol=124,
                rule_type="universal_threshold",
                conditions={},
                weight=1.0
            )
    
    print("✅ Core translation rules defined!")
    print()
    
    # Register domain correlations
    print("🌍 Registering domain correlations...")
    print()
    
    for sid, props in CORE_SYMBOLS.items():
        for domain in props.get("domains", []):
            confidence = 0.85 + hash(str(sid) + domain) % 15 * 0.005
            domain_layer.register_domain_correlation(
                symbol_id=sid, 
                domain=domain, 
                pattern_type="semantic_correlation",
                confidence=confidence
            )
    
    print("✅ Domain correlations registered!")
    print()
    
    # Add relationship chains
    print("🔗 Adding multi-hop relationship chains...")
    print()
    
    relationship_manager.add_relationship_chain(
        from_symbol=124, to_symbol=666,
        intermediate_symbols=[55, 279],
        chain_type="threshold_to_wholeness",
        confidence=0.87
    )
    
    relationship_manager.add_relationship_chain(
        from_symbol=963, to_symbol=111, 
        intermediate_symbols=[124],
        chain_type="spiritual_to_catalyst",
        confidence=0.85
    )
    
    print("✅ Relationship chains added!")
    print()
    
    # Test inference engine
    print("🧪 Testing multi-hop inference...")
    print()
    
    result = inference_engine.infer(
        starting_symbol=124,
        target_domains=["religious", "elemental"],
        max_hops=2
    )
    
    print(f"Starting Symbol: {result['starting_symbol']}")
    print(f"Target Domains: {', '.join(result['target_domains'])}")
    print(f"Paths Found: {len(result['paths_found'])}")
    
    if result["best_path"]:
        print(f"Best Path: {result['best_path']['from']} → {result['best_path']['to']}")
        print(f"Confidence: {result['best_path'].get('confidence', 0):.2f}")
    
    print()
    
    # Generate exports
    print("📄 Generating Obsidian exports...")
    print()
    
    obsidian_dir = OBSIDIAN_EXPORTS
    obsidian_dir.mkdir(parents=True, exist_ok=True)
    
    # Export 1: Symbol Definitions
    symbol_definitions = ObsidianExportLayer.generate_symbol_definitions()
    with open(obsidian_dir / "SYMBOL_DEFINITIONS.md", 'w') as f:
        f.write(symbol_definitions)
    print(f"✓ Generated SYMBOL_DEFINITIONS.md")
    
    # Export 2: Relationship Matrix  
    relationship_matrix = ObsidianExportLayer.generate_relationship_matrix()
    with open(obsidian_dir / "RELATIONSHIP_MATRIX.md", 'w') as f:
        f.write(relationship_matrix)
    print(f"✓ Generated RELATIONSHIP_MATRIX.md")
    
    # Export 3: Cross-Reference Report
    cross_ref = ObsidianExportLayer.generate_cross_reference_report()
    with open(obsidian_dir / "CROSS_REFERENCE_REPORT.md", 'w') as f:
        f.write(cross_ref)
    print(f"✓ Generated CROSS_REFERENCE_REPORT.md")
    
    print()
    print("=" * 60)
    print("✅ CROSS-SYMBOL TRANSLATION LAYER SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("📁 Exported files:")
    print(f"   - {obsidian_dir / 'SYMBOL_DEFINITIONS.md'}")
    print(f"   - {obsidian_dir / 'RELATIONSHIP_MATRIX.md'}")
    print(f"   - {obsidian_dir / 'CROSS_REFERENCE_REPORT.md'}")
    print()

if __name__ == "__main__":
    main()
