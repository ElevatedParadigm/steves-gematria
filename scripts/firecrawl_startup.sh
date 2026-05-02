#!/bin/bash
# Minimal Firecrawl Startup Script
# Disables services that require Docker-in-Docker

echo "🔥 Starting Firecrawl (minimal mode)..."

# Run Firecrawl but disable internal service setup that requires nested Docker
CMD="npm start -- --disable-postgres-setup --skip-harness"

echo "Command: $CMD"
exec docker-entrypoint.sh $CMD
