#!/bin/bash
# Uninstallation Script: Remove Gematria Overnight Research Cron Job
# This script removes the overnight research cron job from your crontab
# Usage: ./scripts/remove_cron.sh

echo "🌹 Removing Steve's Gematria Overnight Research Protocol..."
echo ""
echo "This will remove the cron job that runs at 3:00 AM daily:"
echo "  Command: cd /home/avalonas/.hermes/gematria && ./scripts/run_overnight_sync.sh"
echo ""
echo "Current time: $(date)"
echo ""

# Create a temporary file with crontab minus gematria entries
TEMP_FILE=$(mktemp)
crontab -l 2>/dev/null | grep -v "gematria-overnight\|run_overnight_sync" > "$TEMP_FILE"

# Write back to main crontab (empty if nothing left)
if [ -s "$TEMP_FILE" ]; then
    cat "$TEMP_FILE" > -
else
    echo "# Crontab is now empty" > -
fi

# Clean up temp file
rm -f "$TEMP_FILE"

echo ""
echo "✅ Cron job removed successfully!"
echo ""
echo "To verify it's gone, run:"
echo "  crontab -l | grep gematria"
echo ""
