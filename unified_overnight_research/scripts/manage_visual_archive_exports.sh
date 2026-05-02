#!/bin/bash
# Visual Archive Export Job Manager - Shell Wrapper Script
# ================================================================================
# Provides easy command-line interface for managing Visual Archive export jobs
#
# Usage: ./manage_visual_archive_exports.sh {run|status|retry <job_id>|cleanup}
#
# Examples:
#   ./manage_visual_archive_exports.sh run        # Run export jobs
#   ./manage_visual_archive_exports.sh status     # Show current status
#   ./manage_visual_archive_exports.sh retry 124   # Retry failed export for symbol 124
#   ./manage_visual_archive_exports.sh cleanup    # Archive old exports
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="/home/avalonas/.hermes/gematria"
UNIFIED_OUR_DIR="$BASE_DIR/unified_overnight_research"
PYTHON="${PYTHON:-python3}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════╗"
    echo "║  📦 VISUAL ARCHIVE EXPORT JOB MANAGER                  ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""
}

print_command() {
    echo -e "${BLUE}Command:${NC} $1"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

usage() {
    cat << EOF
Visual Archive Export Job Manager

Usage: $(basename "$0") <command> [options]

Commands:
    run              Run export jobs for all symbols in queue (parallel batch processing)
    status           Show current export job status and queue information
    retry <job_id>   Retry a failed export job (symbol ID, e.g., 124)
    cleanup          Archive completed exports older than 30 days

Examples:
    $(basename "$0") run                     # Process all pending exports
    $(basename "$0") status                  # Check current queue and progress
    $(basename "$0") retry 124               # Retry export for symbol 124
    $(basename "$0") cleanup                 # Clean up old exports

Description:
    This script manages Visual Archive export jobs, processing symbols from
    the database queue in parallel batches. It tracks progress, handles failures
    with retry logic, and logs all activity to both the database and cron output.

Location: $SCRIPT_DIR
EOF
}

main() {
    if [[ $# -lt 1 ]]; then
        usage
        exit 1
    fi
    
    local command="$1"
    shift
    
    case "$command" in
        run)
            print_header
            print_info "Starting Visual Archive export batch processing..."
            
            # Check if Python script exists
            if [[ ! -f "$UNIFIED_OUR_DIR/scripts/manage_visual_archive_exports.py" ]]; then
                print_error "Python script not found!"
                exit 1
            fi
            
            # Run the exports
            "$PYTHON" "$UNIFIED_OUR_DIR/scripts/manage_visual_archive_exports.py" run
            
            local success=$?
            
            if [[ $success -eq 0 ]]; then
                echo ""
                print_success "Export batch completed successfully!"
            else
                echo ""
                print_warning "Export batch completed with some errors"
            fi
            ;;
            
        status)
            print_header
            print_info "Current export job status..."
            
            "$PYTHON" "$UNIFIED_OUR_DIR/scripts/manage_visual_archive_exports.py" status
            
            local success=$?
            
            if [[ $success -eq 0 ]]; then
                echo ""
                print_success "Status retrieved successfully!"
            else
                print_warning "Could not retrieve status"
            fi
            ;;
            
        retry)
            if [[ $# -lt 1 ]]; then
                print_error "Job ID required for retry command"
                echo "Usage: $(basename "$0") retry <job_id>"
                exit 1
            fi
            
            local job_id="$1"
            
            if ! [[ "$job_id" =~ ^[0-9]+$ ]]; then
                print_error "Invalid job ID: $job_id (must be a number)"
                exit 1
            fi
            
            print_header
            print_info "Retrying export for symbol #$job_id..."
            
            "$PYTHON" "$UNIFIED_OUR_DIR/scripts/manage_visual_archive_exports.py" retry "$job_id"
            ;;
            
        cleanup)
            print_header
            print_info "Starting cleanup of completed exports..."
            
            "$PYTHON" "$UNIFIED_OUR_DIR/scripts/manage_visual_archive_exports.py" cleanup
            
            local success=$?
            
            if [[ $success -eq 0 ]]; then
                echo ""
                print_success "Cleanup completed!"
            else
                print_warning "Cleanup completed with some errors"
            fi
            ;;
            
        *)
            print_error "Unknown command: $command"
            usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
