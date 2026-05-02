#!/bin/bash
# Overnight Research Runner - Handles logging, timeout protection, and auto-recovery
# Usage: /home/avalonas/.hermes/gematria/scripts/run_overnight_research.sh

set -e  # Exit on error

WORKDIR="/home/avalonas/.hermes/gematria"
SCRIPT_PATH="${WORKDIR}/scripts/overnight_research.py"
LOG_FILE="${WORKDIR}/logs/overnight_cron.log"
LOCK_FILE="${WORKDIR}/.overnight_running.lock"

echo "$(date '+%Y-%m-%d %H:%M:%S') | Starting overnight research..." | tee -a "$LOG_FILE"

# Acquire lock to prevent concurrent runs
if [ -f "$LOCK_FILE" ]; then
    echo "OVERNIGHT RESEARCH IS ALREADY RUNNING!" | tee -a "$LOG_FILE"
    exit 1
fi
echo $$ > "$LOCK_FILE"

trap 'rm -f "$LOCK_FILE"' EXIT

# Run the overnight research protocol with timeout protection
cd "$WORKDIR"
timeout 420 python "${SCRIPT_PATH}" --cycle-count 1 2>&1 | tee -a "$LOG_FILE"

exit_code=$?

if [ $exit_code -eq 124 ]; then
    echo "TIMED OUT: Overnight research exceeded grace period (7 minutes). Terminating." | tee -a "$LOG_FILE"
    # Optionally send alert here if Telegram configured
elif [ $exit_code -ne 0 ]; then
    echo "FAILED with exit code ${exit_code}" | tee -a "$LOG_FILE"
else
    echo "COMPLETED SUCCESSFULLY" | tee -a "$LOG_FILE"
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') | Overnight research finished (exit code: ${exit_code})" | tee -a "$LOG_FILE"

# Log to database for tracking
python -c "
import json
from pathlib import Path
db_path = Path.home() / '.hermes' / 'gematria' / 'database' / 'gematria_database.json'
try:
    with open(db_path) as f:
        data = json.load(f)
    
    entry = {
        'cron_job': True,
        'exit_code': exit_code,
        'timestamp': datetime.now().isoformat(),
        'status': 'success' if exit_code == 0 else 'failed',
        'output_tail': None  # Would need to capture stdout for full logging
    }
    
    data['config']['last_cron_run'] = entry
    with open(db_path, 'w') as f:
        json.dump(data, f, indent=2)
except Exception as e:
    print(f'Warning: Could not update cron tracking: {e}')
"
