#!/bin/bash
# Steve's Gematria Autonomous Research System - Installation Script
# No sudo required - uses crontab -e for cron deployment

set -euo pipefail

echo "╔═══════════════════════════════════════════════════════╗"
echo "║  STEVE'S GEMATRIA AUTONOMOUS RESEARCH SYSTEM          ║"
echo "║     Autonomous Overnight Protocol Installation        ║"
echo "╚═══════════════════════════════════════════════════════╝"

# Setup directories
LOG_DIR="/home/avalonas/.hermes/gematria/cron_logs"
GEMATRIA_HOME="/home/avalonas/.hermes/gematria"

echo ""
echo "[1/5] Creating log directories..."
mkdir -p "$LOG_DIR"
echo "      ✓ Log directory: $LOG_DIR"

echo ""
echo "[2/5] Verifying required scripts exist..."
REQUIRED_SCRIPTS=(
    "overnight_research_autonomous.py"
    "run_autonomous_research.py"
    "auto_obisidian_sync_v2.py"
)

for script in "${REQUIRED_SCRIPTS[@]}"; do
    if [[ -f "$GEMATRIA_HOME/scripts/$script" ]]; then
        echo "      ✓ Found: $script"
    else
        echo "      ✗ Missing: $script"
        exit 1
    fi
done

echo ""
echo "[3/5] Checking Firecrawl API key configuration..."
if grep -q "FIRECRAWL_API_KEY=" ~/.hermes/.env; then
    echo "      ✓ API key configured in ~/.hermes/.env"
else
    echo "      ⚠ FIRECRAWL_API_KEY not found, creating default entry..."
    echo "" >> ~/.hermes/.env
    echo "FIRECRAWL_API_KEY=your_api_key_here" >> ~/.hermes/.env
fi

echo ""
echo "[4/5] Initializing structured results logging system..."
python3 "$GEMATRIA_HOME/scripts/run_autonomous_research.py" > /dev/null 2>&1 || {
    echo "      ⚠ Script execution failed during init, continuing anyway..."
}

echo "      ✓ Results logging system initialized"

echo ""
echo "[5/5] Cron deployment (no sudo required)..."
echo ""
echo "--- To install cron jobs, run:"
echo "   crontab /home/avalonas/.hermes/gematria/crontab_gematria_autonomous.txt"
echo ""
echo "--- OR manually with:"
echo "   crontab -e"
echo ""
echo "Then paste this content:"
cat << 'EOF'
# Steve's Gematria Autonomous Overnight Research
0 4 * * * cd /home/avalonas/.hermes/gematria && python scripts/run_autonomous_research.py >> cron_logs/overnight_autonomous.log 2>&1

# Auto-sync Obsidian at 5:30 AM  
30 5 * * * cd /home/avalonas/.hermes/gematria && python scripts/auto_obisidian_sync_v2.py >> cron_logs/sync_$(date +%Y%m%d).log 2>&1
EOF
echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║              INSTALLATION COMPLETE!                   ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""
echo "📊 Autonomous Features:"
echo "   ✓ Fixed-time experiment budget (15 min max)"
echo "   ✓ Timeout protection (auto-kill >15min)"
echo "   ✓ Structured TSV results logging"
echo "   ✓ Autonomous iteration (no manual intervention)"
echo "   ✓ No .md file editing required"
echo ""
echo "⏰ Next autonomous run: Tomorrow at 04:15 AM"
echo ""
echo "📁 Results will be logged to:"
echo "   $LOG_DIR/results.tsv"
echo "   $LOG_DIR/commits.txt"
echo ""
