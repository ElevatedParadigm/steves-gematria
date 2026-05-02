#!/usr/bin/env python3
#===============================================================================
# 🔥 GEMATRIA OBSIDIAN HYBRID ARCHITECTURE
#===============================================================================
# Author: Steve & Avalon  
# Purpose: Multi-agent relationship tracking with Obsidian integration  
# Version: 1.0

import os, sys, json, re, hashlib, datetime, shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
# Try both possible database locations
DB_PATH = SCRIPT_DIR.parent / "gematria_database.json"  # First, try relative path
if not DB_PATH.exists():
    fallback_db = "/home/avalonas/.hermes/gematria/gematria_database.json"
    if os.path.exists(fallback_db):
        DB_PATH = Path(fallback_db)
    else:
        # Fallback to root
        GEMATRIA_ROOT = SCRIPT_DIR.parent.parent.parent
        DB_PATH = GEMATRIA_ROOT / "gematria_database.json"

OBSIDIAN_EXPORTS = SCRIPT_DIR.parent / "obsidian_exports"
if not OBSIDIAN_EXPORTS.exists():
    fallback_exports = "/home/avalonas/.hermes/gematria/obsidian_exports"
    if os.path.exists(fallback_exports):
        OBSIDIAN_EXPORTS = Path(fallback_exports)
else:
    if not OBSIDIAN_EXPORTS.exists():
        OBSIDIAN_EXPORTS.mkdir(parents=True, exist_ok=True)

LOG_DIR = SCRIPT_DIR.parent / "logs"
if not LOG_DIR.exists():
    fallback_logs = "/home/avalonas/.hermes/gematria/logs"
    if os.path.exists(fallback_logs):
        LOG_DIR = Path(fallback_logs)

# Use parent directory as vault for Obsidian settings
OBSIDIAN_VAULT = SCRIPT_DIR.parent.parent.parent

# Ensure directories exist
(OBSIDIAN_EXPORTS / "relations").mkdir(parents=True, exist_ok=True)
(LOG_DIR).mkdir(exist_ok=True)

#===============================================================================
# 🔧 CONFIGURATION
#===============================================================================
CONFIG = {
    "obsidian": {
        "vault": str(OBSIDIAN_VAULT),
        "exports": str(OBSIDIAN_EXPORTS),
        "relations_dir": "obsidian_exports/relations",
        "sync_frequency": 3600,  # seconds
    },
    "agents": {
        "pattern_detector": {
            "name": "PatternDetector",
            "role": "detects numerical patterns across domains",
            "capabilities": ["gematria_detection", "domain_analysis"]
        },
        "relationship_mapper": {
            "name": "RelationshipMapper", 
            "role": "maps connections between patterns and symbols",
            "capabilities": ["cross_reference", "relevance_scoring"]
        },
        "temporal_analyzer": {
            "name": "TemporalAnalyzer",
            "role": "tracks timeline sequences and historical patterns",  
            "capabilities": ["timeline_detection", "sequence_analysis"]
        }
    },
    "core_symbols": [124, 963, 55, 111, 279, 666, 2727],
    "domains": ["political_events", "military_coup_themes", "religious_symbolism", 
                "cryptocurrency", "literary_gothic", "esoteric_hex"]
}

#===============================================================================
# 📚 AGENT CLASS DEFINITIONS
#===============================================================================

class PatternDetectorAgent:
    """Detects numerical patterns and domain connections"""
    
    def __init__(self, database):
        self.db = database
    
    def detect(self, item_id: str) -> Dict:
        """Detect gematria patterns in an item"""
        analysis_type = "pattern_detection"
        
        # Simulate detection (would scan actual web content in production)
        detected_patterns = []
        relevance_scores = {
            "military": round((hashlib.md5(item_id.encode()).hexdigest()[-1] - ord('a')) % 100 + 50, 2),
            "religious": round((hashlib.sha1(item_id.encode()).hexdigest()[-1] - ord('a')) % 100 + 30, 2),
            "elemental": round((hashlib.blake2b(item_id.encode()).hexdigest()[-1] - ord('a')) % 100 + 40, 2),
            "politics": round((hashlib.sha256(item_id.encode()).hexdigest()[-1] - ord('a')) % 100 + 60, 2)
        }
        
        return {
            "analysis_type": analysis_type,
            "status": "active",
            "timestamp": datetime.datetime.now().isoformat(),
            "patterns_found": detected_patterns,
            "domain_connections": relevance_scores,
            "symbols_detected": []  # Would be populated from actual scan
        }

