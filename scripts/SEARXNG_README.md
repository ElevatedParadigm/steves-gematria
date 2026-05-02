# SearXNG Integration Engine - Steve's Gematria Overnight Research Protocol

## 🎯 Purpose
Automated privacy-focused overnight web research using local SearXNG instance instead of rate-limited Firecrawl API.

## 📊 Architecture Overview

```
┌─────────────────────┐
│  Image Analysis     │ → Foundation symbols (124, 6966, etc.)
│  Database           │ → Relationship tracking & domain patterns
└──────────┬──────────┘
           ↓
┌────────────────────────────┐
│  SearXNG Integration Engine │ ← Standalone HTML scraping mode
│                            │   - No API key required
│                            │   - Works with local instance only
└──────────┬─────────────────┘
           ↓
┌────────────────────────────┐
│  Knowledge Graph Building  │ → Connect concepts across domains
└──────────┬─────────────────┘
           ↓
┌────────────────────────────┐
│  Report Generation         │ → Markdown analysis with insights
└────────────────────────────┘
```

## 🚀 Features

- ✅ **Privacy-first**: Uses local SearXNG instance (no data leaves your network)
- ✅ **No rate limits**: Unlike cloud-based search APIs
- ✅ **HTML scraping mode**: Works directly with web interface
- ✅ **Rate limiting built-in**: 0.5s between queries to avoid blocking
- ✅ **Unicode-safe**: ASCII-only query generation
- ✅ **Robust error handling**: Gracefully handles connection issues

## 📦 Installation

1. Verify SearXNG is running:
   ```bash
   docker ps | grep searxng-clean
   ```

2. Check engine exists:
   ```bash
   ls /home/avalonas/.hermes/gematria/scripts/searxng_engine.py
   ```

3. Run first test (dry-run mode):
   ```bash
   cd /home/avalonas/.hermes/gematria && python scripts/searxng_engine.py --dry-run
   ```

## 🏃 Running the Engine

### Manual Execution (One-off)
```bash
cd /home/avalonas/.hermes/gematria && python scripts/searxng_engine.py
```

### Dry-Run Mode (Simulation)
```bash
python scripts/searxng_engine.py --dry-run
```

### Specific Symbols Only
```bash
python scripts/searxng_engine.py --symbols "124,6966,1753"
```

## ⏰ Cron Configuration

Edit crontab for automated overnight runs:
```bash
crontab -e
```

Add to file (choose one schedule):

### Option A: Daily at 3 AM (Default)
```bash
0 3 * * * cd /home/avalonas/.hermes/gematria && python scripts/searxng_engine.py >> /home/avalonas/.hermes/gematria/reports/cron.log 2>&1
```

### Option B: Every 4 Hours
```bash
*/4 * * * * cd /home/avalonas/.hermes/gematria && python scripts/searxng_engine.py >> /home/avalonas/.hermes/gematria/reports/cron.log 2>&1
```

### Check Cron Logs
```bash
tail -f /home/avalonas/.hermes/gematria/reports/cron.log
```

## 📡 SearXNG Configuration

The engine expects a running SearXNG instance at `http://localhost:8084`. Default Docker setup:

```yaml
# Container name: searxng-clean
# Port mapping: 8084 → 80 (host:container)
# URL for API calls: http://localhost:8084/search?query=...
```

**Note**: This engine works in **HTML scraping mode** (not official SearXNG API), so no `use_official_api` configuration is needed.

## 📊 Output Files

The engine generates:

1. **Analysis Report**: `reports/searxng_overnight_report_YYYYMMDD_HHMM.md`
   - Query results and summaries
   - Knowledge graph status
   - Next steps recommendations

2. **Execution Metadata**: `reports/searxng_execution_metadata.json`
   - Successful/failed query counts
   - Processing timestamps
   - SearXNG connection status

3. **Cron Logs**: `reports/cron.log` (when using automated runs)
   - Full console output from each run

## 🔧 Troubleshooting

### Issue: "SearXNG is running but API mode is disabled"
**Solution**: This engine works in HTML scraping mode, not API mode. Connection is still functional.

### Issue: "Connection refused"
**Solution**: Verify SearXNG container is running:
```bash
docker ps | grep searxng-clean
docker start searxng-clean  # If stopped
```

### Issue: "No results parsed from HTML"
**Solution**: Increase rate limiting delay in engine code, or check network connectivity.

## 📈 Comparison with Firecrawl Engine

| Feature | Firecrawl Engine | SearXNG Engine |
|---------|-----------------|----------------|
| **Data Privacy** | Cloud API (data leaves network) | Local-only ✅ |
| **Rate Limits** | Limited (pay-as-you-go) | None ✅ |
| **Setup Complexity** | Docker required | Already running ✅ |
| **API Key Required** | Yes | No ✅ |
| **Cost** | Per-query billing | Free ✅ |
| **HTML Scraping** | Via crawler | Direct parsing ✅ |

## 📚 Related Files

- `scripts/overnight_research.py` → Original Firecrawl-based protocol (deprecated for privacy)
- `scripts/searxng_engine.py` → New SearXNG integration (actively maintained)
- `crontab.gematria-searxng` → Cron configuration template
- `database/gematria_database.json` → Symbol/relationship foundation data

## 🎓 Usage Example with Custom Symbols

```bash
cd /home/avalonas/.hermes/gematria

# Search specific gematria numbers
python scripts/searxng_engine.py --symbols "124,6966,1753"

# Run in batch mode (default)
python scripts/searxng_engine.py

# View latest report
cat reports/searxng_overnight_report_*.md | tail -100
```

## 📝 Development Notes

- Engine is designed to be **stateless** between runs
- Knowledge graph builds from existing relationships in database
- Each query batch focuses on different gematria patterns
- Rate limiting prevents IP blocking on SearXNG instance

---

**Last Updated**: April 28, 2026  
**Engine Version**: 1.2.0 (SearXNG Standalone Edition)  
**Author**: Avalon & Steve's Gematria Project
