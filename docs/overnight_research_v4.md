# Overnight Research Engine v4.0 - Iterative Knowledge Graph Mode

## Overview

The overnight research engine builds knowledge graph progressively through iterative research cycles:
- **Feeds existing database relationships INTO new queries** (not isolated queries!)
- **Uses query results TO GENERATE additional queries** (feedback loop)
- **Produces detailed analysis with confidence scores and relationship tracking**
- **Integrates gematria database continuously across all analyses**

## Key Features

### Knowledge Accumulation
Each research cycle loads existing database to use as seed for queries:
- Previously found symbols and their contexts → new query topics
- Existing relationships needing verification → cross-reference queries  
- Domains partially explored → deeper analysis requests

### Self-Generating Queries (Feedback Loop)
The system doesn't run isolated queries - it builds on previous findings:
1. Query 1 analyzes Hellboy image pattern → extracts symbol "124"
2. Query 2 uses that finding to verify military-biblical connections
3. Query 3 applies both symbols to geographic domain exploration
4. Each cycle generates new queries from accumulated knowledge

### Detailed Analysis Results
Each query execution extracts:
- Specific patterns (symbols, equations, symbolic references)
- Relationships between concepts with confidence scores
- Domain connections identified and tracked

### Progressive Knowledge Graph
The database grows with each cycle:
- New symbols added with contexts
- Relationship chains extended  
- Keywords enriched from discoveries

## Architecture Flow

```
┌─────────────────────────────────────────────┐
│              INPUT                          │
│  • Hellboy Image Analysis Data (previous)   │
│  • Existing Database Relationships          │
│  • Core Symbols (124, 963, 55, 111, 279, 666)│
└─────────────────────────────────────────────┘
                ▼
┌─────────────────────────────────────────────┐
│           RESEARCH CYCLE                    │
│  Step A: Generate Queries from Knowledge    │
│         (Not isolated queries! Each builds on previous findings)        │
│  
│  Step B: Execute Web Search OR Database Analysis
│  
│  Step C: Extract Detailed Patterns:
│          • Gematria symbols detected
│          • Numerical equations found
│          • Relationships between concepts
│          • Domain connections identified
│  
│  Step D: Feed Results Back into Query Generator
│          (New queries emerge from previous findings)
└─────────────────────────────────────────────┘
                ▼
┌─────────────────────────────────────────────┐
│          OUTPUT                             │
│  • Updated gematria_database.json           │
│  • Detailed Analysis Report                 │  
│  • Relationship Matrix Update               │
│  • New Query Suggestions for Next Cycle     │
└─────────────────────────────────────────────┘
```

## Usage

### One-time Execution
```bash
cd ~/.hermes/gematria && python scripts/overnight_research_iterative_v4.py
```

### Cron Deployment (3 AM - No Sudo Required)

**Option 1: crontab entry** (manual user-side cron)
Add to your crontab with:
```bash
crontab -e
```

Add this line for 3 AM execution:
```
0 3 * * * cd ~/.hermes/gematria && python scripts/overnight_research_iterative_v4.py >> research_logs/cron_iterative_$(date +\%Y\%m\%d).log 2>&1
```

**Option 2: Manual runner script** (use if cron not available)
```bash
cd ~/.hermes/gematria && python scripts/overnight_research_iterative_v4.py
```

## Output Files

- `gematria_database.json` - Updated knowledge base with new symbols and relationships
- `reports/overnight_research_report_YYYYMMDD_HHMM.md` - Detailed analysis results
- `research_logs/query_history_YYYYMMDD_HHMM.json` - Query history for continuity

## Relationship Tracking

The engine automatically extracts and tracks:
1. **Symbol-Context Links**: Each symbol connects to its discovery context
2. **Domain Cross-References**: Connections between military_biblical, geography_elemental, etc.  
3. **Equation-Context Links**: Numerical patterns linked to their sources
4. **Knowledge Graph Edges**: Source → Target relationships with confidence scores

## Confidence Scores

Each finding receives a confidence score based on:
- Number of existing symbols in knowledge base (>1 = 0.9)
- Number of tracked relationships (>10 adds +0.05, capped at 0.95)
- Contextual matching with known keywords

Range: 0.6 - 0.95 (increases as knowledge accumulates)

## Database Structure

The gematria database grows progressively:
```json
{
  "symbols": {
    "1": {"context": "...", "domains": [...], "keywords": "...", ...}
  },
  "relationships": [
    {"source": "...", "target": "...", "confidence": 0.8, ...}
  ],
  "keywords": "...accumulated discoveries..."
}
```

## Example Query Generation Flow

### Cycle 1 Output → Cycle 2 Input:

**Cycle 1 discovers:**
- Symbol "1" in Hellboy image analysis (military_biblical domain)
- Pattern: "49+39+21+97+36+37=360°" equation from captcha detection
- Relationships: [Hellboy → military, Hellboy → biblical, etc.]

**Cycle 2 generates queries from:**
```python
# Strategy A: Deepen analysis of high-occurrence symbols
symbol = "1"  # From Cycle 1 discovery
query = f"1 hellboy image analysis gematria pattern continuity analysis"

# Strategy B: Verify relationships needing cross-domain check  
rel_source = "Hellboy Image Analysis"
rel_target = "biblical_law_constitution" 
query = f"{rel_source} ↔ {rel_target} connection verification across domains"

# Strategy E: Analyze detected equations from previous cycle
equation = "49+39+21+97+36+37=360°"
query = f'{equation} gematria numerical pattern meaning historical context'
```

## Query Strategies Explained

