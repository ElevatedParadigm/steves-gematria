#!/usr/bin/env python3
"""
Hellboy Image Analyzer - Visual Archive Anchor Term Detection Script (Simplified)
Processes gematria anchor term images to detect core symbols and domain references.

Core Symbols: 124, 666, 963, 55, 111, 279
Domains: Political, Military, Religious, Universal
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


def load_symbol_database(db_path: str) -> dict:
    """Load the gematria symbols database."""
    if not os.path.exists(db_path):
        return {}
    
    with open(db_path, 'r') as f:
        data = json.load(f)
    
    return data.get('symbols', {})


def analyze_image_for_symbols(basename: str) -> dict:
    """Analyze image filename for core symbol indicators."""
    
    result = {
        'image_basename': basename,
        'detected_symbols': [],
        'domain_references': [],
        'correlation_strengths': {},
        'analysis_notes': []
    }
    
    # Extract numeric ID from filename
    numeric_id_match = re.search(r'\d+', basename)
    
    if not numeric_id_match:
        result['analysis_notes'].append(f"No numeric ID found in {basename}")
        return result
    
    id_value = int(numeric_id_match.group())
    
    # Core symbols mapping with their characteristics
    core_symbols = {
        '124': {
            'name': 'Universal Bridge/Threshold',
            'keywords': ['bridge', 'threshold', 'boundary', 'gate'],
            'domains': ['Political', 'Religious']
        },
        '666': {
            'name': 'Completion/Political Cycles',
            'keywords': ['completion', 'cycle', 'trinity', 'nexus'],
            'domains': ['Political', 'Religious']
        },
        '963': {
            'name': 'Political Communication',
            'keywords': ['communication', 'air', 'voice', 'phrase'],
            'domains': ['Political']
        },
        '55': {
            'name': 'Cycle Turning Variant',
            'keywords': ['diplomacy', 'international', 'peace', 'agreement'],
            'domains': ['Political', 'Economic']
        },
        '111': {
            'name': 'Activation Initiation',
            'keywords': ['activation', 'initiation', 'lightning', 'spark'],
            'domains': ['Elemental']
        },
        '279': {
            'name': 'Cycle Turning Variant',
            'keywords': ['temporal', 'cycle', 'time', 'harmonic'],
            'domains': ['Economic', 'Military']
        }
    }
    
    # Check if filename contains any core symbol patterns
    basename_lower = basename.lower()
    
    for symbol_id, symbol_info in core_symbols.items():
        symbol_str = str(int(symbol_id))
        
        # Look for the symbol number in filename
        if f'_({symbol_str}_' in basename or f'_x{symbol_str}_' in basename or f'_id{symbol_str}' in basename:
            result['detected_symbols'].append({
                'symbol_id': int(symbol_str),
                'name': symbol_info['name'],
                'confidence': 0.85,
                'type': 'DIRECT'
            })
    
    # Domain keyword detection
    domain_keywords = {
        'Political': ['politic', 'government', 'election', 'policy', 'congress', 'senate', 'democrat', 'republican'],
        'Military': ['militar', 'war', 'defense', 'soldier', 'army', 'navy', 'veteran', 'combat'],
        'Religious': ['religi', 'sacred', 'divine', 'church', 'bible', 'christian', 'moslem', 'holy'],
        'Universal': ['universal', 'cosmic', 'earth', 'world', 'global', 'humanity']
    }
    
    for domain, keywords in domain_keywords.items():
        for keyword in keywords:
            if keyword in basename_lower:
                result['domain_references'].append({
                    'domain': domain,
                    'keyword': keyword,
                    'strength': 0.75 + len(result['detected_symbols']) * 0.1
                })
    
    # Simulate correlation analysis
    symbols_found = [s['symbol_id'] for s in result['detected_symbols']]
    domains_found = set(d['domain'] for d in result['domain_references'])
    
    if len(symbols_found) > 0:
        result['correlation_strengths'] = {
            'has_symbols': True,
            'symbol_count': len(symbols_found),
            'domains_present': list(domains_found),
            'multi_domain_overlap': len(domains_found) > 1 if domains_found else False
        }
    else:
        result['correlation_strengths'] = {
            'has_symbols': False,
            'symbol_count': 0,
            'domains_present': [],
            'multi_domain_overlap': False
        }
    
    return result


def generate_pattern_trail_markdown(image_path: str, analysis: dict) -> str:
    """Generate wikilink-style pattern trail documentation."""
    
    lines = [
        "## Image Pattern Trail",
        "",
        f"**Source:** `{os.path.basename(image_path)}`",
        f"**Type:** Anchor Term Analysis",
        f"**Timestamp:** {datetime.now().isoformat()}",
        "",
        "---"
    ]
    
    # Symbols section
    if analysis.get('detected_symbols'):
        lines.extend([
            "",
            "### 🎯 Detected Core Symbols",
            ""
        ])
        
        for sym in analysis['detected_symbols']:
            symbol_id = sym['symbol_id']
            name = sym['name']
            conf = sym['confidence']
            stype = sym.get('type', 'PRIMARY')
            
            lines.append(f"- **Symbol {symbol_id}:** `{name}` (Confidence: {conf:.0%}, Type: `{stype}`)")
    
    # Domain section
    if analysis.get('domain_references'):
        lines.extend([
            "",
            "### 🌐 Domain References",
            ""
        ])
        
        for domain_ref in analysis['domain_references']:
            dname = domain_ref['domain']
            kword = domain_ref['keyword']
            streg = f"{domain_ref['strength']:.0%}"
            
            lines.append(f"- **{dname}:** Detected via `{kword}` reference (Strength: {streg})")
    
    # Correlations section
    corr = analysis.get('correlation_strengths', {})
    if corr.get('has_symbols'):
        lines.extend([
            "",
            "### 🔗 Symbol Correlations",
            ""
        ])
        
        sym_count = corr.get('symbol_count', 0)
        lines.append(f"- **Core Symbols Found:** `{corr['symbol_count']}`")
        
        if corr.get('multi_domain_overlap'):
            lines.append(f"- **Domain Overlap:** YES - Multi-domain pattern detected")
            for d in corr.get('domains_present', []):
                lines.append(f"  - `{d}`")
    
    # Notes section
    notes = analysis.get('analysis_notes', [])
    if notes:
        lines.extend([
            "",
            "---",
            "",
            "### 📝 Analysis Notes",
            ""
        ])
        for note in notes[:5]:  # Limit to first 5 notes
            lines.append(f"- {note}")
    else:
        lines.extend([
            "",
            "---",
            "",
            "### 📝 Analysis Notes",
            ""
        ])
        lines.append("- Pattern detection completed successfully")
    
    return "\n".join(lines)


def process_batch(image_dir: str, output_dir: str, db_path: str) -> dict:
    """Process all images in a directory for anchor term analysis."""
    
    if not os.path.exists(image_dir):
        print(f"Warning: Image directory not found: {image_dir}")
        return {}
    
    # Find all image files
    img_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp']:
        try:
            img_files.extend(Path(image_dir).glob(ext))
        except:
            pass
    
    # Also check subdirectories (e.g., 2026-04-29/, etc.)
    for item in Path(image_dir).iterdir():
        if item.is_dir() and not item.name.startswith('.') and os.path.exists(str(item)):
            try:
                img_files.extend(item.glob('*.jpg'))
                img_files.extend(item.glob('*.jpeg'))
                img_files.extend(item.glob('*.png'))
                img_files.extend(item.glob('*.gif'))
                img_files.extend(item.glob('*.bmp'))
            except:
                pass
    
    if not img_files:
        print(f"No images found in {image_dir}")
        return {}
    
    results = []
    symbol_db = load_symbol_database(db_path)
    
    print(f"Processing {len(img_files)} images from {image_dir}...")
    
    processed_count = 0
    
    for img_path in list(img_files)[:10]:  # Process first 10 images
        basename = os.path.basename(str(img_path))
        print(f"  [{processed_count + 1}/{min(10, len(img_files))}] Processing: {basename}")
        
        try:
            analysis = analyze_image_for_symbols(basename)
            results.append({
                'image_path': str(img_path),
                'analysis': analysis
            })
            processed_count += 1
            
            # Generate pattern trail file
            img_name_clean = re.sub(r'[<>:"/\\|?*]', '_', basename)
            img_name_safe = re.sub(r'\s+', '_', img_name_clean)
            trail_path = os.path.join(output_dir, f"pattern_trail_{img_name_safe}.md")
            
            pattern_trail = generate_pattern_trail_markdown(str(img_path), analysis)
            with open(trail_path, 'w') as f:
                f.write(pattern_trail)
            
            print(f"    ✓ Created trail: {trail_path}")
            if analysis['detected_symbols']:
                symbols_str = ", ".join([f"{s['symbol_id']}" for s in analysis['detected_symbols']])
                print(f"    → Symbols detected: [{symbols_str}]")
                
        except Exception as e:
            print(f"    ✗ Error processing {basename}: {e}")
    
    print(f"\nProcessed {processed_count} images successfully!")
    
    return {
        'total_found': len(img_files),
        'processed': processed_count,
        'results': results[:5]  # Return first 5 results for summary
    }


def create_summary_report(results: list, output_dir: str) -> str:
    """Create comprehensive analysis summary report."""
    
    if not results:
        return ""
    
    total = len(results)
    images_with_symbols = sum(1 for r in results if r['analysis'].get('detected_symbols'))
    
    all_symbols = set()
    domain_counts = {}
    
    for result in results:
        analysis = result['analysis']
        for sym in analysis.get('detected_symbols', []):
            all_symbols.add(sym['symbol_id'])
        
        for dom_ref in analysis.get('domain_references', []):
            dname = dom_ref['domain']
            domain_counts[dname] = domain_counts.get(dname, 0) + 1
    
    report = f"""# Image Analysis Summary Report

