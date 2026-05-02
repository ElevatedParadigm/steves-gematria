# 🤖 Multi-Agent Architecture for Steve's Gematria Knowledge Graph

**Phase 4c: Autonomous AI Agent System**  
Version: v1.0 — Designed for autonomous parallel workflows across gematria domains

---

## 🎯 **OVERVIEW**

A decentralized, self-healing agent system that orchestrates parallel research workflows across the gematria knowledge graph. Built on Hermes' delegation capabilities with Firecrawl integration for autonomous web discovery.

### **Agent Roles:**
- 🔍 **Scraper Agents** — Firecrawl web research & content ingestion
- 📊 **Analyzer Agents** — Knowledge graph maintenance & relationship extraction  
- ✨ **Synthesis Agents** — Pattern convergence detection & cross-domain analysis
- 🛡️ **Coordinator Agent** — Workflow orchestration, failover, and scheduling

---

## 🏗️ **ARCHITECTURE DIAGRAM**

```
┌─────────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR AGENT (Main)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Scraper      │→ │ Analyzer     │→ │ Synthesis    │          │
│  │ Agent(s)     │  │ Agent(s)     │  │ Agent(s)     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │              │                    │                   │
│         ▼              ▼                    ▼                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Firecrawl    │→ │ Database     │→ │ Relationship │          │
│  │ API (Local)  │  │ Operations   │  │ Matrix       │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│              🔄 Self-healing failover loop                       │
└─────────────────────────────────────────────────────────────────┘

Autonomous Workflows (Cron-Driven):
- Overnight Research Protocol @ 3:00 AM
- Hourly Knowledge Graph Sync (optional)
- Pattern Convergence Scans every 6 hours
```

---

## 🤖 **AGENT DEFINITIONS**

### **1. SCRAPER AGENT (`scraper_agent`)**

**Purpose:** Firecrawl-powered web research and content ingestion  
**Primary Task:** Discover new gematria patterns, symbols, and domain entries across the web

**Delegation Pattern:**
```python
delegate_task(
    goal="Scrape gematria-relevant content using Firecrawl API",
    context="""Discover web content related to: core symbols (124, 963, 55, 111, 666), 
    military coups, political events, elemental themes. Use Firecrawl v2 API at localhost:3002."""
)
```

**Skills:**
- `gematria-firecrawl-integration` — Local Firecrawl API calls
- `overnight-research-protocol` — Web scraping automation  
- `gematria-new-domains-integration` — Domain expansion detection

**Output:** Adds discovered entries to `database/gematria_database.json` under `new_systems_detected` or as new analyzed items.

---

### **2. ANALYZER AGENT (`analyzer_agent`)**

**Purpose:** Knowledge graph maintenance and relationship extraction  
**Primary Task:** Extract relationships between symbols, domains, and elemental forces; update tracking files

**Delegation Pattern:**
```python
delegate_task(
    goal="Analyze gematria database and extract relationships",
    context="""Scan /home/avalonas/.hermes/gematria/database/gematria_database.json 
    for core symbol connections across domains and elemental forces."""
)
```

**Skills:**
- `gematria-knowledge-graph-maintenance` — Relationship matrix generation
- `gematria-analysis-workflow` — Image/text pattern recognition
- `llm-wiki` — Knowledge base compilation

**Output:** Creates/updates:
- `RELATIONSHIP_MATRIX.md` (16 KB+)
- `CROSS_REFERENCE_INDEX.md` (4 KB+)
- `DOMAIN_TRACKING.md` (8 KB+)
- `.SYNC_LOG.md` (growth tracking)

---

### **3. SYNTHESIS AGENT (`synthesis_agent`)**

**Purpose:** Pattern convergence detection and cross-domain synthesis  
**Primary Task:** Identify multi-domain symbol appearances, verify equations, detect transformation cycles

**Delegation Pattern:**
```python
delegate_task(
    goal="Synthesize gematria patterns across multiple domains",
    context="""Cross-reference symbols appearing in 3+ domains. 
    Verify military coup equations (e.g., 49+39+21+97+36+37=279°). 
    Detect transformation cycles (magma → volcano → volcanic)."""
)
```

