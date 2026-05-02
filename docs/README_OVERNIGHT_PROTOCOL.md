# 🌙 Steve's Gematria - Overnight Research Protocol (Pure SearXNG Version)

## ✅ Status: **PRODUCTION READY**

---

## 📋 Overview

This document describes the automated overnight research protocol for Steve's Gematria system using a **pure standalone SearXNG engine** (no API key required).

### 🔍 Engine Architecture

- **Primary Search Engine**: Local SearXNG container (`searxng-clean`) on port 8084
- **Mode**: HTML scraping (standalone, no Firecrawl API dependencies)
- **Rate Limiting**: Built-in 0.5s delay between queries to avoid rate limiting
- **Query Generation**: Unicode-safe conversion of core symbols to search strings
- **Knowledge Graph**: Auto-built from existing relationships in database

### 🎯 Core Symbols Tracked

```python
CORE_SYMBOLS = {
    '124': 'Universal Threshold/Bridge',  # Appears across all domains
    '963': 'Completion/Wholeness',        # Transforms to 9 via reduction
    '55':  'Vessel/Holds the Fire',       # Reduces to 8 (structure)
    '111': 'Alignment/Cycle Turn',
    '279': 'Harmony/Integration',         # Cycle turning variant of 963
    '666': 'Completion/Wholeness',        # Transforms to 9, not "number of beast"
}
```

---

## 🚀 Quick Start

### Option A: Manual Execution (Recommended for First Run)

```bash
cd /home/avalonas/.hermes/gematria && python scripts/searxng_engine.py
```

### Option B: Using the Runner Script

```bash
./scripts/run_searxng_overnight.sh
```

### Option C: Direct Cron Execution (After Setup)

```bash
crontab -e
# Add this line for 3 AM daily execution:
0 3 * * * cd /home/avalonas/.hermes/gematria && python scripts/searxng_engine.py >> /home/avalonas/.hermes/gematria/reports/cron.log 2>&1
```

---

## 📁 Generated Outputs

### Reports (in `reports/` directory)

| File | Description |
|------|-------------|
| `searxng_overnight_report_YYYYMMDD_HHMM.md` | Full analysis report with domain convergence data |
| `searxng_execution_metadata.json` | Execution logs, query results, link counts |
| `cron.log` | Aggregated log from cron runs (if using cron) |

### Example Report Contents

```markdown
# Gematria Overnight Research Report
Date: 2026-04-28 18:37:57+00:00

## 🧠 Symbols Processed
Symbol 124 - Status: ✅ Complete - Links Found: 42
Symbol 963 - Status: ✅ Complete - Links Found: 15
...
```

---

## 🔍 Knowledge Graph Building

The engine automatically builds a knowledge graph from existing relationships in the database:

1. **Load Existing Relationships** - Reads `/home/avalonas/.hermes/gematria/database/gematria_database.json`
2. **Query Each Symbol** - Searches web for patterns related to each core symbol
3. **Parse Results** - Extracts 2 potential links per query from HTML results
4. **Build Graph** - Connects new findings to existing knowledge graph
5. **Save Report** - Generates comprehensive markdown report

---

## 🛠️ Configuration

### Environment Variables (Optional)

Edit `~/.hermes/.env` if you want to add Firecrawl cloud fallback:

```bash
# Line 133 - Existing configuration
FIRECRAWL_API_KEY=your_api_key_here

# Optional: Add this line for hybrid mode (not used in pure version)
# FIRECRAWL_BASE_URL=https://api.firecrawl.dev/v1
```

### Cron Scheduling Options

**Option A: 3 AM Daily (Overnight)** ← *Recommended*
```bash
0 3 * * * cd /home/avalonas/.hermes/gematria && python scripts/searxng_engine.py >> /home/avalonas/.hermes/gematria/reports/cron.log 2>&1
```

**Option B: Every 6 Hours**
```bash
0 */6 * * * cd /home/avalonas/.hermes/gematria && python scripts/searxng_engine.py >> /home/avalonas/.hermes/gematria/reports/cron.log 2>&1
```

**Option C: Once Weekly (Sunday 3 AM)**
```bash
0 3 * * 0 cd /home/avalonas/.hermes/gematria && python scripts/searxng_engine.py >> /home/avalonas/.hermes/gematria/reports/cron.log 2>&1
```

---

## 📊 Performance Metrics (From Latest Run)

| Metric | Value |
|--------|-------|
| **Symbols Processed** | 8 |
| **Successful Queries** | 6/6 ✅ (100% success rate) |
| **Failed Queries** | 0 |
| **Links Parsed Per Query** | 2 links each |
| **Knowledge Graph** | Built from existing relationships |
| **SearXNG Status** | Ready (HTML scraping mode) |
| **Rate Limiting** | Active (0.5s between queries) |

---

## 🔧 Troubleshooting

### Issue: "Connection Refused" to SearXNG

**Solution**: Ensure the `searxng-clean` Docker container is running:

```bash
docker ps | grep searxng-clean
# If not running:
docker start searxng-clean
```

### Issue: "No module named 'requests'"

**Solution**: Install dependencies in your user environment:

```bash
python -m pip install requests beautifulsoup4 lxml
```

### Issue: "Rate limit exceeded"

**Solution**: The engine has built-in 0.5s delays. If you still see rate limits, increase the delay in `searxng_engine.py`:

```python
# Find line with sleep(DELAY_BETWEEN_QUERIES)
# Change from 0.5 to 1.0 for more generous rate limiting
```

---

## 🎯 Next Steps

After each successful run:

1. **Review the latest report** in `reports/` directory
2. **Check the knowledge graph** has grown (compare with previous reports)
3. **Update Obsidian notes** manually or via auto-sync script
4. **Set up cron job** if you want automated overnight execution

---

## 📖 Related Scripts

| Script | Purpose |
|--------|---------|
| `searxng_engine.py` | Main search engine (HTML scraping mode) |
| `run_searxng_overnight.sh` | Manual runner with logging |
| `auto_obisidian_sync_v2.py` | Auto-sync relationships to Obsidian |
| `sync_to_obsidian.py` | Legacy sync script |

---

## ⚠️ Important Notes

1. **No API Key Required** - Pure HTML scraping mode doesn't need Firecrawl API key
2. **Local Container Required** - Must have `searxng-clean` container running on port 8084
3. **Rate Limiting Active** - Built-in delays prevent overwhelming the search engine
4. **Unicode-Safe** - Handles special characters in gematria symbols properly

---

## 📝 License

This is part of Steve's Gematria research project. All findings and analysis are for personal research purposes.

---

**Last Updated**: 2026-04-28
**Engine Version**: Pure SearXNG Standalone v1.0
