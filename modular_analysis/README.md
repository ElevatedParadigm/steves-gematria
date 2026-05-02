# 🔧 Modular Analysis Components

## Overview
Separate, composable scripts for overnight research that can be:
- **Chained sequentially** (linear mode - all modules in order)
- **Tested independently** (each module standalone)  
- **Swapped easily** (A/B test different components)

## Location
`/home/avalonas/.hermes/gematria/modular_analysis/`

---

## 🏗️ Component Architecture

```
modular_analysis/
├── orchestrator_main.py         # Main entry point that chains modules
├── scraper_module.py            # Web scraping logic (standalone)
├── analyzer_module.py           # Pattern analysis (standalone)
├── graph_builder_module.py      # Relationship iteration (standalone)
├── temporal_tracker_module.py   # Temporal tracking (standalone)
├── heatmap_generator_module.py  # ASCII visualization (standalone)
└── report_generator_module.py   # Report compilation (depends on all)
```

---

## 🚀 Quick Start

### Linear Chain Mode (Full Overnight Research)
```bash
cd /home/avalonas/.hermes/gematria/modular_analysis
python orchestrator_main.py --linear
```

### Independent Component Testing
```bash
# Test each module individually
python modular_analysis/orchestrator_main.py --independent
```

### Cron Installation (3 AM Daily)
```bash
echo "0 3 * * * cd /home/avalonas/.hermes/gematria/modular_analysis && python orchestrator_main.py --linear >> /home/avalonas/.hermes/gematria/cron_logs/modular_overnight.log 2>&1" | crontab -
```

---

## ✨ Comparison with Unified Approach

| Feature | Modular ⚠️ | Unified ✅ |
|---------|------------|------------|
| **Component Testing** | ✅ Easy (test each module separately) | ❌ Must debug entire pipeline |
| **Flexibility** | ✅ Can swap components (e.g., different scraper) | ⚠️ Fixed architecture |
| **Parallel Development** | ✅ Multiple people can work on different modules | ❌ Single person owns whole script |
| **Simple Cron Setup** | ⚠️ One entry but multiple Python files | ✅ One file, zero coordination |
| **Debugging** | ⚠️ Must trace across multiple files | ✅ Full traceback in one place |
| **State Management** | ❌ Need shared data structures | ✅ Handles internally |

---

## 📊 Component Responsibilities

### 1. Scraper Module (`scraper_module.py`)
- **Input**: Query string
- **Output**: List of result dicts (URLs, titles)
- **Can run standalone**: Yes
- **Test command**: `python scraper_module.py`

### 2. Analyzer Module (`analyzer_module.py`)
- **Input**: Results from ScraperModule
- **Output**: PatternAnalysisResult with convergence signals
- **Can run standalone**: Yes (if given results file)
- **Test command**: `python analyzer_module.py --results-file results.json`

### 3. Graph Builder Module (`graph_builder_module.py`)
- **Input**: Results + existing database relationships
- **Output**: New relationship list
- **Can run standalone**: Yes
- **Test command**: `python graph_builder_module.py`

### 4. Temporal Tracker Module (`temporal_tracker_module.py`)
- **Input**: Query sequence + results
- **Output**: TemporalPatternData with frequency counts
- **Can run standalone**: Yes
- **Test command**: `python temporal_tracker_module.py`

### 5. Heatmap Generator Module (`heatmap_generator_module.py`)
- **Input**: Relationship data + symbols
- **Output**: ASCII string for terminal display
- **Can run standalone**: Yes
- **Test command**: `python heatmap_generator_module.py`

### 6. Report Generator Module (`report_generator_module.py`)
- **Input**: Results from ALL other modules
- **Output**: Complete markdown report file
- **Can run standalone**: Only if given all inputs in one dict
- **Depends on**: All previous modules

---

## 🧪 Usage Examples

### Chain Mode (Sequential Execution)
```python
from orchestrator_main import linear_chain_mode
linear_chain_mode()  # Runs: Scraper → Analyzer → Graph Builder → ...
```

### Independent Component Testing
```python
# Test scraper alone
from scraper_module import ScraperModule
scraper = ScraperModule(url="http://localhost:8084/")
results = scraper.search("gematria test")
print(f"Found {len(results)} results")

# Analyze results separately
from analyzer_module import AnalyzerModule  
analyzer = AnalyzerModule()
analysis = analyzer.analyze(results)
print(f"Detected {len(analysis['convergence_signals'])} signals")
```

### Swap Components (A/B Testing)
```python
# Use different scraper implementation (e.g., DuckDuckGo instead of SearXNG)
from custom_scraper_module import CustomScraperModule  # Different scraping logic
custom_scraper = CustomScraperModule(url="https://duckduckgo.com/")

# Keep analyzer same - just change what gets scraped
results = custom_scraper.search("gematria test")
analysis = analyzer.analyze(results)  # Same analysis logic
```

---

## 📁 Output Files

### Linear Chain Mode
Creates reports in: `/home/avalonas/.hermes/gematria/reports/`
- `modular_overnight_report_YYYYMMDD_HHMM.md`

### Independent Mode
Each module prints to stdout, no files written unless explicitly configured.

---

## 🔄 Execution Flow (Linear Chain)

```
orchestrator_main.py (--linear mode)
├── Step 1: ScraperModule.search(query) → results
├── Step 2: AnalyzerModule.analyze(results) → analysis
├── Step 3: GraphBuilderModule.build_relationships(results, []) → new_rels
├── Step 4: TemporalTrackerModule.track() → temporal
├── Step 5: HeatmapGeneratorModule.generate() → ascii_heatmap
└── Step 6: ReportGeneratorModule.generate_report(all outputs) → report.md
```

---

## 🎯 When to Use Each Approach

### Choose Unified (`unified_overnight_research/`) When:
- You want minimal dependencies
- Cron setup must be simple (one-line entry)
- Debugging should be straightforward
- Team has one person maintaining the research pipeline

### Choose Modular (`modular_analysis/`) When:
- You need to test components independently
- Different people will maintain different parts
- You want to A/B test scrapers or analyzers
- Flexibility in component swapping is valuable

---

## 📋 Cron Installation Commands

### Unified Approach (Single Script)
```bash
echo "0 3 * * * cd /home/avalonas/.hermes/gematria/unified_overnight_research && ./run_unified.sh >> /home/avalonas/.hermes/gematria/cron_logs/unified_overnight.log 2>&1" | crontab -
```

### Modular Approach (Python Chain)
```bash
echo "0 3 * * * cd /home/avalonas/.hermes/gematria/modular_analysis && python orchestrator_main.py --linear >> /home/avalonas/.hermes/gematria/cron_logs/modular_overnight.log 2>&1" | crontab -
```

---

**Next:** Test both approaches and choose which to deploy for long-term overnight research operations!
