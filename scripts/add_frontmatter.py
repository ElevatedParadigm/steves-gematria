# 🚀 STEVE'S GEMATRIA + TOLARIA INTEGRATION
## Complete Implementation Guide

**Author:** Avalon  
**Project:** Steve's Gematria Knowledge Base  
**Date:** 2026-04-27  
**Integration Target:** Desktop Markdown Knowledge Management  

---

## 📋 OVERVIEW

This guide implements **Tolaria** as the primary desktop editor for your Steve's Gematria knowledge base, while maintaining full compatibility with existing Obsidian tools and CLI workflows.

### Architecture:
```
┌─────────────────────────────────────────────────┐
│           STEVE'S GEMATRIA SYSTEM               │
├─────────────────────────────────────────────────┤
│  🖥️ Tolaria (Primary GUI Editor)                │
│     ↔️                                        ───▶
│  🔧 CLI Scripts + Python Tools                  │
│     ↔️                                        ───▶
│  📓 Obsidian (Secondary Viewer/Archive)         │
└─────────────────────────────────────────────────┘
          All sharing same Git-backed vault
```

---

## ✅ PREREQUISITES

### Required Software:

1. **Node.js** v20+ ✅ (You have v25.9.0)
2. **pnpm** v8+ 
3. **Rust** stable
4. **WebKit2GTK 4.1** (Linux Tauri requirement)

### Step-by-Step Installation:

```bash
# 1. Install pnpm (via Corepack - built into Node.js)
corepack enable
corepack prepare pnpm@8 -r

# 2. Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
rustup default stable

# 3. Install Linux system dependencies (Debian/Ubuntu 22.04+)
sudo apt update
sudo apt install -y libwebkit2gtk-4.1-dev build-essential curl wget file \
  libxdo-dev libssl-dev libayatana-appindicator3-dev librsvg2-dev libsoup-3.0-dev patchelf

# Verify installations
echo "=== Prerequisites Check ===" && echo ""
node --version  # Should show v25.x.x
pnpm --version   # Should show v8.x.x
cargo --version  # Should show rustc x.y.z
```

### Optional (but recommended):

```bash
# Install Tauri CLI globally (for development)
pnpm add -g @tauri-apps/cli
```

---

## 🔧 INSTALL TOLARIA

### Option A: Official Release (Recommended for Production Use)

```bash
# Download latest release directly
curl -L https://github.com/refactoringhq/tolaria/releases/latest/download/Tolaria.app.tar.gz \
  | tar xzC /opt/

# Create symlink to make it easy to find
sudo ln -s /opt/tolaria/Tolaria.app /usr/local/bin/Tolaria

# Verify installation
Tolaria  # Should open app or show help text
```

### Option B: Clone Source and Run Locally (For Development)

```bash
# Clone repository
git clone https://github.com/refactoringhq/tolaria.git ~/tolaria-source
cd ~/tolaria-source

# Install dependencies
pnpm install

# Run browser-based mock mode (no desktop app needed yet)
pnpm dev

# OR build and run native app
pnpm tauri dev
```

---

## 🗂️ VAULT STRUCTURE DESIGN

### Recommended Structure for Steve's Gematria:

```
/home/avalonas/.hermes/gematria/ (Git repo, Tolaria vault root)
├── 📁 symbols/              # Core gematria symbols
│   ├── 124_universal_threshold.md
│   ├── 963_elevation_completion.md
│   ├── 55_foundation_structure.md
│   ├── 111_activation_vessel.md
│   ├── 279_transformation.md
│   ├── 666_completion_wholeness.md
│   ├── 777_trinity_completion.md     # NEW
│   ├── 13_doorways.md               # NEW
│   └── 888_portals.md               # NEW
│
├── 📁 forces/              # Elemental forces
│   ├── base_4/             # Original 4 elements
│   │   ├── fire_force.md
│   │   ├── earth_force.md
│   │   ├── air_force.md
│   │   └── water_force.md
│   ├── extension/          # Additional forces
│   │   ├── lightning_force.md   # NEW
│   │   ├── ice_force.md         # NEW
│   │   ├── wind_force.md        # NEW
│   │   └── earth_force_ext.md   # NEW (explicit ground reality)
│   └── force_matrix.json    # Relationships between all forces
│
├── 📁 domains/            # Domain-specific analysis
│   ├── politics.md
│   ├── military.md
│   ├── religious.md
│   ├── geographic.md
│   └── cryptocurrency.md      # NEW (from previous implementation)
│
├── 📁 research/          # Analysis results & findings
│   ├── timeline/           # Pattern timeline entries
│   ├── relationships/     # Relationship matrices
│   ├── cross_references/  # Cross-domain synthesis
│   └── heatmaps/          # ASCII correlation heatmaps
│
├── 📁 observations/      # Raw image/text analysis notes
│   ├── images/            # Gematria image files
│   └── transcriptions/    # OCR + manual analysis
│
├── 📁 scripts/           # Automation scripts (Python)
│   ├── overnight_research.py
│   ├── auto_obisidian_sync_v2.py
│   ├── sync_to_obsidian.py
│   └── heatmap_generator.py
│
├── 📁 obsidian_exports/  # Legacy compatibility layer
│   ├── CORE_SYMBOLS_SUMMARY.md
│   ├── PATTERN_MATRIX.md
│   ├── RELATIONSHIP_MATRIX.md
│   └── CROSS_REFERENCE_INDEX.md
│
├── 📄 AGENTS.md          # AI agent instructions (Tolaria feature)
├── 📄 VAULT_STRUCTURE.md # This structure document
└── 📄 TOLARIA_INTEGRATION_GUIDE.md  # Setup guide for users
```

