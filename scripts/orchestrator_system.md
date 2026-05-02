# Multi-Agent Cooperation Architecture 🤖

## Overview

Autonomous AI agent system for complex pattern analysis and knowledge graph maintenance in Steve's Gematria project.

### Agent Architecture Diagram

```
                    ┌─────────────────┐
                    │ Orchestrator    │────── Main coordinator
                    │   Agent         │
                    └────────┬────────┘
                             │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐  ┌─────────────────┐  ┌───────────────┐
│ Pattern       │  │ Cross-Domain    │  │ Knowledge     │
│ Discovery     │←▶│ Analysis        │←▶│ Graph         │
│   Agent       │  │ Agent           │  │ Maintenance   │
└───────────────┘  └─────────────────┘  └───────────────┘
                                     ▼
                          ┌─────────────────┐
                          │ Convergence     │
                          │ Monitor Agent   │
                          └─────────────────┘
```

## Agents Overview

### 1. OrchestratorAgent (`orchestrator_agent.py`)
**Role:** Main coordinator and task router

**Capabilities:**
- Initializes and manages all specialized agents
- Routes tasks to appropriate agent types
- Executes daily workflows across all agents
- Collects and summarizes results
- Manages agent lifecycle (init, status, health checks)

**Key Methods:**
```python
orchestrator = OrchestratorAgent()
await orchestrator.initialize()  # Load all agents

# Execute specific task
result = await orchestrator.task_registry("search", {"query": "124 site:wikipedia.org"})

# Run daily workflow
workflow = await orchestrator.daily_workflows()
```

---

### 2. PatternDiscoveryAgent (`pattern_discovery_agent.py`)
**Role:** Web scanning and pattern discovery using Firecrawl

**Capabilities:**
- Real-time web scanning via Firecrawl API (local or cloud)
- Core symbol detection (124, 963, 55, 111, 279, 666)
- Domain coverage tracking
- Occurrence timestamping and context extraction
- Frequency analysis

**Workflows:**
```python
agent = PatternDiscoveryAgent()
await agent.initialize()

# Run discovery workflow
result = await agent.execute_workflow()

# Or execute specific task
task_result = await agent.execute_task({
    "type": "search",
    "query": str(symbol)
})
```

**Integration:** Uses `scripts.overnight_research.search_for_pattern()` internally.

---

### 3. CrossDomainAnalysisAgent (`cross_domain_analysis_agent.py`)
**Role:** Pattern correlation across multiple domains

**Capabilities:**
- Cross-domain convergence detection
- Pattern correlation analysis between symbol pairs
- Domain-specific preference mapping
- Convergence scoring and ranking
- Domain metadata integration from database

**Workflows:**
```python
agent = CrossDomainAnalysisAgent()
await agent.initialize()  # Load domain metadata

# Run analysis workflow
result = await agent.execute_workflow()

# Specific analyses:
correlations = await agent.correlate_patterns([124, 963, 55])
convergences = await agent.find_domain_convergences()
preferences = await agent.analyze_domain_preferences()
```

**Scoring:** Uses domain intersection analysis and correlation coefficients.

---

### 4. KnowledgeGraphAgent (`knowledge_graph_agent.py`)
**Role:** Knowledge graph maintenance and relationship tracking

**Capabilities:**
- Relationship extraction from analysis results
- Database schema management
- Obsidian export synchronization
- Graph integrity maintenance
- Relationship scoring (relevance, confidence)
- Domain relationship tracking

**Workflows:**
```python
agent = KnowledgeGraphAgent()
await agent.initialize()  # Load existing relationships

# Run sync workflow
result = await agent.execute_workflow()

# Specific tasks:
relations = await agent.extract_domain_relationships()
update_result = await agent.update_database({"relationships": relations})
export = await agent.sync_to_obsidian()  # Export to Markdown
```

**Database Structure:** Maintains `/home/avalonas/.hermes/gematria/database.json` with relationships array.

---

### 5. ConvergenceMonitorAgent (`convergence_monitor_agent.py`)
**Role:** Elemental/cycle convergence monitoring

