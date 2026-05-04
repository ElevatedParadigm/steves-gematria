#!/bin/bash
# 🌙 Steve's Gematria Unified Overnight Research Pipeline - Continuous Loop Mode
# Execute with flags: --name, --schedule "every 10m", --repeat 9999
# Features: Hidden layering, symbol-keying strategies, git version tracking, image-seed

set -e

REPO_PATH="/home/avalonas/.hermes/gematria/unified_overnight_research"
LOG_DIR="${REPO_PATH}/logs"
PID_FILE="${LOG_DIR}/pipeline.pid"

cd "${REPO_PATH}"

# Determine Python path (prefer venv)
PYTHON_CMD="python3"
if [[ -f "/home/avalonas/.hermes/hermes-agent/venv/bin/python" ]]; then
    PYTHON_CMD="/home/avalonas/.hermes/hermes-agent/venv/bin/python"
elif [[ -f "${REPO_PATH}/venv/bin/python" ]]; then
    PYTHON_CMD="${REPO_PATH}/venv/bin/python"
fi

echo "🌙 Steve's Gematria Unified Overnight Research Pipeline"
echo "📍 Repository: ${REPO_PATH}"
echo "🐍 Python: ${PYTHON_CMD}"
echo ""
echo "🔄 Starting continuous loop mode (repeat=9999)"
echo "🔮 Core symbols: 124, 666, 963, 55, 111, 279"
echo "⚡ Hidden layering: ENABLED for symbols 111, 279, 666"
echo "📝 Symbol-keying strategies: PRIMARY/MODERATE/AVERAGE/HIDDEN"
echo "💾 Git version tracking: ENABLED"
echo "🔗 Image-seed bootstrapping: ENABLED"
echo "⏰ Schedule: every 10 minutes"
echo ""

# Check for running process
if [[ -f "${PID_FILE}" ]]; then
    OLD_PID=$(cat "${PID_FILE}")
    if kill -0 "${OLD_PID}" 2>/dev/null; then
        echo "⚠️  Process already running (PID: ${OLD_PID})"
        exit 1
    else
        rm -f "${PID_FILE}"
        echo "🧹 Stale PID file removed"
    fi
fi

# Run the continuous loop with all required options
${PYTHON_CMD} scripts/overnight_research_loop.py --name unified-overnight \
    --schedule "every 10m" \
    --repeat 9999 \
    --enable-hidden-layering \
    --git-version-tracking \
    --symbol-keying-strategies \
    --image-seed

EXIT_CODE=$?

# Write PID file for tracking
if [[ ${EXIT_CODE} -eq 0 ]]; then
    echo $$ > "${PID_FILE}"
fi

exit ${EXIT_CODE}
