#!/usr/bin/env python3
"""
📊 Correlation Heatmap & Relationship Matrix Generator
===========================================================
Generates ASCII and visual heatmaps for gematria symbol correlations.

Usage:
    python3 heatmap_generator.py --db-dir /path/to/database --output-dir /output/path
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Tuple
from collections import defaultdict

# Auto-detect gematria directory
HERE = Path(__file__).resolve().parent.parent
DB_DIR = HERE / "database"
SYMBOLS_FILE = DB_DIR / "symbols.json"
FORCES_FILE = DB_DIR / "forces.json"


class HeatmapGenerator:
    """Generates correlation heatmaps for symbol relationships and cross-domain patterns"""
    
    def __init__(self, db_dir: Path, output_dir: Path):
        self.db_dir = db_dir
        self.output_dir = output_dir or (HERE / "research" / "heatmaps")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load database
        self.symbols = {}
        self.forces = {}
        self.relationship_scores = defaultdict(lambda: defaultdict(float))
        self.domain_correlations = defaultdict(lambda: defaultdict(list))
        
        if SYMBOLS_FILE.exists():
            with open(SYMBOLS_FILE, 'r') as f:
                data = json.load(f)
            self.symbols = {s["symbol_id"]: s for s in data.get("analyzed_symbols", [])}
        
        if FORCES_FILE.exists():
            with open(FORCES_FILE, 'r') as f:
                data = json.load(f)
            self.forces = data.get("forces", {})
    
    def compute_correlation_matrix(self):
        """Compute correlation scores between all symbol pairs"""
        print("\n📊 Computing correlation matrix...")
        
        # Build relationship adjacency from symbol relationships
        for symbol_id, symbol in self.symbols.items():
            relationships = symbol.get("relationships", [])
            for ref_id in relationships:
                if ref_id in self.symbols:
                    # Compute relationship score based on confidence averages
                    src_conf = symbol.get("confidence_score", 0)
                    tgt_conf = self.symbols[ref_id].get("confidence_score", 0)
                    shared_domains = len(set(symbol.get("domains", [])) & 
                                        set(self.symbols[ref_id].get("domains", [])))
                    
                    score = (src_conf + tgt_conf) / 2 + shared_domains * 0.1
                    self.relationship_scores[symbol_id][ref_id] = min(score, 1.0)
        
        # Compute force-domain correlations
        for symbol_id, symbol in self.symbols.items():
            ef = symbol.get("elemental_force")
            for domain in symbol.get("domains", []):
                if ef and ef in self.forces:
                    self.domain_correlations[domain][ef] = {
                        "symbol_count": len(symbol.get("relationships", [])),
                        "avg_confidence": symbol.get("confidence_score", 0)
                    }
        
        return self.relationship_scores, self.domain_correlations
    
    def generate_ascii_heatmap(self, scores: Dict, title: str = "Symbol Correlation Matrix") -> str:
        """Generate ASCII correlation heatmap"""
        
        # Get all symbol IDs and names
        symbols_list = sorted(scores.keys())
        sym_names = {sid: self.symbols[sid].get("name", f"Symbol {sid}") for sid in symbols_list}
        
        if len(symbols_list) == 0:
            return "*No correlations computed*"
        
        n = len(symbols_list)
        
        # Build matrix with correlation scores
        matrix_lines = []
        header = "   " + "    ".join([f"{sid[:3]:>4}" for sid in symbols_list])
        matrix_lines.append(header)
        
        max_len = 20
        for i, src in enumerate(symbols_list):
            row_vals = []
            row_str = f"{sym_names[src][:15]:15}"
            
            for j, dst in enumerate(symbols_list):
                if i == j:
                    row_vals.append(1.0)
                elif dst in scores.get(src, {}):
                    score = scores[src][dst]
                    # Normalize to 0-1 range for color mapping
                    row_vals.append(score)
                else:
                    row_vals.append(0.0)
            
            # Convert scores to ASCII characters (heatmap colors)
            for val in row_vals:
                if val >= 0.9:
                    char = "██"
                elif val >= 0.7:
                    char = "█░"
                elif val >= 0.5:
                    char = "▉▁"
                elif val >= 0.3:
                    char = "▄▅"
                elif val >= 0.1:
                    char = "▀▂"
                else:
                    char = "··"
                row_str += f" {char}"
            
            matrix_lines.append(row_str)
        
        return "\n".join(matrix_lines)
    
    def generate_force_correlation_heatmap(self) -> str:
        """Generate force-domain correlation heatmap"""
        
        domains = sorted(self.domain_correlations.keys())
        forces = [f for f in self.domain_correlations.get(domains[0], {}) if f] if domains else []
        
        if not domains or not forces:
            return "*No force-domain correlations computed*"
        
        matrix_lines = []
        header = "     " + "    ".join("{:>8}".format(f[:3].upper()) for f in forces)
        matrix_lines.append(header)
        
        for domain in domains:
            row_str = f"{domain[:15]:15}"
            force_scores = self.domain_correlations.get(domain, {})
            
            for force in forces:
                if force in force_scores:
                    score = force_scores[force]["avg_confidence"]
                    if score >= 0.9:
                        char = "██"
                    elif score >= 0.7:
                        char = "█░"
                    elif score >= 0.5:
                        char = "▉▁"
                    else:
                        char = "··"
                    row_str += f" {char}"
                else:
                    row_str += "   "
            
            matrix_lines.append(row_str)
        
        return "\n".join(matrix_lines)
    
    def generate_relationship_network(self) -> str:
        """Generate text-based relationship network summary"""
        
        lines = []
        lines.append("# 🕸️ Symbol Relationship Network")
        lines.append("")
        
        # High-confidence relationships only
        high_conf_threshold = 0.6
        
        for src, targets in sorted(self.relationship_scores.items()):
            for dst, score in sorted(targets.items()):
                if score >= high_conf_threshold:
                    src_name = self.symbols[src].get("name", f"Symbol {src}")
                    tgt_name = self.symbols[dst].get("name", f"Symbol {dst}")
                    lines.append(f"{src_name} ⟷ {tgt_name}")
                    lines.append(f"  Score: {score:.3f}, Shared Domains: {len(set(self.symbols[src].get('domains', [])) & set(self.symbols[dst].get('domains', [])))}")
        
        return "\n".join(lines)
    
    def generate_full_report(self):
        """Generate complete heatmap report"""
        
        print("\n📊 Generating correlation heatmaps...")
        
        # Compute correlations
        scores, domain_correlations = self.compute_correlation_matrix()
        
        # Generate files
        outputs = []
        
        # ASCII correlation matrix
        matrix_file = self.output_dir / "symbol_correlation_matrix.md"
        ascii_matrix = self.generate_ascii_heatmap(scores)
        
        content = "---\ntype: heatmap\n---\n\n# 📊 Symbol Correlation Heatmap\n\n```\n" + ascii_matrix + "\n```\n\n*Legend: ██ ≥90% | █░ 70-90% | ▉▁ 50-70% | ▄▅ 30-50% | ▀▂ 10-30% | ·· <10%*\n"
        
        with open(matrix_file, 'w') as f:
            f.write(content)
        outputs.append(matrix_file)
        
        # Force-domain correlation heatmap
        force_file = self.output_dir / "force_domain_correlation.md"
        ascii_force_map = self.generate_force_correlation_heatmap()
        
        content2 = "---\ntype: heatmap\n---\n\n# 🌐 Force-Domain Correlation Heatmap\n\n```\n" + ascii_force_map + "\n```\n"
        
        with open(force_file, 'w') as f:
            f.write(content2)
        outputs.append(force_file)
        
        # Relationship network
        network_file = self.output_dir / "relationship_network.md"
        network_content = "---\ntype: relationships\n---\n\n" + self.generate_relationship_network()
        
        with open(network_file, 'w') as f:
            f.write(network_content)
        outputs.append(network_file)
        
        # Domain coverage report
        domain_coverage_file = self.output_dir / "domain_coverage.md"
        domain_counts = defaultdict(int)
        for symbol in self.symbols.values():
            for domain in symbol.get("domains", []):
                domain_counts[domain] += 1
        
        dc_lines = ["# 📚 Domain Coverage Analysis", "", "## Symbol Distribution by Domain"]
        for domain, count in sorted(domain_counts.items(), key=lambda x: -x[1]):
            dc_lines.append(f"- **{domain}**: {count} symbols")
        
        with open(domain_coverage_file, 'w') as f:
            f.write("\n".join(dc_lines))
        outputs.append(domain_coverage_file)
        
        print(f"   → Created: {matrix_file.name}")
        print(f"   → Created: {force_file.name}")
        print(f"   → Created: {network_file.name}")
        print(f"   → Created: {domain_coverage_file.name}")
        
        return outputs


def main():
    """Main entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate correlation heatmaps for gematria symbols")
    parser.add_argument("--db-dir", type=str, default="/home/avalonas/.hermes/gematria/database", help="Path to database directory")
    parser.add_argument("--output-dir", type=str, default="/home/avalonas/.hermes/gematria/research/heatmaps", help="Output directory for heatmaps")
    
    args = parser.parse_args()
    
    db_dir = Path(args.db_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("📊 CORRELATION HEATMAP GENERATOR")
    print("=" * 60)
    print(f"Database: {db_dir}")
    print(f"Output: {output_dir}")
    print("=" * 60)
    
    generator = HeatmapGenerator(db_dir, output_dir)
    outputs = generator.generate_full_report()
    
    print("\n" + "=" * 60)
    print("✅ HEATMAP GENERATION COMPLETED")
    print("=" * 60)
    print(f"Generated: {len(outputs)} heatmap files")


if __name__ == "__main__":
    main()
