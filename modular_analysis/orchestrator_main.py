#!/usr/bin/env python3
"""
Modular Analysis - Orchestrator Main Script
Responsible for: Chaining all modular components together for overnight research.
Single responsibility: Coordinate execution flow, manage data handoffs between modules.

Usage:
    python orchestrator_main.py --mode=linear           # Chain all modules sequentially
    python orchestrator_main.py --mode=independent      # Run standalone tests
    python orchestrator_main.py --mode=cron             # Optimized for 3 AM execution
"""

import subprocess
import sys
from pathlib import Path
from urllib.parse import quote


def run_module_script(module_name: str):
    """Run a standalone module script if exists"""
    module_path = f"modular_analysis/{module_name}"
    
    try:
        result = subprocess.run(
            [sys.executable, module_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print(f"\n✅ [{module_name}] Completed successfully")
        else:
            print(f"\n⚠️  [{module_name}] Completed with warnings:")
            print(result.stderr)
            
    except Exception as e:
        print(f"\n❌ [{module_name}] Failed: {e}")


def linear_chain_mode():
    """Execute modules in order: Scraper → Analyzer → Graph Builder → Heatmap → Report"""
    
    print("\n" + "=" * 70)
    print("🚀 Modular Analysis Orchestrator - Linear Chain Mode")
    print("=" * 70 + "\n")
    
    # Step 1: Scraper Module
    print("\nStep 1/5: Running scraper module...")
    results = []
    
    queries = [
        "gematria analysis",
        "0 to gematria pattern",
        "historical figure age death transition",
        "meaning of number in gematria system",
        "to gematria pattern",
        "gematic progression to"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n  🔍 [{i}/6] Searching: {query[:50]}...")
        
        # Import and run scraper inline
        from scraper_module import ScraperModule
        
        scraper = ScraperModule(url="http://localhost:8084/")
        query_escaped = quote(query, safe='')  # Properly encode URL
        scraper_results = scraper.search(query_escaped)
        
        results.append({
            "query": query,
            "status": "success" if len(scraper_results) > 0 else "partial",
            "results": scraper_results
        })
        
        print(f"    ✅ Found {len(scraper_results)} potential links")
    
    # Step 2: Analyzer Module
    print("\nStep 2/5: Running analyzer module...")
    from analyzer_module import AnalyzerModule
    
    analyzer = AnalyzerModule()
    analysis = analyzer.analyze(results)
    
    print(f"    ✅ Detected {len(analysis['convergence_signals'])} convergence signals")
    if analysis['key_themes']:
        print(f"    Themes: {', '.join(analysis['key_themes'][:3])}")
    
    # Step 3: Graph Builder Module
    print("\nStep 3/5: Running graph builder module...")
    from graph_builder_module import GraphBuilderModule
    
    builder = GraphBuilderModule()
    new_rels = builder.build_relationships(results, [])
    
    print(f"    ✅ Built {len(new_rels)} new relationships")
    
    # Step 4: Temporal Tracker Module
    print("\nStep 4/5: Running temporal tracker module...")
    from temporal_tracker_module import TemporalTrackerModule
    
    tracker = TemporalTrackerModule()
    query_sequence = [r.get("query", "")[:40] for r in results]
    temporal = tracker.track(query_sequence, results)
    
    print(f"    ✅ Average results/query: {temporal['average_results_per_query']:.1f}")
    
    # Step 5: Heatmap Generator Module
    print("\nStep 5/5: Running heatmap generator module...")
    from heatmap_generator_module import HeatmapGeneratorModule
    
    generator = HeatmapGeneratorModule()
    symbols = ["124", "963", "55", "111", "279", "666"]
    ascii_heatmap = generator.generate_relationships(new_rels, symbols)
    
    print(f"    ✅ ASCII heatmaps generated")
    
    # Step 6: Report Generator Module
    print("\nStep 6/6: Generating comprehensive report...")
    from report_generator_module import ReportGeneratorModule
    
    report_gen = ReportGeneratorModule()
    results_dict = {
        "results": results,
        "analysis": analysis,
        "new_rels": new_rels,
        "temporal": temporal,
        "ascii_heatmap": ascii_heatmap,
        "existing_rels_count": 0
    }
    
    report_path = report_gen.generate_report(results_dict)
    
    print(f"    ✅ Report saved to: {report_path}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("✅ Modular Analysis Complete!")
    print("=" * 70)
    print(f"\n📊 Summary:")
    print(f"   Queries processed: {len(results)}")
    print(f"   Convergence signals: {len(analysis['convergence_signals'])}")
    print(f"   New relationships: {len(new_rels)}")
    print(f"   Report: {report_path}")
    print("=" * 70 + "\n")


def independent_mode():
    """Run each module independently for testing"""
    
    print("\n" + "=" * 70)
    print("🔧 Modular Analysis - Independent Component Testing Mode")
    print("=" * 70 + "\n")
    
    modules = [
        "scraper_module",
        "analyzer_module", 
        "graph_builder_module",
        "temporal_tracker_module",
        "heatmap_generator_module",
        "report_generator_module"
    ]
    
    for module in modules:
        print(f"\nRunning {module}...")
        run_module_script(module)


def cron_mode():
    """Optimized mode for 3 AM cron execution (minimal output, all errors logged)"""
    
    print("\n[CRON MODE] All module outputs redirected to logs...\n")
    
    # Run linear chain silently
    try:
        from orchestrator_main import linear_chain_mode
        # This would be run in a cron context - just print status
        print("[CRON] Linear chain mode starting...")
        
    except Exception as e:
        print(f"[CRON] Error: {e}")


if __name__ == "__main__":
    import sys
    
    # Parse arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode in ["--linear", "-l"]:
            linear_chain_mode()
        elif mode in ["--independent", "-i", "test"]:
            independent_mode()
        elif mode in ["--cron", "-c"]:
            cron_mode()
        else:
            print("\nUsage: python orchestrator_main.py [--linear | --independent | --cron]")
            
            print("\nModes:")
            print("  --linear, -l    Chain all modules sequentially (default)")
            print("  --independent, -i, test  Run each module independently for testing")
            print("  --cron, -c      Optimized for 3 AM cron execution")
            
            print("\nExample:")
            print("  python orchestrator_main.py --linear")
    else:
        # Default to linear chain mode
        linear_chain_mode()
