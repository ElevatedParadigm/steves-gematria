# Firecrawl Architecture for Your Environment (Docker-based)

## ✅ Your Current Setup

You're using **Docker containers** for the Firecrawl API service, not a self-hosted Python installation:

```yaml
Containers:
  - firecrawl-api-1    → Port 3002 (Main API endpoint)
  - firecrawl-redis-1  → Port 6379 (Redis backend)
  - rabbitmq:3         → Ports 5672/15672 (Message queues)
```

**Key Point:** The Docker containers handle all the server logic internally. You don't need the `firecrawl.server.worker` Python module because you're calling the **API endpoints directly**.

---

## 📦 Available API Endpoints (from localhost:3002)

These work without any Python modules:

```python
import requests

# 1. Web scraping
response = requests.post(
    "http://localhost:3002/v1/scrape",
    json={"url": "https://example.com", "options": {}}
)

# 2. Search (v2 format with options parameter)
response = requests.post(
    "http://localhost:3002/v1/search",
    json={
        "query": "gematria patterns",
        "options": {"onlyMainContent": True}
    }
)

# 3. Map scraping (for images/visual patterns)
response = requests.post(
    "http://localhost:3002/v1/mapscrape",
    json={"url": "https://example.com"}
)
```

---

## 🔄 Async Task Runner Options

### Option 1: Use Cron for Background Tasks (Recommended for Your Setup)

Since you have sudo limitation, use your existing cron job for overnight work:

```bash
# Edit crontab
crontab -e
```

Add this line for async overnight tasks:
```
0 3 * * * /home/avalonas/.hermes/gematria/scripts/overnight_research.py >> /home/avalonas/.hermes/gematria/logs/overnight.log 2>&1
```

### Option 2: Manual Background Execution with nohup

```bash
nohup /home/avalonas/.hermes/gematria/scripts/overnight_research.py \
     >> /tmp/firecrawl-async-task.log 2>&1 &
     
# Check status later
ps aux | grep overnight_research
```

### Option 3: Simple Async Worker (Bash-based)

For background monitoring and task queuing:

<tool_call>
<function=write_file>
<parameter=content>
#!/bin/bash
# Firecrawl Async Task Monitor (Docker API wrapper)
set -e

API_URL="${FIRECRAWL_BASE_URL:-http://localhost:3002}"
ENVFILE="/home/avalonas/.hermes/.env"

export $(grep -v '^#' "$ENVFILE" 2>/dev/null | xargs)

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a /tmp/firecrawl-monitor.log
}

case "${1:-status}" in
  status)
    log "Firecrawl API Status Check..."
    curl -s "$API_URL/v1/health" 2>/dev/null || echo "API unreachable (container may be restarting)"
    ;;
  queue)
    log "Async task runner ready (no tasks queued currently)"
    log "Use: overnight_research.py for scheduled tasks"
    ;;
  *)
    log "Usage: $0 {status|queue}"
    exit 1
    ;;
esac
