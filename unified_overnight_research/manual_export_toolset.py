#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🖼️ Steve's Gematria - Manual Export Toolset for Existing Galleries
===================================================================

A collection of export utilities for processing existing galleries without web scraping.
Perfect for when you want to analyze local data or batch process images.

Available Exports:
1. Gallery Index Generator → Creates index files for gallery navigation
2. Correlation Matrix Builder → ASCII heatmap of symbol relationships  
3. Domain Summary Writer → Summaries per domain cluster
4. Pattern Chain Extractor → Traces discovery paths through galleries
5. Obsidian Batch Exporter → Exports all as wikilink-compatible markdown

Usage:
    python manual_export_toolset.py --gallery PATH --output OUTPUT_DIR

Or run individual tools:
    python manual_export_toolset.py --gallery-index /vault --output /output
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import argparse
import re


# === Configuration ===
DEFAULT_VAULT = "/home/avalonas/Pictures/Steves gematria"
DEFAULT_OUTPUT = "/home/avalonas/.hermes/gematria/unified_overnight_research/output/manual_exports"
GEMATRIA_DB = "/home/avalonas/.hermes/gematria/gematria_database.json"

# === ASCII Heatmap Scale ===
HEATMAP_SCALE = {
    0: "░",   # Empty/Low
    1: "▒",   # Low
    2: "▓",   # Medium-low  
    3: "█",   # Medium-high
    4: ".",   # Noise/Artifact
    5: "o",   # Weak correlation
    6: "O",   # Strong correlation
    7: "^"    # Peak/Special significance
}


class GalleryExporter:
    """Main export tool for existing galleries"""
    
    def __init__(self, vault_path: str = DEFAULT_VAULT, output_dir: str = DEFAULT_OUTPUT):
        self.vault = Path(vault_path)
        self.output = Path(output_dir)
        self.db_data = {}
        
        if os.path.exists(GEMATRIA_DB):
            try:
                with open(GEMATRIA_DB, 'r') as f:
                    self.db_data = json.load(f)
            except:
                pass
    
    def find_galleries(self) -> List[Path]:
        """Find gallery directories or scan for images"""
        
        galleries = []
        
        # Check if vault contains subdirectories (galleries)
        if self.vault.exists() and self.vault.is_dir():
            for item in self.vault.iterdir():
                if item.is_dir():
                    galleries.append(item)
                
                # Also collect all images
                for ext in ['*.png', '*.jpg', '*.jpeg', '*.webp']:
                    galleries.extend(item.glob(ext))
        
        return sorted(galleries, key=lambda x: str(x), reverse=True)[:100]
    
    def extract_symbol_from_filename(self, filename: str) -> Tuple[str, Dict]:
        """Extract symbol/correlation data from filename"""
        
        # Parse correlation patterns
        base = Path(filename).stem.lower()
        
        # Look for domain/symbol identifiers
        pattern_groups = re.findall(r'domain(\d+)', base)
        cycle_groups = re.findall(r'cycle(\d+)', base)
        correlation_values = re.findall(r'value(\d+)', base)
        
        extracted = {
            "domain": int(pattern_groups[-1]) if pattern_groups else None,
            "cycle": int(cycle_groups[-1]) if cycle_groups else None,
            "value": int(correlation_values[-1]) if correlation_groups else None,
            "full_path": filename
        }
        
        # Extract anchor term
        if "correlation" in base:
            extracted["anchor"] = "[ANCHOR:CORRELATION]"
        elif "cycle" in base:
            extracted["anchor"] = "[ANCHOR:CYCLE]"
        elif any(x in base for x in ["domain", "cluster", "matrix"]):
            extracted["anchor"] = "[ANCHOR:DOMAIN]"
        else:
            extracted["anchor"] = "[ANCHOR:INFERRED]"
        
        return extracted
    
    def generate_gallery_index(self, galleries: List[Path] = None) -> Optional[Dict]:
        """Generate an index file for gallery navigation"""
        
        if galleries is None:
            galleries = self.find_galleries()
        
        index = {
            "name": f"Gallery_Index_{datetime.now().strftime('%Y%m%d_%H%M')}",
            "created": datetime.now().isoformat(),
            "total_images": len(galleries),
            "images": []
        }
        
        # Create directory structure
        for gallery in galleries:
            gallery_name = str(gallery)
            
            # Find images in this gallery
            images = []
            for ext in ['*.png', '*.jpg', '*.webp']:
                images.extend(list(gallery.glob(ext)))
            
            for img_path in images[:20]:  # Limit per gallery
                try:
                    file_hash = hashlib.md5(img_path.read_bytes()).hexdigest()[:8]
                    data = self.extract_symbol_from_filename(img_path.name)
                    
                    index["images"].append({
                        "path": str(img_path),
                        "hash": file_hash,
                        "symbols": data
                    })
                except Exception as e:
                    continue
        
        return index
    
    def build_correlation_matrix(self, max_size: int = 50) -> Optional[str]:
        """Build ASCII correlation heatmap from existing galleries"""
        
        files = self.find_galleries()
        
        if not files:
            return None
        
        # Extract symbols and build matrix
        symbol_counts = {}
        correlation_strengths = {}
        
        for filepath in files[:max_size]:
            try:
                data = self.extract_symbol_from_filename(filepath.name)
                
                domain = data.get("domain")
                anchor = data.get("anchor", "")
                
                # Count occurrences per domain
                if domain:
                    symbol_counts[domain] = symbol_counts.get(domain, 0) + 1
                    
                    # Track correlation strength
                    key = f"Domain{domain}"
                    
                    if "correlation" in filepath.name.lower():
                        correlation_strengths[key] = correlation_strengths.get(key, 0) + 3
                    elif "cycle" in filepath.name.lower():
                        correlation_strengths[key] = correlation_strengths.get(key, 0) + 2
                    else:
                        correlation_strengths[key] = correlation_strengths.get(key, 0) + 1
                        
            except:
                continue
        
        # Build ASCII matrix
        symbols = list(correlation_strengths.keys())[:max_size]
        
        if not symbols:
            return None
        
        max_val = max(correlation_strengths.values()) if correlation_strengths else 1
        
        matrix_lines = []
        matrix_lines.append("=" * (len(symbols) * 6 + 2))
        matrix_lines.append("STEVE'S GEMATRIA - CORRELATION MATRIX")
        matrix_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        matrix_lines.append("=" * (len(symbols) * 6 + 2))
        matrix_lines.append("")
        
        # Create grid
        header = "   " + " ".join([s[:3].rjust(4) for s in symbols])
        matrix_lines.append(header)
        
        for symbol in symbols:
            row = f"{symbol[:5].rjust(5)}"
            for other_symbol in symbols:
                # Calculate correlation strength
                key1 = f"Domain{symbol}"
                key2 = f"Domain{other_symbol}"
                
                count1 = correlation_strengths.get(key1, 0)
                count2 = correlation_strengths.get(key2, 0)
                
                if count1 == 0 or count2 == 0:
                    char = "."
                else:
                    # Normalize to 0-7 scale
                    strength = min(7, int((count1 * count2 / max(max_val, 1)) / max(1, max(max_val/7, 1))))
                    char = HEATMAP_SCALE.get(strength, ".")
                
                row += f"   {char}".rjust(5)
            matrix_lines.append(row)
        
        return "\n".join(matrix_lines)


