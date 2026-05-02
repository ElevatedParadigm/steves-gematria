#!/usr/bin/env python3
"""
🔄 Auto-Obsidian Sync v2 - Relationship Extraction Engine
==========================================================

Automated sync from gematria database to Obsidian notes format.
Generates relationship matrices and exports structured knowledge.

Integrates with overnight research loop for nightly updates.

Usage:
    python3 auto_obisidian_sync_v2.py [--validate] [--export PATH]

Output:
    - Relationship matrix files
    - Symbol definition notes
    - Force compatibility tables
    - Cross-domain synthesis reports

Phase marker format: === PHASE: AUTO_SYNC ===
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from collections import defaultdict
import re

# Auto-detect gematria directory
HERE = Path(__file__).resolve().parent.parent
GEMATRIA_DIR = HERE
DB_DIR = GEMATRIA_DIR / "database"
SYMBOLS_FILE = DB_DIR / "symbols.json"
FORCES_FILE = DB_DIR / "forces.json"
OBSIDIAN_EXPORT_DIR = GEMATRIA_DIR / "obsidian_exports"


class AutoObsidianSync:
    """Automated sync from gematria database to Obsidian notes"""
    
    def __init__(self, db_dir: Path, export_dir: Optional[Path] = None):
        self.db_dir = db_dir
        self.export_dir = export_dir or (GEMATRIA_DIR / "obsidian_exports")
        
        # Symbol and force data
        self.symbols = {}
        self.forces = {}
        
        # Relationship tracking
        self.relationships_extracted = 0
        self.matrices_generated = 0
        
        # Gematria directory for path resolution
        self.gematria_dir = GEMATRIA_DIR
        
        # Load database on init
        self.load_database()
    
    def load_database(self) -> None:
        """Load symbols and forces from database files"""
        
        if SYMBOLS_FILE.exists():
            try:
                with open(SYMBOLS_FILE, 'r') as f:
                    data = json.load(f)
                self.symbols = {s["symbol_id"]: s for s in data.get("analyzed_symbols", [])}
                print(f"✅ Loaded {len(self.symbols)} symbols from database")
            except Exception as e:
                print(f"⚠️ Error loading symbols: {e}")
                self.symbols = {}
        
        if FORCES_FILE.exists():
            try:
                with open(FORCES_FILE, 'r') as f:
                    data = json.load(f)
                self.forces = data.get("forces", {})
                print(f"✅ Loaded {len(self.forces)} forces from database")
            except Exception as e:
                print(f"⚠️ Error loading forces: {e}")
    
    def ensure_export_directory(self) -> Path:
        """Ensure export directory exists"""
        self.export_dir.mkdir(parents=True, exist_ok=True)
        return self.export_dir
    
    def generate_symbol_definitions(self) -> List[Path]:
        """Generate Obsidian notes for all symbols with YAML frontmatter"""
        
        print("\n" + "=" * 60)
        print("🔄 SYMBOL DEFINITIONS - Generating symbol notes")
        print("=" * 60)
        
        export_dir = self.ensure_export_directory()
        note_files = []
        
        for symbol_id, symbol in self.symbols.items():
            filename = self.export_dir / f"symbol_{symbol_id}.md"
            
            frontmatter = {
                "type": "core-symbol",
                "symbol_id": symbol.get("symbol_id"),
                "name": symbol.get("name", f"Symbol {symbol_id}"),
                "description": symbol.get("description", ""),
                "domains": symbol.get("domains", []),
                "elemental_force": symbol.get("elemental_force"),
                "confidence_score": symbol.get("confidence_score", 0),
                "created": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "tags": [f"symbol:{symbol_id}"] + symbol.get("aliases", []),
            }
            
            content = self._format_markdown(frontmatter, symbol)
            
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"   → Created: {filename.name}")
                note_files.append(filename)
                self.relationships_extracted += 1
                
            except Exception as e:
                print(f"   ❌ Error writing {filename.name}: {e}")
        
        print(f"\n✅ Generated {len(note_files)} symbol definition files")
        return note_files
    
    def generate_relationship_matrix(self) -> Path:
        """Generate relationship matrix file for all symbols"""
        
        print("\n" + "=" * 60)
        print("🔄 RELATIONSHIP MATRIX - Generating correlation matrix")
        print("=" * 60)
        
        export_dir = self.ensure_export_directory()
        matrix_file = export_dir / "relationships_matrix.md"
        
        # Build adjacency data for visualization
        adj_data = []
        
        for symbol_id, symbol in sorted(self.symbols.items()):
            relationships = symbol.get("relationships", [])
            
            for ref_id in relationships:
                if ref_id in self.symbols:
                    target_symbol = self.symbols[ref_id]
                    relationship_type = "direct"
                    
                    adj_data.append({
                        "from": symbol_id,
                        "to": ref_id,
                        "type": relationship_type,
                        "target_name": target_symbol.get("name", "")
                    })
        
        # Generate matrix visualization (ASCII)
        if len(adj_data) > 0:
            try:
                ascii_matrix = self._generate_ascii_matrix(adj_data, len(self.symbols))
                content = "---\ntype: relationships\n---\n\n# 🕸️ Symbol Relationship Matrix\n\n" + ascii_matrix
            except Exception as e:
                print(f"⚠️ ASCII matrix generation error (non-fatal): {e}")
                content = "---\ntype: relationships\n---\n\n# 🕸️ Symbol Relationship Matrix\n\n*" + str(len(adj_data)) + " direct relationships found*\n\nSee individual symbol notes for detailed relationship data."
        else:
            content = "---\ntype: relationships\n---\n\n# 🕉️ Symbol Relationships\n\nNo direct relationships found in current database.\n\n"
        
        try:
            with open(matrix_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   → Created: {matrix_file.name}")
            self.matrices_generated += 1
            self.relationships_extracted += len(adj_data)
            
        except Exception as e:
            print(f"❌ Error writing matrix file: {e}")
        
        return matrix_file
    
    def generate_force_compatibility_tables(self) -> List[Path]:
        """Generate compatibility tables for elemental forces"""
        
        print("\n" + "=" * 60)
        print("🔄 FORCE COMPATIBILITY - Generating force compatibility tables")
        print("=" * 60)
        
        export_dir = self.ensure_export_directory()
        table_files = []
        
        # Generate master compatibility table
        master_table_file = export_dir / "forces_compatibility.md"
        
        if len(self.forces) > 0:
            try:
                content = "---\ntype: elemental-force\n---\n\n# ⚡ Elemental Forces Compatibility Matrix\n\n### Force Definitions & Characteristics\n\n"
                
                for force_name, force_data in sorted(self.forces.items()):
                    emoji = ""
                    if "fire" in force_name: emoji = "🔥"
                    elif "earth" in force_name: emoji = "🌍"
                    elif "air" in force_name: emoji = "🌬️"
                    elif "water" in force_name: emoji = "💧"
                    elif "lightning" in force_name: emoji = "⚡"
                    elif "ice" in force_name: emoji = "❄️"
                    elif "wind" in force_name: emoji = "🌪️"
                    
                    content += f"\n#### {emoji} {force_data.get('name', force_name)}\n\n"
                    content += f"**Description:** {force_data.get('description', '')}\n\n"
                    
                    # Characteristics
                    chars = force_data.get("characteristics", [])
                    if chars:
                        content += "**Characteristics:** " + ", ".join(chars) + "\n\n"
                    
                    # Correlates to symbols
                    correlates = force_data.get("correlates_to", [])
                    if correlates:
                        related_sigs = [str(s) for s in correlates if s in self.symbols]
                        if related_sigs:
                            content += f"**Correlates:** {', '.join(f'S{sid}' for sid in relates)}\n\n"
                    
                    # Complements
                    complements = force_data.get("complements", [])
                    if complements:
                        complement_names = [self.forces[c].get('name', c) for c in complements if c in self.forces]
                        content += f"**Complements:** {', '.join(complement_names)}\n\n"
                
                content += "\n### Compatibility Scores\n\n"
                
                # Build compatibility matrix text representation
                force_names = sorted(self.forces.keys(), key=lambda x: 1000 if "primary" in self.forces.get(x, {}).get("element_type", "") else 0)
                
                for fn in force_names[:4]:  # Top 4 forces
                    fdata = self.forces[fn]
                    content += f"\n{fdata['name']}:\n"
                    
                    matrix_row = f"  {force_names[0]}: {self.forces.get(force_names[0], {}).get('complements', [])[0] if len(self.forces) > 1 else 'N/A'}\n"
                    content += matrix_row
                    
            except Exception as e:
                print(f"⚠️ Compatibility table error (non-fatal): {e}")
        
        else:
            content = "---\ntype: elemental-force\n---\n\n# ⚡ Elemental Forces\n\nNo force definitions available in current database.\n"
        
        try:
            with open(master_table_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   → Created: {master_table_file.name}")
            table_files.append(master_table_file)
            self.matrices_generated += 1
            
        except Exception as e:
            print(f"❌ Error writing compatibility table: {e}")
        
        return table_files
    
    def generate_cross_domain_synthesis(self) -> Path:
        """Generate cross-domain synthesis report"""
        
        print("\n" + "=" * 60)
        print("🔄 CROSS-DOMAIN SYNTHESIS - Generating domain synthesis")
        print("=" * 60)
        
        export_dir = self.ensure_export_directory()
        synthesis_file = export_dir / "cross_domain_synthesis.md"
        
        try:
            # Analyze symbols by domain
            domain_symbols = defaultdict(list)
            for symbol_id, symbol in self.symbols.items():
                for domain in symbol.get("domains", []):
                    domain_symbols[domain].append({
                        "symbol_id": symbol_id,
                        "name": symbol.get("name"),
                        "confidence": symbol.get("confidence_score", 0)
                    })
            
            # Build content
            dt = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
            content = """---