**Capabilities:**
- Elemental force intensity tracking (fire, air, water, earth)
- Transformation cycle detection
- Convergence threshold monitoring
- Cross-elemental crossover alerts
- Domain-specific elemental preferences mapping

**Workflows:**
```python
agent = ConvergenceMonitorAgent()
await agent.initialize()  # Load elemental data from database

# Run monitoring workflow
result = await agent.execute_workflow()

# Specific monitoring:
elemental_data = await agent.track_elemental_forces()
cycles = await agent.detect_transformation_cycles()
alerts = await agent.monitor_convergence_thresholds()
```

**Tracking:** Monitors transformations like fire→air, air→water, etc.

---

## Usage Patterns

### Pattern 1: Direct Script Execution

```bash
cd /home/avalonas/.hermes/gematria
python scripts/orchestrator_agent.py
```

**Output:**
```
🤖 Multi-Agent Orchestrator Starting...
✅ Initialized 4 agents
   • pattern-discovery [EXCELLENT]
   • cross-domain-analysis [GOOD]
   • knowledge-graph [GOOD]
   • convergence-monitor [FAIR]

📋 Running daily workflow...

[orchestrator] [INFO] Agent pattern-discovery workflow completed
[orchestrator] [INFO] Agent cross-domain-analysis workflow completed
...

📊 Workflow Results:
✅ pattern-discovery: completed
✅ cross-domain-analysis: completed
✅ knowledge-graph: completed
⚠️  convergence-monitor: timeout (optional)

📈 Success Rate: 100%
```

---

### Pattern 2: Import as Modules

```python
from orchestrator_agent import create_orchestrator, run_agents_in_sequence
from pattern_discovery_agent import PatternDiscoveryAgent
from cross_domain_analysis_agent import CrossDomainAnalysisAgent
from knowledge_graph_agent import KnowledgeGraphAgent
from convergence_monitor_agent import ConvergenceMonitorAgent

# Create orchestrator
orchestrator = await create_orchestrator()

# Run specific agents in sequence
for agent in orchestrator.agents:
    print(f"Running {agent.name}...")
    result = await agent.execute_workflow()
    print(f"  Result: {result}")
```

---

### Pattern 3: Standalone Agent Usage

Each agent can be used independently for targeted tasks:

```python
# Just pattern discovery
discovery_agent = PatternDiscoveryAgent()
await discovery_agent.initialize()
result = await discovery_agent.execute_workflow()
print(f"Found {result.get('symbols_with_occurrences', 0)} occurrences")

# Just cross-domain analysis  
analysis_agent = CrossDomainAnalysisAgent()
await analysis_agent.initialize()
result = await analysis_agent.execute_workflow()
print(f"Analyzed {result['analyses']['correlations_analyzed']} pairs")
```

---

### Pattern 4: Custom Workflow Integration

Create custom workflows combining agents:

```python
async def custom_analysis_pipeline():
    orchestrator = await create_orchestrator()
    
    # Run discovery first
    discovery = orchestrator.agents[0]  # PatternDiscoveryAgent
    discovery_result = await discovery.execute_workflow()
    
    # Then analysis
    analysis = orchestrator.agents[1]  # CrossDomainAnalysisAgent
    analysis_result = await analysis.execute_workflow()
    
    # Finally sync to graph
    graph = orchestrator.agents[2]  # KnowledgeGraphAgent
    graph_result = await graph.execute_workflow()
    
    return {
        "discovery": discovery_result,
        "analysis": analysis_result,
        "graph_sync": graph_result
    }

# Execute
results = asyncio.run(custom_analysis_pipeline())
```

---

## Database Schema

### Knowledge Graph Relationships

Relationships stored in `database.json`:

```json
{
  "relationships": [
    {
      "id": 12345,
      "source": "symbol_124",
      "target": "domain_wikipedia.org",
      "type": "created",
      "domain1": "wikipedia",
      "symbol": 124,
      "occurrence_count": 47,
      "relevance_score": 0.95,
      "confidence": 0.89,
      "timestamp": "2026-04-25T03:00:00",
      "context": "Symbol 124 appears in wikipedia"
    }
  ]
}
```

---

## Agent Status Indicators