class RelationshipMapperAgent:
    """Maps relationships between patterns and symbols"""
    
    def __init__(self, database):
        self.db = database
        self.relation_counter = 0
    
    def map_relationships(self, item_id: str, detector_result: Dict) -> List[Dict]:
        """Cross-reference patterns with other items"""
        
        relationships = []
        core_symbols = CONFIG["core_symbols"]
        
        for symbol_id in core_symbols:
            if symbol_id in self.db.get("symbols", {}):
                # Generate relationship suggestion
                rel_strength = round(detector_result["domain_connections"]["military"] / 100 * 20, 2)
                
                relationships.append({
                    "id": f"rel_{self.relation_counter:04d}",
                    "symbol_id": str(symbol_id),
                    "symbol_name": self.db["symbols"][str(symbol_id)].get("name", ""),
                    "connection_type": "cross_reference",
                    "relevance_score": round(detector_result["domain_connections"]["military"], 2),
                    "description": f"Pattern connection between {item_id} and symbol {symbol_id}"
                })
                self.relation_counter += 1
        
        return relationships

class TemporalAnalyzerAgent:
    """Tracks timeline sequences and historical patterns"""
    
    def __init__(self, database):
        self.db = database
    
    def analyze_temporal_patterns(self, items: List[Dict]) -> Dict:
        """Analyze temporal sequences across items"""
        
        sequences = []
        timestamps = {}
        
        for item in items:
            ts = item.get("timestamp", "")
            if ts:
                try:
                    dt = datetime.datetime.fromisoformat(ts)
                    timestamp_key = dt.strftime("%Y-%W")  # Year-Week format
                    if timestamp_key not in timestamps:
                        timestamps[timestamp_key] = []
                    timestamps[timestamp_key].append(item)
                except:
                    pass
        
        for week, items_in_week in timestamps.items():
            sequences.append({
                "week": week,
                "items_count": len(items_in_week),
                "symbol_distribution": self._count_symbols(items_in_week)
            })
        
        return {
            "analysis_type": "temporal_sequence",
            "status": "active", 
            "sequences_found": sequences,
            "total_items_analyzed": len(items)
        }
    
    def _count_symbols(self, items):
        counts = {}
        for item in items:
            sym_ids = [s["symbol_id"] for s in item.get("symbols_detected", [])]
            for sid in sym_ids:
                counts[sid] = counts.get(sid, 0) + 1
        return counts

#===============================================================================
# 🏗️ OBSIDIAN HYBRID ARCHITECTURE (MAIN ENGINE)
#===============================================================================

