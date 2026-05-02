#!/usr/bin/env python3
"""
search_patterns.py - STEVE'S GEMATRIA Pattern Extraction Script
Scans image directories and extracts gematria patterns, elemental symbols,
and cross-domain theme mappings from 103 images.

Usage: python search_patterns.py [--input-dir DISCORD_SESSION_PATH]
       python search_patterns.py --quick (fast overview)
"""

import os
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Configuration
BASE_DIR = Path.home() / '.hermes' / 'gematria'
IMAGE_CACHE = Path(BASE_DIR, 'image_cache')  # discord_session/image_cache/
ORGANIZED_DATA = Path(BASE_DIR, 'organized_images_rawdata')
PATTERNS_FOUND = defaultdict(list)
THEME_MAPPINGS = {}


def scan_directory(directory, category_name="uncategorized"):
    """Recursively scan directory and collect image paths"""
    images = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                filepath = Path(root) / file
                relative_path = filepath.relative_to(directory)
                images.append({
                    'path': str(relative_path),
                    'full_path': str(filepath),
                    'category': category_name,
                    'parent_dir': root.split('/')[-1] if '/' in str(root) else root
                })
    return images


def extract_numerology(text_or_filename):
    """Extract numerical patterns from text or filename"""
    patterns = {
        'core_symbols': [],  # 124, 111, 666, 963, etc.
        'sequences': [],     # Mathematical sequences like "51+963+55"
        'special_numbers': [],  # Special dates/years like 2079, 2025
    }
    
    text = str(text_or_filename).lower()
    
    # Core symbol detection
    core_symbol_map = {
        '124': 'universal_threshold',
        '111': 'activation',
        '666': 'completion_wholeness',
        '963': 'cycle_turning',
        '51': 'frequency',
        '55': 'harmony_integration',
    }
    
    for symbol, meaning in core_symbol_map.items():
        if symbol in text:
            patterns['core_symbols'].append({
                'symbol': symbol,
                'meaning': meaning,
                'count': text.count(symbol)
            })
    
    # Sequence detection (numbers separated by +)
    sequences = re.findall(r'(\d+[+\d]*)', text)
    for seq in sequences:
        if len(seq.split('+')) > 1:  # Multi-number sequence
            patterns['sequences'].append(seq.strip())
    
    # Special numbers (years, dates, special values)
    special_numbers = re.findall(r'(?:20\d{2}|[5-9]\d\d|[12]\d\d{3})', text)
    for num in set(special_numbers):
        if num not in ['2025']:  # Filter common year
            patterns['special_numbers'].append(num)
    
    return patterns


def detect_elemental_symbols(text_or_path):
    """Detect elemental force symbols (volcano, fire, etc.)"""
    elements = []
    
    text_lower = str(text_or_path).lower()
    
    # Emoji-based elemental detection
    emoji_map = {
        '🌋': {'name': 'volcano', 'element': 'fire_earth', 'meaning': 'transformation'},
        '🔥': {'name': 'fire', 'element': 'fire', 'meaning': 'passion/transformation'},
        '⚡': {'name': 'lightning', 'element': 'electricity', 'meaning': 'activation'},
        '💧': {'name': 'water', 'element': 'water', 'meaning': 'flow/harmony'},
        '🌊': {'name': 'wave', 'element': 'water', 'meaning': 'cycles'},
    }
    
    for emoji, data in emoji_map.items():
        if emoji in text_lower:
            elements.append(data)
    
    # Keyword-based elemental detection
    keywords = {
        'fire': ['fire', 'burning', 'flame'],
        'earth': ['earth', 'ground', 'soil'],
        'air': ['air', 'wind', 'breath'],
        'water': ['water', 'ocean', 'sea', 'river'],
    }
    
    for element_type, keywords_list in keywords.items():
        for keyword in keywords_list:
            if keyword in text_lower:
                elements.append({
                    'name': element_type.capitalize(),
                    'element': element_type,
                    'meaning': f'{element_type} elemental force',
                    'match': keyword
                })
    
    return list(set(elements))


def detect_cross_domain_themes(image_data):
    """Detect cross-domain theme mappings"""
    themes = []
    filename = image_data['path'].lower()
    content_text = ""  # Would extract from OCR in full implementation
    
    # Political themes
    political_keywords = ['trump', 'canada', 'usa', 'biden', 'hillary', 'maga']
    for kw in political_keywords:
        if kw in filename:
            themes.append('Political')
    
    # Legal themes
    legal_keywords = ['epstein', 'court', 'trial', 'justice', 'legal', 'document', 'files']
    for kw in legal_keywords:
        if kw in filename:
            themes.append('Legal')
    
    # Financial themes
    financial_keywords = ['bitcoin', 'crypto', 'stock', 'bank', 'money', 'coin', 'trading', 'mining']
    for kw in financial_keywords:
        if kw in filename:
            themes.append('Financial')
    
    # Media themes
    media_keywords = ['tiktok', 'news', 'article', 'tweet', 'youtube', 'instagram', 'media']
    for kw in media_keywords:
        if kw in filename:
            themes.append('Media')
    
    # Power figure themes (crosses multiple domains)
    power_figure_keywords = ['gates', 'musk', 'lutnick', 'hillary', 'zuckerberg']
    for kw in power_figure_keywords:
        if kw in filename:
            themes.append('Power Figure')
    
    return list(set(themes))


