# 🔧 Steve's Gematria - Local Runner Tools Suite

## 📋 Overview

This collection of tools works with your **local Firecrawl setup** (Docker on `localhost:3002`) without requiring SearXNG to be active. Perfect for analyzing your existing image vault and processing pattern discoveries.

---

## 🗂️ Available Tools

### 1️⃣ IMAGE-SEED Runner (`run_image_seed.sh`)
**Purpose**: Main entry point for local image analysis  
**Location**: `/unified_overnight_research/scripts/run_image_seed.sh`

**What it does:**
- Reads from your image vault (`/home/avalonas/Pictures/Steves gematria`)
- Extracts anchor terms from filenames (cycle/domain/correlation patterns)
- Sends queries to local Firecrawl API (`http://localhost:3002`)
- Falls back gracefully when search unavailable
- Outputs results to `/unified_overnight_research/output/`

**Quick Start:**
```bash
cd /home/avalonas/.hermes/gematria/unified_overnight_research/scripts
bash run_image_seed.sh
```

---

### 2️⃣ Pattern Trail Exporter (`export_pattern_trails.py`)
**Purpose**: Creates Obsidian-friendly trail documentation  
**Location**: `/unified_overnight_research/export_pattern_trails.py`

**What it does:**
- Scans vault for correlation/cycle files
- Extracts discovery chains and symbol paths
- Creates markdown wikilink entries
- Outputs to `/output/pattern_trails/`

**Quick Start:**
```bash
cd /home/avalonas/.hermes/gematria/unified_overnight_research
python3 export_pattern_trails.py
```

**Sample Output File:**
```markdown
---
tags: [gematria, pattern-trail, correlation_matrix]
created: 2026-04-30 15:30:00
source-image: `domain938_CYCLE1_correlation.png`
status: discovered
---

# Pattern_Correlation_Matrix_938

## Discovery Path

[[correlation_matrix]] → [[Pattern_Correlation_Matrix_938]]

**Anchor Term**: `[ANCHOR:CORRELATION]`  
**Trail Pattern**: `correlation_matrix`

## Correlation Data

| Symbol | Value | Reduction | Domain |
|--------|-------|-----------|--------|
| 938    | 124   | 6         | correlation_matrix |

---

## Related Patterns

- [[124]] - Universal Threshold/Bridge
- [[666]] - Completion/Wholeness  
- [[9]] - Harmony/Integration Cycle
```

---

### 3️⃣ Manual Export Toolset (`manual_export_toolset.py`)
**Purpose**: Batch processing utilities for existing galleries  
**Location**: `/unified_overnight_research/manual_export_toolset.py`

**What it does:**
- **Gallery Index**: Creates JSON navigation structure
- **Correlation Matrix**: ASCII heatmap (░ ▒ ▓ █ . O ^) 
- **Domain Summaries**: Per-cluster documentation
- **Pattern Chain Extractor**: Discovery path tracing

**Commands:**

| Command | Description |
|---------|-------------|
| `python3 manual_export_toolset.py index` | Build gallery index |
| `python3 manual_export_toolset.py matrix` | Create correlation heatmap |
| `python3 manual_export_toolset.py summary` | Generate domain summaries |
| `python3 manual_export_toolset.py all` | Run all exports |

**Example Correlation Matrix:**
```
═════════════════════════════════════════════════════
STEVE'S GEMATRIA - CORRELATION MATRIX
Generated: 2026-04-30 15:35:00
═════════════════════════════════════════════════════

   Domain938 Domain937 Domain936 Domain935 Domain934 Domain933 Domain932 Domain931 
Domain938     O      .      .      .      .      o      .      .     
```

---

### 4️⃣ Overnight Runner (Local Mode) (`overnight_runner_local.py`)
**Purpose**: Automated overnight research without SearXNG  
**Location**: `/unified_overnight_research/overnight_runner_local.py`

**What it does:**
- Scans vault for new images daily (24h modification window)
- Processes symbol galleries and correlations
- Exports trails, matrices, and summaries automatically
- Falls back to direct scraping when search unavailable
- Respects your timezone (EEST 02:00-04:00 overnight)

**Commands:**

