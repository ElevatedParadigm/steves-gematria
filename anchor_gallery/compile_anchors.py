#!/usr/bin/env python3
"""
🔮 Anchor Gallery — Compile Script

Compiles anchor term definitions from JSON into a visual archive markdown file.
Generates the gallery with ASCII art, heat scales, and wikilink cross-references.

Usage:
    python compile_anchors.py [config.json]
    
Example:
    python compile_anchors.py sample_anchors.json
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Heat scale encoding for consistent visual styling
SCALE_CHARS = {
    0: '░',   # lowest intensity
    1: '▒',
    2: '▓',
    3: '█',   # highest intensity
    4: '.',   # separator/pattern element
    5: 'o',   # medium circle
    6: 'O',   # large circle  
    7: '^'    # peak/peak marker
}

HEAT_PATTERN_1 = "░░░░▓▓▓▓█████ ▓▓░░░░░░░░▓░░░░▓█████ ░░░░░░░░▓▓▓░░"
HEAT_PATTERN_2 = "░░░░░░▒▒▒▒▓▓▓▓███ ███ ██████ ██░░░░ ▓▓▓▓▓▓█████ ░"
HEAT_PATTERN_3 = "▓▓░░░░▓▓░░░░▒▒▒▒▓▓▓▓▓███ ████████ ████ ▓▓▓▓████ ██"


def to_heat_scale(intensity, length=40):
    """Convert intensity (0-1) to a heat scale string of given length."""
    if intensity <= 0:
        return "░" * length
    elif intensity >= 1:
        return "█" * length
    
    # Normalize and map to scale characters
    scaled = int(intensity * 8)  # Map 0-1 to 0-7
    chars = [SCALE_CHARS.get(min(scaled, 7), '░') for _ in range(length)]
    
    # Create variation by mixing intensities
    result = []
    for i, char in enumerate(chars):
        local_intensity = (intensity * 8 + (i % 5)) % 8
        result.append(SCALE_CHARS.get(local_intensity, '░'))
    
    return ''.join(result[:length])


def generate_ascii_art(title_prefix=""):
    """Generate ASCII art patterns for the gallery."""
    patterns = {
        "bridge": f"""
{to_heat_scale(0.4, 50)}
{title_prefix}Bridge       │               The End       
──────────────┼─────────────────┬───────────────
Entry         │     TRAVEL     │    EXIT      
{title_prefix}{str(124).rjust(10)}        │  {str(666).rjust(8)}            
Universal     │      →         │   Completion 
Threshold     │      ─        │               
""".strip(),
        
        "threshold": f"""
███████ ▒▒▓░▓▓░█████ ████░░░░░░░░░░▓▓░░░▓█████ ░░░░░░░░░░░░░░░░░░
{title_prefix}Threshold ────┼───────────────┼──────────────
Block          │   BLOCKED     │  OPEN       
███████        │              │              
""".strip(),
        
        "cycle": f"""
