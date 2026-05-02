#!/bin/bash
# Install hourly overnight research cron job
# Usage: sudo ./install_hourly_cron.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRON_FILE="/etc/crontab"
LOG_DIR="${SCRIPT_DIR}/logs"

echo "=== Installing Hourly Overnight Research Cron ==="

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Check if crontab file exists
if [ ! -f "$CRON_FILE" ]; then
    echo "ERROR: /etc/crontab not found!"
    exit 1
fi

# Add hourly cron entry (append if doesn't exist, or replace existing overnight entry)
if grep -q "run_overnight_research.sh" "$CRON_FILE"; then
    echo "Removing existing overnight research entry from crontab..."
    sed -i '/run_overnight_research.sh/d' "$CRON_FILE"
fi

# Append hourly cron entry
echo "0 * * * * /home/avalonas/.hermes/gematria/scripts/run_overnight_research.sh >> /home/avalonas/.hermes/gematria/logs/cron_hourly.log 2>&1" >> "$CRON_FILE"

echo "✓ Cron job installed to /etc/crontab"
echo ""
echo "=== To verify installation: ==="
echo "sudo crontab -l | grep overnight"
echo ""
echo "=== To view logs in real-time: ==="
echo "tail -f /home/avalonas/.hermes/gematria/logs/cron_hourly.log"
echo ""
echo "=== To run manually now (for immediate test): ==="
echo "/home/avalonas/.hermes/gematria/scripts/run_overnight_research.sh"
