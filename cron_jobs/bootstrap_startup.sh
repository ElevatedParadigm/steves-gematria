#!/bin/bash
# Startup Cron for Overnight Research Protocol
# Runs at system boot to initialize gematria database analysis loops

BASE_PATH="/home/avalonas/.hermes/gematria"
LOGS_DIR="$BASE_PATH/cron_logs"

mkdir -p "$LOGS_DIR"

# Log startup
echo "$(date '+%Y-%m-%d %H:%M:%S') === Overnight Research Protocol Started ===" >> "$LOGS_DIR/startup.log"

# Run stability test on gematria database
python3 "$BASE_PATH/scripts/stability_test_enhanced_fixed.py" --timeout 2700 > "$LOGS_DIR/stability_bootstrap.log" 2>&1

if [ $? -eq 0 ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') ✅ Stability test completed at boot" >> "$LOGS_DIR/startup.log"
    
    # Run auto-sync to Obsidian
    python3 "$BASE_PATH/scripts/auto_obisidian_sync_v2.py" > "$LOGS_DIR/sync_bootstrap.log" 2>&1
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') ✅ Auto-sync completed at boot" >> "$LOGS_DIR/startup.log"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') ⚠️ Bootstrap stability test failed, will retry on next scheduled run" >> "$LOGS_DIR/startup.log"
fi

echo "" >> "$LOGS_DIR/startup.log"
echo "==========================================" >> "$LOGS_DIR/startup.log"
