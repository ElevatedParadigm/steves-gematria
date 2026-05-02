#!/bin/bash
# Automated Daily Anomaly Detection Script
# Run via cron: 0 3 * * * /home/avalonas/.hermes/gematria/scripts/auto_anomaly_detection.sh
# Logs output to: ~/logs/anomaly-detection.log

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${HOME}/.hermes/logs/anomaly-detection.log"
OUTPUT_DIR="${HOME}/.hermes/gematria/anomaly_reports"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting anomaly detection..." | tee -a "$LOG_FILE"

# Check dependencies
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 not found!" | tee -a "$LOG_FILE"
    exit 1
fi

if ! [ -f "${SCRIPT_DIR}/auto_anomaly_detection.py" ]; then
    echo "[ERROR] Script not found: auto_anomaly_detection.py" | tee -a "$LOG_FILE"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Run detection script
python3 "${SCRIPT_DIR}/auto_anomaly_detection.py" 2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "[SUCCESS] Anomaly detection completed successfully" | tee -a "$LOG_FILE"
else
    echo "[WARNING] Anomaly detection completed with exit code: $EXIT_CODE" | tee -a "$LOG_FILE"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Finished anomaly detection" | tee -a "$LOG_FILE"

exit 0
