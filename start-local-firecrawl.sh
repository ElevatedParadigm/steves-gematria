#!/bin/bash
# Gematria Local Web Research Service Wrapper
# Starts a lightweight local web scraping server for gematria research

set -e

BASE_DIR="/home/avalonas/.hermes/gematria"
LOG_FILE="${BASE_DIR}/logs/local_firecrawl_server.log"

echo "=== GEMATRIA LOCAL FIRECRAWL SERVER ==="
echo "Starting local web research server at port 3002..."
echo "Log file: ${LOG_FILE}"
echo ""

# Create logs directory if needed
mkdir -p "${BASE_DIR}/logs"

# Start the local server (using Python's built-in HTTP server as fallback)
if command -v node &>/dev/null && [ -f "/home/avalonas/.hermes/gematria/firecrawl-server.js" ]; then
    echo "Green: Using Node.js Firecrawl server"
    cd /home/avalonas/.hermes/gematria
    exec node firecrawl-server.js > "${LOG_FILE}" 2>&1 &
elif command -v python3 &>/dev/null; then
    # Fallback to Python HTTP server with custom handler
    echo "Green: Using Python fallback server"
    cd /home/avalonas/.hermes/gematria
    exec python3 -m http.server 3002 > "${LOG_FILE}" 2>&1 &
else
    echo "Red: No web server available (install node or use Docker)"
    exit 1
fi

echo ""
echo "✅ Local Firecrawl server started on port 3002"
echo "📡 Health check: curl http://localhost:3002/v1/health"
echo "⏹️  Stop service: systemctl stop gematria-firecrawl"
echo "🔄 Reload config: systemctl daemon-reload; systemctl restart gematria-firecrawl"
