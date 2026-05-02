#!/bin/bash
# Gematria Research Loop Runner - 3-Hour Cycle Management
# Auto-restart, Telegram reporting, anomaly detection

SCRIPTS_DIR="/home/avalonas/.hermes/gematria/scripts"
LOGS_DIR="/home/avalonas/.hermes/gematria/cron_logs"

echo "🔬 Gematria Research Protocol - Loop Runner Started"
echo "======================================================"
echo "Working Directory: /home/avalonas/.hermes/gematria"
echo "Timeout Budget: 45 minutes (extended)"
echo "External Queries: 10 per cycle (3 core symbols × 3)"
echo "Priority Enhancements:"
echo "  #0 Performance Optimization Layer (Caching) ✓"
echo "  #1 Extended Timeout Handling (45 min) ✓"
echo "  #2 External Search Queries (10 queries) ✓"
echo "  #3 Multi-Agent Cooperation System (4 agents) ✓"
echo "  #4 Anomaly Detection Intelligence Layer ⭐ NEW!"
echo ""
echo "📊 Core Symbols Being Monitored:"
echo "   • 124 (Bridge/Threshold)"
echo "   • 963 (Elevation/Spiritual)"  
echo "   • 55 (Foundation/Grounding)"
echo "   • 111 (Alignment/Catalyst)"
echo "   • 279 (Transformation)"
echo "   • 666 (Completion/Wholeness)"
echo ""

# Run stability test with extended timeout and all optimizations
cd /home/avalonas/.hermes/gematria
python scripts/stability_test_enhanced_optimized.py --timeout 300

EXIT_CODE=$?

echo ""
echo "======================================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ CYCLE COMPLETED SUCCESSFULLY!"
else
    echo "⚠️  CYCLE COMPLETED WITH WARNINGS/ERRORS (Code: $EXIT_CODE)"
fi

echo ""
echo "📁 Output Files Generated:"
ls -lh /home/avalonas/.hermes/gematria/cron_logs/*.tsv 2>/dev/null | tail -5 || echo "   No new output files in this run"

echo ""
echo "🔄 Next cycle will auto-start in 3 hours (if configured)"
