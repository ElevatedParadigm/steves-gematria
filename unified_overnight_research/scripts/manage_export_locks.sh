#!/bin/bash
# =============================================================================
# Visual Archive Export Lock Manager - Shell Wrapper Script
# =============================================================================
# Usage:
#   ./manage_export_locks.sh check       # Check for lock files before export
#   ./manage_export_locks.sh cleanup     # Remove stale locks
#   ./manage_export_locks.sh safe-cleanup  # Safe cleanup with verification
#   ./manage_export_locks.sh health      # Health check
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="/home/avalonas/.hermes/gematria/unified_overnight_research/scripts/manage_export_locks.py"

# Configuration
LOCK_CHECK_INTERVAL="${LOCK_CHECK_INTERVAL:-15}"  # minutes before export
LOG_FILE="${LOG_FILE:-/home/avalonas/.hermes/cron/output/export-locks.log}"

usage() {
    cat << EOF
Usage: $0 {check|cleanup|safe-cleanup|health} [options]

Commands:
  check              Check for .git/index.lock files before export
  cleanup           Remove stale lock files (direct deletion)
  safe-cleanup      Safe cleanup with git verification and integrity check
  health            Perform full health check of lock management system

Options:
  -s, --subdir DIR   Specific output subdirectory (default: all)
  -v, --verbose      Enable verbose output
  -d, --dry-run      Show what would be done without making changes

Examples:
  $0 check                        # Check for locks in entire output/
  $0 check -s visual_archive      # Check only in visual_archive subdirectory
  $0 safe-cleanup -s visual_archive  # Safe cleanup with verification
  $0 health -v                   # Verbose health check

Cron Integration:
  See /home/avalonas/.hermes/gematria/unified_overnight_research/cron_export_locks
  
EOF
    exit 1
}

# Parse arguments
COMMAND=""
SUBDIR=""
VERBOSE=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        check|cleanup|safe-cleanup|health)
            COMMAND=$1
            ;;
        -s|--subdir)
            SUBDIR="$2"
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            ;;
        -d|--dry-run)
            DRY_RUN=true
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage
            ;;
    esac
    shift 2>/dev/null || shift
done

# Validate command
if [[ -z "$COMMAND" ]]; then
    usage
fi

# Validate Python script exists
if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    echo "ERROR: Python script not found: $PYTHON_SCRIPT" >&2
    exit 1
fi

# Change to base directory and run Python script
cd /home/avalonas/.hermes/gematria/unified_overnight_research

# Build command arguments
ARGS=""
if [[ -n "$SUBDIR" ]]; then
    ARGS="--subdir $SUBDIR"
fi

if [[ "$VERBOSE" == true ]]; then
    export VERBOSE=true
fi

case $COMMAND in
    check)
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Checking for lock files..."
        python3 "$PYTHON_SCRIPT" check $ARGS
        
        if [[ $? -eq 0 ]]; then
            echo "✅ Lock check completed successfully"
        else
            echo "⚠️  Lock check completed with warnings"
            exit 1
        fi
        ;;
        
    cleanup)
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Cleaning up stale lock files..."
        python3 "$PYTHON_SCRIPT" cleanup $ARGS
        
        if [[ $? -eq 0 ]]; then
            echo "✅ Cleanup completed successfully"
        else
            echo "⚠️  Cleanup completed with warnings"
            exit 1
        fi
        ;;
        
    safe-cleanup)
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Running safe cleanup with verification..."
        python3 "$PYTHON_SCRIPT" safe-cleanup $ARGS
        
        if [[ $? -eq 0 ]]; then
            echo "✅ Safe cleanup completed successfully"
        else
            echo "⚠️  Safe cleanup completed with issues (review recommendations)"
            exit 1
        fi
        ;;
        
    health)
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Running health check..."
        python3 "$PYTHON_SCRIPT" health
        
        if [[ $? -eq 0 ]]; then
            echo "✅ Health check completed successfully"
        else
            echo "⚠️  Health check completed with warnings"
            exit 1
        fi
        ;;
        
    *)
        echo "Unknown command: $COMMAND" >&2
        usage
        ;;
esac

exit 0
