#!/bin/bash
# Overnight Research Scanner - Hybrid Training + Automated Scanning
# ~/.hermes/gematria/cron/overnight_research.sh

# Simple wrapper for cron deployment (no sudo required)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKING_DIR="$HOME/.hermes/gematria/scripts"
REPORTS_DIR="$HOME/.hermes/gematria/reports"
JSON_REPORTS_DIR="$HOME/.hermes/gematria/json_reports"
DB_PATH="$HOME/.hermes/gematria/database/gematria_database.json"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting overnight research scan..."
echo "   Training patterns loaded from database"
echo "   Scanning for: 124, 666 (detected), and training to find: 55, 963, 111, 279"

python3 "$WORKING_DIR/overnight_research.py" "$REPORTS_DIR" "$JSON_REPORTS_DIR" "$DB_PATH"

if [ $? -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Scan complete. Reports generated in: $REPORTS_DIR"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Scan completed with errors."
fi