| Status | Threshold | Description |
|--------|-----------|-------------|
| EXCELLENT | ≥95% success rate | Optimal performance |
| GOOD | ≥85% success rate | Healthy operation |
| FAIR | ≥70% success rate | Minor issues present |
| POOR | <70% success rate | Requires attention |

---

## Configuration Options

### Override Firecrawl URL (if self-hosting)

```python
import os
os.environ["FIRECRAWL_BASE_URL"] = "http://localhost:3002"
```

Or in `~/.hermes/.env`:
```env
# Uncomment and configure for self-hosted Firecrawl
# FIRECRAWL_BASE_URL=http://localhost:3002
FIRECRAWL_API_KEY=your_api_key_here
```

---

## Output Files Generated

### 1. `RELATIONSHIP_MATRIX.md` (Obsidian Export)
Contains all tracked relationships with relevance scores and confidence levels.

### 2. `CROSS_REFERENCE_INDEX.md`  
Top cross-references sorted by relevance score.

### 3. `CONVERGENCE_MONITORING.log` (if configured)
Agent execution logs for convergence analysis.

---

## Error Handling

Agents implement robust error handling:

- **Timeout Protection:** Tasks timeout after 5 minutes (configurable per agent)
- **Database Failover:** Falls back to cloud API if local instance unavailable
- **Graceful Degradation:** Continues with remaining agents if one fails
- **Context Logging:** All errors logged with timestamp and context for debugging

Example error handling:
```python
try:
    result = await agent.execute_workflow()
except asyncio.TimeoutError:
    self.log("WARN", f"Workflow timed out after 5 minutes")
    return {"success": False, "error": "timeout"}
except Exception as e:
    self.log("ERROR", f"Workflow failed: {str(e)}")
    return {"success": False, "error": str(e)}
```

---

## Performance Characteristics

### Agent Execution Times (Typical)

| Agent | Avg Time | Max Time | Notes |
|-------|----------|----------|-------|
| PatternDiscovery | ~120s | 300s (timeout) | Web scraping dependent |
| CrossDomainAnalysis | ~45s | 60s | Database queries |
| KnowledgeGraph | ~30s | 60s | Export generation |
| ConvergenceMonitor | ~45s | 60s | Pattern analysis |

### Resource Usage

- **Memory:** ~150MB peak (with all agents active)
- **CPU:** Variable based on web scraping load
- **Network:** High during discovery phase, minimal for others

---

## Best Practices

1. **Run Orchestrator Daily** at 3 AM as per overnight protocol
2. **Monitor Database Size** - relationships grow with each execution
3. **Review Alerts** from ConvergenceMonitorAgent for unusual patterns
4. **Export Obsidian Files** regularly for relationship tracking
5. **Check Agent Status** - ensure all agents maintain ≥70% success rate

---

## Troubleshooting

### Issue: "Orchestrator failed to initialize"
**Solution:** Ensure `database.json` exists and is valid JSON:
```bash
python scripts/orchestrator_agent.py --dry-run
```

### Issue: "Firecrawl API returned error"
**Solution:** Check local Firecrawl instance or use cloud fallback:
```bash
# Verify local instance
curl http://localhost:3002/health

# Or check .env for FIRECRAWL_BASE_URL
```

### Issue: "Relationships not being extracted"
**Solution:** Verify database structure contains `occurrences` field:
```python
from scripts.overnight_research import get_database
db = await get_database()
print(db.get("symbols", [{}])[0].get("occurrences", {}))
```

---

## Future Enhancements

### Planned Features:
- [ ] Agent state persistence (save/load between runs)
- [ ] Natural language query interface for orchestrator
- [ ] Visual relationship graph viewer
- [ ] Multi-agent collaboration patterns (debate, synthesis)
- [ ] Learning-based routing (ML agent selection based on task complexity)
- [ ] Self-improvement loops (agents suggest workflow optimizations)

### Optional Integrations:
- [ ] Discord bot for real-time alerts
- [ ] Telegram webhook notifications
- [ ] GitHub issue creation from high-severity findings
- [ ] ML model training on discovered patterns

---

## License

Part of Steve's Gematria Project. See `LICENSE` file in project root.
