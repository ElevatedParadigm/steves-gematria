#!/usr/bin/env python3
"""
🧿 Steve's Gematria Search Scripts
=====================================
Automated search utilities for the gematria database.
Location: ~/.hermes/gematria/

Usage: Run from terminal or import into Python scripts.
"""

import json
import os
import re
import glob
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

DATABASE_PATH = "~/.hermes/gematria/database/gematria_database.json"
REPORTS_DIR = "~/.hermes/gematria/reports/"
NUMERIC_CORE_SYMBOLS = [124, 963, 55, 111, 666, 17]

# ============================================================================
# CORE FUNCTIONS - Pattern Searching
# ============================================================================

def find_all_core_symbol_mentions():
    """
    Find all mentions of core numeric symbols across analysis reports.
    
    Returns: Dict mapping symbol → {file: line_numbers}
    """
    print(f"🔍 Scanning for core numerical patterns...")
    results = {}
    
    # Core symbol regex pattern (handles "124", "124+", etc.)
    pattern = r'\b(' + '|'.join(map(str, NUMERIC_CORE_SYMBOLS)) + r')\b'
    
    reports = glob.glob(os.path.expanduser(REPORTS_DIR) + "*.md")
    
    for report in reports:
        with open(report, 'r', encoding='utf-8') as f:
            content = f.read()
            
        for symbol in NUMERIC_CORE_SYMBOLS:
            matches = [(m.start(), m.group()) for m in re.finditer(pattern, content)]
            if matches:
                # Group by position and extract context
                positions = [m[0] for m in matches]
                
                if symbol not in results:
                    results[symbol] = {}
                
                results[symbol][report] = {
                    "count": len(matches),
                    "positions": positions[:10],  # First 10 occurrences
                    "context_sample": content[max(0, positions[0]-50):positions[-1]+50] if positions else ""
                }
    
    return results