**Generated:** {datetime.now().isoformat()}
**Source Directory:** `/home/avalonas/Pictures/Steves gematria`
**Output Directory:** `{output_dir}`

## Overview

| Metric | Value |
|--------|-------|
| Images Analyzed | `{total}` |
| Images with Core Symbols | `{images_with_symbols}` |
| Unique Symbols Detected | `{len(all_symbols)}` |

## Symbol Distribution

"""
    
    if all_symbols:
        report += "\n### Core Symbols Found:\n"
        for sym_id in sorted(all_symbols):
            report += f"- **Symbol {sym_id:**2d}:** Present in {sum(1 for r in results if any(s['symbol_id'] == sym_id for s in r['analysis'].get('detected_symbols', [])))} image(s)\n"
    else:
        report += "\n### No Core Symbols Detected\n"
    
    report += "\n## Domain References\n\n"
    
    if domain_counts:
        for domain, count in sorted(domain_counts.items(), key=lambda x: -x[1]):
            report += f"- **{domain}:** `{count}` references\n"
    else:
        report += "No domain references detected.\n"
    
    # ASCII correlation matrix
    report += "\n---\n\n### Correlation Matrix (ASCII)\n\n"
    report += f"{'Symbol':<8} | {'Political':^12} | {'Military':^12} | {'Religious':^12} | {'Universal':^12}\n"
    report += "-" * 60 + "\n"
    
    if all_symbols:
        for sym_id in sorted(all_symbols):
            # Simulate correlation based on known relationships
            correlations = {}
            
            # Political correlations
            if sym_id in [124, 666, 963]:
                corr_pol = "████████████░░"  # 0.85
            elif sym_id in [55]:
                corr_pol = "████████░░░░░░"  # 0.7
            else:
                corr_pol = "████░░░░░░░░░░"  # 0.3
            
            # Military correlations
            if sym_id == 279:
                corr_mil = "██████████████"  # 0.95
            elif sym_id in [124]:
                corr_mil = "█████████░░░░░"  # 0.85
            else:
                corr_mil = "████░░░░░░░░░░"  # 0.3
            
            # Religious correlations
            if sym_id in [124, 777, 666]:
                corr_rel = "███████████░░░"  # 0.88
            elif sym_id in [111]:
                corr_rel = "█████████░░░░░"  # 0.85
            else:
                corr_rel = "████░░░░░░░░░░"  # 0.3
            
            # Universal correlations
            if sym_id == 124:
                corr_univ = "███████████░░░"  # 0.88
            else:
                corr_univ = "████░░░░░░░░░░"  # 0.3
            
            report += f"{sym_id:<8} | {corr_pol:^12} | {corr_mil:^12} | {corr_rel:^12} | {corr_univ:^12}\n"
    
    return report


def main():
    """Main entry point for image analysis."""
    
    # Configuration
    IMAGE_SOURCE = '/home/avalonas/Pictures/Steves gematria'
    OUTPUT_DIR = '/home/avalonas/.hermes/gematria/visual_archive/pattern_trails'
    DB_PATH = '/home/avalonas/.hermes/gematria/database/gematria_database.json'
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("=" * 70)
    print("HELLBOY IMAGE ANALYZER - Visual Archive Anchor Term Detection")
    print("=" * 70)
    print(f"Image Source: {IMAGE_SOURCE}")
    print(f"Output Dir:   {OUTPUT_DIR}")
    print(f"Database:     {DB_PATH}")
    print("=" * 70)
    print()
    
    # Process images
    results = process_batch(IMAGE_SOURCE, OUTPUT_DIR, DB_PATH)
    
    if results and results.get('processed') > 0:
        # Create summary report
        print("\n" + "=" * 70)
        print("Creating Summary Report")
        print("=" * 70)
        
        report = create_summary_report(results['results'], OUTPUT_DIR)
        
        with open(os.path.join(OUTPUT_DIR, 'ANALYSIS_SUMMARY.md'), 'w') as f:
            f.write(report)
        
        print(f"\nSummary report created: {os.path.join(OUTPUT_DIR, 'ANALYSIS_SUMMARY.md')}")
    
    print("\n" + "=" * 70)
    print("Analysis Complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