type: cross-domain-synthesis
---

# 🌐 Cross-Domain Symbol Synthesis Report

*Generated: {dt}*

## Domain Coverage
""".format(dt=dt)
            
            for domain, symbols in sorted(domain_symbols.items()):
                total_confidence = sum(s["confidence"] for s in symbols) / len(symbols) if symbols else 0
                content += f"- **{domain.title()}:** {len(symbols)} symbols (avg confidence: {total_confidence:.2f})\n"
            
            # Top Symbols by Confidence
            if domain_symbols:
                sorted_symbols = sorted(self.symbols.values(), key=lambda s: s.get("confidence_score", 0), reverse=True)
                for symbol in sorted_symbols[:5]:
                    conf = symbol.get("confidence_score", 0)
                    domains = ", ".join(symbol.get("domains", ["general"]))
                    content += f"- **{symbol['name']}** ({symbol.get('symbol_id')}): {conf:.2f} - {domains}\n"
            else:
                content += "\n*No domain data available*\n\n"
            
            content += "\n## Top Symbols by Confidence\n\n"
            
            sorted_symbols = sorted(self.symbols.values(), key=lambda s: s.get("confidence_score", 0), reverse=True)
            for symbol in sorted_symbols[:5]:
                conf = symbol.get("confidence_score", 0)
                domains = ", ".join(symbol.get("domains", ["general"]))
                content += f"- **{symbol['name']}** ({symbol.get('symbol_id')}): {conf:.2f} - {domains}\n"
            
            content += "\n## Cross-Domain Patterns\n\n"
            
            # Look for patterns where same symbols appear in multiple domains
            cross_domain_symbols = []
            for symbol in sorted(self.symbols.values()):
                if len(symbol.get("domains", [])) > 1:
                    cross_domain_symbols.append({
                        "name": symbol.get("name"),
                        "symbol_id": symbol.get("symbol_id"),
                        "domains": symbol.get("domains")
                    })
            
            for ps in cross_domain_symbols:
                content += f"- **{ps['name']}** appears in: {', '.join(ps['domains'])}\n"
            
            # Force-domain correlations
            force_domains = defaultdict(lambda: {"symbols": [], "confidence_sum": 0})
            for symbol in self.symbols.values():
                ef = symbol.get("elemental_force")
                if ef and ef in self.forces:
                    for domain in symbol.get("domains", []):
                        force_domains[ef]["symbols"].append(symbol.get("symbol_id"))
                        force_domains[ef]["confidence_sum"] += symbol.get("confidence_score", 0)
            
            # Convert defaultdict to regular dict for iteration
            force_domains = dict(force_domains)
            
            content += "\n## Force-Domain Correlations\n\n"
            for ef, data in sorted(force_domains.items()):
                avg_conf = data["confidence_sum"] / len(data["symbols"]) if data["symbols"] else 0
                content += f"- **{ef}:** {len(data['symbols'])} symbols (avg: {avg_conf:.2f})\n"
            
            with open(synthesis_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   → Created: {synthesis_file.name}")
            self.matrices_generated += 1
            
        except Exception as e:
            print(f"❌ Error writing synthesis file: {e}")
        
        return synthesis_file
    
    def generate_full_export(self, validate: bool = False) -> List[Path]:
        """Generate complete export including all note types"""
        
        print("\n🔄 AUTO-OBSIDIAN SYNC v2 - Starting full database export")
        print("=" * 60)
        
        export_dir = self.ensure_export_directory()
        
        generated_files = []
        
        # Load fresh data
        self.load_database()
        
        if validate:
            print("\n🔍 VALIDATION MODE - Verifying export integrity")
            
            for filepath in list(export_dir.glob("*.md")):
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                    
                    # Check for valid YAML frontmatter
                    if "---" not in content[:50]:
                        print(f"   ⚠️ {filepath.name}: Missing YAML frontmatter")
                    
                except Exception as e:
                    print(f"   ❌ Error reading {filepath.name}: {e}")
            
            print("\n✅ Validation complete")
        
        else:
            # Generate all exports
            print("\nGenerating exports...")
            
            files = []
            
            # Symbol definitions
            files.extend(self.generate_symbol_definitions())
            
            # Relationship matrix
            matrix_file = self.generate_relationship_matrix()
            files.append(matrix_file)
            
            # Force compatibility tables
            files.extend(self.generate_force_compatibility_tables())
            
            # Cross-domain synthesis
            synthesis_file = self.generate_cross_domain_synthesis()
            files.append(synthesis_file)
        
        print("\n" + "=" * 60)
        print("✅ AUTO-OBSIDIAN SYNC COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"Generated: {len(files)} files in {self.export_dir}")
        
        for fpath in sorted(files, key=lambda p: str(p)):
            rel_path = Path(fpath).relative_to(self.gematria_dir) if self.gematria_dir else Path(fpath)
            print(f"   → {rel_path}")
        
        return files
    
    def _format_markdown(self, frontmatter: Dict[str, Any], symbol_data: Dict[str, Any]) -> str:
        """Format markdown note with YAML frontmatter"""
        
        lines = []
        
        # YAML frontmatter
        lines.append("---")
        for key, value in sorted(frontmatter.items()):
            if isinstance(value, list):
                lines.append(f"{key}: |")
                lines.extend(f"  - {v}" for v in value)
            elif isinstance(value, dict):
                lines.append(f"{key}: |")
                for k2, v2 in sorted(value.items()):
                    lines.append(f"    {k2}: {v2}")
            else:
                lines.append(f"{key}: {value}")
        
        lines.append("---")
        lines.append("")
        
        # Content
        lines.append(f"# 🧪 {symbol_data.get('name', symbol_data.get('symbol_id'))}\n")
        
        description = symbol_data.get("description", "")
        if description:
            lines.append(description)
            lines.append("")
        
        # Add elemental force info if available
        ef = symbol_data.get("elemental_force")
        if ef and ef in self.forces:
            force_info = self.forces[ef]
            lines.append(f"**Elemental Force:** {force_info.get('name', '')} ({force_info.get('description', '')})\n")
        
        # Domains
        domains = symbol_data.get("domains", [])
        if domains:
            domain_str = ", ".join(d.capitalize() for d in domains)
            lines.append(f"**Domains:** {domain_str}\n")
        
        return "\n".join(lines)


def main():
    """Main entry point"""
    
    validate = False
    export_path = None
    
    # Parse arguments
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg.startswith("--validate"):
                validate = True
            elif arg.startswith("--export"):
                try:
                    export_path = Path(arg.split("=")[1])
                except (ValueError, IndexError):
                    print(f"⚠️ Invalid --export path: {arg}")
    
    # Run sync
    config = AutoObsidianSync(DB_DIR, export_path)
    files = config.generate_full_export(validate=validate)
    
    # Summary
    if validate:
        return 0
    
    print("\n" + "=" * 60)
    print("📊 EXPORT SUMMARY")
    print("=" * 60)
    print(f"Files generated: {len(files)}")
    print(f"Relationships extracted: {config.relationships_extracted}")
    print(f"Matrices generated: {config.matrices_generated}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
