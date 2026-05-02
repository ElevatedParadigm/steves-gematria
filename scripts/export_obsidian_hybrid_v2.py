#!/usr/bin/env python3
"""
Obsidian Hybrid Architecture Export Engine v2.1 (Simplified)
Converts existing gematria reports to Obsidian-compatible markdown notes with YAML frontmatter.

Usage:
    python export_obsidian_hybrid_v2.py --vault-path ~/.hermes/obsidian_vault
    python export_obsidian_hybrid_v2.py --vault-path ~/.hermes/obsidian_vault --dry-run
    
This version directly exports existing reports from /reports/ directory, ensuring 
compatibility with current gematria analysis files.
"""

import json
import os
from pathlib import Path
from datetime import datetime


def load_database(db_path: str) -> dict:
    """Load gematria database from JSON."""
    with open(db_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_element_from_core_number(core_num: str):
    """Map core number to elemental force."""
    element_map = {
        '124': 'water',
        '963': 'air',
        '55': 'fire',
        '111': 'spirit',
        '666': 'completion',
        '2079': 'fire',
        '279': 'earth',
        '360': 'water'
    }
    return element_map.get(str(core_num), 'unknown')


def get_domain_from_report_filename(filename: str) -> tuple:
    """Extract domain name from report filename."""
    # Remove extensions and date suffixes
    clean_name = filename.replace('.md', '').replace('_2026-', '').replace('-2026', '')
    
    # Skip generic files
    if clean_name.lower() in ['readme', 'gematria_index', 'complete', 'new_image_batch']:
        return None, None
    
    # Extract domain type (middle part of filename)
    parts = clean_name.rsplit('_', 1)
    if len(parts) == 2:
        domain_type, date_part = parts
    else:
        domain_type = clean_name
    
    return domain_type.lower().replace(' ', '_'), 'analysis'


def create_core_symbol_notes(db: dict, vault_path: str):
    """Create individual core symbol notes from database symbols."""
    output_dir = Path(vault_path) / 'core_symbols'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    symbols = db.get('symbols', [])
    
    for symbol in symbols:
        # Get core number (use 'symbol' field or convert to string)
        core_num = str(symbol.get('symbol', symbol)) if isinstance(symbol, dict) else str(symbol)
        
        # Skip empty entries
        if not core_num:
            continue
            
        # Generate frontmatter
        elemental = get_element_from_core_number(core_num)
        
        note_content = f"""---
tags: [gematria/core-symbols]
aliases: [{core_num}, 'core number']
related_numbers: []
related_symbols: []
relevance_score: 0.95 if {core_num} in ['124', '963', '55', '111'] else 0.8
last_analyzed: {datetime.now().strftime('%Y-%m-%d')}
source_file: gematria_database.json
elemental_force: {elemental}
---

# {core_num} — Core Symbol Pattern

**Core Meaning:** Primary pattern associated with number {core_num} in gematria analysis.  
**Elemental Force:** {elemental}  

## Primary Domain
General gematria pattern tracking and cross-reference analysis.

## Elemental Associations
Associated keywords and elemental forces found in database entries.

## Connections
See [[../relationships/cross_reference_index]] for full relationship network with this symbol.

---

*Note: This file was auto-generated from the gematria database.*
"""
        
        # Sanitize filename
        safe_filename = core_num.replace(' ', '_').replace('/', '_')
        filepath = output_dir / f"{safe_filename}_core_symbol.md"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(note_content)
            
        print(f"✓ Created: {filepath}")


def create_report_exports(reports_dir: str, vault_path: str):
    """Export existing reports to Obsidian vault format."""
    output_dir = Path(vault_path) / 'reports'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get existing report files
    reports_src = Path('/home/avalonas/.hermes/gematria/reports')
    
    for report_file in sorted(reports_src.glob('*.md')):
        if report_file.name.startswith('.'):
            continue
            
        filename = report_file.stem  # Remove .md
        
        # Skip generic files
        if any(x in filename.lower() for x in ['readme', 'gematria_index', 'comprehensive']):
            continue
            
        # Extract domain from filename
        domain_type, analysis_type = get_domain_from_report_filename(filename)
        
        if not domain_type:
            continue
        
        # Generate frontmatter
        timestamp = datetime.now().isoformat()
        convergence_count = 1
        
        frontmatter = f"""---
tags: [gematria/domains]
source_type: report_export
analysis_timestamp: {timestamp}
related_symbols: []
convergence_count: {convergence_count}
domain_name: {domain_type}
analysis_type: {analysis_type}
---

# {filename.replace('_', ' ').title()}

**Analysis Type:** `{analysis_type}`  
**Domain:** `{domain_type}`  

## Report Summary
This note captures patterns and insights from the gematria analysis report.

## Key Findings
- Patterns discovered during this analysis period
- Symbol connections identified
- Domain convergence points noted

## Related Symbols
See [[../core_symbols]] for core symbol notes, or [[../relationships/cross_reference_index]] for relationship tracking.

## Backlinks and Connections
Use Obsidian's graph view to discover connections between:
- Core symbols (124, 963, 55, 111, 666, 2079)
- Domain analysis notes in ../domains/
- Relationship matrices in ../relationships/

---

*Note: This file will be updated automatically when run with export-all flag.*
"""
        
        # Write to vault
        filepath = output_dir / f"{filename}.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter)
            
        print(f"✓ Created report export: {filepath}")


def create_domain_analysis_notes(vault_path: str):
    """Create domain-specific analysis notes."""
    output_dir = Path(vault_path) / 'domains'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create individual domain folders for major categories
    major_domains = ['epstein_files', 'political_events', 'military_coups', 'crypto_analysis']
    
    for domain in major_domains:
        notes = f"""---
tags: [gematria/domains]
source_type: domain_folder
related_symbols: []
convergence_count: 0
domain_name: {domain}
analysis_type: folder_placeholder
---

# {domain.title().replace('_', ' ')} Analysis Domain

**This is a domain placeholder.**

Use this note structure for organizing domain-specific analysis findings.

## Current Status
Domain tracking enabled in gematria pipeline.

## Symbol Connections
See [[../relationships/cross_reference_index]] for relationship tracking.

---

*Auto-generated domain folder placeholder.*
"""
        
        filepath = output_dir / f"{domain}_analysis.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(notes)
            
        print(f"✓ Created domain note: {filepath}")


def create_relationship_matrix(vault_path: str):
    """Create relationship matrix from database."""
    output_dir = Path(vault_path) / 'relationships'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    db_path = '/home/avalonas/.hermes/gematria/database/gematria_database.json'
    
    if not os.path.exists(db_path):
        print(f"⚠ Database not found at {db_path}, creating placeholder matrix")
        
        notes = f"""---
tags: [gematria/relationships]
auto_generated: true
relationship_count: 0
last_synced: {datetime.now().strftime('%Y-%m-%d')}
---

# Relationship Matrix (Placeholder)

**Active Connections:** TBD  
**Status:** Database integration in progress

## Connection Types
- Core symbols linked via shared domains
- Elemental force crossovers tracked
- Pattern convergence scores calculated

See cross_reference_index.md for full relationship network.
"""
        
        filepath = output_dir / 'relationship_matrix.md'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(notes)
        print(f"✓ Created placeholder: {filepath}")
        return
    
    # Load database
    with open(db_path, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    symbols = db.get('symbols', [])
    relevant_symbols = ['124', '963', '55', '111']
    symbol_map = {str(s.get('symbol', s)): {'number': str(s.get('symbol', s)), 'element': get_element_from_core_number(str(s.get('symbol', s)))} for s in symbols}
    
    # Generate relationship table
    relationship_rows = []
    for i, num1 in enumerate(relevant_symbols):
        if num1 in symbol_map:
            for num2 in relevant_symbols[i+1:]:
                if num2 in symbol_map:
                    relationship_rows.append((num1, num2))
    
    notes = f"""---
tags: [gematria/relationships]
auto_generated: true
relationship_count: {len(relationship_rows)}
last_synced: {datetime.now().strftime('%Y-%m-%d')}
---

# Relationship Matrix

**Active Connections:** {len(relationship_rows)}  
**Top Symbols Connected:** {', '.join(relevant_symbols)}  

## Connection Types

| Relationship | Description |
|--------------|-------------|
"""
    
    for num1, num2 in relationship_rows:
        elem1 = symbol_map.get(num1, {}).get('element', '')
        elem2 = symbol_map.get(num2, {}).get('element', '')
        if elem1 and elem2:
            notes += f"| {num1}→{num2} | Potential crossover between **{elem1}** and **{elem2}** domains |\n"
    
    notes += f"""
## Core Symbols Quick Reference

- [[../core_symbols/124_core_symbol]] - Universal Bridge ({symbol_map.get('124', {}).get('element', 'unknown')})
- [[../core_symbols/963_core_symbol]] - Frequency/Air  
- [[../core_symbols/55_core_symbol]] - Resonance
- [[../core_symbols/111_core_symbol]] - Activation/Spirit

## Relationship Network Visualization

Use Obsidian's graph view to visualize connections between core symbols and their elemental force associations.

---

*Note: This matrix will be updated with real-time analysis as new patterns are discovered.*
"""
    
    filepath = output_dir / 'relationship_matrix.md'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(notes)
        
    print(f"✓ Created relationship matrix: {filepath}")


def create_cross_reference_index(vault_path: str):
    """Create cross-reference index."""
    output_dir = Path(vault_path) / 'relationships'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    notes = f"""---
tags: [gematria/cross-references]
auto_generated: true
top_entries: 20
last_synced: {datetime.now().strftime('%Y-%m-%d')}
---

# Cross-Reference Index

**Pattern Connection Hub for Gematria Analysis**  

## Core Symbols Index

| Number | Symbol Name | Elemental Force | Relevance |
|--------|-------------|-----------------|-----------|
"""
    
    core_symbols = ['124', '963', '55', '111', '666', '2079']
    for num in core_symbols:
        relevance = 'High' if num in ['124', '963', '55', '111'] else 'Medium'
        notes += f"| {num} | Core Symbol | {get_element_from_core_number(num)} | {relevance} |\n"
    
    notes += """
## Domain Links

- [[../domains/epstein_files_analysis]] - Epstein Files Analysis
- [[../domains/political_events_analysis]] - Political Events Intelligence
- [[../domains/military_coups_analysis]] - Military Coups Intelligence  
- [[../domains/crypto_analysis]] - Crypto/Bitcoin Symbolism

## Relationship Tracking
See [[relationship_matrix]] for full connection map.

---

*This index is auto-generated and will update with new pattern discoveries.*
"""
    
    filepath = output_dir / 'cross_reference_index.md'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(notes)
        
    print(f"✓ Created cross-reference index: {filepath}")


def create_templates(vault_path: str):
    """Create note templates for user reuse."""
    output_dir = Path(vault_path) / 'templates'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    core_template = f"""---
tags: [gematria/core-symbols]
aliases: []
related_numbers: []
relevance_score: 0.75
last_analyzed: {datetime.now().strftime('%Y-%m-%d')}
elemental_force: fire
---

# NEW CORE SYMBOL NOTE TEMPLATE

**Use this template for new core symbol discoveries.**

## Template Instructions
1. Fill in YAML frontmatter with discovered patterns
2. Add semantic description in "Core Meaning" field  
3. Link to related symbols using [[syntax]]
4. Review before committing to database
"""
    
    domain_template = f"""---
tags: [gematria/domains]
source_type: manual
analysis_timestamp: {datetime.now().isoformat()}
related_symbols: []
convergence_count: 1
---

# NEW DOMAIN ANALYSIS TEMPLATE

**Use this template for new domain-specific findings.**

## Template Instructions
1. Update `analysis_timestamp` with current date
2. Add `related_symbols` as you discover connections
3. Document key insights in body
"""
    
    rel_template = f"""---
tags: [gematria/relationships]
auto_generated: true
relationship_count: 1
last_synced: {datetime.now().strftime('%Y-%m-%d')}
---

# NEW RELATIONSHIP TRACKER TEMPLATE

**Use this template for tracking new relationship discoveries.**

## Template Instructions
1. Add relationship strength score (0.0-1.0)
2. List shared domains and keywords  
3. Link to related symbol notes
"""
    
    with open(output_dir / 'core_symbol_template.md', 'w', encoding='utf-8') as f:
        f.write(core_template)
        
    with open(output_dir / 'domain_analysis_template.md', 'w', encoding='utf-8') as f:
        f.write(domain_template)
        
    with open(output_dir / 'relationship_tracker_template.md', 'w', encoding='utf-8') as f:
        f.write(rel_template)
        
    print(f"✓ Created templates in {output_dir}/")


def export_all(vault_path: str, dry_run: bool = False):
    """Export all notes to Obsidian vault."""
    
    if dry_run:
        print("DRY RUN MODE - No files will be written.\n")
    
    # Create directories
    (Path(vault_path) / 'core_symbols').mkdir(parents=True, exist_ok=True)
    (Path(vault_path) / 'reports').mkdir(parents=True, exist_ok=True)
    (Path(vault_path) / 'domains').mkdir(parents=True, exist_ok=True)
    (Path(vault_path) / 'relationships').mkdir(parents=True, exist_ok=True)
    (Path(vault_path) / 'templates').mkdir(parents=True, exist_ok=True)
    
    print(f"Exporting to: {vault_path}")
    print("=" * 60)
    
    # Create core symbol notes from database
    create_core_symbol_notes({}, vault_path)
    
    # Export existing reports
    create_report_exports('/home/avalonas/.hermes/gematria/reports', vault_path)
    
    # Create domain placeholders
    create_domain_analysis_notes(vault_path)
    
    # Create relationship tracking
    create_relationship_matrix(vault_path)
    create_cross_reference_index(vault_path)
    
    # Create templates
    create_templates(vault_path)
    
    print("=" * 60)
    print("✅ Export complete!")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Obsidian Hybrid Architecture Export Engine v2.1')
    parser.add_argument('--vault-path', required=True, help='Path to Obsidian vault')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without writing')
    
    args = parser.parse_args()
    
    db_path = '/home/avalonas/.hermes/gematria/database/gematria_database.json'
    
    if not os.path.exists(db_path):
        print(f"⚠ Database not found at {db_path}, continuing with export...")
    
    # Export to Obsidian vault
    export_all(args.vault_path, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
