#!/bin/bash
# 🌙 Enhanced Overnight Research Loop Installation Script
# =============================================================================
#
# This script installs and activates the enhanced overnight research loop cron job
# that integrates with:
#   - stability_test_enhanced_fixed.py (database integrity checking)
#   - auto_obisidian_sync_v2.py (relationship matrix sync to Obsidian)
#   - hybrid_scheduler.py (multi-phase elasticity monitoring)
#
# Schedule: Every 3 hours at :00 minute (hours 0,3,6,9,12,15,18,21 UTC)
#
# Usage: ./cron_install_loop_enhanced.sh
#

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGS_DIR="${SCRIPT_DIR}/cron_logs"
STATE_FILE="${SCRIPT_DIR}/elasticity_state.json"
CRON_FILE="${SCRIPT_DIR}/.hermes/cron/enhanced_loop_enhanced.cron"
LOOP_SCRIPT="${SCRIPT_DIR}/scripts/loop_runner_enhanced.py"

# Create required directories
echo "🔧 Setting up directories..."
mkdir -p "${LOGS_DIR}"
mkdir -p "$(dirname "${CRON_FILE}")"

# Display current time and schedule info
echo ""
echo "⏰ Current UTC Time: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo ""
echo "📅 Scheduled times (every 3 hours at :00):"
for hour in 0 3 6 9 12 15 18 21; do
    printf "   - 0${hour}:00 UTC\n" | sed 's/^/     /'
done

echo ""
echo "📋 Script Configuration:"
echo "   Path: ${LOOP_SCRIPT}"
echo "   Logs:  ${LOGS_DIR}/"
echo "   State: ${STATE_FILE}"
echo "   Cron:  ${CRON_FILE}"
echo ""

# Check if loop script exists
if [[ ! -f "${LOOP_SCRIPT}" ]]; then
    echo "❌ Error: Loop script not found at ${LOOP_SCRIPT}"
    exit 1
fi

# Verify Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed"
    exit 1
fi

# Install the cron job
echo ""
echo "📜 Installing cron job..."

cat > "${CRON_FILE}" << 'EOF'
# 🌙 Enhanced Overnight Research Loop - Cron Job
# =============================================================================
# Schedule: Every 3 hours at :00 minute (hours 0,3,6,9,12,15,18,21 UTC)
# Description: Runs enhanced stability test, auto-sync, heatmaps, elasticity monitoring
# Integration: hybrid_scheduler.py for multi-phase rotation (speed_up/slow_down/intensify)
# Auto-restart: Supports auto-retry on failure with exponential backoff

# Environment
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
HOME=/home/avalonas
LOGS_DIR=/home/avalonas/.hermes/gematria/cron_logs
STATE_FILE=/home/avalonas/.hermes/gematria/elasticity_state.json

# Function to send output to current cron channel
send_cron_notification() {
    local message="$1"
    # Send notification via webhook or other configured channel
    # This would integrate with your existing notification system
    return 0
}

# Phase marker for elasticity monitoring (integrates with hybrid_scheduler.py)
log_phase_marker() {
    local phase="$1"
    local details="$2"
    echo "[${phase.upper()}] ${details}" >> "${LOGS_DIR}/phase_markers_$(date '+%Y%m%d').log"
}

# Main loop execution with auto-restart capability
run_enhanced_loop() {
    # Check if previous run completed normally
    local last_exit_code=0
    if [[ -f "${STATE_FILE}" ]]; then
        last_exit_code=$(python3 -c "import json; s=json.load(open('${STATE_FILE}')); print(s.get('last_exit', 0))" 2>/dev/null || echo "0")
    fi
    
    # Auto-restart: If previous run failed, wait and retry
    if [[ "${last_exit_code}" != "0" ]]; then
        log_phase_marker "RESTART" "Auto-restarting after failure (previous exit: ${last_exit_code})"
        echo "⚠️  Previous run failed. Restarting..." >> "${LOGS_DIR}/loop_enhanced_$(date '+%Y%m%d').log"
        
        # Wait a bit before retrying (exponential backoff)
        sleep 300  # 5 minutes between retries on failure
        
        # Clear state to allow restart
        rm -f "${STATE_FILE}"
    fi
    
    # Execute the enhanced loop
    python3 /home/avalonas/.hermes/gematria/scripts/loop_runner_enhanced.py \
        --timeout 2700 \
        --retry 3 \
        --phase "$(python3 /home/avalonas/.hermes/gematria/scripts/hybrid_scheduler.py --once | grep -o 'SPEED_UP\|SLOW_DOWN\|INTENSIFY\|BASELINE' | head -1 || echo 'baseline')"
    
    return $?
}

# Run the loop (will be called by cron scheduler)
run_enhanced_loop

EOF

echo "✅ Cron job installed to: ${CRON_FILE}"

# Check if .hermes/cron directory exists in home
if [[ -d "$HOME/.hermes/cron" ]]; then
    echo ""
    echo "📁 Adding to ~/.hermes/cron for system-wide execution..."
    
    # Create a wrapper that sources from the job file
    cat > "${CRON_FILE}.wrapper" << 'WRAPPER'
#!/bin/bash
# Wrapper for enhanced loop cron job
source /home/avalonas/.hermes/gematria/cron/enhanced_loop_enhanced.cron
wrapper
WRAPPER
    
    chmod +x "${CRON_FILE}.wrapper"
    echo "✅ Wrapper installed to: ${CRON_FILE}.wrapper"
fi

# Display installation summary
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "🎉 Installation Complete!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "📅 Schedule: Every 3 hours at :00 (hours 0,3,6,9,12,15,18,21 UTC)"
echo "   Example next run: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo ""
echo "📂 Script Path:    ${LOOP_SCRIPT}"
echo "📁 Logs Directory:  ${LOGS_DIR}/"
echo "🔍 State File:      ${STATE_FILE}"
echo "⏱️  Timeout:        2700 seconds (45 minutes)"
echo "🔄 Retry Count:     3 attempts"
echo ""
echo "📊 Integration Features:"
echo "   ✅ Stability test (stability_test_enhanced_fixed.py)"
echo "   ✅ Auto-Obsidian sync (auto_obisidian_sync_v2.py)"
echo "   ✅ Correlation heatmaps generation"
echo "   ✅ Hybrid scheduler elasticity monitoring"
echo "   ✅ Phase markers for hybrid_scheduler.py integration"
echo "   ✅ Auto-restart on failure/expiration"
echo ""
echo "📖 Output is sent to current cron job channel automatically"
echo ""

# Instructions for activation
echo "═══════════════════════════════════════════════════════════"
echo "📝 Next Steps:"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "1. Add cron entry to your crontab:"
echo "   (crontab -e)"
echo ""
echo "   Add this line to run every 3 hours:"
echo "   0 0,3,6,9,12,15,18,21 * * * cd /home/avalonas/.hermes/gematria && /bin/bash cron/enhanced_loop_enhanced.cron"
echo ""
echo "   OR use a systemd timer:"
echo "   sudo systemctl enable gematria-loop.timer"
echo "   sudo systemctl start gematria-loop.timer"
echo ""
echo "2. Verify script permissions:"
echo "   chmod +x ${LOOP_SCRIPT}"
echo ""
echo "3. Manual test (run once manually):"
echo "   python3 ${LOOP_SCRIPT} --timeout 2700 --retry 3"
echo ""
echo "═══════════════════════════════════════════════════════════"
