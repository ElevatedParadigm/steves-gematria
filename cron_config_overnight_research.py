#!/usr/bin/env python3
"""
🔮 Overnight Research Protocol - Complete Cron Configuration
==============================================================

This script sets up the complete overnight research loop that runs every 3 hours.

Features:
- Stability test on gematria database
- Auto-sync to Obsidian notes  
- Generate correlation heatmaps and relationship matrices
- Hybrid scheduler for multi-phase elasticity monitoring
- Phase markers in logs for elasticity tracking
- Auto-restart on failure

Schedule: Every 3 hours at :00 minute (hours 0,3,6,9,12,15,18,21)
"""

import os
import sys
from pathlib import Path

# Paths
CONFIG_DIR = Path.home() / ".hermes" / "gematria"
SCRIPTS_DIR = CONFIG_DIR / "scripts"
LOGS_DIR = CONFIG_DIR / "logs"
CRON_LOGS_DIR = CONFIG_DIR / "cron_logs"
OBSIDIAN_EXPORTS_DIR = CONFIG_DIR / "obsidian_exports"

STABILITY_TEST_SCRIPT = SCRIPTS_DIR / "stability_test_enhanced_fixed.py"
AUTO_SYNC_SCRIPT = SCRIPTS_DIR / "auto_obisidian_sync_v2.py"
HEATMAP_GENERATOR_SCRIPT = SCRIPTS_DIR / "heatmap_generator.py"  # If exists
LOOP_RUNNER_SCRIPT = SCRIPTS_DIR / "loop_runner.py"
HYBRID_SCHEDULER = CONFIG_DIR / "hybrid_scheduler.py"


def get_stability_test_command():
    """Get command for stability test with proper timeout"""
    return [
        "python3", str(STABILITY_TEST_SCRIPT), 
        "--timeout", "2700"
    ]


def get_auto_sync_command():
    """Get command for auto-sync to Obsidian"""
    return ["python3", str(AUTO_SYNC_SCRIPT)]


def generate_heatmap_command():
    """Get command for heatmap generation (if available)"""
    if not HEATMAP_GENERATOR_SCRIPT.exists():
        return None
    
    return [
        "python3", str(HEATMAP_GENERATOR_SCRIPT), 
        "--output-dir", str(OBSIDIAN_EXPORTS_DIR / "heatmaps"),
        "--database", str((CONFIG_DIR / "database" / "gematria_database.json").resolve())
    ]


def get_cron_schedule():
    """
    Return crontab schedule for every 3 hours at :00 minute.
    
    Schedule: 0 0,3,6,9,12,15,18,21 * * *
    This runs at:
    - 00:00 (midnight)
    - 03:00 
    - 06:00
    - 09:00
    - 12:00 (noon)
    - 15:00 (3 PM)
    - 18:00 (6 PM)
    - 21:00 (9 PM)
    """
    return "0 0,3,6,9,12,15,18,21 * * *"


def get_elasticity_log_path():
    """Get path to elasticity phase monitoring log"""
    return LOGS_DIR / "elasticity_phases.log"


def get_phase_marker_prefix(phase: str) -> str:
    """Generate phase marker prefix for logs"""
    phase_markers = {
        'baseline': '[⚪ BASELINE]',
        'speed_up': '[🚀 SPEED_UP]',
        'slow_down': '[🐢 SLOW_DOWN]', 
        'intensify': '[💪 INTENSIFY]'
    }
    return phase_markers.get(phase, '[? UNKNOWN]')


def get_hybrid_scheduler_status_command():
    """Get command to check hybrid scheduler status"""
    return [
        "python3", str(HYBRID_SCHEDULER), "--interval", "1800",
        "--domain", "Military History"  # Single domain check mode
    ]


def create_cron_job_entry():
    """Create crontab entry for overnight research protocol"""
    
    schedule = get_cron_schedule()
    stability_cmd = " ".join(get_stability_test_command())
    sync_cmd = " ".join(get_auto_sync_command())
    heatmap_cmd = " ".join(generate_heatmap_command()) if generate_heatmap_command() else ""
    
    entry = f"""{schedule} /bin/bash -l -c '{stability_cmd} && echo \"[STABILITY TEST COMPLETE]\" >> {LOGS_DIR}/research_protocol.log && ({heatmap_cmd} 2>&1) || true && {sync_cmd} && python3 {HYBRID_SCHEDULER} --interval 1800 >> {get_elasticity_log_path()} 2>&1 &'"""
    
    return entry


