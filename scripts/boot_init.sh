#!/bin/bash
# Gematria Opponent System - Boot Init Script
# Starts the adversarial research loop automatically after reboot

set -e

SCRIPT_DIR="/home/avalonas/.hermes/gematria/scripts"
LOG_FILE="/var/log/hermes/gematria-opponent.log"

echo "[GEMATRIA] Starting adversarial research opponent system..."

cd "$SCRIPT_DIR"
nohup python3 opponent_system.py --mode continuous > "$LOG_FILE" 2>&1 &

PID=$!
echo $PID > /tmp/hermes-gematria-pid

echo "[GEMATRIA] Opponent system started (PID: $PID)"

# Set up systemd service wrapper for persistence
systemctl enable hermes-gematria-opponent.service 2>/dev/null || true
systemctl restart hermes-gematria-opponent.service 2>/dev/null || true

echo "[GEMATRIA] ✓ Opponent system auto-start configured"
exit 0
