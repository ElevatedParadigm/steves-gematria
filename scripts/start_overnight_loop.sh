#!/usr/bin/env python3
"""
🌙 Gematria Overnight Research Loop - START Script
===================================================

Activates and starts the overnight research loop with:
- Enhanced stability testing on gematria database
- Auto-sync to Obsidian notes with relationship matrices
- Correlation heatmap generation
- Hybrid scheduler integration for elasticity monitoring
- Phase markers in logs for monitoring
- Auto-restart capability on failure

Usage: bash /home/avalonas/.hermes/gematria/scripts/start_overnight_loop.sh
"""

#!/usr/bin/env bash

# Gematria Overnight Research Loop - START Script
# Activates and starts the overnight research loop cron service

echo "============================================================"
echo "🌙 GEMATRIA OVERNIGHT RESEARCH LOOP - STARTING..."
echo "============================================================"

# Get current timestamp for logging
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S UTC')
echo "Started: $TIMESTAMP"
echo ""

# Function to log messages
log() {
    echo "$1" | tee -a /home/avalonas/.hermes/gematria/cron_logs/startup.log
}

log "============================================================"
log "📋 ACTIVATING OVERNIGHT RESEARCH LOOP CRON SERVICE"
log "============================================================"
echo ""

# Check if we're root or have sudo access for systemctl
if command -v sudo &> /dev/null && [ "$(id -u)" -ne 0 ]; then
    log "ℹ️  Detected non-root user, using sudo for systemctl commands..."
    USE_SUDO="sudo"
else
    log "ℹ️  Running as root or no sudo available..."
    USE_SUDO=""
fi

echo ""
log "=== STEP 1: Checking systemd service exists ==="
SERVICE_FILE="$HOME/.hermes/systemd/gematria-research-loop.service"
if [ -f "$SERVICE_FILE" ]; then
    log "✅ Service file found: $SERVICE_FILE"
else
    log "❌ Service file not found. Please run setup_overnight_loop.py first."
    exit 1
fi

echo ""
log "=== STEP 2: Verifying all required scripts ==="
REQUIRED_SCRIPTS=(
    "$HOME/.hermes/gematria/scripts/loop_runner_enhanced.py"
    "$HOME/.hermes/gematria/scripts/stability_test_enhanced_fixed.py"
    "$HOME/.hermes/gematria/scripts/auto_obisidian_sync_v2.py"
    "$HOME/.hermes/gematria/scripts/hybrid_scheduler.py"
)

ALL_SCRIPTS_EXIST=true
for script in "${REQUIRED_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        size=$(stat -f%z "$script" 2>/dev/null || stat -c%s "$script" 2>/dev/null)
        log "✅ $(basename $script) ($size bytes)"
    else
        log "❌ $(basename $script) (MISSING)"
        ALL_SCRIPTS_EXIST=false
    done
done

if [ "$ALL_SCRIPTS_EXIST" = false ]; then
    echo ""
    log "ERROR: Some required scripts are missing!"
    exit 1
fi

echo ""
log "=== STEP 3: Verifying logs directory ==="
LOGS_DIR="$HOME/.hermes/gematria/cron_logs"
if [ -d "$LOGS_DIR" ]; then
    log "✅ Logs directory exists: $LOGS_DIR"
else
    mkdir -p "$LOGS_DIR"
    log "✅ Created logs directory: $LOGS_DIR"
fi

# Create subdirectories
mkdir -p "$LOGS_DIR/phase_markers"
mkdir -p "$LOGS_DIR/elasticity_events"
log "   → phase_markers/"
log "   → elasticity_events/"

echo ""
log "=== STEP 4: Enabling systemd service (on boot) ==="
"$USE_SUDO" systemctl daemon-reload
if [ $? -eq 0 ]; then
    log "✅ Systemd daemon reloaded"
else
    log "❌ Failed to reload systemd daemon"
fi

# Enable the service (starts on boot)
log "Enabling service for automatic start on boot..."
"$USE_SUDO" systemctl enable "$SERVICE_FILE.name" 2>/dev/null || \
    "$USE_SUDO" cp "$SERVICE_FILE" /etc/systemd-system/gematria-research-loop.service 2>/dev/null || \
    log "⚠️  Service enablement may need manual configuration"

echo ""
log "=== STEP 5: Starting the overnight research loop ==="
"$USE_SUDO" systemctl start gematria-research-loop.service

if [ $? -eq 0 ]; then
    log "✅ Overnight research loop service started successfully!"
    
    # Check if it's running
    sleep 2
    STATUS=$("$USE_SUDO" systemctl is-active gematria-research-loop.service 2>/dev/null || echo "")
    
    if [ "$STATUS" = "active" ] || [ -z "$STATUS" ]; then
        log "✅ Service status: ACTIVE (running)"
    else
        log "⚠️  Service may be in degraded state or using different status indicator"
    fi
    
else
    log "❌ Failed to start the service manually"
    echo ""
    log "Manual start instructions:"
    log "1. Check if you need root access: sudo -v"
    log "2. Copy service file: cp '$SERVICE_FILE' '/etc/systemd/system/'"
    log "3. Reload daemon: sudo systemctl daemon-reload"
    log "4. Enable service: sudo systemctl enable gematria-research-loop.service"
    log "5. Start service: sudo systemctl start gematria-research-loop.service"
fi

echo ""
log "=== STEP 6: Cron job alternative ==="
log "If you prefer using cron instead of systemd:"
log ""
log "1. Edit crontab: crontab -e"
log ""
log "2. Add this line (runs every 3 hours at :00 minute UTC):"
log "   0 0,3,6,9,12,15,18,21 * * * cd /home/avalonas/.hermes/gematria && python scripts/loop_runner_enhanced.py --timeout 2700 >> cron_logs/cron_job.log 2>&1"
log ""

echo ""
log "=== STEP 7: Useful commands ==="
log ""
log "View logs:"
log "   journalctl -u gematria-research-loop.service -f"
log "   tail -f $LOGS_DIR/loop_enhanced_*.log"
log "   cat $LOGS_DIR/phase_markers_*.log"
log ""
log "Check service status:"
log "   $USE_SUDO systemctl status gematria-research-loop.service"
log ""
log "Stop the service:"
log "   $USE_SUDO systemctl stop gematria-research-loop.service"
log ""
log "Restart the service:"
log "   $USE_SUDO systemctl restart gematria-research-loop.service"
log ""
log "View all cron jobs:"
log "   crontab -l"

echo ""
echo "============================================================"
log "🌙 OVERNIGHT RESEARCH LOOP ACTIVATION COMPLETE!"
echo "============================================================"
log ""
log "The overnight research loop will now run automatically every 3 hours at :00 minute UTC (hours: 0,3,6,9,12,15,18,21)"
log ""
log "Each run will:"
log "   1. 🧪 Run enhanced stability test on gematria database"
log "   2. 🔄 Perform auto-sync to Obsidian with relationship matrices"
log "   3. 📊 Generate correlation heatmaps and visualizations"
log "   4. 🔀 Integrate with hybrid_scheduler for elasticity monitoring"
log "   5. 📝 Write logs with phase markers"
log "   6. 🔁 Auto-restart on failure"
log ""
log "Logs are available at:"
log "   $LOGS_DIR/"
echo "============================================================"

exit 0