class ObsidianHybridArchitecture:
    """Implements multi-agent relationship tracking with Obsidian integration"""
    
    def __init__(self):
        self.database = load_database()
        self.detector = PatternDetectorAgent(self.database)
        self.mapper = RelationshipMapperAgent(self.database)
        self.temporal = TemporalAnalyzerAgent(self.database)
        self.exported_items = {}
        
        print("=" * 60)
        print("🔥 OBSIDIAN HYBRID ARCHITECTURE INITIALIZED")
        print("  PatternDetector + RelationshipMapper + TemporalAnalyzer")
        print("=" * 60)
    
    def process_item(self, item_id: str) -> Tuple[Dict, List[Dict], Dict]:
        """Run full multi-agent analysis on an item"""
        
        # Step 1: Pattern detection
        detector_result = self.detector.detect(item_id)
        
        # Step 2: Relationship mapping  
        relationships = self.mapper.map_relationships(item_id, detector_result)
        
        # Step 3: Temporal analysis (on batch of items)
        sample_items = list(self.database.get("analyzed_items", {}).values())[:5]
        temporal_result = self.temporal.analyze_temporal_patterns(sample_items)
        
        return detector_result, relationships, temporal_result
    
    def export_to_obsidian(self, item_id: str) -> str:
        """Export analysis to Obsidian format"""
        
        # Process through all agents
        detector_result, relationships, temporal_result = self.process_item(item_id)
        
        # Update database with results
        self.database["analyzed_items"][item_id] = {
            "symbol_id": item_id.split("_")[-1] if "_" in item_id else item_id,
            "symbol_name": f"pattern_{item_id}",
            "analysis_type": detector_result["analysis_type"],
            "status": detector_result["status"],
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Export main analysis
        export_path = OBSIDIAN_EXPORTS / f"{item_id.upper().replace('-', '_')}.md"
        
        self.export_main_analysis(export_path, detector_result, relationships)
        self.export_relationships(relationships, item_id)
        
        # Log completion
        log_file = LOG_DIR / "hybrid_architecture.log"
        with open(log_file, "a") as f:
            f.write(f"[{datetime.datetime.now().isoformat()}] Exported {item_id} to Obsidian format\n")
        
        return str(export_path)
    
    def export_main_analysis(self, path: Path, detector_result: Dict, relationships: List):
        """Export main analysis markdown"""
        
        detector = self.detector
        
        with open(path, "w") as f:
            f.write("# 🔥 Pattern Analysis: ")
            f.write(str(path.stem) + "\n\n")
            
            if detector_result.get("status") == "active":
                f.write("**Status**: ✅ Active\n\n")
            else:
                f.write("**Status**: ⚠️ Incomplete\n\n")
            
            f.write(f"**Analysis Type**: {detector_result['analysis_type']}\n")
            f.write(f"**Timestamp**: {detector_result.get('timestamp', '')}\n\n")
            
            # Domain connections table
            connections = detector_result.get("domain_connections", {})
            f.write("| Domain | Relevance Score |\n")
            f.write("|--------|-----------------|\n")
            
            for domain, score in sorted(connections.items(), key=lambda x: -x[1]):
                # Handle both int and float scores
                score_num = float(score) if isinstance(score, (int, float)) else 0.0
                bar_width = int(min(20, max(0, score_num / 5))) % 20
                bars = "█" * bar_width + "." if bar_width else "."
                f.write(f"| {domain} | {bars:20} ({score:.1f}) |\n")
            
            f.write("\n---\n")
            f.write("## Related Symbols\n\n")
            core_symbols = CONFIG["core_symbols"]
            
            for symbol_id in core_symbols:
                if symbol_id in self.database.get("symbols", {}):
                    sym_name = self.database["symbols"][str(symbol_id)].get("name", "Unnamed")
                    f.write(f"- **{symbol_id}**: {sym_name}\n")
            
            f.write("\n---\n")
            f.write("*Generated by Obsidian Hybrid Architecture*\n")
    
    def export_relationships(self, relationships: List, item_id: str):
        """Export relationship details to separate files"""
        
        with open(OBSIDIAN_EXPORTS / "RELATIONSHIPS.md", "a") as f:
            for rel in relationships[:10]:  # Top 10 most relevant
                score = rel["relevance_score"]
                bars_width = int(min(15, max(0, float(score) * 2))) % 15
                bars = "█" * bars_width + "." if bars_width else "."
                
                f.write(f"## {rel['id']}\n\n")
                f.write(f"**Symbol**: `{rel['symbol_id']}` - {rel['symbol_name']}\n")
                f.write(f"**Connection Type**: {rel['connection_type']}\n")
                f.write(f"**Relevance Score**: {bars:15} ({score:.2f})\n\n")
                f.write(f"*Description*: {rel['description']}\n\n")
    
    def run_batch_sync(self):
        """Synchronize all unexported items from database"""
        
        items = list(self.database.get("analyzed_items", {}).values())
        exported_ids = set([p.stem.lower() for p in OBSIDIAN_EXPORTS.glob("*.md")])
        
        print(f"🔍 Found {len(items)} items in database...")
        print(f"   Exported to Obsidian: {len(exported_ids)} items\n")
        
        # Find unexported items
        pending = []
        for item in items:
            key = f"{item['symbol_id']}".lower().replace("-", "_").replace(" ", "_")
            if key not in exported_ids:
                pending.append(item)
        
        print(f"⏳ Pending export: {len(pending)} items\n")
        
        # Export unexported items (limit to 5 for demo)
        for i, item in enumerate(pending[:5]):
            export_id = f"pattern_{item['symbol_id']}"
            print(f"[{i+1}/{min(5, len(pending))}] Processing {export_id}...")
            
            try:
                path = self.export_to_obsidian(export_id)
                print(f"   ✅ Exported to: {path}")
            except Exception as e:
                print(f"   ⚠️  Error exporting {export_id}: {e}")
        
        return len(pending[:5])

#===============================================================================
# 🚀 ENTRY POINT
#===============================================================================

def load_database() -> Dict:
    """Load database from JSON file"""
    if not DB_PATH.exists():
        print(f"📁 Creating new database at {DB_PATH}...")
        
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        initial_db = {
            "metadata": {
                "database_name": "Steve's Gematria Database",
                "version": "2.1",
                "maintainers": ["Avalon", "Steve"],
                "location": str(GEMATRIA_ROOT),
                "last_updated": datetime.datetime.now().isoformat(),
                "schema_version": 2.1,
                "core_symbols": CONFIG["core_symbols"],
            },
            "analyzed_items": {},
            "symbols": {}
        }
        
        with open(DB_PATH, "w") as f:
            json.dump(initial_db, f, indent=2)
        
    with open(DB_PATH, "r") as f:
        return json.load(f)

def main():
    print("=" * 60)
    print("🔥 OBSIDIAN HYBRID ARCHITECTURE - GEMATRIA SYSTEM")
    print("=" * 60)
    
    architecture = ObsidianHybridArchitecture()
    
    print("\n✅ Architecture initialized successfully")
    print(f"   Database: {DB_PATH}")
    print(f"   Obsidian exports: {OBSIDIAN_EXPORTS}\n")
    
    # Run batch sync to export all unexported items
    exported = architecture.run_batch_sync()
    
    print("\n" + "=" * 60)
    print("🎉 OBSIDIAN HYBRID ARCHITECTURE COMPLETED!")
    print("=" * 60)
    print(f"\n✅ Exported {exported} items to Obsidian format")
    print(f"📂 Location: {OBSIDIAN_EXPORTS}")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
