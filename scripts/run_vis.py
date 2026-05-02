#!/usr/bin/env python3
"""
STEVE'S GEMATRIA VISUALIZATION ENGINE — QUICKSTART GUIDE v4.2
Simple command-line interface to view symbol relationships and patterns

TYPE THIS IN YOUR TERMINAL:
    python visualization_engine.py

OR USE THESE COMMANDS:
    python scripts/visualization_engine.py           # Show all dashboards
    python scripts/visualization_engine.py --watch   # Live updates (1s interval)
    python scripts/visualization_engine.py --export html     # Generate HTML report
    python scripts/visualization_engine.py --symbol 124     # Focus on single symbol
"""

import subprocess
import sys

def run_visualization():
    """Run the visualization engine and display output"""
    script_path = "/home/avalonas/.hermes/gematria/scripts/visualization_engine.py"
    
    try:
        print("=" * 70)
        print("🌉 STEVE'S GEMATRIA VISUALIZATION ENGINE — v4.2")
        print("=" * 70)
        print()
        
        # Run the visualization engine with default arguments (show all dashboards)
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=False,
            text=True,
            cwd="/home/avalonas/.hermes/gematria"
        )
        
        print()
        print("=" * 70)
        print("🌉 VISUALIZATION ENGINE COMPLETE")
        print("=" * 70)
        
        # Check for HTML export
        html_path = "/home/avalonas/.hermes/gematria/html_report.html"
        import os
        if os.path.exists(html_path):
            size_kb = os.path.getsize(html_path) / 1024
            print(f"\n✅ HTML Report also available at: {html_path} ({size_kb:.1f} KB)")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    run_visualization()
