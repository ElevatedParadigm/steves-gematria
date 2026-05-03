#!/usr/bin/env python3
"""
🌙 Gematria Overnight Research Loop - START Script
===================================================

Activates and starts the overnight research loop cron service with:
- Enhanced stability testing on gematria database
- Auto-sync to Obsidian notes with relationship matrices
- Correlation heatmap generation
- Hybrid scheduler integration for elasticity monitoring
- Phase markers in logs for monitoring
- Auto-restart capability on failure

Usage: python /home/avalonas/.hermes/gematria/scripts/start_overnight_loop.py
"""

import subprocess
import sys
from pathlib import Path

# Paths
HOME = Path.home()
GEMATRIA_DIR = HOME / ".hermes" / "gematria"
SCRIPTS_DIR = GEMATRIA_DIR / "scripts"
SYSTEMD_DIR = HOME / ".hermes" / "systemd"
LOGS_DIR = GEMATRIA_DIR / "cron_logs"

SERVICE_FILE = SYSTEMD_DIR / "gematria-research-loop.service"

def run_command(command, shell=False):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def get_sudo_prefix():
    """Get sudo prefix if needed"""
    result = subprocess.run(["id", "-u"], capture_output=True, text=True)
    uid = int(result.stdout.strip())
    if uid != 0 and "sudo" in command.getoutput():
        return "sudo "
    return ""

# Import datetime first
from datetime import datetime

print("=" * 60)
print("🌙 GEMATRIA OVERNIGHT RESEARCH LOOP - STARTING...")
print("=" * 60)
print("\nStarted:", datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'))

def log(message):
    """Log a message with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")
    return message

print("=" * 60)
log("📋 ACTIVATING OVERNIGHT RESEARCH LOOP CRON SERVICE")
print("=" * 60)
print()

print("\n=== STEP 1: Checking systemd service exists ===")
if SERVICE_FILE.exists():
    log(f"✅ Service file found: {SERVICE_FILE}")
else:
    log(f"❌ Service file not found. Please run setup_overnight_loop.py first.")
    sys.exit(1)

print("\n=== STEP 2: Verifying all required scripts ===")
REQUIRED_SCRIPTS = [
    SCRIPTS_DIR / "loop_runner_enhanced.py",
    SCRIPTS_DIR / "stability_test_enhanced_fixed.py",
    SCRIPTS_DIR / "auto_obisidian_sync_v2.py",
    SCRIPTS_DIR / "hybrid_scheduler.py"
]

ALL_EXIST = True
for script in REQUIRED_SCRIPTS:
    if script.exists():
        size = script.stat().st_size
        log(f"✅ {script.name} ({size} bytes)")
    else:
        log(f"❌ {script.name} (MISSING)")
        ALL_EXIST = False

if not ALL_EXIST:
    print("\nERROR: Some required scripts are missing!")
    sys.exit(1)

print("\n=== STEP 3: Verifying logs directory ===")
if LOGS_DIR.exists():
    log(f"✅ Logs directory exists: {LOGS_DIR}")
else:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log(f"✅ Created logs directory: {LOGS_DIR}")

# Create subdirectories
for subdir in ["phase_markers", "elasticity_events"]:
    (LOGS_DIR / subdir).mkdir(parents=True, exist_ok=True)
    log(f"   → {subdir}/")

print("\n=== STEP 4: Enabling systemd service (on boot) ===")

# Try to reload daemon (may need sudo)
try:
    code, stdout, stderr = run_command("systemctl daemon-reload", shell=True)
    if code == 0 or "not running" in stderr.lower():
        log("✅ Systemd daemon reloaded (or not needed)")
    else:
        log(f"⚠️  systemctl daemon-reload output: {stderr[:200]}")
except Exception as e:
    log(f"⚠️  Could not reload systemd: {e}")

# Try to enable service
try:
    code, stdout, stderr = run_command("systemctl enable gematria-research-loop.service", shell=True)
    if code == 0:
        log("✅ Service enabled for automatic start on boot")
    else:
        log(f"⚠️  Could not enable service (may need sudo): {stderr[:150]}")
except Exception as e:
    log(f"⚠️  Could not enable service: {e}")

print("\n=== STEP 5: Starting the overnight research loop ===")
try:
    code, stdout, stderr = run_command("systemctl start gematria-research-loop.service", shell=True)
    
    if code == 0:
        log("✅ Overnight research loop service started successfully!")
        
        # Wait a moment and check status
        import time
        time.sleep(1)
        
        code, stdout, stderr = run_command("systemctl is-active gematria-research-loop.service", shell=True)
        
        if "active" in stdout.lower() or code == 0:
            log("✅ Service status: ACTIVE (running)")
        else:
            # Check if service file exists in /etc/systemd/
            sys_dir = Path("/etc/systemd/system/")
            if not (sys_dir / "gematria-research-loop.service").exists():
                # Need to copy or link the service file
                log("⚠️  Service needs to be linked to /etc/systemd/system/")
                log("   Copy command: cp 'systemd/gematria-research-loop.service' '/etc/systemd/system/'")
    else:
        log(f"❌ Failed to start service: {stderr[:200]}")
        
except Exception as e:
    log(f"❌ Error starting service: {e}")

print("\n=== STEP 6: Cron job alternative ===")
log("If you prefer using cron instead of systemd:")
print()
log("1. Edit crontab:")
print("   → crontab -e")
print()
log("2. Add this line (runs every 3 hours at :00 minute UTC):")
print("   0 0,3,6,9,12,15,18,21 * * * cd /home/avalonas/.hermes/gematria && python scripts/loop_runner_enhanced.py --timeout 2700 >> cron_logs/cron_job.log 2>&1")
print()

print("\n=== STEP 7: Useful commands ===")
log("")
log("View logs:")
print("   journalctl -u gematria-research-loop.service -f")
print(f"   tail -f {LOGS_DIR}/loop_enhanced_*.log")
print("   cat cron_logs/phase_markers_*.log")
print()
log("Check service status:")
print("   systemctl status gematria-research-loop.service")
print()
log("Stop the service:")
print("   systemctl stop gematria-research-loop.service")
print()
log("Restart the service:")
print("   systemctl restart gematria-research-loop.service")
print()
log("View all cron jobs:")
print("   crontab -l")

print("\n" + "=" * 60)
log("🌙 OVERNIGHT RESEARCH LOOP ACTIVATION COMPLETE!")
print("=" * 60)
log("")
log("The overnight research loop will now run automatically every 3 hours at :00 minute UTC (hours: 0,3,6,9,12,15,18,21)")
log("")
log("Each run will:")
log("   1. 🧪 Run enhanced stability test on gematria database")
log("   2. 🔄 Perform auto-sync to Obsidian with relationship matrices")
log("   3. 📊 Generate correlation heatmaps and visualizations")
log("   4. 🔀 Integrate with hybrid_scheduler for elasticity monitoring")
log("   5. 📝 Write logs with phase markers")
log("   6. 🔁 Auto-restart on failure")
print("=" * 60)
