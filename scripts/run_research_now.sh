#!/bin/bash
###############################################################################
# Steve's Gematria - Research Runner (For Flexible Scheduling)
# Use after "goodnight" command or set to run at specific times
###############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs"
mkdir -p "$LOG_DIR"  # Ensure logs directory exists
LOG_FILE="${LOG_DIR}/research.log"
START_TIME=$(date "+%Y-%m-%d %H:%M:%S")

echo "=== Steve's Gematria Research Started: $START_TIME ===" >> "$LOG_FILE"

cd "${SCRIPT_DIR}"

# Run overnight research with Firecrawl and analysis
python scripts/overnight_research.py >> "${LOG_FILE}" 2>&1

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    END_TIME=$(date "+%Y-%m-%d %H:%M:%S")
    echo "✅ Research completed successfully at ${END_TIME}" >> "$LOG_FILE"
    echo "✓ Overnight analysis complete. Core symbols tracked: 124, 963, 55, 111, 279, 666" >> "$LOG_FILE"
else
    END_TIME=$(date "+%Y-%m-%d %H:%M:%S")
    echo "❌ Research failed with exit code ${EXIT_CODE} at ${END_TIME}" >> "$LOG_FILE"
    echo "Check logs for details: ${SCRIPT_DIR}/logs/research.log" >> "$LOG_FILE"
fi

# Sync to Obsidian if auto-sync is enabled
if [ -f "scripts/auto_obisidian_sync_v2.py" ]; then
    python scripts/auto_obisidian_sync_v2.py >> "${LOG_FILE}" 2>&1
fi

exit $EXIT_CODE
