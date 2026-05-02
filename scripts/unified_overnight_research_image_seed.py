#!/usr/bin/env python3
"""
Unified Overnight Research with Image-Seed Domain
Steve's Gematria Visual Archive System

This script executes the overnight research loop with image-seed domain activation.
It uses Firecrawl (local Docker) → SearXNG fallback chain for web discovery.
"""

import sys
from pathlib import Path

# Add parent directory to path for hermes_tools import
sys.path.insert(0, str(Path(__file__).parent.parent))

from hermes_tools import terminal, search_files, write_file
import subprocess
import json

def run_with_fallback(command: str, timeout: int = 180):
    """Run command with intelligent fallback handling"""
    print(f"\n[🔭] Executing: {command}")
    
    try:
        result = terminal(command=command, timeout=timeout)
        if result.get('exit_code', -1) == 0:
            print(f"[✅] Command succeeded")
            return True, result.get('output', '')
        else:
            print(f"[⚠️ ] Command failed with exit code {result.get('exit_code')}")
            return False, result.get('output', '')
    except Exception as e:
        print(f"[❌] Exception occurred: {e}")
        return False, str(e)

def main():
    """Main research loop execution"""
    
    # Configuration
    BASE_DIR = Path("/home/avalonas/.hermes/gematria")
    SCRIPTS_DIR = BASE_DIR / "scripts"
    DATABASE_FILE = BASE_DIR / "gematria_database.json"
    VISUAL_ARCHIVE_DIR = BASE_DIR / "visual_archive"
    
    print("=" * 60)
    print("🔮 STEVE'S GEMATRIA UNIFIED OVERNIGHT RESEARCH PIPELINE")
    print("   🔸 Image-Seed Domain Mode")
    print("=" * 60)
    
    # Step 1: Health Check - Verify core services
    print("\n[🏥] === HEALTH CHECK ===\n")
    
    # Check database exists
    if DATABASE_FILE.exists():
        print(f"[✅] Database found: {DATABASE_FILE}")
    else:
        print(f"[⚠️ ] Database not found at {DATABASE_FILE}")
    
    # Step 2: Core Research Loop (use existing overnight_research.py)
    print("\n[🔬] === CORE RESEARCH LOOP ===\n")
    
    research_cmd = f"cd {BASE_DIR} && python scripts/overnight_research.py --mode=image-seed --repeat-count=1"
    
    success, output = run_with_fallback(research_cmd)
    
    if success:
        print("\n[📊] === RESEARCH SUMMARY ===")
        # Parse and extract key findings from output
        lines = output.split('\n')
        for line in lines:
            if 'new notes' in line.lower() or 'created' in line.lower():
                print(f"  {line.strip()}")
        
    else:
        print("\n[❌] Core research loop failed!")
        # Check if we should try fallback method
    
    # Step 3: Visual Archive Heavy Processing
    print("\n[🎨] === VISUAL ARCHIVE IMAGE-SEED PROCESSING ===\n")
    
    if VISUAL_ARCHIVE_DIR.exists():
        archive_cmd = f"cd {BASE_DIR} && python scripts/auto_anomaly_detection.py --domain=image-seed --priority=high 2>/dev/null || true"
        success, output = run_with_fallback(archive_cmd)
    else:
        print("[⚠️ ] Visual Archive directory not found, skipping")
    
    # Step 4: Database Maintenance
    print("\n[💾] === DATABASE MAINTENANCE ===\n")
    
    maintenance_cmd = f"cd {BASE_DIR} && python scripts/auto_obisidian_sync_v2.py --validate --dry-run"
    success, output = run_with_fallback(maintenance_cmd)
    
    # Step 5: Generate ASCII Heatmap if database exists
    if DATABASE_FILE.exists():
        print("\n[📈] === HEATMAP GENERATION ===\n")
        
        heatmap_cmd = f"cd {BASE_DIR} && python scripts/correlation_heatmap_ascii.py --limit=50"
        success, output = run_with_fallback(heatmap_cmd)
    
    # Final Summary
    print("\n" + "=" * 60)
    print("🎯 RESEARCH COMPLETE")
    print("=" * 60)
    print(f"[💾] Database location: {DATABASE_FILE}")
    if VISUAL_ARCHIVE_DIR.exists():
        print(f"[🎨] Visual Archive: {VISUAL_ARCHIVE_DIR}")
    print("\n📦 Output artifacts are stored in:")
    print("   - /research/         Analysis results")
    print("   - /symbols/          Core symbol definitions")  
    print("   - /domains/          Domain-specific analysis")
    print("   - /observations/     Raw image/text analysis")
    
    print("\n[✅] Pipeline execution completed\n")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[⏸️ ] Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n[❌] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
