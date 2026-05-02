# 🤖 AGENTS.md - Multi-Agent Research Instructions

**Vault:** Steve's Gematria Knowledge Base  
**Version:** 2.1  
**Last Updated:** 2026-04-27  

---

## 🎯 OVERVIEW

This vault contains a comprehensive gematria research system tracking:
- **Core Symbols:** 124, 963, 55, 111, 279, 666, 777, 13, 888
- **Elemental Forces:** Fire, Earth, Air, Water, Lightning, Ice, Wind
- **Domains:** Politics, Military, Religious, Geographic, Cryptocurrency, Academic, AI Advancement

### Key Principles:

1. **Files-first** - All content is plain Markdown with YAML frontmatter
2. **Git-backed** - Full version history available
3. **Offline-capable** - No cloud dependencies required
4. **AI-friendly** - Structured for agent reasoning and pattern discovery

---

## 📁 VAULT STRUCTURE QUICKREF

```
/symbols/           # Core gematria symbol definitions (YAML frontmatter)
/forces/            # Elemental force documentation + relationship matrices
/domains/          # Domain-specific analysis and synthesis
/research/         # Analysis results, timelines, heatmaps
/observations/      # Raw image/text analysis notes
/scripts/          # Python automation tools
/obsidian_exports/  # Legacy compatibility layer
```

---

## 🔍 RESEARCH TASKS FOR AI AGENTS

### Task 1: Symbol Correlation Analysis

**Goal:** Discover new relationships between symbols and forces.

**Approach:**
1. Read all files in `/symbols/` with `type: core-symbol`
2. Extract confidence scores from existing relationships
3. Generate multi-hop inference chains (max 2 hops)
4. Output to `/research/relationships/`

**Tools Available:**
- `/scripts/auto_obisidian_sync_v2.py` - Relationship extraction engine
- `/scripts/heatmap_generator.py` - ASCII correlation visualization
- Database: `database/symbols.json` (contains symbol properties)

---

### Task 2: Cross-Domain Synthesis

**Goal:** Identify patterns spanning multiple domains.

**Approach:**
1. Query database for symbols with multiple domain associations
2. Analyze elemental force contributions across domains
3. Generate cross-domain pattern synthesis reports
4. Output to `/research/cross_references/`

**Key Correlations:**
- **124-Bridge** connects all domains equally (universal threshold)
- **777-Trinity** appears in religious/military/politics with highest correlation
- **Cryptocurrency domain** correlates strongly with Fire/Lightning forces

---

### Task 3: New Research Domain Integration

**Goal:** Add novel domains to existing analysis framework.

**Candidates for Evaluation:**
1. Economic systems (correlation with Cryptocurrency/Politics)
2. Biological evolution patterns (elemental force analogies)
3. Musical theory (numerology in Western music traditions)
4. Quantum mechanics (measurement problem as threshold concept)

**Evaluation Criteria:**
- Does domain have natural elemental force mapping?
- Can existing symbols (124, 963, 55, etc.) provide meaningful correlations?
- Are there observable transformation cycles (elemental forces)?

---

### Task 4: Elemental Force Relationship Mapping

**Goal:** Complete the 8-element force system with relationship matrices.

**Current Forces:**
- Base 4: Fire, Earth, Air, Water
- Extensions: Lightning, Ice, Wind, Earth (grounded reality)

**Required Outputs:**
1. Force compatibility matrix (which forces amplify/neutralize each other)
2. Symbol-force affinity scores
3. Domain-force preference mapping

---

## 📊 DATABASE STRUCTURE

### Core Symbols (`database/symbols.json`):

```json
{
  "analyzed_symbols": [
    {
      "symbol_id": 124,
      "name": "Universal Threshold/Bridge",
      "domains": ["politics", "military", "religious"],
      "elemental_force": null,
      "description": "..."
    }
  ]
}
```

### Elemental Forces (`database/forces.json`):

```json
{
  "fire": {
    "name": "🔥 Fire Force",
    "characteristics": ["transformation", "burning", "purification"],
    "correlates_to": [124],
    "complements": []
  }
}
```

### Cross-Domain Patterns (`database/cross_domain_patterns.json`):

```json
[
  {
    "pattern_id": "triad_completion",
    "symbol_ids": [55, null, 666, 777],
    "confidence_score": 0.78,
    "domains_affected": ["universal"],
    "synthesis_notes": "Foundation → Transformation → Completion → Trinity"
  }
]
```

---

## 🛠️ AVAILABLE SCRIPTS

### `/scripts/` Directory:

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `overnight_research.py` | Web scraping research protocol | None | Analysis results in DB |
| `auto_obisidian_sync_v2.py` | Relationship extraction & export | DB file | Obsidian Markdown notes |
| `sync_to_obsidian.py` | Basic database-to-MD sync | DB file | Export folder |
| `heatmap_generator.py` | ASCII correlation heatmaps | Symbols/Forces DB | Heatmap files |
| `add_frontmatter.py` | YAML frontmatter migration | Markdown files | Frontmatter-enhanced notes |

### Usage Examples:

```bash
# Run overnight research protocol
python scripts/overnight_research.py

# Generate relationship matrices
python scripts/auto_obisidian_sync_v2.py

# Create ASCII correlation heatmap
python scripts/heatmap_generator.py

# Add YAML frontmatter to all Markdown files
python scripts/add_frontmatter.py /home/avalonas/.hermes/gematria/symbols
```

