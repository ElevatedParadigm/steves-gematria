#!/bin/bash
# Git Lock Monitor Shell Wrapper
# Usage: ./run_git_lock_monitor.sh [output_dir] [--db PATH] [-n|--dry-run]
# Cron example: */5 * * * * /path/to/run_git_lock_monitor.sh output >> /var/log/gematria/lock_monitor.log 2>&1

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GIT_LOCK_MONITOR="${SCRIPT_DIR}/git_lock_monitor.py"

# Default values
OUTPUT_DIR="${1:-output}"
DB_PATH=""
DRY_RUN=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        -n|--dry-run)
            DRY_RUN=true
            ;;
        --db=*)
            DB_PATH="${arg#--db=}"
            ;;
        *)
            # Positional argument (output directory) or ignore
            ;;
    esac
done

# Log to stderr for cron compatibility
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >&2
}

log "Git Lock Monitor starting..."
log "Output directory: ${OUTPUT_DIR:-output}"
log "Mode: $([ "$DRY_RUN" = true ] && echo 'DRY RUN' || echo 'LIVE')"

# Run the Python monitor
if [ -f "${GIT_LOCK_MONITOR}" ]; then
    python3 "${GIT_LOCK_MONITOR}" "${OUTPUT_DIR}" \
        ${DB_PATH:+--db="${DB_PATH}"} \
        ${DRY_RUN+--dry-run} || true
    EXIT_CODE=$?
    
    case $EXIT_CODE in
        0)
            log "No stale locks detected - output directory is clean"
            ;;
        1)
            log "Stale lock was detected and cleaned up successfully"
            ;;
        *)
            log "ERROR: Git lock monitor failed with exit code ${EXIT_CODE}"
            ;;
    esac
else
    log "ERROR: Python monitor script not found at ${GIT_LOCK_MONITOR}"
    exit 2
fi

log "Git Lock Monitor completed"

exit 0
