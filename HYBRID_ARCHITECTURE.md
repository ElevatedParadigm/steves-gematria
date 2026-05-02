# Firecrawl Hybrid Architecture (Option 2)
## Documentation for Steve

---

## What Was Implemented

I've created a **hybrid architecture** that combines both Docker containers and systemd worker services for the Firecrawl API. This provides redundancy and different operational modes:

### Components Created

1. **`/home/avalonas/firecrawl-worker.service`** - Systemd service file (requires sudo for system-wide installation)
2. **`/home/avalonas/.hermes/gematria/firecrawl-worker-runner.sh`** - Standalone runner script (no sudo required!)

---

## Architecture Overview

### Option 2a: Docker-Only (Current Setup)
```bash
# Your existing containers work fine:
docker ps
# firecrawl-api-1     3002    API endpoint for synchronous requests
# firecrawl-redis-1   6379    Redis backend
# rabbitmq:3          5672/15672 Message queue
```

**Use case:** Direct, immediate API access for real-time operations.

### Option 2b: Hybrid with Worker Service (Future Enhancement)
```bash
┌─────────────┐    ┌─────────────┐
│ Firecrawl   │───▶│ Container   │ (API requests)
│ API         │    │ Port 3002   │
└─────────────┘    └─────────────┘

┌─────────────┐    ┌─────────────┐
│ Worker      │◀───│ Systemd     │ (async/queued tasks)
│ Service     │    │ Supervisor  │
└─────────────┘    └─────────────┘
```

**Use case:** Background processing, long-running jobs, overnight research protocol.

---

## Installation Options

### Option 2b-1: System-wide (requires sudo)
```bash
# Step 1: Copy service file to systemd directory
sudo cp /home/avalonas/firecrawl-worker.service /etc/systemd/system/

# Step 2: Reload systemd and enable the service
sudo systemctl daemon-reload
sudo systemctl enable firecrawl-worker

# Step 3: Start the worker
sudo systemctl start firecrawl-worker

# Step 4: Check status
sudo systemctl status firecrawl-worker
```

### Option 2b-2: Manual Runner (No sudo required!) ✅ RECOMMENDED
```bash
# Direct usage
/home/avalonas/.hermes/gematria/firecrawl-worker-runner.sh

# Background with nohup
nohup /home/avalonas/.hermes/gematria/firecrawl-worker-runner.sh > /tmp/worker.log 2>&1 &

# Or use screen/tmux for better session management
screen -S firecrawl-worker
/home/avalonas/.hermes/gematria/firecrawl-worker-runner.sh
```

---

## Usage Scenarios

### Scenario 1: Real-time Web Scraping (Docker API)
```python
import requests

url = "http://localhost:3002/v1/scrape"
headers = {"Authorization": "Bearer YOUR_API_KEY"}
payload = {
    "url": "https://example.com",
    "options": {"onlyMainContent": True}
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

### Scenario 2: Overnight Research Protocol (Worker Service)
The worker service can handle long-running jobs like:
- Multi-domain crawling campaigns
- Batch image analysis
- Overnight research protocol
- Scheduled batch processing

---

## Monitoring

### Check Docker Containers
```bash
docker ps | grep firecrawl
```

### Check Worker Process (if running)
```bash
# Find the worker process
pgrep -f 'firecrawl.server.worker'

# Check logs
tail -f /home/avalonas/.hermes/gematria/logs/worker-run.log
```

### Systemd Status (if installed)
```bash
sudo systemctl status firecrawl-worker
```

---

## Configuration Files

### Environment Variables
The worker service loads from: `/home/avalonas/.hermes/.env`

Required variables already configured in your `.env`:
- `FIRECRAWL_API_KEY=***` (line 133)
- Optional: `FIRECRAWL_BASE_URL=http://localhost:3002`

### Service File Location
```
/home/avalonas/firecrawl-worker.service
```

### Runner Script
```
/home/avalonas/.hermes/gematria/firecrawl-worker-runner.sh
```

---

## Current Status ✅

- **Core Symbols:** 124, 963, 55, 111, 279, 666 (all tracked)
- **Docker Containers:** Running and healthy
- **API Endpoint:** `http://localhost:3002/v1/search` working with v2 format
- **Worker Service:** Available for installation (no sudo required via runner script)

---

## Next Steps for Option 2

Would you like me to:

1. **Install the worker service** (requires sudo access, or use manual runner)
2. **Integrate overnight research protocol** with worker service
3. **Set up systemd timers** for scheduled tasks
4. **Document hybrid architecture** in README.md files

---

## Summary

Option 2 implements a **hybrid architecture** combining:
- ✅ Docker containers (already running - synchronous API access)
- ⏳ Worker service (ready to install - async/background processing)

Both approaches work simultaneously, providing flexibility for different use cases. The manual runner script allows operation without sudo access, making it compatible with your current environment constraints.
