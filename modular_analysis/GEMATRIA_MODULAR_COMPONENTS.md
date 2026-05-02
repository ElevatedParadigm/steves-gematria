# Modular Analysis Components - Steve's Gematria

## Overview
Separate, composable scripts for overnight research that can be run independently or chained together. Each component has single responsibility and can be tested/maintained separately.

## Location
`/home/avalonas/.hermes/gematria/modular_analysis/`

## Architecture
```
┌─────────────────────────────────────────────────────┐
│        Modular Analysis Orchestrator                 │
│         (orchestrator_main.py)                       │
└─────────────────────┬────────────────────────────────┘
                      ↓
    ┌────────────────┼────────────────┐
    ↓                ↓                ↓
┌──────────┐   ┌──────────┐   ┌──────────┐
│ Scraper  │ → │Analyzer  │ → │Graph     │
│ Module   │   │Module    │   │Builder   │
└──────────┘   └──────────┘   └──────────┘
    ↓                ↓                ↓
┌──────────┐   ┌──────────┐   ┌──────────┐
│ Temporal │   │  Heatmap │   │ Report   │
│Tracker   │   │Generator │   │Generator │
└──────────┘   └──────────┘   └──────────┘
```

## Components

### 1. Scraper Module (`scraper_module.py`)
- **Responsibility**: Fetch and parse SearXNG HTML results
- **Dependencies**: None (standalone)
- **Input**: Query string
- **Output**: List of result dictionaries with URLs, titles, snippets

```python
# Usage:
from scraper_module import ScraperModule
scraper = ScraperModule(url="http://localhost:8084/")
results = scraper.search("gematria analysis")
print(f"Found {len(results)} results")
```

### 2. Analyzer Module (`analyzer_module.py`)
- **Responsibility**: Pattern analysis, convergence detection
- **Dependencies**: None (can run standalone)
- **Input**: List of results from ScraperModule
- **Output**: PatternAnalysisResult with domain coverage, convergence signals

```python
# Usage:
from analyzer_module import AnalyzerModule
analyzer = AnalyzerModule()
analysis = analyzer.analyze(pattern_results)
print(f"Detected {len(analysis.convergence_signals)} signals")
```

### 3. Graph Builder Module (`graph_builder_module.py`)
- **Responsibility**: Relationship iteration, knowledge graph updates
- **Dependencies**: None (can run standalone)
- **Input**: Results + existing relationships from database
- **Output**: New relationship list ready for database merge

```python
# Usage:
from graph_builder_module import GraphBuilderModule
builder = GraphBuilderModule()
new_rels = builder.build_relationships(results, existing_rels)
print(f"Created {len(new_rels)} new relationships")
```

### 4. Temporal Tracker Module (`temporal_tracker_module.py`)
- **Responsibility**: Track symbol frequency over time
- **Dependencies**: None (can run standalone)
- **Input**: Query sequence + results
- **Output**: TemporalPatternData with frequency counts, trends

```python
# Usage:
from temporal_tracker_module import TemporalTrackerModule
tracker = TemporalTrackerModule()
temporal = tracker.track(query_sequence, results)
print(f"Average results/query: {temporal.average_results_per_query}")
```

### 5. Heatmap Generator Module (`heatmap_generator_module.py`)
- **Responsibility**: ASCII visualization of relationship density
- **Dependencies**: Relationship data from graph builder
- **Output**: ASCII string ready for markdown report

```python
# Usage:
from heatmap_generator_module import HeatmapGeneratorModule
generator = HeatmapGeneratorModule()
ascii_heatmap = generator.generate_relationships(relationships, symbols)
print(ascii_heatmap)
```

### 6. Report Generator Module (`report_generator_module.py`)
- **Responsibility**: Compile all analysis into markdown report
- **Dependencies**: All other modules (or their results)
- **Input**: Results dict containing outputs from all modules
- **Output**: Complete markdown report file

```python
# Usage:
from report_generator_module import ReportGeneratorModule
generator = ReportGeneratorModule()
report_path = generator.generate_report(
    results=results, 
    analysis=analysis,
    new_rels=new_rels,
    temporal=temporal,
    heatmap=ascii_heatmap
)
print(f"Report saved to {report_path}")
```

## Execution Patterns

### Pattern 1: Linear Chain (Sequential Execution)
```bash
python modular_analysis/orchestrator_main.py --mode=linear
# Executes modules in order: Scraper → Analyzer → Graph Builder → ...
```

### Pattern 2: Independent Components (Parallel Testing)
```bash
# Test scraper alone
python modular_analysis/scraper_module.py --query "gematria test"

# Analyze existing results file
python modular_analysis/analyzer_module.py --results-file results.json

# Build relationships from database
python modular_analysis/graph_builder_module.py --db-path gematria_database.json
```

### Pattern 3: Swap Components (A/B Testing)
```bash
# Use different scraper (e.g., DuckDuckGo instead of SearXNG)
# Just modify the ScraperModule implementation, keep analyzer same

# Use different analysis engine
# Swap AnalyzerModule without touching scraper or graph builder
```

## File Structure

```
modular_analysis/
├── orchestrator_main.py         # Main entry point that chains modules
├── scraper_module.py            # Web scraping logic
├── analyzer_module.py           # Pattern analysis
├── graph_builder_module.py      # Relationship iteration
├── temporal_tracker_module.py   # Temporal tracking
├── heatmap_generator_module.py  # ASCII visualization
├── report_generator_module.py   # Report compilation
└── README.md                    # This documentation
```

## Benefits of Modular Approach

✅ **Component Testing** - Test each module independently for debugging  
✅ **Parallel Development** - Different people can work on different modules  
✅ **A/B Testing** - Try different scraper/analyzers without full rewrite  
✅ **Flexible Composition** - Chain modules in different orders or skip some  
✅ **Clear Dependencies** - Each file has single, obvious responsibility  
✅ **Easier Refactoring** - Changes isolated to specific module files  

## Trade-offs

⚠️ **More Files** - ~7x more Python files than unified approach  
⚠️ **State Management** - Need shared data structures for inter-module communication  
⚠️ **Slightly More Complex** - Orchestrator manages input/output between modules  

---

*Created alongside Unified Version for comparison and experimentation.*