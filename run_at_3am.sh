#!/bin/bash
# STEVE'S GEMATRIA — Overnight Research Runner (No sudo required)
# Runs overnight research at 3:00 AM
# Usage: Run this script at 3 AM via cron or manual execution

cd /home/avalonas/.hermes/gematria

echo "[STEVE'S GEMATRIA] Starting overnight research..."
python scripts/orchestrator_standalone.py
