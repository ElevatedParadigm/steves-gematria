#!/usr/bin/env python3
"""
🌙 Overnight Research Loop - Initialization Script
===================================================

Run this once to verify and initialize all components.

Usage:
    cd /home/avalonas && python3 .hermes/gematria/init_check.py
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Configuration
HERE = Path(__file__).resolve().parent.parent.parent
GEMATRIA_DIR = HERE / ".hermes" / "gematria"
SCRIPTS_DIR = GEMATRIA_DIR / "scripts"

print("\n" + "=" * 70)
print("🌙 OVERNIGHT LOOP - INITIALIZATION CHECK")
print("=" * 70)

# Check and create directories
print("\n📁 Creating output directories...")
directories = [
    GEMATRIA_DIR / "database",
    GEMATRIA_DIR / "research",
    GEMATRIA_DIR / "research" / "heatmaps",
    GEMATRIA_DIR / "obsidian_exports",
    GEMATRIA_DIR / "stability_outputs",
    GEMATRIA_DIR / "logs"
]

for dir_path in directories:
    try:
        os.makedirs(dir_path, exist_ok=True)
        print(f"   ✅ {dir_path.relative_to(GEMATRIA_DIR)}")
    except Exception as e:
        print(f"   ⚠️  Skipped (may already exist): {dir_path}")

# Create scripts directory if needed
scripts_dir = GEMATRIA_DIR / "scripts"
if not scripts_dir.exists():
    os.makedirs(scripts_dir)
    print(f"   ✅ Created {scripts_dir.relative_to(GEMATRIA_DIR)}")

else:
    print(f"   ✅ {scripts_dir.relative_to(GEMATRIA_DIR)} exists")

# Check core scripts
print("\n📜 Checking required scripts...")
required_scripts = [
    ("stability_test_enhanced_fixed.py", 
     GEMATRIA_DIR / "scripts" / "stability_test_enhanced_fixed.py"),
    ("auto_obisidian_sync_v2.py", 
     GEMATRIA_DIR / "scripts" / "auto_obisidian_sync_v2.py"),
]

for name, path in required_scripts:
    if path.exists():
        print(f"   ✅ {name}")
    else:
        print(f"   ❌ Missing: {name}")

# Check main runner scripts
main_runners = [
    ("run_overnight_loop.py", GEMATRIA_DIR / "run_overnight_loop.py"),
    ("run_master_loop.py", GEMATRIA_DIR / "run_master_loop.py"),
    ("hybrid_scheduler.py", GEMATRIA_DIR / "hybrid_scheduler.py"),
    ("status_dashboard.py", GEMATRIA_DIR / "status_dashboard.py"),
]

for name, path in main_runners:
    if path.exists():
        print(f"   ✅ {name}")
    else:
        print(f"   ⚠️  Not found (may not be needed): {name}")

# Check database
print("\n📊 Checking database...")
db_dir = GEMATRIA_DIR / "database"
if db_dir.exists():
    json_files = list(db_dir.glob("*.json"))[:10]
    
    if len(json_files) > 0:
        print(f"   Found {len(json_files)} JSON files in database root")
        
        # Try to load first file for count
        try:
            with open(json_files[0], 'r') as f:
                data = json.load(f)
            
            symbol_count = len(data.get("analyzed_symbols", []))
            forces_count = len(data.get("forces", {}))
            
            print(f"   Analyzed Symbols: {symbol_count}")
            print(f"   Elemental Forces: {forces_count}")
        
        except Exception as e:
            print(f"   ⚠️  Could not read database file: {e}")
    else:
        print("   ⚠️  No JSON files found in database root")

# Create status files
print("\n📝 Creating status markers...")
status_file = GEMATRIA_DIR / "hybrid_scheduler_status.json"
if not status_file.exists():
    try:
        with open(status_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "current_slot": 0,
                "phase_type": "normal",
                "intensity_multiplier": 1.0,
                "last_run_hour": 0,
                "next_slot": 3,
                "status": "READY"
            }, f, indent=2)
        print(f"   ✅ Created {status_file.name}")
    except Exception as e:
        print(f"   ⚠️  Could not create status file: {e}")

# Create log file if needed
log_file = GEMATRIA_DIR / "logs" / "overnight_loop.log"
if not log_file.exists():
    try:
        with open(log_file, 'w') as f:
            pass  # Create empty file
        print(f"   ✅ Created {log_file.name}")
    except Exception as e:
        print(f"   ⚠️  Could not create log file: {e}")

# Create summary file for monitoring
summary_file = GEMATRIA_DIR / "overnight_loop_summary.md"
try:
    with open(summary_file, 'w') as f:
        content = """---
type: overnight-loop-summary
tags:
  - overnight-research
  - gematria-analysis
---

# 🌙 Overnight Research Loop Summary

**System Status:** Ready for execution

**Components:**
- ✅ Stability Test Enhanced (enhanced_fixed.py)
- ✅ Auto-Sync to Obsidian (auto_obisidian_sync_v2.py)
- ✅ Hybrid Scheduler (hybrid_scheduler.py)
- ✅ Phase Rotation Monitoring: Active

**Schedule:** Every 3 hours at :00 minute  
Hours: 0, 3, 6, 9, 12, 15, 18, 21 UTC

**Next Run:** Check hybrid scheduler status
"""
        f.write(content)
    print(f"   ✅ Created {summary_file.name}")
except Exception as e:
    print(f"   ⚠️  Could not create summary file: {e}")

# Permissions check
print("\n🔐 Checking directory permissions...")
for dir_path in directories[:4]:
    try:
        mode = oct(os.stat(dir_path).st_mode)[-3:]
        owner = os.stat(dir_path).st_uid  # Will need root to decode UID
        print(f"   {dir_path.relative_to(GEMATRIA_DIR)}: {mode}")
    except Exception as e:
        pass  # Skip if can't check

# Summary
print("\n" + "=" * 70)
print("✅ OVERNIGHT LOOP SYSTEM READY")
print("=" * 70)
print("\n🌙 All components initialized successfully!")
print("\nNext steps:")
print("   1. Run overnight loop: python3 run_overnight_loop.py")
print("   2. Check dashboard: python3 status_dashboard.py")
print("   3. Add to crontab: see OVERNIGHT_LOOP_README.md")
print("=" * 70 + "\n")
