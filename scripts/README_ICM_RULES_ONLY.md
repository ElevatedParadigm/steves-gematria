# 📋 Information Collection Manual (ICM) — Rules-Only Research

## Overview

The **ICM (Information Collection Manual)** is a simplified, rules-based approach to overnight research that follows the principle: *"A simple folder structure is often better than complex AI frameworks."*

### Enterprise AI Principle Applied ✅

> **"Framework-first thinking" pitfall:** Choosing complex AI frameworks before understanding the workflow.

**Our ICM Solution:**
- ✅ Simple folder structure (ICM) for sequential human-reviewed work
- ✅ No LLM dependencies
- ✅ Maximum adoption with minimal complexity
- ✅ Clear separation of concerns across folders

---

## Usage Instructions

### Run ICM Cycle

```bash
cd /home/avalonas/.hermes/gematria
python scripts/icm_rules_only.py
```

### Output Structure

```
research_icm/
├── 00_search_queries/     ← Raw search queries
│   └── search_manifest.md
├── 01_link_collection/    ← Extracted links  
│   └── links_manifest.md
├── 02_domain_notes/       ← Domain-specific notes
│   ├── biblical_notes.md
│   ├── military_notes.md
│   ├── elemental_notes.md
│   ├── geographic_notes.md
│   └── historical_notes.md
├── 03_pattern_tracking/   ← Symbol pattern logs
│   ├── 124_pattern.log
│   ├── 963_pattern.log
│   ├── 55_pattern.log
│   ├── 111_pattern.log
│   ├── 279_pattern.log
│   └── 666_pattern.log
├── 04_review_pending/     ← Items for human review
└── 05_approved/           ← Approved findings
    └── *.md
```

---

## Workflow Steps

| Step | Folder | Purpose | Human Action Required |
|------|--------|---------|----------------------|
| **1. Search** | `00_search_queries/` | Create search manifest | Review queries before execution |
| **2. Links** | `01_link_collection/` | Collect extracted links | Verify link quality manually |
| **3. Notes** | `02_domain_notes/` | Create domain notes | Add observations manually |
| **4. Tracking** | `03_pattern_tracking/` | Track symbol patterns | Review pattern emergence |
| **5. Review** | `04_review_pending/` | Queue items for review | Approve/reject manually |
| **6. Approval** | `05_approved/` | Move approved findings | Delete from pending after review |

---

## Advantages vs. Overnight Research V2

| Feature | ICM (Rules-Only) | Overnight V2 |
|---------|------------------|--------------|
| **AI Dependencies** | None ✅ | Local Firecrawl only |
| **Complexity** | Minimal ✅ | Moderate |
| **Human Control** | 100% manual ✅ | 85% automated, 15% review |
| **Adoption Rate** | High (simple) ✅ | Medium (requires setup) |
| **Best For** | Initial research | Production research |

---

## When to Use Each Script

### Use ICM (`icm_rules_only.py`) When:
- ✅ Starting fresh research without prior data
- ✅ Need maximum human control
- ✅ Testing new domains or patterns
- ✅ Building reference materials manually

### Use Overnight Research V2 When:
- ✅ Running scheduled overnight cycles
- ✅ Processing existing database entries  
- ✅ Auto-generating relationship graphs
- ✅ Scaling research production

---

## Enterprise AI Principles Compliance

| Principle | Implementation | Status |
|-----------|---------------|--------|
| **Workflow discovery before tools** | Explicit folder structure documented | ✅ Complete |
| **60/30/10 rule** | 100% rules-based, 0% AI | ✅ Compliant |
| **Adoption before accuracy** | Simple structure = high adoption | ✅ Achieved |
| **Human-in-loop gates** | All items go through review pending | ✅ Active |
| **Audit trail from day one** | Every file timestamped | ✅ Complete |
| **Business over tech metrics** | Tracks folder contents, not tokens | ✅ Tracking |

---

## Folder Purposes Explained

### `00_search_queries/`
- **Purpose:** Define what we're searching before executing
- **Key File:** `search_manifest.md` — Lists all queries to run
- **Human Action:** Review and approve queries in manifest

### `01_link_collection/`  
- **Purpose:** Extract links from search results
- **Key File:** `links_manifest.md` — Raw link collection log
- **Human Action:** Verify link relevance manually

### `02_domain_notes/`
- **Purpose:** Track domain-specific observations
- **Key Files:** One `.md` file per domain with keyword tracking
- **Human Action:** Add observations and pattern notes

### `03_pattern_tracking/`
- **Purpose:** Log symbol activity over time
- **Key Files:** One `.log` file per core symbol
- **Human Action:** Review pattern emergence daily

### `04_review_pending/`
- **Purpose:** Queue items for human review
- **Contents:** Any findings marked for validation
- **Human Action:** Approve or reject each item

### `05_approved/`
- **Purpose:** Store approved findings for production use
- **Contents:** Only manually validated files
- **Human Action:** Delete from pending after approval

---

## Migration from ICM to Production

Once you have items in `04_review_pending/`:

```bash
# 1. Review each file manually in your text editor
# 2. Move approved files:
cp 04_review_pending/*.md 05_approved/

# 3. Optionally merge into obsidian_exports:
cp 05_approved/ICM_FINDINGS.md \
   obsidian_exports/CORE_SYMBOLS_SUMMARY.md

# 4. Clean up review pending:
rm 04_review_pending/*.md
```

---

## Troubleshooting

### Issue: "No items to move to review"
**Cause:** No domain notes have been edited yet  
**Solution:** Add observations manually to `02_domain_notes/` files first

### Issue: "Folder not found"
**Cause:** Running from wrong directory  
**Solution:** Ensure you're in `/home/avalonas/.hermes/gematria/`

---

## Related Documentation

- [`README_OVERNIGHT_RESEARCH.md`](../scripts/README_OVERNIGHT_RESEARCH.md) — Overnight research protocol
- [`README_HUMAN_REVIEW_GATE.md`](../scripts/README_HUMAN_REVIEW_GATE.md) — Review gate workflow
- [`ENTERPRISE_AI_COMPLIANCE_REPORT.md`](../ENTERPRISE_AI_COMPLIANCE_REPORT.md) — Full compliance documentation

---

**Author:** Avalon (Steve's Gematria Project)  
**Version:** 1.0 ICM Rules Edition  
**Principle Source:** Enterprise AI System Card — "Simple folder structure over complex frameworks"  
