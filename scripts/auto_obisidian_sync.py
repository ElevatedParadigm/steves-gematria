#!/usr/bin/env python3
"""
Obsidian Auto-Sync - Automated Knowledge Graph Maintenance
This script runs in the background to continuously maintain and update
the Obsidian knowledge graph with relationships between core symbols,
domain convergences, and pattern matrices.

Usage: Add to crontab to run every hour or overnight
        0 * * * * cd /home/avalonas/.hermes/gematria && python scripts/auto_obsidian_sync.py
"""

import json
import os
from datetime import datetime
from pathlib import Path
import sys

# Import from gematria-analysis-workflow for data access
try:
    from gematria_analysis_workflow import (
        core_symbols_db,
        domain_convergence_tracker,
        pattern_matrix_analyzer
    )
except ImportError:
    # Fallback if not yet installed
    print("Installing gematria dependencies...")
    os.system("pip install -q pydantic")

from typing import List, Dict, Any

class ObsidianSyncEngine:
    """Automated Obsidian knowledge graph synchronization engine"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.sync_dir = Path("/home/avalonas/.hermes/gematria/obsidian_exports")
        self.sync_dir.mkdir(parents=True, exist_ok=True)
        
        # Relationship tracking
        self.rel_matrix_file = self.sync_dir / "RELATIONSHIP_MATRIX.md"
        self.cross_ref_index = self.sync_dir / "CROSS_REFERENCE_INDEX.md"
        self.change_log = self.sync_dir / ".SYNC_LOG.md"
        
    def load_database(self) -> Dict:
        """Load the core gematria database"""
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARNING] Database not found or corrupted: {e}")
            return {}
    
    def extract_relationships(self, db: Dict) -> List[Dict]:
        """Extract all relationships between symbols, domains, and patterns"""
        relationships = []
        
        # 1. Core Symbol Relationships
        for symbol_name, occurrences in db.get("core_symbols", {}).items():
            for occurrence in occurrences.get("occurrences", []):
                # Find related domains
                if "keywords" in occurrence:
                    for keyword in occurrence["keywords"]:
                        relationships.append({
                            "type": "keyword_association",
                            "source": symbol_name,
                            "target": f"#domain-{keyword.lower()}",
                            "weight": 1.0,
                            "context": occurrence.get("text")
                        })
                
                # Find related high-impact patterns
                for hi_impact in db.get("high_impact", {}).values():
                    if any(keyword in keyword.lower() for keyword in hi_impact.get("keywords", [])):
                        relationships.append({
                            "type": "high_impact_link",
                            "source": symbol_name,
                            "target": f"#high-impact-{hi_impact['symbol']}",
                            "weight": 0.8,
                            "context": hi_impact.get("text")
                        })
        
        # 2. Domain Convergence Relationships
        for domain, analysis in db.get("domain_convergence", {}).items():
            related_symbols = analysis.get("related_symbols", [])
            for symbol_name, count in related_symbols.items():
                relationships.append({
                    "type": "domain_connection",
                    "source": f"#domain-{domain.lower()}",
                    "target": symbol_name,
                    "weight": count / 10.0,  # Normalize by frequency
                    "context": analysis.get("analysis")
                })
        
        # 3. Pattern Matrix Relationships
        matrix_data = db.get("pattern_matrix", {})
        for pattern_type, data in matrix_data.items():
            symbols_in_pattern = data.get("symbols", [])
            if len(symbols_in_pattern) >= 2:
                for i, sym1 in enumerate(symbols_in_pattern):
                    for sym2 in symbols_in_pattern[i+1:]:
                        relationships.append({
                            "type": "matrix_correlation",
                            "source": f"#matrix-{pattern_type.lower()}",
                            "target": f"{sym1} ↔ {sym2}",
                            "weight": 0.9,
                            "context": data.get("description")
                        })
        
        return relationships
    
    def extract_cross_references(self, db: Dict) -> List[Dict]:
        """Extract cross-references for the index"""
        cross_refs = []
        
        # Cross-reference core symbols with domains
        for symbol_name, occurrences in db.get("core_symbols", {}).items():
            symbol_data = occurrences
            
            # Find matching domains
            domain_matches = [domain for domain, analysis 
                            in db.get("domain_convergence", {}).items() 
                            if any(symbol_name.lower() in str(v).lower() 
                                  for v in analysis.values())]
            
            if domain_matches:
                cross_refs.append({
                    "symbol": symbol_name,
                    "domains": ", ".join(domain_matches),
                    "frequency": occurrences.get("total_frequency", 0)
                })
        
        # Cross-reference high-impact symbols
        for hi_impact in db.get("high_impact", {}).values():
            related_symbols = []
            all_symbols = list(db.get("core_symbols", {}).keys())
            for sym in all_symbols:
                if any(term in term.lower() for term in hi_impact.get("keywords", [])):
                    related_symbols.append(sym)
            
            if related_symbols:
                cross_refs.append({
                    "symbol": hi_impact["symbol"],
                    "category": hi_impact.get("category", "High Impact"),
                    "related_to": ", ".join(related_symbols[:5]),  # Top 5
                    "relevance_score": hi_impact.get("relevance_score", 0)
                })
        
        return cross_refs
    
    def update_relationship_matrix(self, relationships: List[Dict]):
        """Update the relationship matrix markdown file"""
        self.rel_matrix_file.parent.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.rel_matrix_file, 'w') as f:
            f.write(f"# 🔗 Relationship Matrix\n\n")
            f.write(f"**Auto-synced:** {timestamp}\n\n")
            f.write(f"> **This document tracks all known relationships**\n\n")
            
            # Summary statistics
            total_rels = len(relationships)
            relation_types = set(r["type"] for r in relationships)
            unique_symbols = set()
            
            for r in relationships:
                unique_symbols.add(r["source"])
                unique_symbols.add(r["target"])
            
            f.write(f"## 📊 Statistics\n\n")
            f.write(f"- **Total Relationships:** `{total_rels}`\n")
            f.write(f"- **Relationship Types:** {', '.join(relation_types)}\n")
            f.write(f"- **Entities Involved:** `{len(unique_symbols)}`\n\n")
            
            # Relationship breakdown by type
            for rel_type in sorted(relation_types):
                type_rels = [r for r in relationships if r["type"] == rel_type]
                f.write(f"## {rel_type.upper().replace('_', ' ')}\n\n")
                
                # Group by source symbol
                by_source = {}
                for r in type_rels:
                    source = r["source"]
                    if source not in by_source:
                        by_source[source] = []
                    by_source[source].append(r)
                
                f.write(f"### {len(by_source)} source entities\n\n")
                
                for source, links in list(sorted(by_source.items()))[:10]:  # Top 10
                    targets = [f"- [`{r['target']}`({r['weight']:.2f})]({r['target']})" 
                              for r in links[:3]]  # Top 3 per source
                    f.write(f"**`{source}`** →\n")
                    if targets:
                        f.write("\n".join(targets))
                    f.write("\n\n")
            
            f.write("---\n\n")
            f.write("> *This matrix updates automatically. Relationships detected from*\n")
            f.write(f"> `- {total_rels} ` total connections across the knowledge base.*\n")
    
    def update_cross_reference_index(self, cross_refs: List[Dict]):
        """Update the cross-reference index"""
        self.cross_ref_index.parent.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.cross_ref_index, 'w') as f:
            f.write(f"# 📚 Cross-Reference Index\n\n")
            f.write(f"**Last updated:** {timestamp}\n\n")
            
            # Core symbols index
            f.write("## 🔢 Core Symbols Index\n\n")
            
            sorted_refs = sorted(cross_refs, 
                               key=lambda x: x.get("frequency", 0) or x.get("relevance_score", 0), 
                               reverse=True)
            
            for ref in sorted_refs[:20]:  # Top 20 cross-refs
                symbol = ref.get("symbol", "Unknown")
                frequency = ref.get("frequency", "?")
                
                if "domains" in ref:
                    f.write(f"- [`{symbol}`](./core_symbols_summmary.md#--{symbol.lower().replace(' ', '-')})\n      {ref['domains']}\n\n")
                elif "category" in ref:
                    f.write(f"- **`{symbol}`** (`{ref['category']}`)\n    ↔️ {ref['related_to'][:50]}...\n\n")
            
            f.write("---\n\n")
            f.write(f"> *Index contains `{len(cross_refs)}` total cross-references.*\n")
    
    def update_sync_log(self, db: Dict):
        """Update the change log"""
        self.change_log.parent.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_symbols = len(db.get("core_symbols", {}))
        total_domains = len(db.get("domain_convergence", {}))
        high_impact_count = len(db.get("high_impact", {}))
        
        with open(self.change_log, 'w') as f:
            f.write(f"## 📝 Obsidian Sync Log\n\n")
            f.write(f"**Last sync:** {timestamp}\n\n")
            
            f.write(f"### Current State\n\n")
            f.write(f"- **Core Symbols tracked:** `{total_symbols}`\n")
            f.write(f"- **Domain Convergences tracked:** `{total_domains}`\n")
            f.write(f"- **High-Impact Patterns:** `{high_impact_count}`\n\n")
            
            # Recent changes (would need version tracking for full history)
            f.write("---\n\n")
            f.write("> *Check `RELATIONSHIP_MATRIX.md` and `CROSS_REFERENCE_INDEX.md`\n")
            f.write(f"> for the latest knowledge graph updates.*\n")
    
    def run_auto_sync(self):
        """Main sync routine"""
        print("\n" + "="*60)
        print("🔄 OBSIDIAN AUTO-SYNC RUNNING")
        print("="*60)
        
        db = self.load_database()
        
        if not db:
            print("[ERROR] Could not load database. Exiting.")
            return
        
        print(f"[INFO] Database loaded: {len(db.get('core_symbols', {}))} core symbols")
        
        relationships = self.extract_relationships(db)
        print(f"[INFO] Extracted {len(relationships)} relationships")
        
        cross_refs = self.extract_cross_references(db)
        print(f"[INFO] Extracted {len(cross_refs)} cross-references")
        
        self.update_relationship_matrix(relationships)
        print(f"[✓] Updated RELATIONSHIP_MATRIX.md")
        
        self.update_cross_reference_index(cross_refs)
        print(f"[✓] Updated CROSS_REFERENCE_INDEX.md")
        
        self.update_sync_log(db)
        print(f"[✓] Updated .SYNC_LOG.md")
        
        print("="*60 + "\n")


def main():
    """Main entry point"""
    db_path = "/home/avalonas/.hermes/gematria/gematria_database.json"
    
    if not os.path.exists(db_path):
        print(f"[ERROR] Database not found: {db_path}")
        print("[INFO] Run overnight_research.py first to generate database")
        return
    
    engine = ObsidianSyncEngine(db_path)
    engine.run_auto_sync()


if __name__ == "__main__":
    main()
