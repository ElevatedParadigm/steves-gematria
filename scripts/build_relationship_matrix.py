#!/usr/bin/env python3
"""
Relationship Matrix Generator - Gematria Connection Analysis
Maps correlations between symbols, elements, and domains to reveal hidden patterns.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import argparse

def load_database():
    """Load the gematria database"""
    db_path = Path.home() / ".hermes" / "gematria" / "database" / "gematria_database.json"
    if not db_path.exists():
        db_path = Path("/home/avalonas/.hermes/gematria/database/gematria_database.json")
    with open(db_path) as f:
        return json.load(f)

def calculate_correlation_matrix(symbols_data):
    """Calculate correlation coefficients between all symbol pairs"""
    correlations = {}
    
    for i in range(len(symbols_data)):
        for j in range(i + 1, len(symbols_data)):
            sym1 = symbols_data[i]
            sym2 = symbols_data[j]
            
            id1 = sym1.get('id_str', f'sym{i+1}')
            id2 = sym2.get('id_str', f'sym{j+1}')
            
            feat1 = [sym1.get("relevance", 0), 
                     1 if "active" in sym1.get("status", "") else 0,
                     len(sym1.get("found_files", []))]
            feat2 = [sym2.get("relevance", 0), 
                     1 if "active" in sym2.get("status", "") else 0,
                     len(sym2.get("found_files", []))]
            
            n = len(feat1)
            mean1 = sum(feat1) / n
            mean2 = sum(feat2) / n
            
            num = sum((feat1[k] - mean1) * (feat2[k] - mean2) for k in range(n))
            
            var1 = sum((x - mean1) ** 2 for x in feat1)
            var2 = sum((x - mean2) ** 2 for x in feat2)
            
            if var1 > 0 and var2 > 0:
                corr = num / (var1 ** 0.5 * var2 ** 0.5)
                key = f"{id1}-{id2}"
                correlations[key] = abs(corr)
    
    return correlations

def generate_html_report(symbols_data, correlations, output_file):
    """Generate HTML visualization report"""
    
    sorted_symbols = sorted(symbols_data, 
                          key=lambda s: s.get("relevance", 0), 
                          reverse=True)[:8]
    
    max_relevance = max((s.get("relevance", 0) for s in symbols_data), default=0)
    total_files = sum(len(s.get("found_files", [])) for s in symbols_data)
    active_symbols = len([s for s in symbols_data if s.get("status") in ["active", "rare"]])
    
    strong_count = sum(1 for v in correlations.values() if abs(v) >= 0.8)
    medium_count = sum(1 for v in correlations.values() if 0.6 <= abs(v) < 0.8)
    weak_count = len(correlations) - strong_count - medium_count
    
    # Limit correlations to top 30 pairs for size management
    sorted_pairs = sorted(correlations.items(), 
                         key=lambda x: x[1], 
                         reverse=True)[:30]
    limited_correlations = {k:v for k,v in sorted_pairs}
    
    rel_json_str = json.dumps(limited_correlations)
    id_list = [s.get("id_str", f"sym{i+1}") for i, s in enumerate(sorted_symbols)]

    html_parts = []
    
    # Header section
    html_parts.append('<!DOCTYPE html>')
    html_parts.append('<html lang="en">')
    html_parts.append('<head>')
    html_parts.append('  <meta charset="UTF-8">')
    html_parts.append('  <meta name="viewport" content="width=device-width, initial-scale=1.0">')
    html_parts.append(f'  <title>Gematria Relationship Matrix</title>')
    html_parts.append('  <script src="https://cdn.tailwindcss.com"></script>')
    html_parts.append('<style>')
    html_parts.append('.relevance-bar { background: linear-gradient(90deg, #3b82f6 0%, #10b981 50%, #ef4444 100%); }')
    html_parts.append('.strong-correlation { background: #ef4444; }')
    html_parts.append('.medium-correlation { background: #eab308; }')
    html_parts.append('.weak-correlation { background: #6b7280; }')
    html_parts.append('.cell-0.8+ { color: #fca5a5; font-weight: bold; }')
    html_parts.append('.cell-0.6-0.8 { color: #fcd34d; }')
    html_parts.append('.cell-other { color: #9ca3af; }')
    html_parts.append('</style>')
    html_parts.append('</head>')
    html_parts.append('<body class="bg-gray-900 text-white min-h-screen">')
    
    # Main content container
    html_parts.append('  <div class="max-w-7xl mx-auto p-6">')
    html_parts.append('    <!-- Header -->')
    html_parts.append('    <header class="mb-12 border-b border-gray-700 pb-6">')
    html_parts.append('      <h1 class="text-4xl font-bold mb-3">🔮 Gematria Relationship Matrix</h1>')
    html_parts.append(f'      <p class="text-gray-400 text-lg">Correlation Analysis: Symbol Interconnections & Elemental Forces</p>')
    html_parts.append('      <div class="mt-4 flex gap-4 text-sm flex-wrap">')
    html_parts.append(f'        <span class="px-4 py-2 bg-blue-900 rounded-md">Symbols: {len(symbols_data)}</span>')
    html_parts.append(f'        <span class="px-4 py-2 bg-green-900 rounded-md">Active: {active_symbols}</span>')
    html_parts.append(f'        <span class="px-4 py-2 bg-purple-900 rounded-md">Max Relevance: {max_relevance:.3f}</span>')
    html_parts.append('      </div>')
    html_parts.append('    </header>')
    
    # Key statistics
    html_parts.append('    <!-- Key Statistics -->')
    html_parts.append('    <section class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">')
    html_parts.append(f'      <div class="bg-gray-800 p-6 rounded-xl border border-gray-700">')
    html_parts.append('        <h2 class="text-lg font-semibold text-blue-400 mb-2">Max Relevance Score</h2>')
    html_parts.append(f'        <p class="text-4xl font-bold text-white">{max_relevance:.3f}</p>')
    html_parts.append('        <p class="text-gray-400 text-sm mt-2">Highest correlation detected</p>')
    html_parts.append('      </div>')
    html_parts.append(f'      <div class="bg-gray-800 p-6 rounded-xl border border-gray-700">')
    html_parts.append('        <h2 class="text-lg font-semibold text-green-400 mb-2">Total Files Found</h2>')
    html_parts.append(f'        <p class="text-4xl font-bold text-white">{total_files}</p>')
    html_parts.append('        <p class="text-gray-400 text-sm mt-2">Across all symbols</p>')
    html_parts.append('      </div>')
    
    html_parts.append(f'      <div class="bg-gray-800 p-6 rounded-xl border border-gray-700">')
    html_parts.append('        <h2 class="text-lg font-semibold text-purple-400 mb-2">Strong Correlations</h2>')
    html_parts.append(f'        <p class="text-4xl font-bold text-white">{strong_count}</p>')
    html_parts.append('        <p class="text-gray-400 text-sm mt-2">&ge; 0.8 coefficient</p>')
    html_parts.append('      </div>')
    
    html_parts.append(f'      <div class="bg-gray-800 p-6 rounded-xl border border-gray-700">')
    html_parts.append('        <h2 class="text-lg font-semibold text-yellow-400 mb-2">Medium Correlations</h2>')
    html_parts.append(f'        <p class="text-4xl font-bold text-white">{medium_count}</p>')
    html_parts.append('        <p class="text-gray-400 text-sm mt-2">0.6 - 0.8 coefficient</p>')
    html_parts.append('      </div>')
    html_parts.append('    </section>')
    
    # Top symbols
    html_parts.append('    <!-- Top Symbols -->')
    html_parts.append('    <section class="mb-12">')
    html_parts.append('      <h2 class="text-2xl font-bold mb-4 border-b border-gray-700 pb-2">Top Symbols by Relevance</h2>')
    html_parts.append('      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">')
    
    for symbol in sorted_symbols:
        id_str = symbol.get("id_str", "Unknown")
        relevance = symbol.get("relevance", 0)
        status = symbol.get("status", "unknown")
        elemental_forces = symbol.get("elemental_forces", [])
        
        if max_relevance > 0:
            bar_width = (relevance / max_relevance * 100)
        else:
            bar_width = 0
        
        status_badge = ""
        if status == "active":
            status_badge = '⭐'
        elif status == "rare":
            status_badge = '✨'
        elif status == "developing":
            status_badge = '🔍'
        
        border_color = "border-red-500" if relevance >= 0.9 else "border-green-500" if relevance >= 0.7 else "border-yellow-500"
        text_red = "text-red-400" if relevance >= 0.9 else "text-green-400" if relevance >= 0.7 else "text-yellow-400"
        
        html_parts.append('        <div class="bg-gray-800 rounded-xl p-6 border-l-4 ' + border_color + '">')
        html_parts.append('          <div class="flex justify-between items-start mb-2">')
        html_parts.append('            <h3 class="text-xl font-bold">' + status_badge + ' ' + id_str + '</h3>')
        html_parts.append('            <span class="text-sm text-gray-400 uppercase">' + status + '</span>')
        html_parts.append('          </div>')
        html_parts.append('          <!-- Relevance Score -->')
        html_parts.append('          <div class="relative h-8 mb-3 rounded overflow-hidden bg-gray-900">')
        html_parts.append('            <div class="absolute inset-0 relevance-bar" style="width: ' + str(round(bar_width, 1)) + '%"></div>')
        html_parts.append('          </div>')
        html_parts.append('          <div class="flex items-center justify-between text-sm mb-4">')
        html_parts.append('            <span class="text-gray-300">Relevance Score:</span>')
        html_parts.append('            <span class="text-2xl font-bold ' + text_red + '">' + str(round(relevance, 3)) + '</span>')
        html_parts.append('          </div>')
        html_parts.append('          <!-- Elemental Forces -->')
        
        for force in elemental_forces[:4]:
            html_parts.append('            <div class="flex items-center gap-2 my-1">')
            html_parts.append('              <span class="text-xs uppercase font-semibold text-gray-500">' + force + '</span>')
            html_parts.append('<div class="h-2 flex-1 bg-gray-700 rounded-full overflow-hidden">')
            html_parts.append('<div class="h-full bg-gradient-to-r from-blue-600 to-purple-600" style="width: 80%"></div></div></div>')
        
        html_parts.append('        </div>')
    
    html_parts.append('      </div>')
    html_parts.append('    </section>')
    
    # Correlation distribution
    html_parts.append('    <!-- Correlation Distribution -->')
    html_parts.append('    <section class="mb-12">')
    html_parts.append('      <h2 class="text-2xl font-bold mb-4 border-b border-gray-700 pb-2">Correlation Distribution</h2>')
    html_parts.append('      ')
    html_parts.append('<div class="grid grid-cols-1 md:grid-cols-3 gap-6">')
    html_parts.append('        <div class="bg-gradient-to-br from-red-900/50 to-red-900/20 p-6 rounded-xl border border-red-800">')
    html_parts.append('          <h3 class="text-lg font-semibold text-red-300 mb-2">Strong Relationships</h3>')
    html_parts.append('          <p class="text-gray-300">Symbols with &ge; 0.8 correlation coefficient</p>')
    html_parts.append(f'          <p class="text-3xl font-bold mt-4">{strong_count}</p>')
    html_parts.append('        </div>')
    
    html_parts.append('        <div class="bg-gradient-to-br from-yellow-900/50 to-yellow-900/20 p-6 rounded-xl border border-yellow-800">')
    html_parts.append('          <h3 class="text-lg font-semibold text-yellow-300 mb-2">Medium Relationships</h3>')
    html_parts.append('          <p class="text-gray-300">Symbols with 0.6 - 0.8 correlation coefficient</p>')
    html_parts.append(f'          <p class="text-3xl font-bold mt-4">{medium_count}</p>')
    html_parts.append('        </div>')
    
    html_parts.append('        <div class="bg-gradient-to-br from-gray-700/50 to-gray-700/20 p-6 rounded-xl border border-gray-600">')
    html_parts.append('          <h3 class="text-lg font-semibold text-gray-300 mb-2">Weak/Marginal</h3>')
    html_parts.append('          <p class="text-gray-300">Symbols with &lt; 0.6 correlation coefficient</p>')
    html_parts.append(f'          <p class="text-3xl font-bold mt-4">{weak_count}</p>')
    html_parts.append('        </div>')
    html_parts.append('      </div>')
    html_parts.append('    </section>')
    
    # Detailed relationships table - pre-built static HTML (no JS needed!)
    html_parts.append('    <!-- Detailed Relationships Table -->')
    html_parts.append('    <section class="mb-12">')
    html_parts.append('      <h2 class="text-2xl font-bold mb-4 border-b border-gray-700 pb-2">Relationship Correlations</h2>')
    html_parts.append('      ')
    html_parts.append('      <!-- Pre-built correlation matrix (no JS required - instant load!) -->')
    html_parts.append('      <div id="correlation-table" class="overflow-x-auto">')
    html_parts.append('        <table class="w-full bg-gray-800 rounded-xl border border-gray-700">')
    html_parts.append('          <thead>')
    html_parts.append('            <tr class="bg-gray-700">')
    html_parts.append('              <th class="p-3 text-left font-semibold">Symbol</th>')
    
    header_cells = []
    for i, symbol in enumerate(sorted_symbols):
        escaped_id = symbol.get("id_str", f"sym{i+1}").replace('"', '&quot;')
        header_cells.append(f'<th class="p-3 text-center">{escaped_id}</th>')
    
    html_parts.append(''.join(header_cells))
    html_parts.append('            </tr>')
    html_parts.append('          </thead>')
    html_parts.append('          <tbody id="correlations-body">')
    
    # First row header (current symbol) with all correlations to others as second column values
    for i in range(len(sorted_symbols)):
        sym1 = sorted_symbols[i]
        trigger_id = sym1.get("id_str", f"sym{i+1}")
        
        cells_for_trigger = []
        cells_for_trigger.append(f'<td class="p-3 font-bold bg-gray-750">{trigger_id}</td>')
        
        for j in range(i+1, len(sorted_symbols)):
            sym2 = sorted_symbols[j]
            id1 = sym1.get('id_str', f'sym{i+1}')
            id2 = sym2.get('id_str', f'sym{j+1}')
            pair_key = f"{id1}-{id2}"
            
            val = correlations.get(pair_key)
            
            if val is not None:
                if val >= 0.9:
                    class_name = 'strong-correlation cell-0.8+'
                    display = f'{val:.2f}'
                elif val >= 0.8:
                    class_name = 'medium-correlation cell-0.8+'
                    display = f'{val:.2f}'
                elif val >= 0.6:
                    class_name = 'weak-correlation'
                    display = f'{val:.2f}'
                else:
                    class_name = 'cell-other'
                    display = f'{val:.2f}'
            else:
                class_name = 'cell-other'
                display = '-'
            
            cell = f'<td class="p-3 text-center {class_name}">{display}</td>'
            cells_for_trigger.append(cell)
        
        row_html = '<tr>' + ''.join(cells_for_trigger) + '</tr>'
        html_parts.append(row_html)
    
    html_parts.append('          </tbody>')
    html_parts.append('        </table>')
    html_parts.append('      </div>')
    
    # Correlation legend
    html_parts.append('      <!-- Correlation legend -->')
    html_parts.append('      <div class="mt-6 space-y-2">')
    html_parts.append('        <div class="flex items-center gap-4 p-3 bg-gray-800 rounded-lg">')
    html_parts.append('          <div class="w-16 h-3 relevance-bar rounded"></div>')
    html_parts.append('          <div class="flex-1 space-y-1 text-sm">')
    html_parts.append('            <div class="flex justify-between">')
    html_parts.append('              <span class="text-red-400 font-bold">&ge; 0.9</span>')
    html_parts.append('              <span class="text-gray-300">High Priority - Core symbols with strong connections</span>')
    html_parts.append('            </div>')
    html_parts.append('            <div class="flex justify-between">')
    html_parts.append('              <span class="text-yellow-400">0.7 - 0.9</span>')
    html_parts.append('              <span class="text-gray-300">Active - Frequently referenced patterns</span>')
    html_parts.append('            </div>')
    html_parts.append('            <div class="flex justify-between">')
    html_parts.append('              <span class="text-green-400">0.5 - 0.7</span>')
    html_parts.append('              <span class="text-gray-300">Developing - Emerging correlations detected</span>')
    html_parts.append('            </div>')
    html_parts.append('            <div class="flex justify-between">')
    html_parts.append('              <span class="text-blue-400">&lt; 0.5</span>')
    html_parts.append('              <span class="text-gray-300">Rare - Sporadic mentions, potential outliers</span>')
    html_parts.append('            </div>')
    html_parts.append('          </div>')
    html_parts.append('        </div>')
    html_parts.append('      </div>')
    html_parts.append('    </section>')
    
    # Footer
    html_parts.append('    <!-- Footer -->')
    html_parts.append('    <footer class="mt-12 pt-6 border-t border-gray-700 text-center text-gray-500 text-sm">')
    html_parts.append('      <p>Generated by Gematria Analysis Engine</p>')
    html_parts.append('      <p class="text-xs mt-2">Analyzing elemental forces, file correlations, and symbol relationships</p>')
    html_parts.append('    </footer>')
    html_parts.append('  </div>')
    
    html_parts.append('</body>')
    html_parts.append('</html>')
    
    # Write to file
    html_content = ''.join(html_parts)
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"HTML visualization written to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Build Gematria Relationship Matrix")
    parser.add_argument("--output", "-o", type=str, required=True, 
                       help="Output file path (use .html for web report)")
    args = parser.parse_args()
    
    # Load database
    db = load_database()
    symbols_data = db.get("symbols", [])
    
    if not symbols_data:
        print("Error: No symbols found in database!", file=sys.stderr)
        sys.exit(1)
    
    # Calculate correlation matrix
    correlations = calculate_correlation_matrix(symbols_data)
    
    # Generate output
    generate_html_report(symbols_data, correlations, args.output)

if __name__ == "__main__":
    main()