def search_for_number_sequence(search_query):
    """
    Search for a specific number sequence across all reports.
    
    Args:
        search_query: String like "124", "963+55", etc.
    
    Returns: List of (file, match) tuples with context
    """
    print(f"🔍 Searching for: {search_query}")
    matches = []
    
    # Pattern to find number sequences (flexible matching)
    pattern = search_query.replace('+', r'\+?')  # Allow optional plus signs
    
    reports = glob.glob(os.path.expanduser(REPORTS_DIR) + ".*")
    
    for report in sorted(reports):
        if not os.path.isfile(report):
            continue
            
        with open(report, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all matches with line context
        for match in re.finditer(pattern, content, re.IGNORECASE):
            line_num = content[:match.start()].count('\n') + 1
            context_lines = content[max(0, match.start()-200):match.end()+200]
            
            matches.append({
                "file": report,
                "line": line_num,
                "match": match.group(),
                "context": context_lines.strip()[:300] + ("..." if len(context_lines) > 300 else "")
            })
    
    return matches


def analyze_frequency_patterns():
    """
    Analyze frequency of core symbol appearances across reports.
    
    Returns: Dict mapping symbol → {file: count, total_count}
    """
    print(f"📊 Analyzing frequency patterns...")
    results = {}
    
    reports = glob.glob(os.path.expanduser(REPORTS_DIR) + ".*")
    
    for report in sorted(reports):
        if not os.path.isfile(report):
            continue
            
        with open(report, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for symbol in NUMERIC_CORE_SYMBOLS:
            count = len(re.findall(rf'\b{symbol}\b', content))
            
            if count > 0:
                if symbol not in results:
                    results[symbol] = {"files": {}, "total": 0}
                
                results[symbol]["files"][report] = count
                results[symbol]["total"] += count
    
    return results


def find_elemental_force_references():
    """
    Find references to elemental forces (fire, volcano, etc.) across reports.
    
    Returns: List of {file, line, match, context} tuples
    """
    print(f"🔥 Scanning for elemental force references...")
    matches = []
    
    # Keywords for elemental themes
    elemental_keywords = [r'\b(volcano|fire|elemental|transformation)\b', 
                         r'🌋',                          # Emoji patterns
                         r'\b(frequency|resonance)\b']   # Frequency references
    
    reports = glob.glob(os.path.expanduser(REPORTS_DIR) + ".*")
    
    for report in sorted(reports):
        if not os.path.isfile(report):
            continue
            
        with open(report, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            # Check for elemental keywords or emoji
            if any(re.search(pattern, line) for pattern in elemental_keywords[:2]):
                context = ' '.join(lines[max(0, line_num-3):line_num+3]).strip()
                matches.append({
                    "file": report,
                    "line": line_num,
                    "keyword": [k for k in elemental_keywords if re.search(k, line)][0],
                    "content": context.strip()[:200]
                })
    
    return matches


# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

def load_database():
    """Load the structured JSON database."""
    with open(os.path.expanduser(DATABASE_PATH), 'r', encoding='utf-8') as f:
        return json.load(f)


def export_search_results(search_type, results):
    """Export search results to a formatted file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.expanduser(f"~/.hermes/gematria/reports/search_{timestamp}.txt")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# 🔍 {search_type.upper()} SEARCH RESULTS\n")
        f.write(f"# Generated: {datetime.now().isoformat()}\n")
        f.write("# " + "="*70 + "\n\n")
        
        if search_type == "core_symbols":
            for symbol, data in results.items():
                f.write(f"\n## Symbol: {symbol}\n")
                for file, info in data.items():
                    f.write(f"File: {file}\n")
                    f.write(f"Count: {info['count']}\n")
                    if 'positions' in info:
                        f.write(f"Positions: {info['positions']}\n")
        
        elif search_type == "number_sequence":
            for match in results:
                f.write(f"\n**File:** {match['file']}\n")
                f.write(f"**Line:** {match['line']}\n")
                f.write(f"**Match:** {match['match']}\n\n")
                f.write(f"`{match['context']}`\n")
    
    print(f"✅ Results exported to: {output_file}")
    return output_file


# ============================================================================
# MAIN EXECUTION INTERFACE
# ============================================================================

def main_menu():
    """Interactive menu for search operations."""
    print("\n" + "="*60)
    print("🧿 STEVE'S GEMATRIA SEARCH UTILITIES")
    print("="*60)
    
    while True:
        print("\nOptions:")
        print("1. Find all core symbol mentions across reports")
        print("2. Search for specific number sequence")
        print("3. Analyze frequency patterns of core symbols")
        print("4. Find elemental force references")
        print("5. Export current database entries to text file")
        print("6. View database metadata and structure")
        print("0. Exit")
        
        choice = input("\nEnter option [0-6]: ").strip()
        
        if choice == "1":
            results = find_all_core_symbol_mentions()
            print(f"\nFound core symbol mentions in {len(results)} symbols:")
            for symbol, data in results.items():
                print(f"  → Symbol {symbol}: {len(data)} files")
            
            export_choice = input("\nExport to text file? (y/n): ").strip().lower()
            if export_choice == 'y':
                output_file = export_search_results("core_symbols", results)
        
        elif choice == "2":
            query = input("\nEnter number sequence (e.g., 124, 963+55): ").strip()
            matches = search_for_number_sequence(query)
            
            if matches:
                print(f"\nFound {len(matches)} match(es):")
                for i, match in enumerate(matches[:10], 1):  # Show first 10
                    print(f"\n{i}. File: {match['file']}")
                    print(f"   Line {match['line']}: {match['match']}")
            else:
                print("\nNo matches found.")
            
        elif choice == "3":
            results = analyze_frequency_patterns()
            print(f"\nFrequency analysis for {len(results)} symbols:")
            for symbol, data in sorted(results.items(), key=lambda x: x[1]['total'], reverse=True):
                files = len(data['files'])
                print(f"  → Symbol {symbol}: {data['total']} total mentions across {files} files")
            
        elif choice == "4":
            results = find_elemental_force_references()
            print(f"\nFound {len(results)} elemental force references:")
            for i, result in enumerate(results[:10], 1):
                print(f"{i}. [{result['file']}:L{result['line']}]")
                print(f"   {result['keyword']} keyword detected")
        
        elif choice == "5":
            db = load_database()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.expanduser(f"~/.hermes/gematria/reports/database_export_{timestamp}.txt")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(db, f, indent=2)
            
            print(f"\n✅ Database exported to: {output_file}")
        
        elif choice == "6":
            db = load_database()
            print("\n📊 DATABASE METADATA:")
            metadata = db.get('metadata', {})
            for key, value in metadata.items():
                print(f"  {key}: {value}")
            
        elif choice == "0":
            print("\n👋 Exiting...")
            break


if __name__ == "__main__":
    main_menu()