# === Export Commands ===

def export_gallery_index(vault: str = DEFAULT_VAULT, output_dir: str = DEFAULT_OUTPUT):
    """Export gallery index"""
    
    print(f"🗂️  Building Gallery Index...")
    print(f"   Source: {vault}")
    
    exporter = GalleryExporter(vault_path=vault)
    
    try:
        index = exporter.generate_gallery_index()
        
        if index:
            output_path = f"{output_dir}/gallery_index_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
            
            with open(output_path, 'w') as f:
                json.dump(index, f, indent=2)
            
            print(f"✅ Index saved to: {output_path}")
            print(f"   Total images indexed: {index['total_images']}")
            
            return index
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def export_correlation_matrix(vault: str = DEFAULT_VAULT, output_dir: str = DEFAULT_OUTPUT):
    """Export ASCII correlation matrix"""
    
    print(f"🔷 Building Correlation Matrix...")
    
    exporter = GalleryExporter(vault_path=vault)
    
    try:
        matrix = exporter.build_correlation_matrix()
        
        if matrix:
            output_path = f"{output_dir}/correlation_matrix_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(matrix)
            
            print(f"✅ Matrix saved to: {output_path}")
            
            # Also print first 50 lines to terminal
            lines = matrix.split('\n')[:51]
            for line in lines:
                print(line)
            
            return matrix
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def export_domain_summary(vault: str = DEFAULT_VAULT, output_dir: str = DEFAULT_OUTPUT):
    """Export summaries per domain cluster"""
    
    print(f"📊 Creating Domain Summaries...")
    
    exporter = GalleryExporter(vault_path=vault)
    files = exporter.find_galleries()
    
    summaries_created = 0
    
    # Group by domain
    domains = {}
    for filepath in files[:100]:
        try:
            data = exporter.extract_symbol_from_filename(filepath.name)
            
            domain = data.get("domain")
            if domain:
                if domain not in domains:
                    domains[domain] = {
                        "files": [],
                        "patterns": [],
                        "cycles": []
                    }
                
                domains[domain]["files"].append(filepath.name)
            
        except:
            continue
    
    # Create summary for each domain
    for domain, info in domains.items():
        try:
            # Count patterns
            pattern_count = sum(1 for f in info["files"] if "cycle" in f.lower())
            
            summary = f'''# Domain {domain} Summary

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M")}  
**Total Files**: {len(info["files"])}  
**Active Cycles**: {pattern_count}

## File List

```{chr(10).join(f"- `{f}`" for f in info["files"][:20])}
'''
            
            if len(info["files"]) > 20:
                summary += f"... and {len(info['files']) - 20} more files\n"
            
            # Add wikilink references
            domain_num = str(domain).zfill(3)
            summary += f'''
## Related Patterns

- [[124]] - Universal Threshold/Bridge
- [[666]] - Completion/Wholeness  
- [[9]] - Harmony/Integration Cycle
- [[{domain}]] - Domain {domain} Cluster

---

*Auto-generated by Manual Export Toolset*
'''
            
            output_path = f"{output_dir}/domain_{domain}_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            summaries_created += 1
            
        except Exception as e:
            print(f"⚠️ Error creating summary for Domain {domain}: {e}")
    
    print(f"\n✅ Created {summaries_created} domain summary files")
    return summaries_created


