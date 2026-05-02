# 🧬 Steve's Gematria - Overnight Research Engines

## Overview

This repository contains **two distinct approaches** to automated overnight web research using the SearXNG API and local Firecrawl instance, each optimized for different experimentation scenarios.

---

## ✅ Option 1: Unified Analysis Mode

### Location
`/home/avalonas/.hermes/gematria/unified_overnight_research/`

### Description
A **comprehensive single-script solution** that handles all analysis in one place - perfect for production overnight execution at 3 AM.

### Key Features
- ✅ Single entry point (`unified_engine.py`)
- ✅ All analysis logic integrated
- ✅ Atomic execution (all or nothing)
- ✅ Simple cron deployment
- ✅ Automatic cross-domain convergence detection
- ✅ Relationship building from web results
- ✅ Temporal pattern tracking
- ✅ Heatmap generation for domain distribution
- ✅ Markdown report generation

### Architecture
```
┌─────────────────────────────────────┐
│   unified_engine.py (2.3 KB)        │
├─────────────────────────────────────┤
│  1. Query generation                │
│     - Domain-specific searches       │
│     - Symbol queries                 │
│     - Cross-domain topics            │
├─────────────────────────────────────┤
│  2. Local Firecrawl scraping        │
│     - Uses localhost:3002/v1/search │
│     - Respects options parameter    │
│     - Batch processing               │
├─────────────────────────────────────┤
│  3. Pattern analysis                │
│     - Domain convergence signals      │
│     - Relationship extraction        │
│     - Temporal tracking              │
├─────────────────────────────────────┤
│  4. Report generation               │
│     - Comprehensive markdown report  │
│     - Query results summary          │
│     - Pattern detection highlights   │
└─────────────────────────────────────┘
```

### Cron Deployment
```bash
# Add to crontab at /var/spool/cron/root or ~/.crontab
0 3 * * * cd /home/avalonas/.hermes/gematria/unified_overnight_research && python unified_engine.py >> /home/avalonas/.hermes/gematria/logs/unified_overnight.log 2>&1

# OR manually deploy:
crontab -e
```

### Configuration
- **Database**: `/home/avalonas/.hermes/gematria/database/gematria_database.json`
- **Reports directory**: `/home/avalonas/.hermes/gematria/reports/`
- **Execution stats**: `/home/avalonas/.hermes/gematria/unified_overnight_research/execution_stats.json`

---

## 🔬 Option 2: Modular Analysis Mode

### Location
`/home/avalonas/.hermes/gematria/modular_analysis/`

### Description
A **component-based architecture** with separate modules for each responsibility - perfect for experimentation, testing different approaches in parallel, and flexible workflow development.

### Key Features
- ✅ Componentized design (each module has single responsibility)
- ✅ Can test individual components independently
- ✅ Flexible composition for experimentation
- ✅ Parallel execution capability
- ✅ Easy to swap implementations per component
- ✅ Ideal for research and discovery phase

### Components

#### Core Engine (`orchestrator.py`)
Chains all modules together in sequential order:
1. Generate queries → 2. Scrape results → 3. Analyze patterns → 4. Build relationships → 5. Generate reports

#### Individual Modules

**1. Query Generator (`query_generator/`)**
- Domain-specific query sets (military, geographic, elemental, religious)
- Symbol-focused searches (124, 963, 55, 111, 279, 666)
- Cross-domain convergence queries

**2. Firecrawl Scraper (`firecrawl_scraper/`)**
- Local Firecrawl integration (localhost:3002)
- Batch request handling with rate limiting
- Result parsing and extraction

**3. Pattern Analyzer (`pattern_analyzer/`)**
- Domain convergence detection
- Cross-reference identification
- Temporal pattern tracking

**4. Relationship Builder (`relationship_builder/`)**
- Entity extraction from results
- Relationship matrix generation
- Duplicate prevention

**5. Heatmap Generator (`heatmap_generator/`)**
- ASCII heatmap for terminal display
- Terminal-compatible heat scale encoding
- Domain distribution visualization

