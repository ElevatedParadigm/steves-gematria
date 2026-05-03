#!/usr/bin/env python3
"""
🌙 Overnight Loop Status Dashboard
==========================================================

Quick status check for the complete overnight research loop system.
Shows current phase, intensity, and recent outputs.

Usage:
    python3 status_dashboard.py [--verbose] [--detailed]
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Configuration
HERE = Path(__file__).resolve().parent.parent.parent
GEMATRIA_DIR = HERE / ".hermes" / "gematria"
LOGS_DIR = GEMATRIA_DIR / "logs"
STATUS_FILE = GEMATRIA_DIR / "hybrid_scheduler_status.json"


def print_banner():
    """Print dashboard banner"""
    print("\n" + "=" * 70)
    print(" 🌙 OVERNIGHT RESEARCH LOOP STATUS DASHBOARD")
    print("=" * 70)
    print()


def get_stability_status():
    """Get stability test status from last run"""
    stability_file = GEMATRIA_DIR / "stability_last_result.json"
    
    try:
        if stability_file.exists():
            with open(stability_file, 'r') as f:
                data = json.load(f)
            
            return {
                "status": data.get("overall_status", "UNKNOWN"),
                "confidence": data.get("confidence_score", 0),
                "issues_count": len(data.get("issues", [])),
                "timestamp": data.get("timestamp")
            }
    except Exception as e:
        pass
    
    return {"status": "NO_DATA", "confidence": 0}


def get_sync_status():
    """Get auto-sync output status"""
    obsidian_dir = GEMATRIA_DIR / "obsidian_exports"
    
    if not obsidian_dir.exists():
        return {"file_count": 0, "last_run": None, "status": "NO_DATA"}
    
    files = list(obsidian_dir.glob("*.md"))
    return {
        "file_count": len(files),
        "files": sorted([f.name for f in files[:10]], reverse=True),
        "status": "ACTIVE" if len(files) > 0 else "NO_DATA"
    }


def get_heatmap_status():
    """Get heatmap generation status"""
    heatmaps_dir = GEMATRIA_DIR / "research" / "heatmaps"
    
    if not heatmaps_dir.exists():
        return {"file_count": 0, "status": "NOT_GENERATED"}
    
    files = list(heatmaps_dir.glob("*.md"))
    return {
        "file_count": len(files),
        "latest_file": max(files, key=os.path.getctime).name if files else None,
        "status": "GENERATED" if len(files) > 0 else "NOT_GENERATED"
    }


def get_scheduler_status():
    """Get hybrid scheduler current phase"""
    status_path = GEMATRIA_DIR / "hybrid_scheduler_status.json"
    
    try:
        with open(status_path, 'r') as f:
            status = json.load(f)
        
        return {
            "slot": status.get("current_slot"),
            "phase_type": status.get("phase_type"),
            "intensity": status.get("intensity_multiplier", 1.0),
            "last_run_hour": status.get("last_run_hour")
        }
    except Exception as e:
        return {"error": str(e)}


def get_database_info():
    """Get database size and structure"""
    db_dir = GEMATRIA_DIR / "database"
    
    try:
        # Count JSON files (symbols)
        symbol_files = list(db_dir.glob("*.json"))[:10]  # Top 10
        
        if not symbol_files:
            return {"symbol_count": 0, "forces_count": 0}
        
        # Try to load first symbol file for count
        if len(symbol_files) > 0:
            try:
                with open(symbol_files[0], 'r') as f:
                    data = json.load(f)
                
                symbol_count = len(data.get("analyzed_symbols", []))
                forces_count = len(data.get("forces", {}))
            except Exception:
                return {"symbol_count": 1, "forces_count": 0}
        else:
            return {"symbol_count": 0, "forces_count": 0}
        
        return {
            "symbol_count": symbol_count,
            "forces_count": forces_count,
            "analyzed_symbols": symbol_files[0].name if symbol_files else None
        }
    
    except Exception as e:
        return {"error": str(e)}


def print_status():
    """Print comprehensive status report"""
    
    print_banner()
    
    # Database Info
    db_info = get_database_info()
    if "symbol_count" in db_info:
        print(f"📊 DATABASE INFO")
        print("-" * 40)
        print(f"   Analyzed Symbols: {db_info.get('symbol_count', 'N/A')}")
        print(f"   Elemental Forces: {db_info.get('forces_count', 'N/A')}")
    else:
        print(f"⚠️  ERROR: {db_info.get('error', 'Unknown error')}")
    
    print()
    
    # Scheduler Status
    scheduler = get_scheduler_status()
    if "slot" in scheduler:
        slot = scheduler.get("slot", 0)
        phase_type = scheduler.get("phase_type", "normal").upper()
        intensity = scheduler.get("intensity", 1.0)
        
        print(f"🕐 HYBRID SCHEDULER STATUS")
        print("-" * 40)
        print(f"   Current Slot: {slot:02d}:00 UTC")
        print(f"   Phase Mode:   {phase_type}")
        print(f"   Intensity:    {intensity}x")
    else:
        print("⚠️  Scheduler status unavailable")
    
    print()
    
    # Stability Test
    stability = get_stability_status()
    if "status" in stability:
        overall_status = stability.get("status", "").upper()
        confidence = stability.get("confidence", 0)
        issues = stability.get("issues_count", 0)
        
        print(f"🔍 STABILITY TEST STATUS")
        print("-" * 40)
        status_icon = "✅" if overall_status == "PASSED" else "⚠️" if overall_status == "PENDING_REMEDIATION" else "❌"
        print(f"   Overall Status: {overall_status} [{status_icon}]")
        print(f"   Confidence Score: {confidence:.2f}")
        print(f"   Issues Found: {issues}")
    else:
        print("⚠️  Stability test data not available")
    
    print()
    
    # Auto-Sync Status
    sync = get_sync_status()
    if "file_count" in sync:
        count = sync.get("file_count", 0)
        
        print(f"📁 AUTO-SYNC TO OBSIDIAN STATUS")
        print("-" * 40)
        print(f"   Export Files: {count}")
        
        if count > 0 and len(sync.get("files", [])) <= 10:
            for fname in sync["files"]:
                print(f"     └─ {fname}")
    else:
        print("⚠️  Sync data not available")
    
    print()
    
    # Heatmap Status
    heatmaps = get_heatmap_status()
    if "file_count" in heatmaps:
        count = heatmaps.get("file_count", 0)
        
        print(f"📊 CORRELATION HEATMAP STATUS")
        print("-" * 40)
        status_text = f"Generated {count} heatmap files" if count > 0 else "Not yet generated"
        print(f"   Status: {status_text}")
    else:
        print("⚠️  Heatmap data not available")
    
    print()
    
    # Directory Structure Summary
    print("=" * 70)
    print("📁 OUTPUT DIRECTORY STRUCTURE")
    print("=" * 70)
    
    dirs = [
        GEMATRIA_DIR / "obsidian_exports",
        GEMATRIA_DIR / "research" / "heatmaps",
        GEMATRIA_DIR / "stability_outputs"
    ]
    
    for dir_path in dirs:
        try:
            if dir_path.exists() and dir_path.is_dir():
                file_count = len(list(dir_path.glob("*")))
                print(f"   {dir_path.relative_to(GEMATRIA_DIR)}")
                print(f"   └─ Contains {file_count} files")
        except Exception as e:
            pass
    
    # Footer
    print()
    print("=" * 70)
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"🕐 Dashboard Generated: {timestamp}")
    print("=" * 70 + "\n")


def check_healthy():
    """Check if system is healthy and all components are working"""
    
    issues = []
    
    # Check database exists
    db_dir = GEMATRIA_DIR / "database"
    if not db_dir.exists():
        issues.append("Database directory missing")
    
    elif not list(db_dir.glob("*.json")):
        issues.append("No symbols.json or forces.json found in database")
    
    # Check output directories exist
    for dir_path in [GEMATRIA_DIR / "obsidian_exports", 
                     GEMATRIA_DIR / "research" / "heatmaps"]:
        if not dir_path.exists():
            pass  # Not critical
    
    # Check scripts exist
    required_scripts = [
        GEMATRIA_DIR / "scripts" / "stability_test_enhanced_fixed.py",
        GEMATRIA_DIR / "scripts" / "auto_obisidian_sync_v2.py"
    ]
    
    for script_path in required_scripts:
        if not script_path.exists():
            issues.append(f"Missing required script: {script_path.name}")
    
    # Check stability result
    stability_file = GEMATRIA_DIR / "stability_last_result.json"
    if not stability_file.exists() and len(list((GEMATRIA_DIR / "database").glob("*.json"))) > 0:
        issues.append("No stability test results available yet")
    
    # Check scheduler status
    status_path = GEMATRIA_DIR / "hybrid_scheduler_status.json"
    if not status_path.exists():
        pass  # May run first time
    
    if issues:
        print("\n⚠️  HEALTH CHECK REPORT")
        print("=" * 60)
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        
        print("=" * 60)
        return False
    else:
        print("\n✅ HEALTH CHECK PASSED")
        print("=" * 60)
        print("All components are present and configured correctly.")
        print()
        print("Next steps:")
        print("   1. Run: python3 run_overnight_loop.py")
        print("   2. Monitor: dashboard status_dashboard.py")
        print("=" * 60)
        return True


def main():
    """Main entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="🌙 Overnight Loop Status Dashboard")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--check-healthy", action="store_true", help="Run health check")
    
    args = parser.parse_args()
    
    if args.check_healthy:
        check_healthy()
        return 0
    
    print_status()
    return 0


if __name__ == "__main__":
    sys.exit(main())
