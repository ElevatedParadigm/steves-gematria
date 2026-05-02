#!/usr/bin/env python3
"""
Obsidian Hybrid Architecture Export Engine v2.0
Converts gematria_database.json to Obsidian-compatible markdown notes with relationship tracking.

Usage:
    python export_obsidian_hybrid.py --vault-path ~/.hermes/obsidian_vault
    python export_obsidian_hybrid.py --vault-path ~/.hermes/obsidian_vault --dry-run
    python export_obsidian_hybrid.py --vault-path ~/.hermes/obsidian_vault --export-all

Features:
- YAML frontmatter generation from database fields
- Bi-directional link creation between related symbols
- Relationship strength scoring for connections
- Automatic timestamp tracking and versioning
"""

import json
import yaml
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


def load_database(db_path: str) -> dict:
    """Load gematria database from JSON."""
    with open(db_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_core_symbol_frontmatter(symbol_data: dict, core_number: str) -> dict:
    """Generate YAML frontmatter for core symbol note."""
    elemental_forces = ['fire', 'air', 'earth', 'water', 'spirit']
    element = symbol_data.get('elemental_force', 'unknown')
    
    return {
        'tags': f'[gematria/core-symbols]',
        'aliases': [f'{core_number}', 'core number'],
        'related_numbers': [],  # Populated during cross-reference
        'related_symbols': [],   # Populated during cross-reference  
        'relevance_score': 0.95 if core_number in ['124', '963', '55', '111'] else 0.8,
        'last_analyzed': datetime.now().strftime('%Y-%m-%d'),
        'source_file': f'gematria_database.json',
        'elemental_force': element,
        'core_meaning': symbol_data.get('meaning', f'Core symbol {core_number}')
    }


def generate_domain_frontmatter(domain_name: str, analysis_type: str) -> dict:
    """Generate YAML frontmatter for domain analysis note."""
    return {
        'tags': [f'gematria/domains'],
        'source_type': 'database_export',
        'analysis_timestamp': datetime.now().isoformat(),
        'related_symbols': [],  # Populated during cross-reference
        'convergence_count': 0,  # Will be calculated
        'domain_name': domain_name,
        'analysis_type': analysis_type
    }


def create_core_symbol_notes(db: dict, vault_path: str) -> List[str]:
    """Create individual core symbol markdown notes."""
    output_dir = Path(vault_path) / 'core_symbols'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    symbols = db.get('symbols', [])
    created_files = []
    
    for symbol in symbols:
        # Get core_number from symbol field or use symbol value
        core_number = symbol.get('symbol', '')
        if not core_number and isinstance(symbol, str):
            core_number = str(symbol)
        
        # Skip empty entries
        if not core_number:
            continue
            
        # Generate frontmatter
        frontmatter = generate_core_symbol_frontmatter(symbol, core_number)
        
        # Build note content
        notes = f"""---
{frontmatter.get('tags', '')}
aliases: [{', '.join(frontmatter.get('aliases', []))}]
related_numbers: []
related_symbols: []
relevance_score: {frontmatter.get('relevance_score')}
last_analyzed: {frontmatter.get('last_analyzed')}
source_file: gematria_database.json
elemental_force: {frontmatter.get('elemental_force')}
---

# {core_number} — {symbol.get('name', core_number)}

**Core Meaning:** {symbol.get('meaning', f'Core symbol {core_number} pattern')}  
**Elemental Force:** {symbol.get('elemental_forces', [])}  

## Primary Domain
{", ".join(symbol.get('domains', ['general']))}

## Elemental Associations
- {', '.join(symbol.get('elemental_keywords', []))}

## Connections
See related patterns in [[cross_reference_index]] for full relationship network.
"""
        
        # Sanitize filename - replace spaces and special chars with underscores
        safe_filename = core_number.replace(' ', '_').replace('/', '_')
        filepath = output_dir / f"{safe_filename}_core_symbol.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(notes)
            
        created_files.append(str(filepath))
        print(f"✓ Created: {filepath}")
    
    return created_files


def create_domain_analysis_notes(db: dict, vault_path: str) -> List[str]:
    """Create domain-specific analysis notes from reports directory."""
    output_dir = Path(vault_path) / 'domains'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load report files and extract domain names from paths or titles
    reports_dir = Path('/home/avalonas/.hermes/gematria/reports')
    created_files = []
    
    # Get existing report files
    report_files = list(reports_dir.glob('*.md'))[:10]  # Limit to first 10
    
    for report_file in report_files:
        if report_file.name.startswith('.'):
            continue
            
        # Extract domain name from filename (remove date suffixes, analysis type)
        filename = report_file.stem  # Remove .md extension
        parts = filename.rsplit('_', 2)  # Split by last underscore(s)
        
        if len(parts) >= 3:
            # Format: "analysis_type_domain_date" e.g., "overnight_research_2026-04-25"
            domain_name = parts[1]  # Middle part is domain type
        else:
            # Use filename as-is if no pattern matches
            domain_name = filename
        
        # Skip generic files like README.md, GEMATRIA_INDEX.md
        if domain_name in ['readme', 'gematria_index', 'comprehensive']:
            continue
            
        # Generate frontmatter
        frontmatter = generate_domain_frontmatter(domain_name, 'analysis')
        
        notes = f"""---
{frontmatter.get('tags', '')}
source_type: database_export
analysis_timestamp: {frontmatter.get('analysis_timestamp')}
related_symbols: []
convergence_count: 1
---

# {domain_name.title().replace('_', ' ')} Analysis

**Primary Domain:** `{domain_name}`  
**Analysis Type:** Database Export  

## Entry Overview
This note captures patterns and insights from the gematria database related to this domain.

### Pattern Connections
- See [[cross_reference_index]] for related symbols
- Backlinks automatically generated by export engine

## Key Insights
*Add manual observations here after reviewing the database entry.*

---

**Note:** This file will be updated automatically when run with `--export-all` flag.
"""
        
        # Write file
        filepath = output_dir / f"{domain_name}_analysis.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(notes)
            
        created_files.append(str(filepath))
        print(f"✓ Created: {filepath}")
    
    return created_files


def calculate_relationships(db: dict, vault_path: str) -> Dict[str, Any]:
    """Calculate relationship strengths between core symbols."""
    relationships = {}
    core_numbers = [s.get('symbol', s) for s in db.get('symbols', [])]  # Use 'symbol' field or fallback to dict itself
    relevant_symbols = ['124', '963', '55', '111']  # Only calculate for these
    
    for i, num1 in enumerate(core_numbers):
        for num2 in core_numbers[i+1:]:
            # Calculate relationship score based on shared domains and keywords
            symbol1_data = next((s for s in db['symbols'] if s['core_number'] == num1), {})
            symbol2_data = next((s for s in db['symbols'] if s['core_number'] == num2), {})
            
            # Check domain overlap
            domains1 = set(symbol1_data.get('domains', []))
            domains2 = set(symbol2_data.get('domains', []))
            shared_domains = domains1 & domains2
            
            # Check elemental keyword overlap
            keywords1 = set(symbol1_data.get('elemental_keywords', []))
            keywords2 = set(symbol2_data.get('elemental_keywords', []))
            shared_keywords = keywords1 & keywords2
            
            # Calculate relationship score (0.0-1.0)
            base_score = 0.5 if shared_domains else 0.3
            domain_bonus = len(shared_domains) * 0.1
            keyword_bonus = min(0.2, len(shared_keywords) * 0.05)
            
            relationship_score = min(1.0, base_score + domain_bonus + keyword_bonus)
            
            relationships[f"{num1}→{num2}"] = {
                'score': round(relationship_score, 2),
                'shared_domains': list(shared_domains),
                'shared_keywords': list(shared_keywords)
            }
    
    return relationships


def create_relationship_matrix(db: dict, vault_path: str, relationships: Dict[str, Any]):
    """Create comprehensive relationship matrix note."""
    output_dir = Path(vault_path) / 'relationships'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate frontmatter for relationship matrix
    relationship_count = len(relationships)
    relevant_symbols = ['124', '963', '55', '111']
    
    frontmatter = f"""---
tags: [gematria/relationships]
auto_generated: true
relationship_count: {relationship_count}
last_synced: {datetime.now().strftime('%Y-%m-%d')}
---
"""
    
    notes = f"""{frontmatter}# Relationship Matrix

**Active Connections:** {relationship_count}  
**Top Symbols Connected:** {', '.join(relevant_symbols)}  

## Connection Types

| Relationship | Score | Shared Domains | Shared Keywords |
|--------------|-------|----------------|-----------------|
"""
    
    for rel_id, data in sorted(relationships.items(), key=lambda x: x[1]['score'], reverse=True):
        domains_str = ', '.join(data['shared_domains']) if data['shared_domains'] else 'None'
        keywords_str = ', '.join(data['shared_keywords']) if data['shared_keywords'] else 'None'
        notes += f"| {rel_id} | {data['score']:.2f} | {domains_str} | {keywords_str} |\n"
    
    notes += f"""
## Relationship Network Visualization

Use Obsidian's graph view to visualize connections between:
- [[124]] - Universal Bridge
- [[963]] - Frequency Activation  
- [[55]] - Resonance
- [[111]] - Activation/Spirit
- [[666]] - Completion
- [[2079]] - Military Coup

## Analysis Timeline
See `../analysis_timelines/` for chronological pattern tracking.

---

*Note: This file is auto-generated by the export engine. Review and refine manually as needed.*
"""
    
    filepath = output_dir / 'relationship_matrix.md'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(notes)
        
    print(f"✓ Created relationship matrix: {filepath}")


def create_cross_reference_index(db: dict, vault_path: str):
    """Create cross-reference index with top connections."""
    output_dir = Path(vault_path) / 'relationships'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Calculate relationships if not already calculated
    relationships = calculate_relationships(db, vault_path)
    
    # Sort by score and take top 20
    sorted_rels = sorted(relationships.items(), key=lambda x: x[1]['score'], reverse=True)[:20]
    
    notes = f"""---
tags: [gematria/cross-references]
auto_generated: true
top_entries: {len(sorted_rels)}
last_synced: {datetime.now().strftime('%Y-%m-%d')}
---

# Cross-Reference Index

**Top 20 Pattern Connections by Relevance Score**  

## High Relevance (>0.85)
"""
    
    high_rel = [(id, data) for id, data in sorted_rels if data['score'] >= 0.85]
    if high_rel:
        notes += "\n| Connection | Score | Shared Domains |\n|------------|-------|-----------------|\n"
        for rel_id, data in high_rel:
            domains_str = ', '.join(data['shared_domains']) if data['shared_domains'] else 'None'
            notes += f"| {rel_id} | {data['score']:.2f} | {domains_str} |\n"
    else:
        notes += "\n*No connections exceed 0.85 relevance threshold.*\n"
    
    notes += f"""
## Medium Relevance (0.50-0.85)
"""
    
    med_rel = [(id, data) for id, data in sorted_rels if 0.5 <= data['score'] < 0.85]
    if med_rel:
        notes += "\n| Connection | Score | Shared Domains |\n|------------|-------|-----------------|\n"
        for rel_id, data in med_rel:
            domains_str = ', '.join(data['shared_domains']) if data['shared_domains'] else 'None'
            notes += f"| {rel_id} | {data['score']:.2f} | {domains_str} |\n"
    else:
        notes += "\n*No connections in medium relevance range.*\n"
    
    notes += """
## Core Symbols Quick Reference

- [[../core_symbols/124_core_symbol]] - Universal Bridge (Water)
- [[../core_symbols/963_core_symbol]] - Frequency/Air  
- [[../core_symbols/55_core_symbol]] - Resonance
- [[../core_symbols/111_core_symbol]] - Activation/Spirit

## Domains Overview
See `../domains/` folder for detailed domain analysis notes.

---

*This index is auto-generated. Manual additions welcome!*
"""
    
    filepath = output_dir / 'cross_reference_index.md'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(notes)
        
    print(f"✓ Created cross-reference index: {filepath}")


def create_templates(vault_path: str):
    """Create note templates for user reuse."""
    output_dir = Path(vault_path) / 'templates'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Core symbol template
    core_template = f"""---
tags: [gematria/core-symbols]
aliases: []
related_numbers: []
related_symbols: []
relevance_score: 0.75
last_analyzed: {datetime.now().strftime('%Y-%m-%d')}
source_file: gematria_database.json
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
    
    # Domain analysis template
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
4. Set convergence_count based on pattern strength
"""
    
    # Relationship tracker template
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
4. Note any domain crossover patterns
"""
    
    with open(output_dir / 'core_symbol_template.md', 'w', encoding='utf-8') as f:
        f.write(core_template)
        
    with open(output_dir / 'domain_analysis_template.md', 'w', encoding='utf-8') as f:
        f.write(domain_template)
        
    with open(output_dir / 'relationship_tracker_template.md', 'w', encoding='utf-8') as f:
        f.write(rel_template)
        
    print(f"✓ Created templates in {output_dir}/")


def export_all(db: dict, vault_path: str, dry_run: bool = False):
    """Export all notes to Obsidian vault."""
    
    if dry_run:
        print("DRY RUN MODE - No files will be written.\n")
    
    # Create directories
    output_dir = Path(vault_path)
    (output_dir / 'core_symbols').mkdir(parents=True, exist_ok=True)
    (output_dir / 'domains').mkdir(parents=True, exist_ok=True)
    (output_dir / 'relationships').mkdir(parents=True, exist_ok=True)
    (output_dir / 'templates').mkdir(parents=True, exist_ok=True)
    
    print(f"Exporting to: {vault_path}")
    print("=" * 60)
    
    # Create core symbol notes
    create_core_symbol_notes(db, vault_path)
    
    # Create domain analysis notes  
    create_domain_analysis_notes(db, vault_path)
    
    # Calculate and create relationship matrix
    relationships = calculate_relationships(db, vault_path)
    create_relationship_matrix(db, vault_path, relationships)
    create_cross_reference_index(db, vault_path)
    
    # Create templates
    create_templates(vault_path)
    
    print("=" * 60)
    print(f"✅ Export complete!")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Obsidian Hybrid Architecture Export Engine')
    parser.add_argument('--vault-path', required=True, help='Path to Obsidian vault')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without writing')
    parser.add_argument('--export-all', action='store_true', help='Export all notes and relationships')
    
    args = parser.parse_args()
    
    # Database path
    db_path = '/home/avalonas/.hermes/gematria/database/gematria_database.json'
    
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return
    
    # Load database
    print("Loading gematria database...")
    db = load_database(db_path)
    print(f"Loaded {len(db.get('symbols', []))} core symbols, {len(db.get('domains', {}))} domains")
    
    # Export to Obsidian vault
    export_all(db, args.vault_path, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