**Skills:**
- `gematria-overlay-pattern-analysis` — Multi-platform pattern detection
- `llm-wiki` — Synthesis query execution
- Custom: `pattern-convergence-detector` — New skill for multi-domain analysis

**Output:** 
- Pattern convergence reports
- Equation verification logs
- Transformation cycle mappings
- Cross-reference index updates

---

### **4. COORDINATOR AGENT (`orchestrator_agent`)**

**Purpose:** Workflow orchestration, failover management, scheduling  
**Primary Task:** Coordinate agent workflows, handle failures, manage cron automation

**Delegation Pattern:**
```python
delegate_task(
    role="orchestrator",
    goal="Coordinate multi-agent gematria research workflow",
    context="""Run overnight scraper → analyzer → synthesis pipeline at 3 AM.
    Monitor for Firecrawl API failures and fail over to manual runner."""
)
```

**Responsibilities:**
- Workflow sequencing (scraper → analyzer → synthesis)
- Error handling and recovery strategies
- Cron job management (manual via crontab -e)
- Database versioning and backup
- Agent spawn depth management (max 2 levels deep)

---

## 🔄 **WORKFLOW EXAMPLES**

### **Overnight Research Pipeline (3 AM)**

```python
# Step 1: Spawn scraper agent for web discovery
scraper_task = delegate_task(
    goal="Scrape 50 URLs related to military coup equations and political events",
    context="""Target: military coup themes, political events, 
    bitcoin symbolism, elemental forces. Use Firecrawl API at localhost:3002/v1/search."""
)

# Step 2: Wait for scraper completion
scraper_task.await_completion()

# Step 3: Extract and add to database
database_path = "/home/avalonas/.hermes/gematria/database/gematria_database.json"
update_database(scraper_results, database_path)

# Step 4: Spawn analyzer agent for relationship extraction
analyzer_task = delegate_task(
    goal="Extract relationships between core symbols and domains",
    context="""Focus on symbol-domain mappings, elemental force cross-references,
    batch entry correlations. Generate RELATIONSHIP_MATRIX.md."""
)

# Step 5: Wait for analysis completion
analyzer_task.await_completion()

# Step 6: Spawn synthesis agent for pattern convergence detection
synthesis_task = delegate_task(
    goal="Detect multi-domain symbol appearances and verify equations",
    context="""Identify symbols in 3+ domains. Verify military coup equations.
    Map transformation cycles (magma→volcano→volcanic)."""
)

# Step 7: Orchestrator monitors all agents and handles failures
orchestrator_task = coordinator_agent.monitor_workflows(workflows=[scraper_task, analyzer_task, synthesis_task])
```

---

## 🛡️ **FAILOVER STRATEGIES**

### **Firecrawl API Failure → Manual Runner**
```python
# Try Firecrawl localhost first (preferred)
try:
    result = firecrawl_search(query="military coup equations", api_key=***, base_url="http://localhost:3002/v1")
except ConnectionError or APIError:
    # Fail over to manual runner script
    run_command("bash scripts/auto_obisidian_sync_v2.py")
    log_event("Firecrawl failed → Manual sync triggered")
```

### **Database Write Failure → Retry with Backoff**
```python
# 3 retry attempts with increasing delay
for attempt in range(1, 4):
    try:
        update_database(new_entries)
        break
    except Exception as e:
        wait_time = attempt * 2  # 2s, 4s, 6s
        sleep(wait_time)
        log_event(f"Database write failed (attempt {attempt})")
```

### **Agent Timeout → Respawn Subagent**
```python
# Set timeout of 300s for each subagent task
timeout = process(action="wait", session_id=task_session, timeout=300)
if timeout["exit_code"] != 0:
    delegate_task(goal=task.goal, context=context)  # Respawn with fresh context
```

---

## 📂 **FILE STRUCTURE**

