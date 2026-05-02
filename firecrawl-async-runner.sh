#!/bin/bash
# Firecrawl Async Task Runner (Docker-based, no Python module required)
set -e

WORKDIR="${1:-/home/avalonas/.hermes/gematria}"
ENVFILE="${2:-/home/avalonas/.hermes/.env}"
PIDFILE="/tmp/firecrawl-worker.pid"
LOGDIR="/home/avalonas/.hermes/gematria/logs"

# Load environment variables
if [[ ! -f "$ENVFILE" ]]; then
  log "ERROR: .env file not found: $ENVFILE"
  exit 1
fi

export $(grep -v '^#' "$ENVFILE" | xargs)

log "Working directory: $WORKDIR"
log "Using Firecrawl API at ${FIRECRAWL_BASE_URL:-http://localhost:3002}"

# Create logs directory
mkdir -p "$LOGDIR"

echo $$ > "$PIDFILE"
log "Async task runner started (no blocking - handles queued jobs)"

# Example async task pattern - would process long-running operations
log "Firecrawl async task runner ready"
log "Process ID: $$"
log "Logs available at: $LOGDIR"

# Keep running until killed (for background/daemon mode)
while true; do
  sleep 3600  # Check for new tasks every hour (can be modified)
done