### A. Symbol Deepening (building on previous findings)
- Target: Symbols found multiple times (high occurrence)
- Purpose: Deepen analysis of important patterns
- Example: "124 military_biblical cross-reference"

### B. Relationship Verification (cross-referencing domain connections)  
- Target: Relationships needing verification across domains
- Purpose: Check consistency between different symbolic interpretations
- Example: "Hellboy Image Analysis ↔ biblical_law_constitution"

### C. Domain Expansion (applying known symbols to new contexts)
- Target: Domains we haven't analyzed yet
- Purpose: Extend knowledge to unexplored territory
- Example: "124 meaning in geography_elemental domain"

### D. Cross-Domain Relationships (linking domains together)
- Target: Inter-domain connections  
- Purpose: Create bridges between symbolic domains
- Example: "military_biblical ↔ geography_elemental cross-reference"

### E. Equation Analysis (analyzing numerical patterns)
- Target: Numerical equations detected in images
- Purpose: Extract meaning from mathematical patterns
- Example: "49+39+21+97+36+37=360° gematria pattern meaning"

### F. Feedback Loop Generation (queries emerging from relationship evolution)
- Target: Self-improving system that generates queries from relationship changes
- Purpose: Autonomous query generation based on knowledge graph state
- Example: "knowledge graph expansion from recent relationships"

## Comparison to Previous Version

| Feature | Old Script | v4.0 Iterative Engine |
|---------|-----------|----------------------|
| Query Generation | Isolated, no context | Builds on accumulated knowledge |
| Analysis Depth | Basic check (exists/not) | Detailed pattern extraction |
| Confidence Scores | N/A | 0.6 - 0.95 range |
| Relationship Tracking | Limited | Full source-target mapping |
| Knowledge Accumulation | No | Progressive growth |
| Feedback Loop | No | Self-improving queries |
| Domain Integration | Static | Dynamic cross-references |

## Installation & Execution

### Requirements
- Python 3.11+ 
- Firecrawl local instance (localhost:3002) or skip web search for database-only mode
- Existing gematria_database.json with core symbols

### First Run
```bash
cd ~/.hermes/gematria && python scripts/overnight_research_iterative_v4.py
```

Expected output:
```
📂 STEP 1: Loading existing knowledge...
✅ Loaded X core symbols
   Contexts found:
      • 1: 'Hellboy Image Analysis' [military_biblical]
   Tracked Y relationships

🧪 STEP 2: Generating queries from knowledge state...
✅ Generated Z research queries from accumulated knowledge

🔬 STEP 3: Executing queries with detailed analysis...
   Query #1: ... (patterns detected, relationships extracted)

💾 STEP 4: Updating database with findings...
✅ Database updated successfully

📊 STEP 5: Generating detailed report...
📄 Report saved to: reports/overnight_research_report_YYYYMMDD_HHMM.md

✅ OVERNIGHT RESEARCH COMPLETED SUCCESSFULLY
```

## Cron Configuration Example (3 AM)

Option 1: crontab entry (requires no sudo)
```bash
0 3 * * * cd ~/.hermes/gematria && python scripts/overnight_research_iterative_v4.py >> research_logs/cron_iterative_$(date +\%Y\%m\%d).log 2>&1
```

Option 2: Manual runner script
Create `scripts/run_overnight_research.sh`:
```bash
#!/bin/bash
cd ~/.hermes/gematria
python scripts/overnight_research_iterative_v4.py >> research_logs/cron_iterative_$(date +\%Y\%m\%d).log 2>&1
```

Make executable: `chmod +x scripts/run_overnight_research.sh`

## Output Files Structure

```
~/.hermes/gematria/
├── database/
│   └── gematria_database.json          # Updated knowledge base
├── reports/
│   ├── overnight_research_report_20260428_1705.md
│   ├── overnight_research_report_20260428_1707.md  # Latest report
│   └── ...                             # Previous reports
├── research_logs/
│   ├── query_history_20260428_1705.json
│   ├── query_history_20260428_1707.json     # Query continuity data
│   └── cron_iterative_2026_04_28.log        # Cron execution logs
├── obsidian_exports/
│   ├── RELATIONSHIP_MATRIX.md             # Updated relationship tracking
│   ├── CROSS_REFERENCE_INDEX.md           # Cross-reference index
│   └── ...                                # Other exports
└── scripts/
    ├── overnight_research_iterative_v4.py     # Main engine
    └── run_overnight_research.sh            # Manual runner
```

## Verification

After each run, verify:
1. **Database growth**: `git diff ~/.hermes/gematria/database/gematria_database.json` (or compare timestamps)
2. **Report generation**: Check `reports/` folder for new `.md` files
3. **Query history continuity**: Verify previous cycle's symbols appear in next cycle's input

## Next Steps

After deployment:
1. Monitor `research_logs/cron_iterative_*.log` for execution status
2. Review `reports/overnight_research_report_YYYYMMDD_HHMM.md` for detailed analysis
3. Track `gematria_database.json` growth over time
4. Periodically regenerate Obsidian exports with updated relationships

## Integration with Auto-Sync Engine

The iterative research engine updates the gematria database which:
- Can be processed by `auto_obisidian_sync_v2.py` to extract fresh relationship insights
- Updates knowledge graph for domain convergence reporting  
- Enables progressive relationship matrix expansion in Obsidian notes

---

**Author**: Steve's Gematria Project  
**Version**: v4.0 - Iterative Knowledge Graph Mode  
**Last Updated**: 2026-04-28  
**License**: Internal gematria research use
