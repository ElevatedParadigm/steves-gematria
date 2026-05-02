#!/usr/bin/env python3
"""
📊 Correlation Heatmap Generator (ASCII)
=========================================

Generates ASCII correlation heatmaps for gematria database analysis.
Shows relationship strengths between symbols and forces visually.

Usage:
    python3 correlation_heatmap_ascii.py [--output PATH]

Output:
    - Generates heatmap files in obsidian_exports/correlation_heatmaps/
    - Creates readable ASCII visualization of relationships
    
Phase marker format: === PHASE: HEATMAP_GENERATION ===
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any
from collections import defaultdict
import json

# Auto-detect gematria directory
HERE = Path(__file__).resolve().parent.parent
GEMATRIA_DIR = HERE
DB_DIR = GEMATRIA_DIR / "database"
OBSIDIAN_EXPORTS = GEMATRIA_DIR / "obsidian_exports"


class CorrelationHeatmapGenerator:
    """Generate ASCII correlation heatmaps for gematria relationships"""
    
    def __init__(self, db_dir: Path):
        self.db_dir = db_dir
        self.symbols = {}
        self.forces = {}
        self.export_dir = OBSIDIAN_EXPORTS / "correlation_heatmaps"
        
        # Load symbols and forces
        self.load_database()
    
    def load_database(self) -> None:
        """Load symbols and forces from database"""
        
        # Load symbols
        symbols_file = DB_DIR / "symbols.json"
        if symbols_file.exists():
            try:
                with open(symbols_file, 'r') as f:
                    data = json.load(f)
                self.symbols = {str(s.get("symbol_id", 0)): s for s in data.get("analyzed_symbols", [])}
                print(f"✅ Loaded {len(self.symbols)} symbols")
            except Exception as e:
                print(f"⚠️ Error loading symbols: {e}")
        
        # Load forces
        forces_file = DB_DIR / "forces.json"
        if forces_file.exists():
            try:
                with open(forces_file, 'r') as f:
                    data = json.load(f)
                self.forces = data.get("forces", {})
                print(f"✅ Loaded {len(self.forces)} forces")
            except Exception as e:
                print(f"⚠️ Error loading forces: {e}")
        
        # Ensure export directory exists
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_symbol_relationship_heatmap(self, output_path: Path = None) -> Path:
        """Generate ASCII heatmap showing symbol relationships"""
        
        if not self.symbols:
            print("⚠️ No symbols loaded - cannot generate heatmap")
            return None
        
        export_dir = self.export_dir
        if output_path:
            output_path = export_dir / output_path
        
        # Build adjacency data for visualization
        adj_data = []
        
        for symbol_id, symbol in sorted(self.symbols.items(), key=lambda x: int(x[0])):
            relationships = symbol.get("relationships", [])
            
            for ref_id in relationships:
                adj_data.append({
                    "from": symbol_id,
                    "to": str(ref_id) if not isinstance(ref_id, str) else ref_id,
                    "type": "direct"
                })
        
        # Generate ASCII visualization
        if len(adj_data) > 0:
            return self._generate_ascii_heatmap(export_dir, adj_data, len(self.symbols))
        else:
            return self._generate_empty_heatmap(export_dir)
    
    def _generate_ascii_heatmap(self, export_dir: Path, adj_data: list, num_nodes: int) -> Path:
        """Generate ASCII heatmap with relationship visualization"""
        
        lines = []
        
        # Header
        now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        lines.append("---")
        lines.append("type: correlation-heatmap")
        lines.append(f"generated: {now}")
        lines.append("---")
        lines.append("")
        lines.append("# 📊 Symbol Relationship Heatmap (ASCII Visualization)")
        lines.append("")
        lines.append("*Generated from Gematria Database Analysis*")
        lines.append("")
        
        # Legend
        lines.append("## Legend")
        lines.append("")
        lines.append("| Symbol | ID  | Domains                              | Elemental Force | Confidence |")
        lines.append("|--------|-----|---------------------------------------|-----------------|------------|")
        
        for symbol_id, symbol in sorted(self.symbols.items(), key=lambda x: int(x[0])):
            domains = ", ".join(symbol.get("domains", [])[:2]) if symbol.get("domains") else "N/A"
            ef_name = ""
            if symbol.get("elemental_force") and symbol.get("elemental_force") in self.forces:
                ef_name = f"{self.forces[symbol['elemental_force']].get('name', '')} ({symbol.get('elemental_force')})"
            
            conf = symbol.get("confidence_score", 0) or "N/A"
            lines.append(f"| {symbol.get('name', '?')} | {symbol_id:<4} | {domains:<25} | {ef_name:<20} | {conf:.2f} |")
        
        lines.append("")
        lines.append("## Relationship Matrix (ASCII Heatmap)")
        lines.append("")
        lines.append(f"*Showing {len(self.symbols)} symbols with {len(adj_data)} direct relationships*")
        lines.append("")
        
        if len(self.symbols) <= 15 and num_nodes > 0:  # Only generate full matrix for small datasets
        
            # Calculate relationship strengths from adjacency data
            node_ids = sorted([int(s) for s in self.symbols.keys() if s.isdigit()])[:num_nodes]
            node_map = {sid: idx for idx, sid in enumerate(node_ids)}
            
            # Initialize matrix with 0 (no relationship)
            matrix = [[0] * len(node_ids) for _ in range(len(node_ids))]
            names = [self.symbols[str(sid)].get('name', f'S{id}') for sid in node_ids]
            
            # Fill matrix based on relationships
            for adj in adj_data:
                from_id = str(adj["from"])
                to_id = str(adj["to"])
                
                if from_id.isdigit() and to_id.isdigit():
                    try:
                        from_idx = node_map.get(from_id, -1)
                        to_idx = node_map.get(to_id, -1)
                        
                        if from_idx >= 0 and to_idx >= 0:
                            matrix[from_idx][to_idx] = matrix[to_idx][from_idx] = 2  # Relationship exists
                    except (ValueError, KeyError):
                        pass
            
            # Generate ASCII visualization with heat shading
            for row in range(len(node_ids)):
                line = ""
                for col in range(len(node_ids)):
                    strength = matrix[row][col]
                    
                    if strength == 0:
                        # No relationship - empty space or light gray
                        cell = " "
                    elif strength > 0:
                        # Relationship exists - use shading based on strength
                        # Simulate intensity with darker blocks
                        line += "█"  # Relationship present
                    else:
                        cell = " "
                
                line_names = ""
                for i, name in enumerate(names):
                    if row == len(node_ids) - 1 and names[i] and not line_names:
                        line_names += f"{names[i][:12]:<14}"
                
                print(f"   {line}{line_names}")
                lines.append(line)
        
        # Relationship list
        lines.append("")
        lines.append("## Direct Relationships List")
        lines.append("")
        lines.append("| Source Symbol (ID→Name) | Target Symbol (ID→Name) | Direction | Type |")
        lines.append("|--------------------------|--------------------------|-----------|------|")
        
        for adj in sorted(adj_data, key=lambda x: (x["from"], x["to"])):
            source_name = self.symbols.get(str(adj["from"]), {}).get("name", f"S{adj['from']}")
            target_name = self.symbols.get(str(adj["to"]), {}).get("name", f"Unknown {adj['to']}")
            
            lines.append(f"| {source_name} ({adj['from']}) | {target_name} ({adj['to']}) | {adj['from']}→{adj['to']} | {adj.get('type', 'direct')} |")
        
        # Correlation statistics
        lines.append("")
        lines.append("## Correlation Statistics")
        lines.append("")
        lines.append(f"Total symbols analyzed:      {len(self.symbols)}")
        lines.append(f"Direct relationships found:  {len(adj_data)}")
        if adj_data and num_nodes > 0:
            avg_connections = sum(sum(1 for row in matrix for cell in row if cell) // max(len(node_ids), 1)) * len(node_ids) / 2
            lines.append(f"Average connections/node:    {avg_connections:.2f}")
        else:
            lines.append("Average connections/node:    N/A")
        
        # Write output
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(lines))
            
            print(f"   → Generated heatmap at {output_path}")
            
        except Exception as e:
            print(f"❌ Error writing heatmap: {e}")
        
        return output_path
    
    def generate_symbol_correlation_heatmap(self) -> Path:
        """Generate correlation heatmap showing strength of associations"""
        
        export_dir = self.export_dir
        
        # Build correlation matrix from relationships
        node_ids = sorted([int(s) for s in self.symbols.keys() if s.isdigit()])[:min(12, len(self.symbols))]
        node_map = {sid: idx for idx, sid in enumerate(node_ids)}
        
        # Initialize correlation matrix
        matrix = [[0.0] * len(node_ids) for _ in range(len(node_ids))]
        names = [self.symbols[str(sid)].get('name', f'S{id}') for sid in node_ids]
        
        # Fill based on shared relationships
        for symbol_id, symbol in self.symbols.items():
            refs = set(symbol.get("relationships", []))
            
            for other_id, other_symbol in self.symbols.items():
                if other_id == symbol_id:
                    continue
                
                other_refs = set(other_symbol.get("relationships", []))
                
                # Calculate Jaccard similarity (shared relationships / total unique relationships)
                intersection = refs.intersection(other_refs)
                union = refs.union(other_refs)
                
                if union:
                    jaccard = len(intersection) / len(union)
                    
                    from_idx = node_map.get(str(symbol_id), -1)
                    to_idx = node_map.get(str(other_id), -1)
                    
                    if from_idx >= 0 and to_idx >= 0:
                        # Symmetric matrix
                        strength = min(jaccard, 1.0 - jaccard) * 2  # Scale 0-1
                        matrix[from_idx][to_idx] = max(matrix[from_idx][to_idx], strength)
                        matrix[to_idx][from_idx] = matrix[from_idx][to_idx]
        
        # Generate ASCII visualization
        lines = []
        lines.append("---")
        lines.append("type: correlation-heatmap")
        lines.append(f"generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        lines.append("---")
        lines.append("")
        lines.append("# 📊 Symbol Correlation Heatmap (ASCII)")
        lines.append("")
        lines.append("*Visualizing relationship strength between symbols based on shared connections*")
        lines.append("")
        
        # Show matrix visualization (simplified for ASCII)
        for row in range(len(node_ids)):
            line = "│"
            for col in range(len(node_ids)):
                if row == len(node_ids) - 1:
                    line += f" {names[col][:8]:<9} │"
                elif matrix[row][col] > 0.5:
                    line += " ■"  # Strong correlation
                elif matrix[row][col] > 0.3:
                    line += " ▒"  # Medium correlation
                elif matrix[row][col] > 0.1:
                    line += " ░"  # Weak correlation
                else:
                    line += "  "  # No correlation
            
            print(line)
            lines.append(line)
        
        # Legend
        lines.append("")
        lines.append("## Legend")
        lines.append("")
        lines.append("| Symbol | ID  | Domains                              | Elemental Force | Confidence |")
        lines.append("|--------|-----|---------------------------------------|-----------------|------------|")
        
        for symbol_id, symbol in sorted(self.symbols.items(), key=lambda x: int(x[0])):
            domains = ", ".join(symbol.get("domains", [])[:2]) if symbol.get("domains") else "N/A"
            ef_name = self.forces.get(symbol.get("elemental_force"), {}).get('name', '') or ""
            
            lines.append(f"| {symbol.get('name', '?')} | {symbol_id:<4} | {domains:<25} | {ef_name:<20} | {symbol.get('confidence_score', 0):.2f} |")
        
        # Write output
        heatmap_path = export_dir / "symbols_correlation_heatmap.md"
        try:
            with open(heatmap_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(lines))
            
            print(f"✅ Generated correlation heatmap at {heatmap_path}")
        
        except Exception as e:
            print(f"❌ Error writing correlation heatmap: {e}")
        
        return heatmap_path
    
    def generate_force_correlation_heatmap(self) -> Path:
        """Generate ASCII heatmap showing force compatibility"""
        
        export_dir = self.export_dir
        
        lines = []
        lines.append("---")
        lines.append("type: force-correlation-heatmap")
        lines.append(f"generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        lines.append("---")
        lines.append("")
        lines.append("# ⚡ Elemental Force Compatibility Heatmap (ASCII)")
        lines.append("")
        
        # Generate compatibility matrix based on complement/relationship data
        force_names = sorted(self.forces.keys())[:4]  # Top 4 forces
        
        if len(force_names) > 1:
            print("## Force Compatibility Matrix")
            print()
            
            for i, f1 in enumerate(force_names):
                row_line = "│" + " ─ " * (len(force_names) - 1) + " │"
                
                for f2 in force_names:
                    if i == len(force_names) - 1:
                        # Row labels
                        row_line += f" {self.forces[f1]['name'][:6]:<8} │"
                    elif f1 in self.forces.get(f2, {}).get("complements", []):
                        row_line += " ■"  # Compatible (complement)
                    else:
                        row_line += "  "  # No specific relationship
                
                print(row_line)
                lines.append(row_line)
            
            # Legend
            lines.append("")
            lines.append("## Legend")
            lines.append("")
            lines.append("■ = Compatible/Complementary forces")
            lines.append("  = Neutral or no direct relationship")
        
        else:
            print("⚠️ Insufficient force definitions for compatibility matrix")
        
        # Write output
        heatmap_path = export_dir / "forces_correlation_heatmap.md"
        try:
            with open(heatmap_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(lines))
            
            print(f"✅ Generated force compatibility heatmap at {heatmap_path}")
        
        except Exception as e:
            print(f"❌ Error writing force heatmap: {e}")
        
        return heatmap_path
    
    def generate_full_heatmap_export(self, output_path: Path = None) -> List[Path]:
        """Generate all heatmap exports"""
        
        print("\n📊 CORRELATION HEATMAP GENERATOR - Starting full heatmap export")
        print("=" * 60)
        
        generated_files = []
        
        # Load fresh data
        self.load_database()
        
        if not self.symbols:
            print("❌ No symbols loaded - skipping heatmap generation")
            return []
        
        # Generate symbol relationship heatmap
        rel_heatmap_path = output_path or "symbol_relationships.md"
        generated_files.append(self.generate_symbol_relationship_heatmap(rel_heatmap_path))
        
        # Generate correlation heatmap
        corr_heatmap_path = self.generate_symbol_correlation_heatmap()
        generated_files.append(corr_heatmap_path)
        
        # Generate force compatibility heatmap
        force_heatmap_path = self.generate_force_correlation_heatmap()
        generated_files.append(force_heatmap_path)
        
        # Summary
        print("\n" + "=" * 60)
        print("✅ HEATMAP GENERATION COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"Generated {len(generated_files)} heatmap files:")
        
        for fpath in generated_files:
            rel_path = Path(fpath).relative_to(GEMATRIA_DIR) if GEMATRIA_DIR else Path(fpath)
            print(f"   → {rel_path}")
        
        return generated_files


def main():
    """Main entry point"""
    
    # Parse arguments
    output_path = None
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg.startswith("--output"):
                try:
                    output_path = Path(arg.split("=")[1])
                    print(f"Output path set to: {output_path}")
                except (ValueError, IndexError):
                    pass
    
    # Generate heatmaps
    generator = CorrelationHeatmapGenerator(DB_DIR)
    files = generator.generate_full_heatmap_export(output_path=output_path)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
