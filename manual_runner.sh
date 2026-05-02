#!/bin/bash
# Manual Runner for Enhanced Overnight Research Protocol
# Supports both stability tests and normal overnight runs

SCRIPTS_DIR="/home/avalonas/.hermes/gematria/scripts"
LOGS_DIR="/home/avalonas/.hermes/gematria/cron_logs"
DATABASE="/home/avalonas/.hermes/gematria/database/gematria_database.json"
MAX_TIMEOUT=${1:-2700}  # Default: 45 minutes (production range), override with arg

echo "=========================================="
echo "🌙 Overnight Research Protocol - Manual Runner"
echo "=========================================="
echo "Timeout Budget: ${MAX_TIMEOUT}s ($(python3 -c "print(f'{self.MAX_TIMEOUT/60:.1f} minutes')") minutes)"
echo "Logs Directory: ${LOGS_DIR}"
echo "=========================================="
echo ""

# Run stability test for extended timeout verification (recommended first run)
echo "🧪 Running Stability Test First..."
python3 "${SCRIPTS_DIR}/stability_test_enhanced_fixed.py" --timeout ${MAX_TIMEOUT}

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Stability test passed!"
    echo ""
    echo "=========================================="
    echo "🌙 Overnight Research Protocol - Complete!"
    echo "=========================================="
    echo ""
    
    # Generate summary report
    python3 "${SCRIPTS_DIR}/auto_obisidian_sync_v2.py" --mode "overnight-completion"
    
else
    echo ""
    echo "❌ Stability test failed. Check logs in ${LOGS_DIR}/"
fi
