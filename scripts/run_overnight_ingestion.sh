#!/bin/bash
# STEVE'S GEMATRIA - Overnight Multi-Source Ingestion Pipeline
# Runs at 3:00 AM automatically to scan expanded news sources and RSS feeds
# Author: Hermes Autonomous Research System
# Date: April 26, 2026

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKING_DIR="/home/avalonas/.hermes/gematria"
LOG_FILE="${WORKING_DIR}/logs/${YEAR}-${MONTH}-${DAY}_ingestion.log"
REPORT_DIR="${WORKING_DIR}/batch_reports"

# Create directories if they don't exist
mkdir -p "${WORKING_DIR}/logs"
mkdir -p "${REPORT_DIR}"

echo "=================================================="
echo "🚀 STEVE'S GEMATRIA - Overnight Ingestion Pipeline"
echo "=================================================="
echo "Working directory: ${WORKING_DIR}"
echo "Log file: ${LOG_FILE}"
echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S UTC')"
echo ""

# Run the unified ingestion orchestrator
cd "${WORKING_DIR}"

python3 scripts/unified_ingestion_orchestrator.py 2>&1 | tee "${LOG_FILE}"

EXIT_CODE=$?

if [ ${EXIT_CODE} -eq 0 ]; then
    echo ""
    echo "=================================================="
    echo "✅ Overnight ingestion pipeline completed successfully!"
    echo "=================================================="
else
    echo ""
    echo "=================================================="
    echo "❌ Overnight ingestion pipeline failed with exit code: ${EXIT_CODE}"
    echo "=================================================="
fi

# Send notification if needed (can enable Telegram/webhook)
# curl -X POST https://your-webhook-url.com/ingestion-status \
#     -H "Content-Type: application/json" \
#     -d "{\"status\": \"${EXIT_CODE}\", \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"

exit ${EXIT_CODE}
