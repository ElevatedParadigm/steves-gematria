#!/usr/bin/env python3
"""
ASCII Art Visualization Engine — Terminal-based relationship graphs
Displays gematria pattern connections in ASCII format for terminal monitoring
"""

import json
from pathlib import Path
from datetime import datetime

DB_PATH = "/home/avalonas/.hermes/gematria/database/gematria_database.json"

def load_symbols():
    with open(DB_PATH, 'r') as f:
        db = json.load(f)
    symbols = {k: v for k, v in db.get('symbols', {}).items()}
    return symbols

def draw_relationship_graph(symbols):
    """ASCII art relationship graph showing core symbol connections"""
    print("\n" + "="*80)
    print("       STEVE'S GEMATRIA — KNOWLEDGE GRAPH RELATIONSHIPS")
    print("="*80)
    
    # Draw ASCII nodes with connections
    print("\n🔮 CORE SYMBOL CONNECTIONS 🔮\n")
    
    for i, (num1, sym1) in enumerate(sorted(symbols.items(), key=lambda x: len(x[0]), reverse=True)[:4]):
        if isinstance(num1, str):
            num1 = int(num1)
            
        node1 = f" {num1} "
        
        # Show connections to other symbols
        for num2, sym2 in sorted(symbols.items(), key=lambda x: len(x[0]), reverse=True)[i+1:i+4]:
            if isinstance(num2, str):
                num2 = int(num2)
            
            conn_line = f"{'|' if i == 0 else '/'} {num2}"
            print(f"{node1}  {conn_line}")
        
        print("-" * 30)
    
    # Draw elemental associations
    print("\n🔥 ELEMENTAL FORCES 🔥\n")
    elemental_map = {
        'fire': ['55', '666'],
        'earth': ['124', '17'],
        'water': ['963', '279'],
        'air': ['111', '55']
    }
    
    for element, symbols_list in elemental_map.items():
        print(f"  {element.upper()}: {', '.join(symbols_list)}")
    
    # Show domain convergence heat map (ASCII)
    print("\n📊 DOMAIN CONVERGENCE HEAT MAP 📊\n")
    domains = ['Political', 'Religious', 'Economic', 'Military', 'Elemental']
    print("         " + "  ".join(domains))
    print("-" * (25 * len(domains)))
    
    # ASCII heatmap for political events
    heat = [
        ['██████', '████░░', '███░░░', '█░░░░░', '░░░░░░'],  # High
        ['████░░', '███░░░', '██░░░░', '█░░░░░', '░░░░░░'],
        ['███░░░', '██░░░░', '█░░░░░', '░░░░░░', '░░░░░░'],
        ['█░░░░░', '█░░░░░', '░░░░░░', '░░░░░░', '░░░░░░']  # Low
    ]
    
    for i, pattern in enumerate(['High Conv.', 'Med Conv.', 'Low Conv.', 'Sparse']):
        print(f"  {pattern:12}", end="")
        row = heat[i] if len(row) < len(domains) else heat[-1]
        for domain in domains[:4]:
            cell = row[i % len(row)] if i < len(row) else '░'
            print(f"  {cell}", end="")
        print()

def draw_symbol_network(symbols):
    """ASCII network visualization showing symbol density"""
    print("\n🌐 SYMBOL NETWORK DENSITY 🌐\n")
    
    # Create a simple grid representation
    grid_size = 20
    nodes_per_row = 6
    
    print("Node Density Grid:")
    print("-" * (15 * nodes_per_row))
    
    sorted_symbols = sorted(symbols.items(), key=lambda x: int(x[0]) if isinstance(x[0], str) else x[0])
    row_start = 0
    
    for row in range(grid_size // 2):
        for col in range(nodes_per_row):
            idx = row * nodes_per_row + col
            if idx < len(sorted_symbols):
                num, data = sorted_symbols[idx]
                if isinstance(num, str):
                    num = int(num)
                density = min(data.get('relevance_score', 0) * 15, '███' * 3)
                print(f"{density} {num:4d}", end="")
            else:
                print("  .", end="")
        print()

def draw_temporal_analysis():
    """ASCII temporal pattern analysis"""
    print("\n🕐 TEMPORAL PATTERN ANALYSIS 🕐\n")
    
    # Simulated ASCII timeline visualization
    timeline = [
        "██████████████",  # Peak correlation
        "████████░░░░░░░░",
        "█████░░░░░░░░░░░░",
        "███░░░░░░░░░░░░░░░",
        "░░███░░░░░░░░░░░░░",
        "░░░░░███░░░░░░░░░░",  # Low correlation
    ]
    
    for i, bar in enumerate(timeline):
        labels = ['High', 'Med-High', 'Medium', 'Med-Low', 'Low', 'Sparse']
        label = labels[i] if i < len(labels) else 'Minimal'
        print(f"  {label:10}│{bar}")

def main():
    print("Loading gematria database...")
    symbols = load_symbols()
    
    print(f"Loaded {len(symbols)} symbols\n")
    
    # Draw relationship graph
    draw_relationship_graph(symbols)
    
    # Draw symbol network
    draw_symbol_network(symbols)
    
    # Draw temporal analysis
    draw_temporal_analysis()
    
    print("\n" + "="*80)
    print("Visualization complete. Press Ctrl+C to exit.")
    print("="*80)

if __name__ == '__main__':
    main()
