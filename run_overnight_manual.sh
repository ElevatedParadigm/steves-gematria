#!/bin/bash
# 🌙 GEMATRIA OVERNIGHT MANUAL RUNNER
# Run this script daily or via your preferred scheduler

set -e  # Exit on error

echo "=== 🌙 Gematria Overnight Research Started ==="
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Navigate to gematria directory
cd /home/avalonas/.hermes/gematria

# Run overnight research
python scripts/overnight_research.py

# Check exit status
if [ $? -eq 0 ]; then
    echo ""
    echo "=== ✅ Overnight Research Completed Successfully ==="
    
    # Log completion time
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Daily research completed" >> logs/daily_summary.log
    
else
    echo ""
    echo "=== ❌ Overnight Research Failed ===" >&2
    exit 1
fi

echo ""
echo "Database entries updated. See: gematria_database.json"
echo "Log files in: logs/"
