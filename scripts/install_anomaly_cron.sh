#!/bin/bash
# Install Automated Anomaly Detection Cron Job
# Usage: ./install_anomaly_cron.sh
# This will set up daily 3 AM anomaly detection

set -e  # Exit on error

echo "=============================================="
echo "Install Automated Anomaly Detection Crontab"
echo "=============================================="
echo ""

# Define paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRONTAB_FILE="/home/avalonas/.hermes/gematria/crontab.gematria-anomaly"
CURRENT_CRONTAB="$HOME/.crontab.bak.$(date +%Y%m%d_%H%M%S)"

echo "📝 Current crontab backup location: $CURRENT_CRONTAB"
echo ""

# Backup current crontab if it exists
if [ -f "$HOME/.crontab" ]; then
    echo "💾 Backing up existing crontab..."
    cp "$HOME/.crontab" "$CURRENT_CRONTAB"
    echo "   ✓ Backup saved to: $CURRENT_CRONTAB"
else
    echo "ℹ️  No existing crontab found (this is OK)"
fi

echo ""
echo "📋 Crontab content to install:"
echo "-------------------------------------------"

# Show the crontab that will be installed
cat "$CRONTAB_FILE" | grep "^#" || true
echo ""
echo "# Option 1: Daily at 3 AM (recommended)"
echo "0 3 * * * cd /home/avalonas/.hermes/gematria && python3 scripts/test_anomaly_detection.py >> ~/.hermes/logs/anomaly-detection.log 2>&1"
echo "-------------------------------------------"

echo ""
read -p "Install this crontab? (y/N): " confirm

if [[ "$confirm" =~ ^[Yy]$ ]]; then
    echo ""
    echo "✅ Installing crontab..."
    
    # Install crontab
    crontab "$CRONTAB_FILE" 2>/dev/null || {
        # If direct install fails, add line manually
        echo "0 3 * * * cd /home/avalonas/.hermes/gematria && python3 scripts/test_anomaly_detection.py >> ~/.hermes/logs/anomaly-detection.log 2>&1" >> "$HOME/.crontab"
        
        if [ ! -f "$HOME/.crontab.bak.$(date +%Y%m%d_%H%M%S)" ]; then
            echo "💾 Also backed up to: $CURRENT_CRONTAB"
        fi
    }
    
    # Verify installation
    echo ""
    echo "📋 Installed crontab:"
    crontab -l
    
    echo ""
    echo "✅ Crontab installed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Check logs after first run: tail -f ~/.hermes/logs/anomaly-detection.log"
    echo "2. View reports in: ~/.hermes/gematria/anomaly_reports/"
    echo "3. To remove later: crontab -e  (then delete the anomaly line)"
    
else
    echo ""
    echo "❌ Crontab installation cancelled"
    echo ""
    echo "To install manually, run:"
    echo "  crontab /home/avalonas/.hermes/gematria/crontab.gematria-anomaly"
fi

echo ""
echo "=============================================="
echo "Cron Installation Complete"
echo "=============================================="
