#!/usr/bin/env python3
"""
Gematria Dashboard Launcher
Launches either console or web dashboard based on command line arguments.
Usage: 
  ./run_dashboard.py [console|--console]  → Terminal visualization
  ./run_dashboard.py [web|--web]         → Flask web dashboard (requires flask)
  ./run_dashboard.py                     → Auto-detects from environment
"""

import json
import os
import sys
from pathlib import Path

# Add gematria scripts to path
PROJECT_ROOT = Path.home() / ".hermes" / "gematria"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from dashboard import display_dashboard
from visualization_engine import generate_html_report


def load_database():
    """Load the gematria database and extract metrics."""
    db_path = PROJECT_ROOT / "database" / "gematria_database.json"
    
    try:
        with open(db_path, 'r') as f:
            data = json.load(f)
        
        # Extract metrics from database
        metadata = data.get("metadata", {})
        entries = data.get("entries", {})
        
        core_symbols = metadata.get("core_symbols", [])
        search_indices = data.get("search_indices", {})
        
        # Count images
        images = data.get("images", [])
        image_count = len(images)
        
        # Extract unique symbols from all entries
        all_symbols = set()
        for entry_key, entry_data in entries.items():
            detected = entry_data.get("core_symbols_detected", [])
            all_symbols.update(detected)
        
        # Calculate correlations (placeholder - would need actual analysis data)
        symbol_correlations = {}
        for symbol in search_indices.get("core_numbers", []):
            symbol_correlations[str(symbol)] = {
                "occurrences": sum(1 for e in entries.values() if str(symbol) in e.get("core_symbols_detected", [])),
                "contexts": list(set(str(symbol) * 3)),
            }
        
        # Extract unique domains from metadata
        domains_tracked = metadata.get("domains_tracked", [])
        elemental_forces = metadata.get("elemental_forces", [])
        
        # Get latest timestamps
        image_timestamps = [img.get("timestamp", "") for img in images if img.get("timestamp")]
        latest_timestamp = max(image_timestamps) if image_timestamps else "N/A"
        
        # Count batch reports
        batch_reports = list(entries.keys())
        
        return {
            "core_symbols": core_symbols,
            "all_symbols_detected": sorted(list(all_symbols)),
            "image_count": image_count,
            "latest_timestamp": latest_timestamp,
            "batch_reports": batch_reports[:10],  # Top 10 batches
            "domains_tracked": domains_tracked,
            "elemental_forces": elemental_forces,
            "symbol_correlations": symbol_correlations,
        }
    
    except Exception as e:
        print(f"⚠ Error loading database: {e}")
        return {}


def get_dashboard_mode():
    """Determine dashboard mode from arguments or environment."""
    # Check for explicit argument
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if "--console" in arg or arg == "console":
            return "console"
        elif "--web" in arg or arg == "web":
            return "web"
    
    # Check environment variable
    mode = os.getenv("GEMATRIA_DASHBOARD_MODE", "").lower()
    if mode:
        return mode
    
    # Default to console
    return "console"


def main():
    """Main entry point for dashboard launcher."""
    print("=" * 70)
    print("       ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓")
    print("         GEMATRIA DASHBOARD     ")
    print("       ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓")
    print("=" * 70)
    print()
    
    mode = get_dashboard_mode()
    print(f"🔮 Dashboard Mode: {mode.upper()}")
    print()
    
    if mode == "web":
        try:
            import flask
            print("✅ Flask available - Web dashboard enabled")
            
            # Generate HTML report first
            db = load_database()
            
            app = generate_html_report(db=db)
            
            print("🌐 Starting web dashboard server...")
            print(f"   Access at: http://localhost:5000")
            print()
            
            # Run in threaded mode for multi-user access
            app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
            
        except ImportError:
            print("❌ Flask not installed. Falling back to console dashboard.")
            main()  # Auto-switch to console mode
            
    else:
        print(f"📊 Console Dashboard Mode")
        print()
        
        # Use the existing dashboard.py display function
        display_dashboard()


if __name__ == "__main__":
    main()
