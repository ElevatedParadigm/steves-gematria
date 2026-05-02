#!/bin/bash
# Overnight Research Protocol - Cron Job Runner
# Auto-restarts on research cycle expiration
# Runs every 3 hours (can be modified)

SCRIPTS_DIR="/home/avalonas/.hermes/gematria/scripts"
LOGS_DIR="/home/avalonas/.hermes/gematria/cron_logs"
INTERVAL=10800  # 3 hours in seconds (default), can be overridden via env

# Ensure logs directory exists
mkdir -p "$LOGS_DIR"

# Check if python script exists
if [ ! -f "${SCRIPTS_DIR}/loop_runner.py" ]; then
    echo "❌ Error: loop_runner.py not found"
    exit 1
fi

echo "🌙 Overnight Research Protocol Starting..."
echo "Interval: $INTERVAL seconds ($(python3 -c "print(f'{self.INTERVAL/3600:.1f}')") hours)"

# Run the loop runner in background with interval control
python3 "${SCRIPTS_DIR}/loop_runner.py" --interval "$INTERVAL" &

# Capture process ID
RUNNER_PID=$!

echo "📋 Cron job started with PID: $RUNNER_PID"
echo "📁 Log directory: $LOGS_DIR"

# Keep track of runner for auto-restart capability
# The loop_runner.py handles its own restart logic internally

# This cron job will exit after starting the process
# The main loop continues running in background
exit 0