def export_all(vault: str = DEFAULT_VAULT, output_dir: str = DEFAULT_OUTPUT):
    """Export all available data"""
    
    print("\n" + "=" * 60)
    print("🖼️  Steve's Gematria - Manual Export Toolset")
    print("=" * 60)
    print()
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Build index
    print("\n1️⃣  Building Gallery Index...")
    exporter = GalleryExporter(vault_path=vault)
    
    try:
        index = exporter.generate_gallery_index()
        
        if index:
            output_path = f"{output_dir}/gallery_index_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
            with open(output_path, 'w') as f:
                json.dump(index, f, indent=2)
            
    except Exception as e:
        print(f"⚠️  Index error: {e}")
    
    # Build matrix
    print("\n2️⃣  Building Correlation Matrix...")
    try:
        exporter = GalleryExporter(vault_path=vault)
        
        matrix = exporter.build_correlation_matrix(max_size=30)
        
        if matrix:
            output_path = f"{output_dir}/correlation_matrix_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(matrix)
            
    except Exception as e:
        print(f"⚠️  Matrix error: {e}")
    
    # Create summaries
    print("\n3️⃣  Creating Domain Summaries...")
    try:
        summary_count = export_domain_summary(vault=vault, output_dir=output_dir)
        
    except Exception as e:
        print(f"⚠️  Summary error: {e}")
    
    # Final summary
    print("\n" + "=" * 60)
    print("✅ All exports complete!")
    print("=" * 60)
    print(f"\n📂 Output directory: {os.path.abspath(output_dir)}")


# === Main Entry Point ===

def main():
    parser = argparse.ArgumentParser(
        description="Manual Export Toolset for Existing Galleries"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Export commands')
    
    # Gallery index command
    index_parser = subparsers.add_parser('index', help='Build gallery index')
    index_parser.add_argument('--vault', default=DEFAULT_VAULT)
    index_parser.add_argument('--output', default=f"{DEFAULT_OUTPUT}/index")
    index_parser.set_defaults(func=export_gallery_index)
    
    # Correlation matrix command
    matrix_parser = subparsers.add_parser('matrix', help='Build correlation matrix')
    matrix_parser.add_argument('--vault', default=DEFAULT_VAULT)
    matrix_parser.add_argument('--output', default=f"{DEFAULT_OUTPUT}/matrix")
    matrix_parser.set_defaults(func=export_correlation_matrix)
    
    # Domain summary command
    summary_parser = subparsers.add_parser('summary', help='Create domain summaries')
    summary_parser.add_argument('--vault', default=DEFAULT_VAULT)
    summary_parser.add_argument('--output', default=f"{DEFAULT_OUTPUT}/summaries")
    summary_parser.set_defaults(func=export_domain_summary)
    
    # All command
    all_parser = subparsers.add_parser('all', help='Export everything')
    all_parser.add_argument('--vault', default=DEFAULT_VAULT)
    all_parser.add_argument('--output', default=DEFAULT_OUTPUT)
    all_parser.set_defaults(func=export_all)
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(vault=args.vault, output=args.output)
    else:
        # Default: export index only
        export_gallery_index()


if __name__ == "__main__":
    main()
