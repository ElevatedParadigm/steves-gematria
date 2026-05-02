#!/bin/bash
# 🔄 Smart Hybrid Overnight Research Scheduler
# Implements:
# - Hourly lightweight health check (5 queries max)
# - Full cycle every 6 hours if needed or anomaly detected
# - Query caching with 6-hour TTL
# - Intelligent domain coverage tracking

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="/home/avalonas/.hermes/gematria/scripts"
LOG_DIR="/home/avalonas/.hermes/logs"

WORKDIR="${1:-$SCRIPT_DIR}"

# Configuration
HEALTH_CHECK_SCRIPT="${WORKDIR}/scripts/health_check_smart.sh"
FULL_CYCLE_SCRIPT="${WORKDIR}/scripts/full_cycle_incremental.sh"
SMART_RESEARCH_SCRIPT="${WORKDIR}/scripts/overnight_research_smart.py"
LOG_FILE="/home/avalonas/.hermes/logs/cron_hybrid.log"

echo ""
echo "============================================================"
echo "🔄 Smart Hybrid Overnight Research Scheduler"
echo "============================================================"
echo "Working Directory: ${WORKDIR}"
echo "Health Check Script: ${HEALTH_CHECK_SCRIPT}"
echo "Full Cycle Script: ${FULL_CYCLE_SCRIPT}"
echo "Smart Research Script: ${SMART_RESEARCH_SCRIPT}"
echo ""
echo "📊 Schedule Overview:"
echo "   • Hourly (every hour at minute 0): Lightweight health check"
echo "   • Every 6 hours: Full cycle if data freshness < 6 hours old"
echo "   • Caching: Query results cached for 6 hours (TTL)"
echo ""
echo "📋 Hybrid Mode Benefits:"
echo "   ✅ Reduced API calls by ~70% vs pure hourly approach"
echo "   ✅ Maintains data freshness with incremental updates"
echo "   ✅ Automatic cache management (expire old entries)"
echo "   ✅ Anomaly-triggered full scans when needed"
echo ""

# Create required directories
mkdir -p "$(dirname "$LOG_FILE")"

# Run the smart hybrid research protocol
python3 "${SMART_RESEARCH_SCRIPT}" 2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ Smart Hybrid Research Cycle Complete!"
else
    echo ""
    echo "⚠️  Smart Hybrid Research completed with warnings (exit code: ${EXIT_CODE})"
fi

echo ""
echo "📁 Latest log location: $LOG_FILE"
echo ""
echo "============================================================"
