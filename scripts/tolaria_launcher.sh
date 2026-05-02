#!/bin/bash
#===============================================================================
# 🔥 GEMATRIA OVERNIGHT RESEARCH - TOLARIA LAUNCHER
#===============================================================================
# Author: Steve & Avalon  
# Purpose: Launch overnight research with Docker health checks and fallback logic
# Version: 2.1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/logs/overnight_direct_scan.log"
API_KEY=""

# Load environment variables silently
if [ -f "$HOME/.hermes/.env" ]; then
    set -a; source $HOME/.hermes/.env; set +a
    if [ ! -z "$FIRECRAWL_API_KEY" ]; then
        API_KEY="$FIRECRAWL_API_KEY"
    fi
fi

echo ""
echo "============================================================"
echo "  🔥 GEMATRIA OVERNIGHT RESEARCH ENGINE"
echo "============================================================"
echo "  Launcher: Tolaria v2.1"
echo "============================================================"
echo ""

# Health check for containers
check_container() {
    local container=$1
    local port=$2
    if curl -s --max-time 2 "http://localhost:${port}/health" &>/dev/null; then
        echo "✅ $container: Running"
        return 0
    else
        echo "⚠️  $container: Not responding (using fallback mode)"
        return 1
    fi
}

echo "🔍 Checking Docker container health..."
check_container "firecrawl-api-1" 3002 || true

# Determine execution mode
if [ -n "$API_KEY" ]; then
    MODE="auto_fallback"
    echo ""
    echo "🎯 Mode: Auto fallback (local + direct web scraping)"
else
    MODE="direct"
    echo ""
    echo "🎯 Mode: Direct web research (no API key configured)"
fi

# Run main engine
echo ""
echo "⏳ Starting overnight research scan..."
echo ""

cd "$SCRIPT_DIR" && \
python3 direct_web_research.py >> "$LOG_FILE" 2>&1 || \
python3 scripts/overnight_research.py >> "$LOG_FILE" 2>&1 || {
    echo "❌ Research engine failed to start"
    exit 1
}

echo ""
echo "============================================================"
echo " ✅ SUCCESS: Overnight Research Complete!"
echo "📊 Log file: $LOG_FILE"
echo "============================================================"
echo ""
# tail -f "$SCRIPT_DIR/logs/*.log" # Optional: keep watching logs
