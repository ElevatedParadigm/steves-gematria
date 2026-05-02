#!/bin/bash
# =============================================================================
# Steve's Gematria - Manual Overnight Research Runner (SearXNG Pure Version)
# =============================================================================
# Usage: ./run_searxng_overnight.sh
# Purpose: Execute overnight research using local SearXNG container
# Container: searxng-clean (localhost:8084)
# Rate Limiting: Built-in 0.5s between queries to avoid rate limiting
# =============================================================================

set -e  # Exit on error

GEMATRIA_DIR="/home/avalonas/.hermes/gematria"
LOG_FILE="${GEMATRIA_DIR}/reports/cron.log"
REPORTS_DIR="${GEMATRIA_DIR}/reports"

echo "=== Gematria Overnight Research Runner ===" 
echo "Starting overnight research with SearXNG engine..."
echo ""

cd "${GEMATRIA_DIR}"

# Run the SearXNG engine (HTML scraping mode - no API key needed)
python scripts/searxng_engine.py 2>&1 | tee -a "${LOG_FILE}"

exit_code=${PIPESTATUS[0]}

if [ ${exit_code} -eq 0 ]; then
    echo ""
    echo "✅ Overnight research completed successfully!"
    echo "📄 Check the latest report:"
    ls -t ${REPORTS_DIR}/searxng_overnight_report_*.md | head -1
else
    echo ""
    echo "❌ Overnight research encountered errors. Check the log for details."
fi

echo ""
echo "=== End of Run ==="

exit 0
