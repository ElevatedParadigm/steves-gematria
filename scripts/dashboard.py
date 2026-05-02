#!/usr/bin/env python3
"""
Multi-Agent Dashboard System — Pure Python Console Visualization
No external dependencies required (except json, datetime from stdlib)
Provides real-time monitoring output for terminal sessions
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Configuration
DB_PATH = "/home/avalonas/.hermes/gematria/database/gematria_database.json"
OBSIDIAN_EXPORTS = "/home/avalonas/.hermes/gematria/obsidian_exports"
CRON_LOGS = "/home/avalonas/.hermes/gematria/cron_logs"

CORE_SYMBOLS = [124, 666, 963, 55, 111, 279]

def colored(text, color):
    """Simple ANSI color coding for terminal output"""
    colors = {
        'green': '\033[92m',
        'blue': '\033[94m',
        'purple': '\033[95m',
        'orange': '\033[93m',
        'red': '\033[91m',
        'reset': '\033[0m'
    }
    return colors.get(color, '') + text + colors['reset']

def load_database():
    """Load gematria database and extract key metrics - UPDATED for new structure"""
    try:
        with open(DB_PATH, 'r') as f:
            db = json.load(f)
        
        # Get symbols array from database (new structure)
        symbols_list = db.get('symbols', [])
        
        # Convert list to dict for easier access
        symbol_dict = {}
        for s in symbols_list:
            symbol_num = str(s.get('symbol', ''))
            symbol_dict[symbol_num] = {
                'value': s.get('symbol', ''),
                'name': s.get('name', 'Unknown'),
                'elemental_force': s.get('elemental_force', 'Unknown'),
                'status': s.get('status', 'unknown'),
                'found_files': len(s.get('found_in_files', [])),
                'notes': s.get('notes', '')[:50] + '...' if len(s.get('notes', '')) > 50 else s.get('notes', '')
            }
        
        # Calculate relevance score based on found files and status
        for num, data in symbol_dict.items():
            if data['status'] == 'active':
                data['relevance_score'] = round(0.9 + (data['found_files'] * 0.05), 3)
            elif data['status'] == 'rare':
                data['relevance_score'] = round(0.7 + (data['found_files'] * 0.05), 3)
            elif data['status'] in ['legacy_verified', 'legacy_active']:
                data['relevance_score'] = round(0.6 + (data['found_files'] * 0.05), 3)
            else:
                data['relevance_score'] = round(0.5 + (data['found_files'] * 0.05), 3)
            
            # Set active_connections based on found files (proxy for correlation strength)
            data['active_connections'] = data['found_files'] + len(symbol_dict) * 0.1
        
        # Extract metadata
        metadata = db.get('metadata', {})
        domains_tracked = metadata.get('domains_tracked', [])
        
        # Get core symbols from list
        core_symbols = [str(s) for s in CORE_SYMBOLS if str(s) in symbol_dict]
        
        return {
            'symbols': symbol_dict,
            'domains': domains_tracked,
            'core_symbols': core_symbols,
            'elemental_forces': metadata.get('elemental_forces', [])
        }
    except Exception as e:
        print(colored(f"Database load error: {e}", "red"))
        return {'symbols': {}, 'domains': [], 'core_symbols': CORE_SYMBOLS}

def get_obsidian_files():
    """Get list of obsidian export files"""
    try:
        files = []
        for filename in sorted(os.listdir(OBSIDIAN_EXPORTS)):
            if filename.endswith('.md'):
                filepath = os.path.join(OBSIDIAN_EXPORTS, filename)
                stat = os.stat(filepath)
                files.append({
                    'name': filename,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                    'path': filepath
                })
        return files
    except Exception as e:
        print(colored(f"Observatory load error: {e}", "red"))
        return []

def get_latest_cron_logs():
    """Get latest cron execution logs"""
    try:
        logs = []
        for filename in sorted(os.listdir(CRON_LOGS), reverse=True)[:3]:
            filepath = os.path.join(CRON_LOGS, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    content = f.read()[:1500]  # First 1.5KB of log
                stat = os.stat(filepath)
                logs.append({
                    'filename': filename,
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                    'size': stat.st_size,
                    'preview': content.strip()
                })
        return logs
    except Exception as e:
        print(colored(f"Cron log load error: {e}", "red"))
        return []

def display_dashboard():
    """Display main dashboard with live stats"""
    print("=" * 80)
    print("                    🌉 STEVE'S GEMATRIA KNOWLEDGE GRAPH")
    print("                Multi-Agent Dashboard — Live Monitoring")
    print("=" * 80)
    print(f"Dashboard Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 80)
    
    # Load data with updated function
    db = load_database()
    obsidian_files = get_obsidian_files()
    cron_logs = get_latest_cron_logs()
    
    # Calculate metrics
    total_symbols = len(db['symbols'])
    total_connections = sum(s.get('active_connections', 0) for s in db['symbols'].values())
    max_relevance = max((s['relevance_score'] for s in db['symbols'].values()), default=0)
    
    # Display stats
    print(f"\n📊 {colored('LIVE METRICS', 'blue')}")
    print(colored(f"   Total Symbols Tracked:        ", "green") + str(total_symbols))
    print(colored(f"   Active Connections:           ", "green") + f"{colored(str(int(total_connections)), 'green')}")
    print(colored(f"   Max Relevance Score:          ", "green") + f"{colored(f'{max_relevance:.3f}', 'blue')}")
    print(colored(f"   Obsidian Export Files:        ", "green") + str(len(obsidian_files)))
    
    # Core symbols status
    print(f"\n🔮 {colored('CORE SYMBOLS STATUS', 'purple')}")
    print("-" * 50)
    
    for num, data in sorted(db['symbols'].items(), key=lambda x: x[1]['relevance_score'], reverse=True):
        value = str(data['value']) if isinstance(data['value'], str) else data['value']
        name = data.get('name', 'Unknown')[:25]
        rel_score = data['relevance_score']
        conns = int(data.get('active_connections', 0))
        
        # Color code relevance score
        if rel_score >= 0.9:
            color = 'green'
            label = colored('★ EXCELLENT', 'green')
        elif rel_score >= 0.7:
            color = 'blue'
            label = colored('✓ GOOD', 'blue')
        else:
            color = 'orange'
            label = colored('○ DEVELOPING', 'orange')
        
        # Show elemental force
        elem = data.get('elemental_force', 'Unknown')[:12]
        
        print(f"  {value:<8} [{label:>12}] {name:<27} {elem} ({conns} files)")
    
    # Obsidian exports summary
    print(f"\n📝 {colored('OBSIDIAN EXPORTS', 'blue')}")
    print("-" * 50)
    for file in obsidian_files[:6]:  # Show top 6 files
        size_kb = f"{file['size'] / 1024:.1f}"
        modified = file['modified']
        print(f"  • {file['name']:<40} ({size_kb}KB, {modified})")
    if len(obsidian_files) > 6:
        print(f"  ... and {len(obsidian_files) - 6} more files")
    
    # Latest cron runs
    if cron_logs:
        print(f"\n⏰ {colored('LATEST OVERNIGHT RESEARCH LOGS', 'blue')}")
        print("-" * 50)
        for log in cron_logs:
            filename = log['filename']
            modified = log['modified']
            preview_lines = log['preview'].split('\n')[:3]
            
            print(f"\n  {filename}:")
            for line in preview_lines:
                if len(line) > 70:
                    line = line[:67] + "..."
                print(f"    {line}")
    
    # API endpoints info
    print(f"\n🔌 {colored('API ENDPOINTS', 'orange')}")
    print("-" * 50)
    print("  This dashboard can be integrated into:")
    print("    • Web server (Flask/FastAPI)")
    print("    • WebSocket real-time updates")
    print("    • Dashboard embedding in Obsidian")
    
    # Footer
    print("\n" + "=" * 80)
    print(colored("✨ Multi-Agent Architecture Complete ✨", "green"))
    print("=" * 80)
    print(f"\nDatabase: {DB_PATH}")
    print(f"Exports: {OBSIDIAN_EXPORTS}")
    print(f"Cron Logs: {CRON_LOGS}")

def display_relationship_graph():
    """ASCII art relationship visualization"""
    print("\n" + "=" * 80)
    print("                STEVE'S GEMATRIA — KNOWLEDGE GRAPH VISUALIZATION")
    print("=" * 80)
    
    db = load_database()
    symbols = db['symbols']
    
    print("\n🔮 CORE SYMBOL NETWORK (ASCII Graph)\n")
    
    # Draw nodes with connections
    sorted_symbols = sorted(symbols.items(), key=lambda x: len(str(x[0])), reverse=True)
    
    # Show connections between symbols
    print("  Symbol Connections (Top 4):\n")
    symbol_list = list(sorted_symbols[:4])
    for i, (num1, data1) in enumerate(symbol_list):
        value1 = str(data1['value'])
        
        # Show connections to other visible nodes
        conn_str = f"\n     └────┬──> {symbol_list[i+1][0] if i+1 < len(symbol_list) else '...'}"
        print(conn_str)
    
    # Elemental associations
    print("\n🔥 ELEMENTAL FORCES\n")
    elemental_map = {
        'fire': ['55', '666'],
        'earth': ['124', '17', '279'],
        'water': ['124'],
        'air': ['963', '137']
    }
    
    for element, symbols_list in elemental_map.items():
        print(f"  {element.upper()}: {' '.join(symbols_list)}")
    
    # Domain convergence
    domains = db['domains']
    print("\n📊 DOMAIN CONVERGENCE INDEX\n")
    domain_names = ['Political', 'Religious', 'Economic', 'Military', 'Elemental']
    print("         " + "  ".join(domain_names))
    
    for domain_name, data in domains.items():
        if isinstance(domain_name, str):
            domain_name = domain_name.title()
        else:
            domain_name = str(domain_name).title()
        
        if domain_name in domain_names:
            score = data.get('correlation_score', 0) if data else 0
            bar_len = int(score * 20) if isinstance(score, (int, float)) and 0 <= score <= 1 else 5
            bar = '█' * bar_len + '░' * (20 - bar_len)
            print(f"  {domain_name:<10}│{bar}")

def display_temporal_analysis():
    """ASCII temporal pattern visualization"""
    print("\n🕐 TEMPORAL PATTERN ANALYSIS\n")
    
    # ASCII timeline visualization
    timeline = [
        '██████████████',  # Peak correlation
        '████████░░░░░░░░',
        '█████░░░░░░░░░░░░',
        '███░░░░░░░░░░░░░░░',
        '░░███░░░░░░░░░░░░░',
        '░░░░░███░░░░░░░░░░',  # Low correlation
    ]
    
    labels = ['High Conv.', 'Med-High', 'Medium', 'Med-Low', 'Low', 'Sparse']
    
    for i, bar in enumerate(timeline):
        label = labels[i] if i < len(labels) else f'Level {i+1}'
        print(f"  {label:<12}│{bar}")

def display_api_data():
    """Display detailed symbol data in JSON format"""
    print("\n📦 API DATA STRUCTURE\n")
    
    db = load_database()
    
    print("Core Symbols Data Structure:")
    print(f"  - symbols: {len(db['symbols'])} entries")
    print(f"  - domains: {len(db['domains'])} domains tracked")
    print(f"  - core_symbols: {db['core_symbols']}")
    
    sample_symbol = list(db['symbols'].values())[0] if db['symbols'] else {}
    print("\nSample Symbol Entry Keys:")
    for key in ['value', 'name', 'elemental_force', 'status', 'active_connections']:
        print(f"  - {key}: {sample_symbol.get(key, 'N/A')}")

def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) > 1:
        if '--api' in sys.argv or '-a' in sys.argv:
            display_api_data()
        elif '--graph' in sys.argv or '-g' in sys.argv:
            display_relationship_graph()
        elif '--temporal' in sys.argv or '-t' in sys.argv:
            display_temporal_analysis()
        else:
            display_dashboard()
    else:
        display_dashboard()
    
    print("\n" + "=" * 80)
    print("Dashboard complete. Press Ctrl+C to exit.")
    print("=" * 80)

if __name__ == '__main__':
    main()
