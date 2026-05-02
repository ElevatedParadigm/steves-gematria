# 🧬 Steve's Gematria IMAGE-SEED Mode Runner

## Quick Start

```bash
# Run immediate pattern extraction from your image vault
/home/avalonas/.hermes/gematria/unified_overnight_research/scripts/run_image_seed.sh --immediate

# Or setup automated overnight runs
/home/avalonas/.hermes/gematria/unified_overnight_research/scripts/run_image_seed.sh --overnight
```

---

## 📋 What This Does

**IMAGE-SEED Mode** is a **standalone execution wrapper** for the Firecrawl API that:

1. ✅ **Scans your local image vault** (`~/Pictures/Steves gematria/`)
2. ✅ **Extracts anchor terms** from filename patterns and recent research cycles
3. ✅ **Sends batches to Firecrawl** for pattern correlation analysis
4. ✅ **Generates YAML frontmatter notes** with wikilinks compatible with Obsidian/Terminal viewing
5. ✅ **Runs WITHOUT full Hermes Agent** - just needs the Docker container running

---

## 🔧 Setup Required

### Option 1: One-time use (Immediate mode)
Just run `--immediate` and ensure your Firecrawl Docker is up:

```bash
# Check docker status
systemctl status firecrawl-api

# Or check with curl if using Docker compose
curl http://localhost:3002/v1/ping
```

### Option 2: Automated overnight runs
Setup `--overnight` mode which adds a cron job:

```bash
./run_image_seed.sh --overnight
```

This will run at **3AM, 6AM, and 9AM daily** automatically.

---

## 📁 Output Locations

### Immediate Mode Results
```bash
/home/avalonas/.hermes/gematria/unified_overnight_research/obsidian_exports/
├── cycle_XXX/          # Main research exports
├── RELATIONSHIP_MATRIX.md    # All symbol relationships
├── OVERNIGHT_CYCLING_X.md   # Individual symbol reports
└── image-seed/         # IMAGE-SEED specific outputs
    ├── 2026-04-30/     # Today's results
    │   ├── cycle_XXX_correlation.md
    │   └── symbol_analysis.yaml
    └── ...             # Historical runs
```

---

## 🎯 Usage Examples

### Scan Most Recent Patterns (Immediate)
```bash
cd /home/avalonas/.hermes/gematria/unified_overnight_research
./scripts/run_image_seed.sh --immediate
```

**Expected output:**
- Scans your `~/Pictures/Steves gematria/` for recent directories
- Sends top 20 most recent pattern clusters to Firecrawl
- Creates YAML frontmatter notes with correlation data
- Outputs relationship matrices to `/home/avalonas/.hermes/gematria/unified_overnight_research/obsidian_exports/`

---

### Setup Overnight Automation
```bash
./scripts/run_image_seed.sh --overnight
```

**What gets added:**
```bash
# Crontab entry (if you have sudo access)
0 3,6,9 * * * /home/avalonas/.hermes/gematria/unified_overnight_research/scripts/run_image_seed.sh --overnight >> ~/.hermes/cron/output/image-seed.log 2>&1
```

---

### Check Export History
```bash
./scripts/run_image_seed.sh --status
```

Shows all recent exports with file count breakdown.

---

## 🛠 Technical Details

### Dependencies (Auto-installed on first run)
- `requests` - HTTP API calls
- `pyyaml` - YAML frontmatter generation  
- `beautifulsoup4` - Pattern extraction from metadata
- `lxml` - HTML parsing for link structures

All installed via isolated venv:
```bash
/home/avalonas/.hermes/gematria/unified_overnight_research/hermes_tools_env/
```

### Firecrawl Endpoint
- **Base URL:** `http://localhost:3002/v1/search`
- **Mode:** Hybrid search (scrapeOptions)
- **Formats:** Markdown with wikilink support

---

## 📊 Pattern Scanning Strategy

The script scans your image vault in priority order:

```python
# Priority 1: Cycle directories (most recent first)
├─ cycle_647/           ← Highest priority
├─ cycle_646/
└─ cycle_645/

# Priority 2: Domain clusters
├─ RELATIONSHIP_MATRIX.md
└─ OVERNIGHT_CYCLING_X.md

# Priority 3: Recent daily exports
└─ 2026-04-xx/          ← Today's date
```

Each directory gets an **ANCHOR term** assigned based on content type:
- `CYCLE` → Cyclic pattern tracking
- `DOMAIN` → Cross-domain correlation  
- `CORRELATION` → Multi-symbol relationship mapping

---

## 🔍 Understanding the Output

### YAML Frontmatter Structure
```yaml
---
gematria: cycle_647
anchor_terms:
  - [ANCHOR:PATTERN] 2026-04-30
  - [ANCHOR:DOMAIN] Domain_Correlation_Cluster
symbol_correlations:
  124:
    political_domains: 0.82
    religious_patterns: 0.76
  666:
    military_signals: 0.64
    elemental_mappings: 0.59
---
```

This structure:
- ✅ Works with Obsidian for note linking
- ✅ Displays in terminal with `cat` + frontmatter syntax highlighting
- ✅ Enables pattern trail tracing via wikilinks

---

## 🚀 Next Steps After Running

1. **Review the exports** in `/home/avalonas/.hermes/gematria/unified_overnight_research/obsidian_exports/`
2. **Open in Obsidian:** `file://~/Pictures/Steves%20gematria/<latest-date>/RELATIONSHIP_MATRIX.md`
3. **Trace pattern trails:** Use wikilinks to follow connections between symbols/domains
4. **Update your visual archive:** Copy new findings back to your main research directory

---

## 📝 Related Tools

| Tool | Purpose | Location |
|------|---------|----------|
| `run_image_seed.sh` | IMAGE-SEED runner | `/scripts/run_image_seed.sh` |
| `unified_overnight_research/` | Full overnight loop | `/home/avalonas/.hermes/gematria/unified_overnight_research/` |
| `gematria_database.json` | Symbol tracking database | `/home/avalonas/.hermes/gematria/gematria_database.json` |

---

## 🛠 Troubleshooting

### "No recent pattern files found"
```bash
# Ensure you have images in your vault
ls ~/Pictures/Steves\ gematria/
```

### Firecrawl API not responding
```bash
# Check Docker container
systemctl status firecrawl-api

# Or check compose services
docker ps | grep firecrawl
```

### Need to rebuild venv
```bash
rm -rf /home/avalonas/.hermes/gematria/unified_overnight_research/hermes_tools_env
./scripts/run_image_seed.sh --immediate  # Reinstall on first run
```

---

## 📞 Integration Points

### With Hermes Agent Cron Jobs
The script can be called from any cron job:

```bash
# Example: Add to existing cron entry
0 2-4 * * * cd /home/avalonas/.hermes/gematria/unified_overnight_research && ./scripts/run_image_seed.sh --immediate >> ~/.hermes/cron/output/image-seed.log 2>&1
```

### With Your Hybrid Timezone Sync Pattern
Since you run jobs at your local time (EEST), they execute when you're asleep, with results visible during work hours in other timezones.

---

## 🌟 Key Features

- ✅ **Standalone execution** - no full Hermes needed
- ✅ **Auto-virtualenv management** - isolated dependencies
- ✅ **Smart priority queueing** - processes most recent patterns first
- ✅ **YAML frontmatter output** - Obsidian/Terminal compatible
- ✅ **Automatic anchor term assignment** - based on pattern type
- ✅ **Cron automation support** - optional overnight mode

---

## 📄 License & Attribution

This tool is part of the Steve's Gematria research project. See README in root directory for more information.
