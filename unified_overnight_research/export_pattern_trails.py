#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧬 Steve's Gematria - Pattern Trail Exporter
===========================================

Creates Obsidian-friendly text files showing the discovery chain of symbols.
Each trail shows how one symbol led to another, with correlation data and anchor terms.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Configuration
VAULT_PATH = "/home/avalonas/.hermes/gematria/unified_overnight_research"
OUTPUT_DIR = f"{VAULT_PATH}/output/pattern_trails"
GEMATRIA_DB = f"{VAULT_PATH}/../gematria_database.json"


def load_gematria_database():
    """Load the gematria database if it exists"""
    if os.path.exists(GEMATRIA_DB):
        with open(GEMATRIA_DB, 'r') as f:
            return json.load(f)
    return {}


def scan_image_vault_for_trails():
    """Scan image vault for files that can form trails"""
    vault = Path("/home/avalonas/Pictures/Steves gematria")
    
    if not vault.exists():
        print(f"⚠️ Vault doesn't exist at: {vault}")
        return []
    
    # Find image files with patterns
    trail_files = []
    for ext in ['*.png', '*.jpg', '*.webp']:
        trail_files.extend(vault.glob(ext))
    
    # Sort by modification time (newest first)
    trail_files = sorted(trail_files, key=lambda x: x.stat().st_mtime, reverse=True)[:50]
    
    print(f"📂 Found {len(trail_files)} recent image files in vault")
    return [str(f) for f in trail_files]


def extract_trail_path(filename):
    """Extract the 'trail' from a filename"""
    # Example: domain938_CYCLE1_correlation.png
    # Trail would be: 938 → cycle_1
    
    base = Path(filename).stem.lower()
    
    # Look for correlation/cycle patterns
    if "correlation" in base or "cycle" in base:
        parts = base.replace("correlation", "").replace("cycle", "").split("_")
        
        trail_path = []
        for part in parts[:5]:  # First 5 parts
            # Try to extract numeric values
            import re
            nums = re.findall(r'\d+', part)
            if nums:
                trail_path.append(nums[0])
        
        return " → ".join(trail_path) if trail_path else str(filename)
    
    return filename


def create_trail_entry(source_file, target_concept, correlation_data=None):
    """Create an Obsidian wikilink entry"""
    
    trail_name = extract_trail_path(source_file)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    entry = f'''---
tags: [gematria, pattern-trail, {trail_name}]
created: {timestamp}
source-image: `{source_file.split("/")[-1]}`
status: discovered
---

# [[{target_concept}]]

## Discovery Path

[[{trail_name}]] → [[{target_concept}]]

**Anchor Term**: `correlation`  
**Trail Pattern**: `{trail_name}`

## Correlation Data

| Symbol | Value | Reduction | Domain |
|--------|-------|-----------|--------|
'''
    
    if correlation_data:
        for symbol, data in correlation_data.items():
            entry += f"| {symbol} | {data.get('value', '?')} | {data.get('reduction', '?')} | {data.get('domain', '?')} |\n"
    else:
        entry += "| *N/A* | *Unknown* | *Unknown* | *Unknown* |\n"
    
    entry += '''
---

## Related Patterns

- [[124]] - Universal Threshold/Bridge
- [[666]] - Completion/Wholeness  
- [[9]] - Harmony/Integration Cycle
- [[17]] - Vessel/Holds the Fire

## Notes

*Automatically discovered by IMAGE-SEED runner*
'''
    
    return entry


def export_trails():
    """Export pattern trails to text files"""
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("\n📝 Exporting Pattern Trails...")
    print("=" * 50)
    
    # Load any existing data
    gematria_db = load_gematria_database()
    
    # Scan for trail files
    trail_files = scan_image_vault_for_trails()
    
    if not trail_files:
        print("ℹ️ No trail files found. Creating example trails...")
        # Create sample trails for demonstration
        create_sample_trails(gematria_db)
        return
    
    # Process each file
    exported_count = 0
    for filepath in trail_files[:20]:  # Limit to first 20 for now
        try:
            # Parse filename
            filename = Path(filepath).name
            
            # Create trail entry
            target = f"Pattern_{extract_trail_path(filepath)}"
            
            # Check gematria db for related data
            correlation_data = {}
            if "938" in str(filepath):
                correlation_data["938"] = {
                    "value": 124,
                    "reduction": "6", 
                    "domain": "correlation_matrix"
                }
            
            entry = create_trail_entry(
                source_file=filepath,
                target_concept=target,
                correlation_data=correlation_data
            )
            
            # Write to file
            output_filename = f"{target}.md"
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(entry)
            
            exported_count += 1
            print(f"✅ Exported: {output_filename}")
            
        except Exception as e:
            print(f"⚠️ Error processing {filepath}: {e}")
    
    print(f"\n📊 Summary: Exported {exported_count} pattern trail files")
    print(f"📂 Output directory: {os.path.abspath(OUTPUT_DIR)}")


def create_sample_trails(gematria_db):
    """Create example trails for demonstration"""
    
    sample_trails = [
        (["124", "666", "9"], "Domain 938 Correlation Cycle"),
        (["1", "2", "3"], "Basic Triangle Pattern"),
        (["49", "39", "21"], "Couplet Sequence"),
    ]
    
    for trail, concept in sample_trails:
        entry = create_trail_entry("example.png", concept)
        
        # Remove wikilink brackets from filename reference
        content = entry.replace("[[example]]", "[[example.png]]")
        
        output_path = os.path.join(OUTPUT_DIR, f"{concept}.md")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)


def main():
    """Main entry point"""
    print("🧬 Steve's Gematria - Pattern Trail Exporter")
    print("=" * 50)
    print()
    
    # Check dependencies
    if not os.path.exists(GEMATRIA_DB):
        print(f"⚠️ Warning: Gematria database not found at {GEMATRIA_DB}")
        print("   Creating trails without correlation data...")
    
    # Export trails
    export_trails()
    
    print("\n✨ Trail export complete!")
    print("📂 View exported trails in:", os.path.abspath(OUTPUT_DIR))


if __name__ == "__main__":
    main()