| Command | Description |
|---------|-------------|
| `python3 overnight_runner_local.py` | Single run, then exit |
| `python3 overnight_runner_local.py --continuous` | Continuous loop mode |
| `python3 overnight_runner_local.py --continuous --interval 60` | Loop every 60 min |

---

## 📂 Output Structure

```
/unified_overnight_research/
├── output/
│   ├── pattern_trails/          # Obsidian-friendly trail docs
│   │   ├── Pattern_Correlation_Matrix_938.md
│   │   └── Pattern_Domain_742_cycle55_.md
│   ├── manual_exports/          # Batch export results
│   │   ├── gallery_index_*.json
│   │   ├── correlation_matrix_*.txt
│   │   └── domain_*_summary_*.md
│   └── CURRENT_STATUS.md        # Latest run summary
├── scripts/
│   ├── run_image_seed.sh        # Main IMAGE-SEED runner
│   └── README_RUNNER_LOCAL.md   # This documentation
└── overnight_runner_local.py    # Automated loop tool
```

---

## 🎯 Quick Reference

### Running Analysis

```bash
# One-time image analysis
cd /home/avalonas/.hermes/gematria/unified_overnight_research/scripts
bash run_image_seed.sh

# Export pattern trails (Obsidian format)
python3 export_pattern_trails.py

# Generate correlation heatmap
python3 manual_export_toolset.py matrix

# Create all exports at once
python3 manual_export_toolset.py all

# Run overnight in continuous mode
python3 overnight_runner_local.py --continuous --interval 120
```

### Export Paths by Purpose

| Task | Tool | Command |
|------|------|---------|
| Analyze vault | IMAGE-SEED | `bash run_image_seed.sh` |
| Obsidian trails | Pattern Exporter | `python3 export_pattern_trails.py` |
| ASCII matrix | Manual Toolset | `python3 manual_export_toolset.py matrix` |
| Domain docs | Manual Toolset | `python3 manual_export_toolset.py summary` |
| Automation | Overnight Runner | `python3 overnight_runner_local.py --continuous` |

---

## 📊 Status Tracking

All tool runs update `/unified_overnight_research/CURRENT_STATUS.md`:

```markdown
## ✅ Local Runner Mode Active

Firecrawl API: http://localhost:3002
Containers: All healthy
Last Run: 2026-04-30 15:30:00

### Last Results
- Files Processed: 47
- Patterns Exported: 12
- Duration: 23.4s

Next Steps:
✅ Available runners are ready for local execution!
```

---

## 🛠️ Docker Management

All Firecrawl containers are managed via Docker Compose at `/home/avalonas/.hermes/gematria/firecrawl/docker-compose.yaml`

### Common Commands

| Action | Command |
|--------|---------|
| List containers | `docker compose ps` |
| View logs | `docker compose logs -f` |
| Restart all | `docker compose down && docker compose up -d` |
| Check health | `curl http://localhost:3002` |

### Access via Portainer

1. Open `http://localhost:8000`
2. Login (admin/admin or check config)
3. Navigate to Containers → firecrawl-api-1
4. View logs and manage lifecycle

---

## 🎯 Recommended Workflow

### Daily Analysis Cycle

1. **Morning** - Review overnight results in `CURRENT_STATUS.md`
2. **Midday** - Run manual exports if needed:
   ```bash
   python3 manual_export_toolset.py matrix
   python3 export_pattern_trails.py
   ```
3. **Evening** - Trigger overnight research if not auto-running

### Continuous Mode Setup

```bash
# Start continuous analysis loop
cd /home/avalonas/.hermes/gematria/unified_overnight_research
python3 overnight_runner_local.py --continuous --interval 120

# Or run IMAGE-SEED immediately, then start loop
bash scripts/run_image_seed.sh &
python3 overnight_runner_local.py --continuous
```

---

## 📖 See Also

- [README_RUNNER_LOCAL.md](scripts/README_RUNNER_LOCAL.md) - Local mode overview
- [CURRENT_STATUS.md](../CURRENT_STATUS.md) - Latest system status
- SYSTEM_STATUS.md - Firecrawl container health checks

---

**Created**: 2026-04-30  
**Mode**: Local Runner (Firecrawl Docker + SearXNG optional)  
**Status**: ✅ All tools operational
