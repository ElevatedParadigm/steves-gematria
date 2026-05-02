#!/bin/bash
# run_overnight_wrapper.sh - overnight research execution wrapper
# Mode: overnight with image-seed bootstrapping
python scripts/unified_overnight_research_image_seed.py --mode=overnight --image-seed --repeat-count=9999

# Activate the hermes-agent virtual environment
source /home/avalonas/.hermes/hermes-agent/venv/bin/activate

# Set required environment variables
export PYTHONPATH="${PYTHONPATH:+$:}:$(pwd)"

# Run the orchestrator with specified arguments
exec python /home/avalonas/.hermes/gematria/scripts/orchestrator.py "$@"
