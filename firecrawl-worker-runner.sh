#!/bin/bash
# Firecrawl Worker Runner (Standalone, no systemd required)
set -e

WORKDIR="${1:-/home/avalonas/.hermes/gematria}"
ENVFILE="${2:-/home/avalonas/.hermes/.env}"
PIDFILE="/tmp/firecrawl-worker.pid"
LOGDIR="/home/avalonas/.hermes/gematria/logs"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOGDIR:-/tmp}/firecrawl-worker.log" 2>/dev/null || echo "$1" >&2
}

if [[ ! -f "$ENVFILE" ]]; then
  log "ERROR: .env file not found: $ENVFILE"
  exit 1
fi

mkdir -p "${LOGDIR:-/tmp}"
export $(grep -v '^#' "$ENVFILE" | xargs)
export BIND_ADDRESS="${BIND_ADDRESS:-0.0.0.0}"
export PORT="${PORT:-3002}"

log "Working directory: $WORKDIR"
log "Port: $PORT (Binding to $BIND_ADDRESS)"

if ! python -c "import firecrawl.server.worker" 2>/dev/null; then
  log "ERROR: firecrawl.server.worker module not found. Install with: pip install firecrawl"
  exit 1
fi

echo $$ > "$PIDFILE"
exec /usr/bin/python -m firecrawl.server.worker
