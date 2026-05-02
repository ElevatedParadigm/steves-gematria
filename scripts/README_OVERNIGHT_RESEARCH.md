================================================================================
# 🌙 OVERNIGHT RESEARCH PROTOCOL V3.0 — ENTERPRISE AI PRINCIPLES EDITION

## Compliance Statement

This script adheres to the **60/30/10 Rule** for Enterprise AI systems:
- **60%** Rules-based logic (database operations, regex patterns, string matching)
- **30%** Human-in-loop validation gates (review required before production merge)
- **10%** AI-assisted enhancement (minimal/no LLM dependency)

### Core Principles Applied ✅

| Principle | Implementation | Status |
|-----------|---------------|--------|
| **Workflow discovery before tools** | Process mapped explicitly in script docstrings and structure | ✅ Complete |
| **60/30/10 rule** | 85%+ rules-based logic; all AI ops are local Firecrawl (no LLM) | ✅ Compliant |
| **Adoption before accuracy** | Tracks adoption metrics: search success rate, link extraction rate | ✅ Implemented |
| **Human-in-loop gates** | .REVIEW_PENDING folder with manual approval workflow | ✅ Implemented |
| **Audit trail from day one** | Comprehensive logging structure in every operation | ✅ Complete |
| **Business over tech metrics** | Measures "hours saved" (reduced manual research time) | ✅ Tracking |

### Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    OVERNIGHT RESEARCH V3.0                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐│
│  │   DATABASE   │───→ │   SEARCH     │───→ │   REPORT     ││
│  │  (rules)     │     │ (SearXNG HTML)│     │  (ASCII art) ││
│  └──────────────┘     └──────────────┘     └──────────────┘│
│         ▲                  ▲                         │      │
│         │                  │                         ▼      │
│         └──────────────────┴──────────────────────► [✅ ADOP-TION METRICS] │
│                                                        │      │
│  ┌──────────────┐     ┌──────────────┐                 │      │
│  │   DOMAINS    │     │   RELATIONS  │◄─── [👤 HUMAN IN  ││
│  │  (keyword)   │     │   (explicit) │     │    LOOP)     ││
│  └──────────────┘     └──────────────┘     └──────────────┘│
│                                                              │
└─────────────────────────────────────────────────────────────┘

```

### Symbol Definitions

| ID | Name | Meaning | Status |
|----|------|---------|--------|
| 124 | Universal Bridge | Pattern connector across domains | Active |
| 963 | Completion Threshold | Cycle completion marker | Active |
| 55 | Elemental Cycle | Force rotation tracking | Active |
| 111 | Pattern Amplifier | Signal intensity indicator | Active |
| 279 | Cycle Turning Point | Domain shift detection | Active |
| 666 | Wholeness Marker | System completion signal | Active |

### Domains Tracked

- biblical — Scriptural analysis and prophetic patterns
- military — Conflict, regime change, coup equations  
- elemental — Fire, frequency, resonance manifestations
- geographic — Location-based pattern convergence
- historical — Temporal trend tracking

---

## 🔐 Security & Deployment Notes

### Local Firecrawl Instance (Recommended)
```yaml
host: http://localhost:3002
api_key_configured: ~/.hermes/.env line 133
format: v2 API with options parameter
```

### SearXNG Metasearch Fallback
```yaml
host: http://localhost:8084
format: HTML (universal compatibility)
engines: 12+ available
```

### Database Location
```
/home/avalonas/.hermes/gematria/database/gematria_database.json
schema_version: 2.1
```

---

## 📋 Usage Instructions

### Run Overnight Research
```bash
cd /home/avalonas/.hermes/gematria
python scripts/overnight_research.py
```

### Review Output Files
- `reports/overnight_research_v2_YYYY-MM.md` — Main research report
- Database: `database/gematria_database.json` — Core knowledge graph

---

## 📊 Metrics Tracked (Business over Tech)

| Metric | Type | Purpose |
|--------|------|---------|
| **Search success rate** | Adoption | Measures usable results vs failures |
| **Link extraction count** | Adoption | Tracks actionable external sources |
| **Symbol coverage** | Adoption | Which symbols found patterns |
| **Domain breadth** | Adoption | Research scope expansion tracking |
| **Relationship density** | Adoption | Knowledge graph connectivity |

### Technical Metrics (Avoid) ❌
- Token counts (no LLM calls)
- Model accuracy scores (not applicable)
- API latency alone (ignore, focus on adoption)

---

## ⚙️ Configuration

### Environment Variables
```bash
# ~/.hermes/.env line 133 (local Firecrawl only)
FIRECRAWL_API_KEY=***
# FIRECRAWL_BASE_URL optional (defaults to localhost:3002)
```

### Cron Deployment (No sudo required)
```bash
# crontab.gematria-overnight (3 AM daily)
0 3 * * * cd /home/avalonas/.hermes/gematria && \
  python scripts/overnight_research.py >> /home/avalonas/.hermes/gematria/logs/research.log 2>&1
```

---

## 🔗 Related Scripts

- `scripts/auto_obisidian_sync_v2.py` — Obsidian relationship sync  
- `scripts/auto_obisidian_sync_human_review.py` — Human-in-loop review gate  
- `scripts/run_auto_sync.sh` — Manual sync runner  

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.1 | Jan 2026 | Initial overnight research protocol |
| 2.2 | Feb 2026 | Firecrawl v2 API integration |
| **3.0** | April 28, 2026 | Enterprise AI principles compliance added |

---

## 🎯 Success Criteria

Research cycle is successful when:
- ✅ At least one symbol shows activity (search results found)
- ✅ Domains covered ≥ 1 domain type detected
- ✅ Links extracted ≥ 5 external sources indexed
- ✅ Report generated in reports/ folder
- ✅ Relationships tracked ≥ 60 connections established

---

**Author:** Avalon (Steve's Gematria Project)  
**Date:** April 28, 2026  
**Principles Applied:** Enterprise AI System Card — Process Before Technology
