#!/bin/bash
# Installation Script: Install Gematria Overnight Research Cron Job
# This script adds the overnight research cron job to your crontab
# Usage: ./scripts/install_cron.sh

echo "🌉 Installing Steve's Gematria Overnight Research Protocol..."
echo ""
echo "This will add a cron job to run at 3:00 AM daily:"
echo "  Command: cd /home/avalonas/.hermes/gematria && ./scripts/run_overnight_sync.sh"
echo "  Log file: /home/avalonas/.hermes/gematria/logs/sync.log"
echo ""
echo "Current time: $(date)"
echo ""

# Create cron entry with proper escaping
CRON_ENTRY="0 3 * * * cd /home/avalonas/.hermes/gematria && ./scripts/run_overnight_sync.sh >> /home/avalonas/.hermes/gematria/logs/sync.log 2>&1"

# Check if this crontab entry already exists to avoid duplicates
if crontab -l | grep -q "gematria-overnight"; then
    echo "⚠️ Cron job for gematria-overnight already exists. Removing it first..."
    crontab -l | grep -v "gematria-overnight" > /tmp/crontab_temp.$$
    mv /tmp/crontab_temp.$$ -
    echo ""
fi

# Add the new cron entry
echo "$CRON_ENTRY" >> ~/.crontab.gematria-overnight

# Now merge it into current crontab
CURRENT_CRONTAB=$(crontab -l 2>/dev/null || true)

if [ -n "$CURRENT_CRONTAB" ]; then
    # Combine existing crontab with new entry
    printf "%s\n%s\n" "$CURRENT_CRONTAB" "$CRON_ENTRY" > ~/.crontab.gematria-overnight.new
else
    # First time user, just use the new entry
    mv ~/.crontab.gematria-overnight ~/.crontab.gematria-overnight.new
fi

# Write to main crontab
cat ~/.crontab.gematria-overnight > -
rm -f ~/.crontab.gematria-overnight* 2>/dev/null

echo ""
echo "✅ Cron job installed successfully!"
echo ""
echo "To verify, run:"
echo "  crontab -l | grep gematria"
echo ""
echo "To remove this cron job later, run:"
echo "  ./scripts/remove_cron.sh"
echo ""
