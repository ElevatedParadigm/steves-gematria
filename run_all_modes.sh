#!/bin/bash
# STEVE'S GEMATRIA — All Tasks Runner Script
# Usage: ./run_all_modes.sh [mode]

cd /home/avalonas/.hermes/gematria

case "${1:-all}" in
    overnight)
        echo "🌙 Starting overnight research..."
        python scripts/orchestrator_standalone.py
        ;;
    hourly)
        echo "⏰ Starting hourly sync..."
        python scripts/auto_obisidian_sync_v2.py
        ;;
    pattern)
        echo "🔍 Starting pattern scan..."
        python scripts/orchestrator_standalone.py --mode pattern
        ;;
    health)
        echo "✅ Running health check..."
        python scripts/scheduler.py --immediate --health
        ;;
    all)
        echo "🚀 Running ALL tasks immediately..."
        python scripts/scheduler.py --immediate
        ;;
esac
