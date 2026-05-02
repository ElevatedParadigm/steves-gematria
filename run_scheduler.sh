#!/bin/bash
# STEVE'S GEMATRIA — Scheduler Runner Script
# Usage: ./run_scheduler.sh [mode] [--immediate]

cd /home/avalonas/.hermes/gematria

MODE=${1:-all}
IMMEDIATE=false

if [[ "$2" == "--immediate" ]]; then
    IMMEDIATE=true
fi

case $MODE in
    overnight)
        echo "🌙 Running Overnight Research..."
        python scripts/scheduler.py --mode overnight
        ;;
    hourly)
        echo "⏰ Running Hourly Sync..."
        python scripts/scheduler.py --mode hourly
        ;;
    pattern)
        echo "🔍 Running Pattern Scan..."
        python scripts/scheduler.py --mode pattern
        ;;
    health)
        echo "✅ Running Health Check..."
        python scripts/scheduler.py --immediate --health
        ;;
    all | *)
        if [[ "$IMMEDIATE" == "true" ]]; then
            echo "🚀 Running ALL tasks immediately..."
            python scripts/scheduler.py --immediate
        else
            echo "🔄 Starting scheduler (background mode)..."
            echo "Press Ctrl+C to stop"
            python scripts/scheduler.py
        fi
        ;;
esac