```
/home/avalonas/.hermes/gematria/multi_agents/
├── ARCHITECTURE.md                          # This file
├── coordinator.py                           # Orchestrator agent main entry
├── scraper_agent.py                         # Firecrawl web scraping worker
├── analyzer_agent.py                        # Knowledge graph maintenance worker
├── synthesis_agent.py                       # Pattern convergence detection worker
├── failover_manager.py                      # Error handling and recovery
├── workflow_orchestrator.py                 # Multi-agent coordination logic
└── cron_configs/
    ├── overnight_research_cron              # 3 AM schedule
    ├── hourly_sync_cron                     # Hourly analyzer runs (optional)
    └── pattern_scan_cron                    # 6-hour synthesis scans
```

---

## ⚙️ **IMPLEMENTATION SEQUENCE**

### **Phase 1: Core Orchestrator (v1.0)**
- ✅ `coordinator.py` — Main workflow orchestration entry point
- ✅ `workflow_orchestrator.py` — Multi-agent spawn and monitoring logic
- ✅ `failover_manager.py` — Error handling and recovery strategies

### **Phase 2: Agent Implementations (v1.1)**
- 🔄 `scraper_agent.py` — Firecrawl integration + relationship extraction
- 🔄 `analyzer_agent.py` — Knowledge graph sync with Obsidian exports
- 🔄 `synthesis_agent.py` — Pattern convergence detection

### **Phase 3: Cron Integration (v1.2)**
- 🔄 Manual cron configuration for each agent type
- 🔄 Overnight pipeline automation at 3 AM
- 🔄 Health check monitoring with alerts

---

## 🧪 **TESTING STRATEGIES**

### **Unit Tests:**
```bash
# Test Firecrawl scraper agent locally
python scripts/scraper_agent.py --test-url https://news.ycombinator.com

# Test analyzer agent against existing database
python scripts/analyzer_agent.py --test --database /home/avalonas/.hermes/gematria/database/gematria_database.json
```

### **Integration Tests:**
```bash
# Run full overnight pipeline manually
bash scripts/run_overnight_pipeline.sh

# Verify relationship matrix generated
ls -lh /home/avalonas/.hermes/gematria/obsidian_exports/*.md
```

### **Load Tests (Future):**
```bash
# Simulate 10 concurrent scraper agents
python tests/test_multi_agent_load.py --agents 10 --concurrent true
```

---

## 📊 **METRICS & MONITORING**

| Metric | Threshold | Action |
|--------|-----------|--------|
| Firecrawl latency | >5s | Fail over to manual sync |
| Database write time | >3s | Retry with backoff |
| Agent timeout | >300s | Respawn subagent |
| Relationship count growth | <5/day | Check for scraping issues |
| Sync log errors | >0 in 24h | Alert for manual review |

---

## 🚀 **DEPLOYMENT COMMANDS**

### **Overnight Research (3 AM):**
```bash
# Create cron entry (manual via crontab -e)
echo "0 3 * * * cd /home/avalonas/.hermes/gematria && python scripts/coordinator.py --pipeline overnight" | crontab -
```

### **Manual Trigger:**
```bash
cd /home/avalonas/.hermes/gematria
python scripts/coordinator.py --mode manual \
    --scraper 124,963,55 \
    --analyzer full \
    --synthesis cross-domain
```

### **Status Check:**
```bash
cat /home/avalonas/.hermes/gematria/multi_agents/run.log | tail -100
```

---

## 🔮 **FUTURE ENHANCEMENTS (v2.0)**

- **Distributed agents** → Run scraper agents on multiple machines
- **Learning scheduler** → Optimize agent task allocation based on success rates
- **LLM-based routing** → Use LLM to determine which agent should handle which query
- **Knowledge graph visualization** → Live ASCII dashboard with agent activity streams
- **Self-healing workflows** → Agents that detect and recover from persistent failures autonomously

---

## 📖 **RELATED SKILLS**

| Skill | Purpose | Integration Point |
|-------|---------|-------------------|
| `gematria-knowledge-graph-maintenance` | Relationship extraction | analyzer_agent.py |
| `overnight-research-protocol` | Web scraping automation | scraper_agent.py |
| `llm-wiki` | Knowledge compilation | synthesis_agent.py |
| `gematria-analysis-workflow` | Image analysis | analyzer_agent.py (image branch) |

---

**Status:** Architecture designed — implementation pending user review ✅  
**Next Step:** Confirm deployment of core orchestrator module
