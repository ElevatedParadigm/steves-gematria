#!/usr/bin/env python3
"""
Setup Gematria Overnight Research Loop Cron Job
================================================

Creates systemd service and cron configuration for scheduled execution.
Schedule: Every 3 hours at :00 minute (hours 0,3,6,9,12,15,18,21 UTC)
"""

import sys
from pathlib import Path

# Paths
GEMATRIA_DIR = Path.home() / ".hermes" / "gematria"
SCRIPTS_DIR = GEMATRIA_DIR / "scripts"
LOGS_DIR = GEMATRIA_DIR / "cron_logs"
SYSTEMD_DIR = Path.home() / ".hermes" / "systemd"

# Required scripts
REQUIRED_SCRIPTS = [
    SCRIPTS_DIR / "loop_runner_enhanced.py",
    SCRIPTS_DIR / "stability_test_enhanced_fixed.py",
    SCRIPTS_DIR / "auto_obisidian_sync_v2.py",
    SCRIPTS_DIR / "hybrid_scheduler.py"
]

def verify_scripts():
    """Verify all required scripts exist"""
    print("\n" + "=" * 60)
    print("📋 VERIFYING REQUIRED SCRIPTS")
    print("=" * 60)
    
    all_exist = True
    for script in REQUIRED_SCRIPTS:
        if script.exists():
            size = script.stat().st_size
            print(f"✅ {script.name} ({size / 1024:.1f}KB)")
        else:
            print(f"❌ {script.name} (MISSING)")
            all_exist = False
    
    return all_exist

def create_logs_directory():
    """Create logs directory with proper permissions"""
    print("\n" + "=" * 60)
    print("📁 CREATING LOGS DIRECTORY")
    print("=" * 60)
    
    if not LOGS_DIR.exists():
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created logs directory: {LOGS_DIR}")
        LOGS_DIR.chmod(0o755)
        print(f"   → Permissions set to 755")
    
    else:
        print(f"✅ Logs directory exists: {LOGS_DIR}")
    
    # Create subdirectories if they don't exist
    for subdir in ["phase_markers", "elasticity_events"]:
        dir_path = LOGS_DIR / subdir
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"   → Created: {dir_path}")
    
    return True

def create_systemd_service():
    """Create systemd service for scheduled execution"""
    print("\n" + "=" * 60)
    print("⚙️  CREATING SYSTEMD SERVICE")
    print("=" * 60)
    
    systemd_file = SYSTEMD_DIR / "gematria-research-loop.service"
    
    service_content = '''# Gematria Overnight Research Loop - Systemd Service
# ========================================================
# Schedule: Every 3 hours at :00 minute (hours 0,3,6,9,12,15,18,21 UTC)
# Auto-restart enabled with proper phase markers for elasticity monitoring
# Integrates with hybrid_scheduler.py for multi-phase elasticity monitoring

[Unit]
Description=Gematria Overnight Research Loop - Enhanced Stability & Sync Service
Documentation=https://hermes-agent.nousresearch.com/docs
After=network.target time-sync.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=no
WorkingDirectory=/home/avalonas/.hermes/gematria
ExecStart=/usr/bin/python3 /home/avalonas/.hermes/gematria/scripts/loop_runner_enhanced.py --timeout 2700
TimeoutStartSec=3600
TimeoutStopSec=60

# Environment and Paths
Environment="PYTHONUNBUFFERED=1"
Environment="GEMATRIA_DIR=/home/avalonas/.hermes/gematria"
Environment="HOME=/home/avalonas"
Environment="TZ=UTC"

# Logging
StandardOutput=journal+console
StandardError=journal+console
SyslogIdentifier=gematria-research-loop

# Restart policy for auto-restart on failure
Restart=on-failure
RestartSec=30
StartLimitBurst=3
StartLimitIntervalSec=120

# Resource limits
MemoryMax=512M
MemoryHigh=256M
CPUQuota=50%

[Install]
WantedBy=multi-user.target
'''
    
    with open(systemd_file, 'w') as f:
        f.write(service_content)
    
    print(f"✅ Created systemd service: {systemd_file}")
    print("\n   To enable the service:")
    print(f"   → sudo systemctl daemon-reload")
    print(f"   → sudo systemctl enable {systemd_file.name}")
    print(f"   → sudo systemctl start {systemd_file.name}")
    
    return True

def create_cron_config():
    """Create cron job configuration"""
    print("\n" + "=" * 60)
    print("📅 CREATING CRON CONFIGURATION")
    print("=" * 60)
    
    cron_config = GEMATRIA_DIR / "cron_job_config.txt"
    
    cron_content = '''# Gematria Overnight Research Loop - Cron Job Configuration
# =========================================================
# Schedule: Every 3 hours at :00 minute (hours 0,3,6,9,12,15,18,21 UTC)
# =========================================================

# CRON JOB LINE (add this to crontab with: crontab -e)
0 0,3,6,9,12,15,18,21 * * * cd /home/avalonas/.hermes/gematria && python scripts/loop_runner_enhanced.py --timeout 2700 >> cron_logs/cron_job.log 2>&1

# Alternative: Add this entire block to crontab with: crontab -e
# ==========================================
0 0,3,6,9,12,15,18,21 * * * cd /home/avalonas/.hermes/gematria && python scripts/loop_runner_enhanced.py --timeout 2700 --retry 3 >> cron_logs/cron_job.log 2>&1
# ==========================================

# To check existing crontab: crontab -l
# To edit crontab: crontab -e
# To remove this job: Edit the line above or run: crontab -e and delete the line
'''
    
    with open(cron_config, 'w') as f:
        f.write(cron_content)
    
    print(f"✅ Created cron configuration: {cron_config}")
    print("\n   To install via crontab:")
    print(f"   → crontab -e")
    print(f"\n   Or use the installation script:")
    print(f"   → bash {SCRIPTS_DIR}/install_cron_loop.sh")
    
    return True

def main():
    """Main setup function"""
    print("=" * 60)
    print("🌙 GEMATRIA OVERNIGHT RESEARCH LOOP - CRON INSTALLER")
    print("=" * 60)
    print("\nThis will set up the overnight research loop with:")
    print("  • Enhanced stability testing on gematria database")
    print("  • Auto-sync to Obsidian notes with relationship matrices")
    print("  • Correlation heatmap and relationship visualization generation")
    print("  • Logs with phase markers for elasticity monitoring")
    print("  • Auto-restart capability on failure")
    print("=" * 60)
    
    # Verify scripts exist
    if not verify_scripts():
        print("\n❌ Required scripts are missing. Please create them manually or run the installation script.")
        return False
    
    # Create logs directory
    create_logs_directory()
    
    # Create systemd service
    create_systemd_service()
    
    # Create cron config
    create_cron_config()
    
    print("\n" + "=" * 60)
    print("✅ CRON INSTALLATION COMPLETE!")
    print("=" * 60)
    
    print("\n📋 NEXT STEPS:")
    print("=" * 60)
    print("1. Reload systemd daemon:")
    print("   → sudo systemctl daemon-reload")
    print("\n2. Enable the service (starts on boot):")
    print("   → sudo systemctl enable gematria-research-loop.service")
    print("\n3. Start the service:")
    print("   → sudo systemctl start gematria-research-loop.service")
    print("\n4. Install cron job (alternative to systemd):")
    print("   → crontab -e  # Add the cron line from config file")
    print("\n5. View logs:")
    print("   → journalctl -u gematria-research-loop.service -f")
    print("   → tail -f cron_logs/loop_enhanced_*.log")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