---

## 📝 MIGRATE TO YAML FRONTMATTER FORMAT

### Before/After Example:

**Before (plain Markdown):**
```markdown
# Universal Threshold (Bridge)

Symbol ID: 124
Domains: [politics, military, religious]
Elemental Force: none
Confidence Score: 0.95

## Description
Universal threshold connecting all domains...
```

**After (with YAML frontmatter):**
```markdown
---
symbol_id: 124
name: Universal Threshold / Bridge
aliases: [universal, threshold, bridge, connector]
description: "Universal threshold connecting all domains"
domains:
  - politics
  - military
  - religious
elemental_force: null
confidence_score: 0.95
related_symbols:
  - symbol_id: 777
    relation: correlates_to
    score: 0.85
  - symbol_id: 666
    relation: completes_cycle
    score: 0.88
created: "2026-04-27"
last_modified: "2026-04-27"
tags: [core, bridge, universal]
---

## Description
Universal threshold connecting all domains...
```

### Migration Script (Python):

<tool_call>
<function=write_file>
<parameter=content>
#!/usr/bin/env python3
"""
Gematria Vault YAML Frontmatter Adder
Converts plain Markdown notes to Tolaria-compatible format with frontmatter.

Usage: python add_frontmatter.py [--recursive] [--dry-run]
"""

import os
import yaml
import sys
from pathlib import Path
from datetime import datetime

def add_frontmatter_to_file(filepath):
    """Add YAML frontmatter to a Markdown file."""
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check if already has frontmatter
    if content.strip().startswith('---'):
        print(f"[✅] {filepath} - Already has frontmatter")
        return False
    
    # Extract title (first H1 or first line)
    lines = content.split('\n')
    title = "Untitled"
    
    for line in lines[:5]:  # Check first 5 lines
        if line.startswith('# '):
            title = line[2:].strip()
            break
    
    # Create frontmatter
    frontmatter = {
        'title': title,
        'created': datetime.now().strftime('%Y-%m-%d'),
        'last_modified': datetime.now().strftime('%Y-%m-%d'),
    }
    
    # Add type-based metadata
    content_lower = content.lower()
    if 'symbol_id' in content_lower or 'symbol id:' in content_lower:
        frontmatter['type'] = 'core-symbol'
    elif 'force' in content_lower and 'elemental' in content_lower:
        frontmatter['type'] = 'elemental-force'
    elif 'domain' in content_lower:
        frontmatter['type'] = 'domain-analysis'
    else:
        frontmatter['type'] = 'analysis-note'
    
    # Try to extract domains if mentioned
    import re
    domain_pattern = r'(politics|military|religious|geographic|cryptocurrency|academic|social-media|ai-advancement)'
    match = re.search(domain_pattern, content_lower)
    if match:
        frontmatter['domains'] = [match.group()]
    
    # Create frontmatter string
    fm_lines = []
    for key, value in frontmatter.items():
        if isinstance(value, list):
            fm_lines.append(f'{key}:')
            for item in value:
                fm_lines.append(f'  - {item}')
        else:
            fm_lines.append(f'{key}: "{value}"')
    
    frontmatter_str = '---\n' + '\n'.join(fm_lines) + '\n---\n'
    
    # Write with frontmatter
    new_content = frontmatter_str + content
    
    if not os.environ.get('DRY_RUN'):
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"[✅] {filepath} - Added frontmatter")
    
    return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Add YAML frontmatter to gematria vault files')
    parser.add_argument('directory', type=str, help='Directory to process')
    parser.add_argument('--recursive', '-r', action='store_true', help='Process subdirectories')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed')
    
    args = parser.parse_args()
    
    root = Path(args.directory)
    
    if not root.exists():
        print(f"[❌] Directory not found: {root}")
        sys.exit(1)
    
    markdown_files = list(root.rglob('*.md'))
    
    modified_count = 0
    already_having_fm_count = 0
    
    for filepath in markdown_files:
        try:
            if args.recursive or '.hermes/gematria' in str(filepath):
                was_modified = add_frontmatter_to_file(filepath)
                if was_modified and not args.dry_run:
                    modified_count += 1
                elif was_modified and args.dry_run:
                    print(f"Would modify: {filepath}")
                    modified_count += 1
                else:
                    already_having_fm_count += 1
        except Exception as e:
            print(f"[⚠️] Error processing {filepath}: {e}")
    
    print("\n" + "=" * 60)
    print(f"Summary:")
    print(f"  Files with frontmatter added: {modified_count}")
    print(f"  Files already had frontmatter: {already_having_fm_count}")
    print(f"Total files processed: {modified_count + already_having_fm_count}")

if __name__ == '__main__':
    main()
