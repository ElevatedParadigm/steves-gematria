#!/bin/bash
# ASCII Correlation Heatmap Generator - Manual Runner
# Usage: ./run_correlation_heatmap.sh [--output PATH]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HEATMAP_SCRIPT="$SCRIPT_DIR/scripts/correlation_heatmap_ascii.py"
DEFAULT_OUTPUT="${SCRIPT_DIR}/obsidian_exports/HEATMAP_CORRELATION.md"

# Parse arguments
OUTPUT_FLAG=false
OUTPUT_PATH=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --output)
            OUTPUT_FLAG=true
            OUTPUT_PATH="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--output PATH]"
            exit 1
            ;;
    esac
done

# Run heatmap generator
python "$HEATMAP_SCRIPT" --output "$OUTPUT_PATH" 2>&1 | head -60