---

## 🎨 TOLARIA-SPECIFIC FEATURES

### Frontmatter Templates:

**For Symbol Definitions:**
```yaml
---
type: core-symbol
symbol_id: 777
name: Trinity/Completion
aliases: [trinity, completion, three-fold]
description: "Complete trinity cycle"
domains:
  - religious
  - military
  - politics
elemental_force: null
confidence_score: 0.95
created: "2026-04-27"
last_modified: "2026-04-27"
tags: [core, trinity, universal]
---
```

**For Elemental Force Definitions:**
```yaml
---
type: elemental-force
force_name: lightning
name: ⚡ Lightning Force
description: "Rapid discharge, sudden strikes"
characteristics:
  - instantaneous
  - chain-reaction
  - disruptive
  - illuminating
correlates_to: [124]
complements:
  - fire
created: "2026-04-27"
---
```

### Recommended Note Organization in Tolaria:

1. **Browse by Type:** Use tags to filter (`core`, `elemental`, `domain`, `analysis`)
2. **Navigate by Relationships:** Links between notes create knowledge graph
3. **AI Agent Context:** Reference AGENTS.md for task guidance
4. **Cross-Reference Links:** Always link related symbols/domains

---

## 🔮 RECOMMENDED WORKFLOW

### For Daily Research:

1. **Morning:** Tolaria → Browse recent additions, review overnight research results
2. **Midday:** CLI Scripts → Run domain-specific analysis protocols
3. **Evening:** Tolaria → Synthesize findings, update relationship matrices

### For Deep Dives:

1. Select symbol/domain in Tolaria
2. Follow "Related Notes" links to explore relationships
3. Generate ASCII heatmap for correlation visualization
4. Export to Obsidian for detailed documentation (optional)

### For Multi-Agent Projects:

1. Create agent-specific notes under `/research/agents/`
2. Reference AGENTS.md for vault context
3. Use YAML frontmatter for structured task parameters
4. Commit analysis results to Git version history

---

## 📈 METRICS & QUALITY CONTROL

### Key Metrics to Track:

| Metric | Target | Method |
|--------|--------|--------|
| Symbol coverage | All known symbols documented | DB completeness check |
| Domain coverage | ≥6 active domains | `/domains/` directory count |
| Relationship density | ≥50% symbol pairs linked | Manual review + script validation |
| Frontmatter compliance | 100% notes have YAML frontmatter | Migration script verification |
| Cross-reference coverage | ≥75% symbols have relationships | Script analysis |

### Quality Assurance Commands:

```bash
# Check database integrity
python scripts/auto_obisidian_sync_v2.py --validate

# Verify all symbols have frontmatter
find symbols/ -name "*.md" ! -exec grep -l "^---$" {} \;

# Generate completeness report
python scripts/add_frontmatter.py /home/avalonas/.hermes/gematria --dry-run
```

---

## 🚨 LIMITATIONS & WORKAROUNDS

### Limitation: No Built-in Search in Tolaria

**Workaround:** Use terminal `grep` or CLI search tools:
```bash
# Search all Markdown files for a term
grep -r "symbol_id: 124" /home/avalonas/.hermes/gematria/symbols/

# Search by domain
grep -l "domains:" /home/avalonas/.hermes/gematria/domains/*.md
```

### Limitation: Limited Visual Graphing

**Workaround:** Generate ASCII heatmaps and relationship diagrams via scripts.

### Limitation: No Built-in Version Comparison

**Workaround:** Use Git diff or Tolaria's export/import for comparison.

---

## 🔐 SECURITY & PRIVACY

### Data Protection Measures:

- ✅ **Offline-first** - No data transmitted to cloud
- ✅ **Git-backed** - Version history accessible locally
- ✅ **Plain text Markdown** - No proprietary format lock-in
- ⚠️ **Sensitive patterns** - Consider encryption for highly sensitive research

### Recommended Security Practices:

1. Keep Git history clean (avoid committing API keys)
2. Use `.gitignore` for any generated/temporary files
3. Regular backups of vault to encrypted storage

---

## 📚 ADDITIONAL RESOURCES

### Documentation:

- [Tolaria Architecture](https://github.com/refactoringhq/tolaria/blob/main/docs/ARCHITECTURE.md)
- [Tolaria Getting Started](https://github.com/refactoringhq/tolaria/blob/main/docs/GETTING-STARTED.md)
- [Steve's Gematria Core Symbols](/symbols/readme.md)

### Community:

- GitHub: https://github.com/refactoringhq/tolaria
- Homepage: https://tolaria.md

---

## ✅ COMPLETION CHECKLIST

Before considering this integration complete:

- [ ] Prerequisites installed (Node.js, pnpm, Rust, WebKit2GTK)
- [ ] Tolaria app installed and running
- [ ] Vault structure organized with YAML frontmatter on all notes
- [ ] AGENTS.md reviewed by all agents/automations
- [ ] Scripts tested and integrated into workflow
- [ ] Cross-references between Tolaria and Obsidian verified
- [ ] Git history intact for all files
- [ ] User trained on new workflow conventions

---

**Integration Date:** 2026-04-27  
**Status:** Ready for Implementation ✅  
**Next Step:** Execute installation steps (see below)