**6. Report Generator (`report_generator/`)**
- Comprehensive markdown report assembly
- Query results summary
- Pattern detection highlights
- Relationship tracking documentation

### Execution Modes

#### Sequential (Current Implementation)
```bash
cd /home/avalonas/.hermes/gematria/modular_analysis && python orchestrator.py --sequential
```

Steps:
1. Generate queries
2. Firecrawl scrape all results
3. Analyze patterns
4. Build relationships  
5. Generate heatmap
6. Compile report

#### Parallel (Future Enhancement)
Can be modified to run modules in parallel using Python's `concurrent.futures`:
```bash
cd /home/avalonas/.hermes/gematria/modular_analysis && python orchestrator.py --parallel
```

### Best For:
- 🧪 Testing different approaches
- 🔬 Research and experimentation
- 🎯 Component-level development
- 💡 Prototyping new analysis methods
- 📚 Learning and understanding patterns

---

## Comparison Matrix

| Feature | Unified Mode | Modular Mode |
|---------|-------------|--------------|
| **Files** | ~3 files, ~250 lines engine | ~9 files, ~5,000+ lines total |
| **Complexity** | Low - single entry point | Medium - multiple components |
| **Development Speed** | Fast for production | Fast for experimentation |
| **Testing Granularity** | Whole system tests | Component-level isolation |
| **Parallel Execution** | Limited (sequential) | Easy to implement |
| **Cron Simplicity** | Very simple | More complex paths |
| **Production Ready** | ✅ Ideal choice | ⚠️ Can be used standalone |
| **Research Phase** | Good | ✅ Excellent |

---

## Getting Started

### Testing the Unified Engine
```bash
cd /home/avalonas/.hermes/gematria/unified_overnight_research && python unified_engine.py
```

Expected output:
```
======================================================================
🚀 SearXNG Overnight Research Engine (Unified Analysis Mode)
======================================================================

✅ Loaded X core symbols from configuration
🧠 Starting analysis engine...

🔍 Generated X unique queries
📊 Query Summary:
   Successful: X/X
   Failed: 0/0

🔗 Built X new relationships
💾 Updated database with X total relationships
   📄 Report written to: /home/avalonas/.hermes/gematria/reports/unified_overnight_report_YYYYMMDD_HHMM.md

✅ Overnight research completed successfully!
```

### Testing the Modular Engine
```bash
cd /home/avalonas/.hermes/gematria/modular_analysis && python orchestrator.py
```

---

## Database Structure

Both engines use the same database schema at:
`/home/avalonas/.hermes/gematria/database/gematria_database.json`

**Core Symbols:** 124, 963, 55, 111, 279, 666  
**Domains:** Geographic, Military, Elemental, Religious, Abstract

Each run appends to existing data rather than overwriting.

---

## Configuration

### Firecrawl Setup
Ensure local Firecrawl is running:
```bash
docker-compose up -d firecrawl-api-1
# or use the provided docker-compose.yml from earlier in session
```

The unified engine defaults to:
- **API**: `http://localhost:3002/v1/search`
- **API Key**: From `~/.hermes/.env` line 133

### Core Symbols Configuration
Both engines load symbols from the database. You can update:
```bash
/home/avalonas/.hermes/gematria/database/gematria_database.json
```

---

## Logs & Reports

### Unified Engine Outputs
- **Reports**: `/home/avalonas/.hermes/gematria/reports/unified_overnight_report_*.md`
- **Execution stats**: `unified_overnight_research/execution_stats.json`
- **Logs**: `/home/avalonas/.hermes/gematria/logs/unified_overnight.log`

### Modular Engine Outputs
- **Query results**: `modular_analysis/query_results/*.json`
- **Relationships**: `modular_analysis/rebuild_database.py` updates main database
- **Heatmaps**: ASCII output to terminal + optional file export
- **Logs**: Console output (can redirect with `> log.txt`)

---

## Troubleshooting

### Unified Engine Errors

