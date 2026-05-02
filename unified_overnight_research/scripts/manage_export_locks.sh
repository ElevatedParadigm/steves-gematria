#!/bin/bash
# =============================================================================
# Visual Archive Export Lock Manager Wrapper Script
# =============================================================================
# Usage:
#   ./manage_export_locks.sh check       # Check for lock files before export
#   ./manage_export_locks.sh cleanup     # Remove stale locks
#   ./manage_export_locks.sh safe-cleanup  # Safe cleanup with verification
#   ./manage_export_locks.sh health      # Health check
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH="/home/avalonas/.hermes/gematria/unified_overnight_research/scripts/manage_export_locks.py"

usage() {
    echo "Usage: $0 {check|cleanup|safe-cleanup|health} [options]"
    echo ""
    echo "Commands:"
    echo "  check       Check for .git/index.lock files before export"
    echo "  cleanup     Remove stale lock files"
    echo "  safe-cleanup Perform safe cleanup with git verification"
    echo "  health      Perform full health check of lock management system"
    echo ""
    echo "Options:"
    echo "  -s, --subdir DIR    Specific output subdirectory (default: all)"
    echo ""
    exit 1
}

# Parse arguments
COMMAND=""
SUBDIR=""

while [[ $# -gt 0 ]]; do
    case $1 in
        check|cleanup|safe-cleanup|health)
            COMMAND=$1
            ;;
        -s|--subdir)
            SUBDIR="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

if [[ -z "$COMMAND" ]]; then
    usage
fi

# Change to script directory and run Python script
cd /home/avalonas/.hermes/gematria/unified_overnight_research/scripts

case $COMMAND in
    check)
        python3 manage_export_locks.py check
        ;;
    cleanup)
        if [[ -n "$SUBDIR" ]]; then
            python3 manage_export_locks.py cleanup --subdir "$SUBDIR"
        else
            python3 manage_export_locks.py cleanup
        fi
        ;;
    safe-cleanup)
        if [[ -n "$SUBDIR" ]]; then
            python3 manage_export_locks.py safe-cleanup --subdir "$SUBDIR"
        else
            python3 manage_export_locks.py safe-cleanup
        fi
        ;;
    health)
        python3 manage_export_locks.py health
        ;;
    *)
        echo "Unknown command: $COMMAND"
        usage
        ;;
esac
