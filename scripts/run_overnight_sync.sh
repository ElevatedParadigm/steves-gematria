#!/bin/bash
# Steve's Gematria - Manual Runner Script
# Execute manually at preferred times, or schedule via /usr/lib/python3/cron/daily/etc.

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
LOG_FILE="/home/avalonas/.hermes/gematria/logs/sync.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "============================================================" | tee -a "$LOG_FILE"
echo "🌉 GEMATRIA OVERNIGHT SYNC STARTED [$TIMESTAMP]" | tee -a "$LOG_FILE"
echo "============================================================" | tee -a "$LOG_FILE"

cd "$SCRIPT_DIR/.." || exit 1

# Run the overnight research script
python scripts/auto_obisidian_sync_v2.py

EXIT_CODE=$?

echo "" | tee -a "$LOG_FILE"
echo "============================================================" | tee -a "$LOG_FILE"
echo "🌉 Overnight Sync Completed [$TIMESTAMP]" | tee -a "$LOG_FILE"
echo "Exit Code: $EXIT_CODE" | tee -a "$LOG_FILE"
echo "============================================================" | tee -a "$LOG_FILE"

if [ $EXIT_CODE -eq 0 ]; then
    echo "✨ Success! Reports generated in obsidian_exports/" >> "$LOG_FILE"
else
    echo "⚠️  Errors occurred. Check logs: cat $LOG_FILE | grep -i error" >> "$LOG_FILE"
fi

exit $EXIT_CODE