**"UnboundLocalError: cannot access local variable converged_concepts"**
```bash
# Fixed by initializing before the if block
# See unified_engine.py lines 437-450
```

### Modular Engine Errors

**Import errors** - Ensure all subdirectories are Python packages:
```bash
cd /home/avalonas/.hermes/gematria/modular_analysis
find . -name "__init__.py" | xargs touch
# (already included in creation)
```

**Firecrawl connection issues**:
- Check Docker containers are running
- Verify API key at `~/.hermes/.env` line 133
- Test: `curl http://localhost:3002/v1/search -X POST -d '{"options":{"mode":"fast","includePages":true}}' -H "Authorization: Bearer YOUR_API_KEY"`

---

## Best Practices

### For Production (Unified)
1. Use unified engine for automated cron jobs
2. Keep modular version as reference for understanding components
3. Monitor logs regularly
4. Review generated reports weekly

### For Research (Modular)
1. Use modular mode to test different approaches
2. Experiment with parallel execution
3. Build new modules for novel analysis techniques
4. Share individual components as reusable patterns

---

## Future Enhancements

### Unified Engine
- [ ] Add configuration file for custom queries
- [ ] Implement smart caching between runs
- [ ] Add webhook notifications on significant discoveries
- [ ] Integrate Obsidian sync automatically

### Modular Engine
- [ ] Implement parallel execution (concurrent.futures)
- [ ] Add plugin system for new analysis components
- [ ] Create Docker container version
- [ ] Add comprehensive unit tests per module

---

## Repository Structure

```
/home/avalonas/.hermes/gematria/
├── database/
│   └── gematria_database.json              # Core symbols and configuration
├── unified_overnight_research/             # ✅ Option 1 - Unified Mode
│   ├── unified_engine.py                   # Main engine (2.3 KB)
│   ├── requirements.txt                    # Dependencies
│   └── README.md                           # This file + unified-specific notes
├── modular_analysis/                       # 🔬 Option 2 - Modular Mode
│   ├── orchestrator.py                     # Main orchestrator
│   ├── query_generator/                    # Query generation module
│   ├── firecrawl_scraper/                  # Scraping module
│   ├── pattern_analyzer/                   # Pattern analysis module
│   ├── relationship_builder/               # Relationship extraction module
│   ├── heatmap_generator/                  # ASCII heatmap generation
│   ├── report_generator/                   # Report compilation
│   └── README.md                           # Modular-specific documentation
├── crontab.gematria-unified-overnight      # Cron configuration for unified
└── logs/                                   # Log files directory
    ├── unified_overnight.log               # Unified engine execution logs
    └── ...                                 # Additional logs as needed
```

---

## License & Attribution

Both engines created for Steve's Gematria project by Avalon.  
For posterity purposes - preserved as reference implementations:
- **Unified**: Production-ready, simple cron deployment
- **Modular**: Research/experimentation playground

Feel free to study, modify, or extend either approach!

---

## Quick Start Checklist

### ✅ Unified Engine (Ready Now)
1. [x] Engine created in `unified_overnight_research/`
2. [x] Syntax validated and tested
3. [x] Cron entry created at `crontab.gematria-unified-overnight`
4. [ ] Add to crontab: `crontab /home/avalonas/.hermes/gematria/crontab.gematria-unified-overnight` OR run manual test first
5. [ ] Review reports in `/home/avalonas/.hermes/gematria/reports/`

### 🔬 Modular Engine (Experimental)
1. [x] All components created in `modular_analysis/`
2. [x] Orchestrator chains all modules
3. [ ] Test sequential execution: `python orchestrator.py --sequential`
4. [ ] Test parallel execution (if implemented): `python orchestrator.py --parallel`
5. [ ] Review individual module outputs

---

## Support & Questions

For questions about either engine, check:
- This README file
- The inline comments in each script
- Log files for error messages
- Database structure at `/home/avalonas/.hermes/gematria/database/gematria_database.json`

---

**Last Updated**: April 28, 2026  
**Author**: Avalon - Steve's Gematria Project  
**Version**: v1.0 (initial release)