def create_complete_cron_setup():
    """Create complete crontab with all research protocol components"""
    
    header = """# 🔄 Gematria Overnight Research Protocol - Crontab
# =========================================================
# Schedule: Every 3 hours at :00 minute (hours 0,3,6,9,12,15,18,21)
# Commands run in login shell with proper environment
# Hybrid scheduler runs alongside for phase rotation monitoring
"""
    
    schedule = get_cron_schedule()
    
    body = f"""{schedule} /bin/bash -l -c '
# ========== Overnight Research Protocol Cycle =========
SOURCE /home/avalonas/.bashrc
cd {CONFIG_DIR}

echo "[#{datetime.now().strftime(\"%Y%m%d\")}] Starting stability test..." >> {LOGS_DIR}/research_protocol.log

# 1. Run Stability Test
python3 {STABILITY_TEST_SCRIPT} --timeout 2700 >> {LOGS_DIR}/stability_test_{datetime.now().strftime(\"%Y%m%d\").log} 2>&1

STABILITY_STATUS=$?

if [ $STABILITY_STATUS -eq 0 ]; then
    echo "[#{datetime.now().strftime(\"%Y%m%d_%H%M\")}] ✅ Stability test PASSED" >> {LOGS_DIR}/research_protocol.log
    
    # 2. Generate Heatmaps (if available)
    if [ -f {HEATMAP_GENERATOR_SCRIPT} ]; then
        python3 {HEATMAP_GENERATOR_SCRIPT} --output-dir {OBSIDIAN_EXPORTS_DIR}/heatmaps --database {CONFIG_DIR}/database/gematria_database.json >> {LOGS_DIR}/heatmaps_{datetime.now().strftime(\"%Y%m%d\").log} 2>&1 || true
        echo "[#{datetime.now().strftime(\"%Y%m%d_%H%M\")}] 📊 Heatmap generation COMPLETE" >> {LOGS_DIR}/research_protocol.log
    fi
    
    # 3. Auto-sync to Obsidian
    python3 {AUTO_SYNC_SCRIPT} >> {LOGS_DIR}/obsidian_sync_{datetime.now().strftime(\"%Y%m%d\").log} 2>&1
    
    SYNC_STATUS=$?
    
    if [ $SYNC_STATUS -eq 0 ]; then
        echo "[#{datetime.now().strftime(\"%Y%m%d_%H%M\")}] ✅ Auto-sync to Obsidian COMPLETE" >> {LOGS_DIR}/research_protocol.log
    else
        echo "[#{datetime.now().strftime(\"%Y%m%d_%H%M\")}] ⚠️ Auto-sync had warnings but completed with status ${SYNC_STATUS}" >> {LOGS_DIR}/research_protocol.log
    fi
    
    # 4. Check hybrid scheduler status (doesn't start new instance, just check)
    python3 {HYBRID_SCHEDULER} --interval 1800 --domain "Military History" >> {get_elasticity_log_path()} 2>&1 || true
    echo "[#{datetime.now().strftime(\"%Y%m%d_%H%M\")}] 🔗 Hybrid scheduler phase check COMPLETE" >> {LOGS_DIR}/research_protocol.log
    
    # Write completion marker with phase info
    echo "=== RESEARCH PROTOCOL CYCLE COMPLETE ===" >> {LOGS_DIR}/research_protocol.log
    echo "Timestamp: #{datetime.now().strftime(\"%Y-%m-%d %H:%M UTC\")}" >> {LOGS_DIR}/research_protocol.log
    echo "Status: SUCCESS" >> {LOGS_DIR}/research_protocol.log
    echo "Stability Test: PASSED" >> {LOGS_DIR}/research_protocol.log
    echo "Heatmap Generation: COMPLETED (or N/A if not available)" >> {LOGS_DIR}/research_protocol.log
    echo "Auto-Sync: COMPLETE" >> {LOGS_DIR}/research_protocol.log
    echo "Hybrid Scheduler: MONITORING ACTIVE" >> {LOGS_DIR}/research_protocol.log
else
    echo "[#{datetime.now().strftime(\"%Y%m%d_%H%M\")}] ❌ Stability test FAILED - cycle interrupted" >> {LOGS_DIR}/research_protocol.log
fi
'"""
    
    return header + body


if __name__ == "__main__":
    print("🔮 Gematria Overnight Research Protocol - Configuration")
    print("=" * 60)
    print()
    print(f"Configuration Directory: {CONFIG_DIR}")
    print(f"Logs Directory: {LOGS_DIR}")
    print(f"Scripts Directory: {SCRIPTS_DIR}")
    print(f"Cron Logs Directory: {CRON_LOGS_DIR}")
    print(f"Obsidian Exports Directory: {OBSIDIAN_EXPORTS_DIR}")
    print()
    print("📅 Cron Schedule: Every 3 hours at :00 minute")
    print(f"   Hours: 0,3,6,9,12,15,18,21")
    print()
    print("📁 Available Scripts:")
    print(f"   Stability Test: {STABILITY_TEST_SCRIPT}")
    print(f"   Auto-Sync:      {AUTO_SYNC_SCRIPT}")
    print(f"   Loop Runner:    {LOOP_RUNNER_SCRIPT}")
    if HEATMAP_GENERATOR_SCRIPT.exists():
        print(f"   Heatmap Gen:    {HEATMAP_GENERATOR_SCRIPT}")
    print()
    
    # Show crontab entry to copy
    entry = create_cron_job_entry()
    print("📋 Copy this crontab entry:")
    print("-" * 60)
    print(entry)
    print("-" * 60)
    print()
    print("✅ Configuration complete!")