░░▒▓███ ▓▓█████ ████ ██████ ░░░░░▓▓▓▓▓░░░░░░░▓▓░░░░░░░░░░░░░░░░
{title_prefix}Cycle    →  Start of new phase ← End of cycle  
─────────────────┬──────────┬───────────────
124               │ →        │ 666            
Universal         │ ─       │   Wholeness    
Bridge            │ ────────┤               
""".strip()
    }
    
    return patterns.get("bridge", HEAT_PATTERN_1)


def load_anchor_definitions(config_path):
    """Load anchor definitions from JSON file."""
    with open(config_path, 'r') as f:
        data = json.load(f)
    
    return data.get("anchors", [])


def create_anchor_entry(anchor, index):
    """Create markdown entry for a single anchor term."""
    lines = []
    
    # Header with wikilink
    title = anchor.get("title", "[[UNSET-TITLE]]")
    lines.append(f"# {title}")
    lines.append("")
    
    # Core connection section
    core = anchor.get("core_connection", {})
    trigger = core.get("trigger", "unknown context")
    symbol_flow = core.get("symbol_flow", "SYMBOL1 → SYMBOL2")
    transformation = core.get("transformation", "")
    
    lines.append("## Core Connection")
    lines.append(f"- **Trigger**: {trigger}")
    lines.append(f"- **Symbol Flow**: `{symbol_flow}`")
    lines.append(f"- **Transformation**: {transformation}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Symbol values table
    symbols = anchor.get("symbols", [])
    if not symbols:
        # Default structure for MVP prototype
        lines.append("### Symbol Values\n")
        lines.append("| Stage | Symbol | Numeric Value | Meaning |\n")
        lines.append("|-------|--------|---------------|---------|\n")
        lines.append("| Entry | [[124]] | 1+2+4=7       | Universal Threshold / The Bridge |\n")
        lines.append('| Exit  | [[666]] | 6+6+6=18→9    | Completion / Wholeness (not "evil") |\n')
        lines.append("")
        symbol_flow_data = {
            "entry": {"symbol": "124", "value": "7", "name": "Universal Threshold / The Bridge"},
            "exit": {"symbol": "666", "value": "9", "name": "Completion / Wholeness"}
        }
    else:
        symbol_flow_data = symbols
        lines.append("### Symbol Values\n")
        lines.append("| Stage | Symbol | Numeric Value | Meaning |\n")
        lines.append("|-------|--------|---------------|---------|\n")
        for stage in symbols:
            s = stage.get("symbol", "UNSET")
            val = stage.get("value", "N/A")
            name = stage.get("name", "")
            lines.append(f"| {stage.get('stage', 'N/A')} | [[{s}]] | {val} | {name} |\n")
        lines.append("")
    
    # ASCII art section
    ascii_title = anchor.get("ascii_title", "Transformation Visualization")
    title_prefix = f"## {title_prefix}: " if title_prefix else ""
    ascii_art = generate_ascii_art(ascii_title)
    
    lines.append("---")
    lines.append("")
    lines.append("### ASCII Interpretation\n")
    lines.append("```\n")
    lines.append(ascii_art)
    lines.append("\n```\n")
    lines.append("")
    
    # Quote-style interpretation box
    quote = anchor.get("interpretation_quote", 
            f"{title_prefix}The transformation is the key insight. "
            f"What enters as separation exits as integration. "
            f"This reveals: **separation → connection → wholeness**.")
    
    lines.append("> " + quote.replace('\n', "\n> "))
    lines.append("")
    
    # Wikilinks and cross-domains section
    relations = anchor.get("relations", [])
    if not relations:
        lines.append("---")
        lines.append("")
        lines.append("### Wikilinks & Cross-Domains\n")
        lines.append("- `[[124]]` → triggers domain: [the veil / mystery / entry]")
        lines.append(f"- Related to [[666-Wholeness]] (cycle variant)")  
        lines.append("- Appears in: [military coups], [hero's journey], [religious texts]")
    else:
        lines.append("---")
        lines.append("")
        lines.append("### Wikilinks & Cross-Domains\n")
        for rel in relations:
            key = rel.get("symbol", "SYMBOL").lower()
            domain = rel.get("domain", "unknown")
            related = rel.get("related_to", "")
            contexts = rel.get("contexts", [])
            
            if key == "124":
                sym = rel.get('symbol', '124')
                lines.append(f"- `[[{sym}]]` → triggers domain: {domain}")
            elif key == "666":
                sym = rel.get('symbol', '666')
                lines.append(f"- `[[{sym}]]` → triggers domain: {domain}")
                
            if related:
                lines.append(f"- Related to [[{related}]] (cycle variant)")
            
            for ctx in contexts:
                lines.append(f"- Appears in: [{ctx}]")
    
    lines.append("")
    
    # Observations section
    observations = anchor.get("observations", [])
    if not observations:
        lines.append("---")
        lines.append("")
        lines.append("### Observations\n")
        lines.append("- The transformation is always catalyzed by *something* crossing the threshold")
        lines.append(f"- {title_prefix} as a bridge value shows up in contexts requiring transition")
        lines.append('- This isn\'t linear progress — it\'s circular integration (hence 666→9)')
    else:
        lines.append("---")
        lines.append("")
        lines.append("### Observations\n")
        for obs in observations:
            if isinstance(obs, str):
                lines.append(f"- {obs}")
            else:
                lines.append(f"- **{obs.get('title', 'Observation')}**:\n")
                for detail in obs.get('details', []):
                    lines.append(f"  - {detail}")
    
    lines.append("")
    
    # Tags section
    tags = anchor.get("tags", [])
    if not tags:
        tags = ["#threshold", "#transformation", "#bridge", "#veil"]
        
    lines.append("---")
    lines.append("")
    lines.append(f"**Tags**: {', '.join(tags)}\n")
    
    return ''.join(lines)


def generate_gallery(config_path, output_path):
    """Generate the complete gallery from anchor definitions."""
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    
    # Load and compile anchors
    anchors = load_anchor_definitions(config_path)
    
    entries = []
    for i, anchor in enumerate(anchors, 1):
        entry_html = create_anchor_entry(anchor, i)
        entries.append(entry_html)
    
    # Add gallery header
    header = f"""🔮 Anchor Gallery — Steve's Gematria Visual Archive
================================================

## {datetime.now().strftime('%Y-%m-%d')} — Prototype v1.0

### Purpose

A visual archive documenting the foundational **anchor terms** and **symbolic connections** 
that emerge across domains in Steve's Gematria research. This prototype focuses on capturing 
the core mechanism of symbolic transformation: how certain numbers or sequences act as bridges 
between different conceptual states.

> **The Bridge doesn't just connect points — it *transforms* them.**

---

## 📊 Core Symbols Featured

"""
    
    # Add legend for symbols
    header += """| Symbol | Value | Meaning |
|--------|-------|---------|
| [[124]] | 7 or 124 | Universal Threshold / The Bridge |
| [[666]] | 9 or 6+6+6=18→9 | Completion / Wholeness (not "evil") |

---

## 📜 Gallery Entries

"""
    
    # Add separator between entries
    header += "---\n\n"
    
    # Combine all entries
    gallery_content = header + '\n\n'.join(entries)
    
    # Write to output file
    with open(output_path, 'w') as f:
        f.write(gallery_content)
    
    print(f"✅ Gallery generated: {output_path}")
    print(f"   Total entries: {len(anchors)}")
    print(f"   Output written successfully!")
    
    return len(anchors)


def main():
    """Main entry point."""
    # Default config path
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        # Look in same directory as script
        script_dir = Path(__file__).parent
        config_path = script_dir / "sample_anchors.json"
    
    output_dir = Path(__file__).parent / "output"
    output_path = output_dir / "gallery_v1.md"
    
    if not os.path.exists(config_path):
        print(f"❌ Config file not found: {config_path}")
        print(f"   Please provide a path to your anchors JSON or add sample_anchors.json")
        sys.exit(1)
    
    print("🔮 Anchor Gallery — Compilation Starting")
    print("=" * 50)
    print(f"Input:  {config_path}")
    print(f"Output: {output_path}")
    print("=" * 50)
    print()
    
    try:
        count = generate_gallery(config_path, output_path)
        print()
        print(f"✅ Gallery compilation complete! ({count} entries)")
        print()
        print("Next steps:")
        print("  • Review: less output/gallery_v1.md")
        print("  • Edit: nano sample_anchors.json")
        print("  • Regenerate: python compile_anchors.py")
        
    except Exception as e:
        print(f"❌ Error generating gallery: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
