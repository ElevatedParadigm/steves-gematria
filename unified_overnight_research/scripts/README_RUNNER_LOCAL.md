# 🧬 Steve's Gematria IMAGE-SEED Runner (Local Mode)

## ✅ Current Status

### Firecrawl Services
| Service | Container ID | Status | Notes |
|---------|--------------|--------|-------|
| **Firecrawl API** | `firecrawl-api-1` | ✅ Running | Local Docker on port 3002 |
| **Redis** | `redis:alpine` | ✅ Running | Cache layer |
| **RabbitMQ** | `rabbitmq:3-management` | ✅ Running | Message queue |
| **SearXNG Search** | Not started | ⚠️ Optional | Needed for full web scraping |

### Available Runners
- ✅ **IMAGE-SEED mode**: Local image analysis + Firecrawl search (works without SearXNG)
- ⏸️ **Overnight loop**: Full automated research (requires SearXNG)
- 🔄 **Manual export**: Export tools (no web scraping needed)

---

## 🚀 Running IMAGE-SEED with Local Firecrawl

The `run_image_seed.sh` script is ready to use! It will:

1. **Read from your image vault** (`/home/avalonas/Pictures/Steves gematria`)
2. **Extract patterns** using local Firecrawl API (`http://localhost:3002`)
3. **Process symbol galleries** and domain clusters
4. **Handle missing search gracefully** (falls back to direct scraping)

### Quick Start

```bash
cd /home/avalonas/.hermes/gematria/unified_overnight_research/scripts
bash run_image_seed.sh
```

This will:
- ✅ Extract anchor terms from image filenames
- ✅ Run local Firecrawl pattern extraction
- ✅ Process symbol correlations automatically
- ✅ Output results to `/unified_overnight_research/output/`

---

## 📊 What Gets Processed

The script processes files matching these patterns:

| Pattern | Purpose | Examples |
|---------|---------|----------|
| `*_CYCLE_*` | Cycle analysis galleries | `domain938_CYCLE1.png`, `domain938_CYCLE2_cycle666.png` |
| `*_DOMAIN_*` | Domain clusters | `domain938_CORRELATION_124_666_9.png` |
| `*_MATRIX_*` | Matrix/structure analysis | Various matrix types for symbol relationships |

### Anchor Term Extraction Logic

The script automatically identifies anchor terms:
- `[ANCHOR:CYCLE]` → Files with "cycle" in filename
- `[ANCHOR:DOMAIN]` → Files with domain/cluster/matrix keywords  
- `[ANCHOR:CORRELATION]` → Default fallback

---

## 🛠️ Available Export Tools

Since you're using local runner scripts, here are useful export tools:

### 1. **Pattern Trail Exporter**
Export the chain of symbol discoveries as text files:
```bash
# This creates readable trails in Obsidian/terminal format
python3 /home/avalonas/.hermes/gematria/unified_overnight_research/export_pattern_trails.py
```

### 2. **Symbol Correlation Matrix**
Generate ASCII heatmap of symbol relationships:
```bash
python3 /home/avalonas/.hermes/gematria/unified_overnight_research/correlation_matrix_exporter.py
```

### 3. **Domain Summary Generator**
Create summary documents per domain cluster:
```bash
python3 /home/avalonas/.hermes/gematria/unified_overnight_research/domain_summary_generator.py
```

---

## 📋 Next Options - What Would You Like to Do?

**A)** Run the IMAGE-SEED script now (analyzes your image vault)

**B)** Create a new export tool for pattern trails (Obsidian-friendly)

**C)** Set up an overnight runner that works without SearXNG

**D)** Create manual export scripts for existing galleries

**E)** Something else... tell me what!

Just reply with the letter or describe what you'd like to build! 🎯