def analyze_images():
    """Main analysis function"""
    print("=" * 70)
    print("STEVE'S GEMATRIA PATTERN EXTRACTION V1.0")
    print("=" * 70)
    
    # Scan all organized image directories
    categories = ['political', 'legal', 'financial', 'media']
    
    for category in categories:
        category_path = Path(ORGANIZED_DATA, category) if Path(ORGANIZED_DATA, category).exists() else IMAGE_CACHE
        try:
            images = scan_directory(category_path, category)
            print(f"\n📁 Analyzing {category.upper()} directory ({len(images)} images)...")
            
            for image in images:
                patterns = extract_numerology(image['path'])
                elements = detect_elemental_symbols(image['path'])
                themes = detect_cross_domain_themes(image)
                
                if patterns or elements or themes:
                    analysis_result = {
                        'image': image,
                        'gematria_patterns': patterns,
                        'elemental_symbols': elements,
                        'themes': themes,
                        'scan_time': datetime.now().isoformat()
                    }
                    
                    PATTERNS_FOUND[image['path']] = analysis_result
                    
        except Exception as e:
            print(f"  Error scanning {category}: {e}")
    
    return PATTERNS_FOUND


def generate_summary(patterns_found):
    """Generate pattern extraction summary"""
    print("\n" + "=" * 70)
    print("PATTERN EXTRACTION SUMMARY")
    print("=" * 70)
    
    # Core symbols found
    core_symbol_counts = defaultdict(int)
    for img, data in patterns_found.items():
        for symbol_data in data['gematria_patterns']['core_symbols']:
            core_symbol_counts[symbol_data['symbol']] += symbol_data['count']
    
    print("\n🔢 CORE GEMATRIA SYMBOLS DETECTED:")
    for symbol, count in sorted(core_symbol_counts.items(), key=lambda x: -x[1]):
        bar = '█' * min(count // 5, 20)
        print(f"   {symbol}: {count} occurrences [{bar}]")
    
    # Elemental symbols found
    elemental_counts = defaultdict(int)
    for img, data in patterns_found.items():
        for elem in data['elemental_symbols']:
            key = f"{elem['name']} ({elem['element']})"
            elemental_counts[key] += 1
    
    print("\n🌋 ELEMENTAL SYMBOLS DETECTED:")
    for element, count in sorted(elemental_counts.items(), key=lambda x: -x[1]):
        print(f"   {element}: {count} occurrences")
    
    # Theme mappings
    theme_counts = defaultdict(int)
    for img, data in patterns_found.items():
        for theme in data['themes']:
            theme_counts[theme] += 1
    
    print("\n🗺️ CROSS-DOMAIN THEME MAPPINGS:")
    for theme, count in sorted(theme_counts.items(), key=lambda x: -x[1]):
        print(f"   {theme}: {count} images")
    
    # Cross-domain examples
    print("\n🔗 CROSS-DOMAIN EXAMPLES:")
    cross_domain_examples = [img for img, data in patterns_found.items() if len(data['themes']) > 1]
    for example in cross_domain_examples[:10]:  # Top 10
        print(f"   • {example}: {', '.join(data['themes'])}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Steve\'s Gematria Pattern Extraction')
    parser.add_argument('--input-dir', type=str, help='Image directory path')
    parser.add_argument('--quick', action='store_true', help='Quick overview mode')
    
    args = parser.parse_args()
    
    # Use configured paths or argument
    base_dir = args.input_dir if args.input_dir else Path(ORGANIZED_DATA)
    
    if not base_dir.exists():
        print(f"Error: Directory {base_dir} does not exist")
        print(f"Expected path: {Path(ORGANIZED_DATA)}")
        return
    
    # Run analysis
    patterns_found = analyze_images()
    
    if patterns_found:
        generate_summary(patterns_found)
        
        # Save detailed report
        summary_path = Path(base_dir.parent, 'pattern_extraction_report.txt')
        with open(summary_path, 'w') as f:
            f.write("# GEMATRIA PATTERN EXTRACTION REPORT\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write(f"# Total images analyzed: {len(patterns_found)}\n\n")
            
            for img, data in patterns_found.items():
                f.write(f"\n## {img}\n")
                f.write(f"Categories: {', '.join(data['themes'])}\n")
                if data['gematria_patterns']['core_symbols']:
                    f.write("Gematria Symbols:\n")
                    for sym in data['gematria_patterns']['core_symbols']:
                        f.write(f"   - {sym['symbol']} ({sym['meaning']})\n")
                if data['elemental_symbols']:
                    f.write("Elemental Symbols:\n")
                    for elem in data['elemental_symbols']:
                        f.write(f"   - {elem['name']} ({elem['element']})\n")
        
        print(f"\n📄 Detailed report saved to: {summary_path}")


if __name__ == '__main__':
    main()
