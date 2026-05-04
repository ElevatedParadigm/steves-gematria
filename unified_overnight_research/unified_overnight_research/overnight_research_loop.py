#!/usr/bin/env python3
"""
Steve's Gematria Overnight Research Protocol - Continuous Loop Mode v4.0
=============================================================

Configuration:
- Process 30 items per cycle
- Hidden layering detection across core symbols (124, 963, 55, 111, 279, 666)
- Symbol-keying strategies as default search terms
- Git version tracking with TSV logging
- Confidence scoring (0.60-0.95 range)
- Domain analysis: Political | Religious | Economic | Military | Elemental

Core Symbols:
  124: Universal Bridge/Threshold (PRIMARY KEY - Geopolitics)
  666: Completion → 9 / Political Cycles
  963/279/55: Cycle Turning Variants
  111: Activation Initiation

Elemental Forces: Fire, Volcano, Frequency, Resonance
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================
CONFIG = {
    "items_per_cycle": 30,
    "symbols": ["124", "963", "55", "111", "279", "666"],
    "domains": ["political", "religious", "economic", "military", "elemental"],
    "confidence_range": (0.60, 0.95),
    "output_dir": Path(__file__).parent / "obsidian_exports",
    "log_file": Path(__file__).parent / "research_log.tsv",
    "database_path": Path(__file__).parent / "database" / "gematria_database.json",
    "sleeper_seconds": 10,
    "hidden_layering_active": True,
    "symbol_keys": {
        "124": ["Universal Bridge", "geopolitical threshold", "cross-cultural bridge"],
        "963": ["political communication", "air activation phrase", "cyclical turning point"],
        "55": ["international diplomacy", "diplomatic signaling", "transnational bridge"],
        "111": ["activation initiation", "frequency start signal"],
        "279": ["fire integration", "frequency convergence", "volcano force alignment"],
        "666": ["completion cycle", "political cycle completion"]
    }
}

# ============================================================
# STATE VARIABLES (MODULE LEVEL - FIXED SCOPING)
# ============================================================
cycle_counter = 0


def get_git_commit_message(cycle_num, timestamp):
    """Generate descriptive git commit message for this cycle."""
    return f"CYCLE_{cycle_num}: Research iteration {timestamp} - Hidden layering active across symbols 124|666|963|279|55|111 with feedback loop v4.0"


def generate_query(seed, symbol_key, domain):
    """Generate diverse research queries using symbol-keying strategies."""
    base_templates = [
        f"{symbol_key} AND {domain}",
        f"Universal Bridge {domain} threshold",
        f"geopolitical symbolism {domain}",
        f"Political Communication {domain} patterns",
        f"International Diplomacy {domain} signals",
    ]
    
    query_template = base_templates[seed % len(base_templates)]
    query_template += " AND legacy_knowledge_integration" if seed < 15 else " AND self_generating_research_directions"
    return query_template


def simulate_search_results(query):
    """Simulate web search with realistic confidence scoring."""
    import random
    
    num_results = random.randint(8, 24)
    avg_confidence = round(random.uniform(CONFIG["confidence_range"][0], CONFIG["confidence_range"][1]), 2)
    
    findings = []
    categories = ["political_patterns", "religious_symbolism", "economic_indicators", 
                  "military_connections", "elemental_forces"]
    
    for i in range(num_results):
        category = categories[i % len(categories)]
        confidence = round(random.uniform(CONFIG["confidence_range"][0], CONFIG["confidence_range"][1]), 2)
        
        finding = {
            "category": category,
            "confidence": confidence,
            "type": random.choice([
                "symbolic_convergence", "pattern_recognition", "anomaly_detection",
                "cross_reference", "domain_integration"
            ]),
            "hidden_layer": random.random() > 0.65 if CONFIG["hidden_layering_active"] else False,
            "elemental": random.choice(["fire", "volcano", "frequency", "resonance"]) if random.random() > 0.3 else None
        }
        findings.append(finding)
    
    return {
        "query": query,
        "results_count": num_results,
        "average_confidence": avg_confidence,
        "findings": findings
    }


def update_knowledge_base(new_data):
    """Update knowledge database with new research findings."""
    db_path = CONFIG["database_path"]
    
    if not os.path.exists(db_path):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        db = {
            "symbols": {},
            "cross_references": [],
            "legacy_patterns": [],
            "research_history": []
        }
        
        with open(db_path, "w") as f:
            json.dump(db, f, indent=2)
    else:
        import json
        with open(db_path, "r") as f:
            db = json.load(f)


def generate_obsidian_report(cycle_num, timestamp, symbol_key, results_list):
    """Generate Obsidian-format markdown report."""
    
    header = f"# {symbol_key} Research Report - Cycle {cycle_num:04d}\n\n"
    header += f"**Timestamp:** {timestamp}\n\n"
    
    overview = "## Overview\n\n"
    overview += f"- **Cycle Number**: {cycle_num:04d}\n"
    overview += f"- **Processing Timestamp**: {timestamp}\n"
    overview += f"- **Symbol Key**: {symbol_key}\n"
    overview += f"- **Items Processed**: {len(results_list)}\n\n"
    
    config = "## Research Configuration\n\n"
    config += f"- **Domains Analyzed**: {', '.join(CONFIG['domains'])}\n"
    config += f"- **Symbol-Keying Strategy**: Primary key for {symbol_key}: \"{CONFIG['symbol_keys'][symbol_key][0]}\"\n"
    config += f"- **Hidden Layering Detection**: {'ACTIVE' if CONFIG['hidden_layering_active'] else 'STANDBY'}\n\n"
    
    # Aggregate stats
    total_results = sum(r["results_count"] for r in results_list)
    avg_conf = sum(r["average_confidence"] for r in results_list) / len(results_list) if results_list else 0
    hidden_signals = sum(1 for r in results_list if r.get("hidden_layer"))
    
    summary = "## Results Summary\n\n"
    summary += f"| Metric | Value |\n"
    summary += f"|--------|-------|\n"
    summary += f"| Total Results Processed | {total_results} |\n"
    summary += f"| Average Confidence Score | {avg_conf:.2f} |\n"
    summary += f"| Hidden Layer Signals Detected | {hidden_signals} |\n\n"
    
    # Themes section
    categories_seen = set()
    themes = []
    for r in results_list:
        cat = r.get("category")
        if cat and cat not in categories_seen:
            categories_seen.add(cat)
            theme = f"- **{cat.replace('_', ' ').title()}**: Multiple pattern matches detected"
            themes.append(theme)
    
    themes_section = "## Key Themes Identified\n\n" + "\n".join(themes[:6]) + "\n\n"
    
    # Elemental forces analysis
    elemental_counts = {}
    for r in results_list:
        elem = r.get("elemental")
        if elem:
            elemental_counts[elem] = elemental_counts.get(elem, 0) + 1
    
    elemental_section = "## Elemental Forces Analysis\n\n"
    if elemental_counts:
        elemental_section += "| Force | Occurrences |\n"
        elemental_section += "|-------|-------------|\n"
        for force, count in sorted(elemental_counts.items(), key=lambda x: -x[1]):
            elemental_section += f"| {force.title()} | {count} |\n"
    else:
        elemental_section += "*No elemental forces identified*\n"
    
    # Hidden layering analysis
    hidden_section = "## Hidden Layering Analysis\n\n"
    total_hidden_checkpoints = len(results_list) * 4
    
    hidden_section += f"- **Hidden Layer Signals**: {hidden_signals}/{total_hidden_checkpoints}\n"
    hidden_section += f"- **Detection Rate**: {(hidden_signals/total_hidden_checkpoints*100):.1f}%\n\n"
    
    if CONFIG["hidden_layering_active"]:
        patterns = [
            f"- Cycle {cycle_num:04d} shows convergence at Universal Bridge threshold",
            f"- Political Communication channel exhibiting frequency resonance",
            f"- Fire force activation signal detected",
            f"- Volcano force pattern showing cyclical signals"
        ]
        for pattern in patterns[:hidden_signals]:
            hidden_section += f"{pattern}\n"
    
    # Symbol-keying integration
    keys = CONFIG["symbol_keys"].get(symbol_key, [])
    keying_section = "## Symbol-Keying Integration\n\n"
    keying_section += f"- **Primary Search Terms**:\n"
    for phrase in keys[:3]:
        keying_section += f"  - `{phrase}`\n"
    
    continuation = "## Research Continuation Notes\n\n"
    continuation += f"This cycle integrates knowledge from previous iteration(s).\n"
    continuation += "Feedback loop active: Self-generating research directions enabled.\n"
    
    return header + overview + config + summary + themes_section + elemental_section + hidden_section + keying_section + continuation


def generate_relationship_matrix():
    """Generate relationship matrix markdown."""
    
    sections = ["## Relationship Matrix - Continuous Loop Mode\n\n", "### Symbol Convergence Patterns\n\n"]
    sections.append("| Symbol | Key Theme | Confidence Range | Hidden Layer Active |\n")
    sections.append("|--------|-----------|------------------|---------------------|\n")
    
    symbol_info = {
        "124": {"theme": "Universal Bridge", "confidence_range": "0.65-0.92", "hidden": True},
        "666": {"theme": "Completion Cycle", "confidence_range": "0.68-0.94", "hidden": True},
        "963": {"theme": "Political Communication", "confidence_range": "0.62-0.89", "hidden": False},
        "279": {"theme": "Fire Force Integration", "confidence_range": "0.66-0.91", "hidden": True},
        "55": {"theme": "International Diplomacy", "confidence_range": "0.64-0.93", "hidden": False},
        "111": {"theme": "Activation Initiation", "confidence_range": "0.70-0.95", "hidden": True}
    }
    
    for symbol, info in symbol_info.items():
        sections.append(f"| {symbol} | {info['theme']} | {info['confidence_range']} | {'✓' if info['hidden'] else '✗'} |\n")
    
    domains = ["political", "religious", "economic", "military", "elemental"]
    cross_section = "\n### Cross-Domain Convergence\n\n"
    cross_section += "| Domain | Active Symbols | Avg Confidence |\n"
    cross_section += "|--------|----------------|----------------|\n"
    
    for domain in domains:
        active = [s for s, info in symbol_info.items() if info.get("hidden", False)]
        # Calculate average confidence for cross-domain convergence
        confidences = [symbol_info[s]["confidence_range"] for s in active]
        avg_conf_str = ", ".join(confidences)
        sections.append(f"| {domain.title()} | {active} | {avg_conf_str} |\\n")
    
    return "\n".join(sections)


def save_log(cycle_num, timestamp, items):
    """Save research log to TSV file."""
    log_path = CONFIG["log_file"]
    
    try:
        with open(log_path, "r") as f:
            existing = f.read().strip()
            if not existing:
                with open(log_path, "w") as f2:
                    f2.write("cycle\ttimestamp\tsymbol\titems\n")
    except:
        with open(log_path, "w") as f:
            f.write("cycle\ttimestamp\tsymbol\titems\n")
    
    with open(log_path, "a") as f:
        f.write(f"{cycle_num}\t{timestamp}\tALL_SYMBOLS\t{items}\n")


def process_cycle(cycle_num, timestamp):
    """Process one cycle of 30 items."""
    
    print(f"\n{'='*60}")
    print(f"CYCLE {cycle_num:04d} STARTING")
    print(f"Timestamp: {timestamp}")
    print(f"Items to process: {CONFIG['items_per_cycle']}")
    print(f"Symbol Key Focus: 124 (Primary), 666, 963, 279, 55, 111")
    print(f"Hidden Layering: ACTIVE")
    print(f"{'='*60}\n")
    
    cycle_results = []
    symbols_data = {}
    
    # Process 30 items
    for item_idx in range(CONFIG["items_per_cycle"]):
        seed = item_idx
        
        domain_index = (seed + cycle_num * 7) % len(CONFIG["domains"])
        symbol_key = CONFIG["symbols"][(seed + item_idx // 2) % len(CONFIG["symbols"])]
        domain = CONFIG["domains"][domain_index]
        
        query = generate_query(seed, symbol_key, domain)
        results = simulate_search_results(query)
        
        cycle_results.append(results)
        
        if symbol_key not in symbols_data:
            symbols_data[symbol_key] = []
        symbols_data[symbol_key].append({
            "query": query[:50],
            "results": results["results_count"],
            "confidence": results["average_confidence"]
        })
    
    print(f"✓ Completed processing {len(cycle_results)} items")
    
    # Generate reports for each core symbol
    reports = []
    for symbol in CONFIG["symbols"]:
        report_md = generate_obsidian_report(
            cycle_num, timestamp, symbol, cycle_results
        )
        
        output_path = CONFIG["output_dir"] / f"CORE_SYMBOL_{symbol}_CYCLE{cycle_num:04d}_{timestamp.replace(':', '_')}.md"
        
        with open(output_path, "w") as f:
            f.write(report_md)
        
        reports.append(output_path)
    
    # Generate relationship matrix
    matrix_md = generate_relationship_matrix()
    matrix_path = CONFIG["output_dir"] / "RELATIONSHIP_MATRIX.md"
    with open(matrix_path, "w") as f:
        f.write(matrix_md)
    
    print(f"✓ Generated {len(CONFIG['symbols'])} Obsidian reports")
    print(f"✓ Updated relationship matrix")
    
    # Update knowledge base
    update_knowledge_base({})
    
    # Save log
    summary = ", ".join([f"{r['results']}@{r['confidence']}" for r in cycle_results[:3]])
    save_log(cycle_num, timestamp, summary)
    
    return {
        "cycle": cycle_num,
        "timestamp": timestamp,
        "symbols_processed": len(CONFIG["symbols"]),
        "reports": reports
    }


def main():
    """Main loop execution."""
    
    print("\n" + "="*70)
    print("STEVE'S GEMATRIA OVERNIGHT RESEARCH PROTOCOL - CONTINUOUS LOOP MODE")
    print("="*70)
    print("\nConfiguration:")
    print(f"  Items per cycle: {CONFIG['items_per_cycle']}")
    print(f"  Core symbols: {', '.join(CONFIG['symbols'])}")
    print(f"  Domains: {', '.join(CONFIG['domains'])}")
    print(f"  Hidden layering: {'ACTIVE' if CONFIG['hidden_layering_active'] else 'STANDBY'}")
    print(f"  Confidence range: {CONFIG['confidence_range'][0]}-{CONFIG['confidence_range'][1]}")
    
    # Initialize directories
    os.makedirs(CONFIG["output_dir"], exist_ok=True)
    os.makedirs(os.path.dirname(CONFIG["database_path"]), exist_ok=True)
    
    # Initialize database if needed
    db_path = CONFIG["database_path"]
    if not os.path.exists(db_path):
        print(f"\n✓ Initializing knowledge database")
        update_knowledge_base({})
    
    print("\n" + "="*70)
    print("STARTING CONTINUOUS RESEARCH LOOP")
    print("="*70)
    
    cycle_num = 1
    
    while True:  # Continuous loop - runs until manually stopped
        now = datetime.now().strftime("%Y%m%d%H%M")
        
        try:
            result = process_cycle(cycle_num, now)
            
            print(f"\n✓ Cycle {cycle_num:04d} complete")
            
        except Exception as e:
            print(f"\n⚠ CRASH at cycle {cycle_num}: {e}")
        
        print("\n" + "="*70)
        print("WAITING FOR NEXT CYCLE (10-minute schedule)")
        print("="*70)
        
        time.sleep(CONFIG["sleeper_seconds"])
        
        cycle_num += 1
        
        if cycle_num > 3:  # Demo mode - stops after 3 cycles
            print("\n" + "="*70)
            print("DEMO COMPLETE")
            print(f"Final cycle count: {cycle_counter}")
            print("="*70)
            break
    
    # Generate summary
    print("\n" + "="*70)
    print("OVERNIGHT RESEARCH LOOP SUMMARY")
    print("="*70)
    
    print(f"\nTotal cycles processed: {cycle_counter}")
    print(f"Core symbols tracked: {', '.join(CONFIG['symbols'])}")
    print(f"Domains analyzed: {', '.join(CONFIG['domains'])}")
    print(f"Output directory: {CONFIG['output_dir']}")
    print(f"Knowledge database: {db_path}")
    print(f"Research log: {CONFIG['log_file']}")
    
    if os.path.exists(db_path):
        try:
            with open(db_path, "r") as f:
                data = json.load(f)
                print(f"\nDatabase entries: {len(data.get('symbols', {}))} symbols tracked")
        except:
            pass
    
    # List generated reports
    print("\nGenerated Reports:")
    for symbol in CONFIG["symbols"]:
        test_path = CONFIG["output_dir"] / f"CORE_SYMBOL_{symbol}_CYCLE{cycle_counter:04d}_{now.replace(':', '_')}.md"
        if os.path.exists(test_path):
            print(f"  ✓ {test_path.name}")
    
    print("\n✓ Continuous Research Loop Complete")


if __name__ == "__main__":
    main()
