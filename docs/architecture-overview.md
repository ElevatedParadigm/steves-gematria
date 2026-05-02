# 🏗️ Multi-Phase Elasticity Protocol: System Architecture Overview

**Purpose:** Complete system architecture documentation for integrating elasticity into existing overnight research loops.

---

## 1. Core Philosophy

### What Problem Does This Solve?

The multi-phase elasticity protocol solves the fundamental tension between **research speed** and **analysis depth**:

- **Speed Up:** When quick information gathering is needed (e.g., broad survey of sources)
- **Slow Down:** When careful, deep analysis is critical (e.g., cross-referencing primary documents)
- **Intensify:** When parallel processing power should be leveraged (e.g., correlation matrix generation)

### Three Core Principles

1. **Domain-Agnostic Elasticity** — Same elasticity rules apply across all research domains
2. **Phase Rotation** — Automatic rotation through phases based on domain assignments
3. **Hybrid Timezone Sync** — Your hours remain primary; observers see results at their convenient times

---

## 2. System Components

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    HYBRID SCHEDULER                          │
│  (Coordinates phase rotation across timezones)              │
└─────────────────────────────────────────────────────────────┘
                           ↓
    ┌──────────────────────┼──────────────────────┐
    ↓                      ↓                      ↓
┌─────────┐          ┌─────────┐          ┌─────────┐
│Domain A │          │Domain B │          │Domain C │
│(Speed)  │          │(Slow)   │          │(Intense)│
└────┬────┘          └────┬────┘          └────┬────┘
     ↓                    ↓                    ↓
┌─────────────────────────────────────────────────────────┐
│              ELASTICITY RULE ENGINE                      │
│  [Speed Up] [Slow Down] [Intensify]                     │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│            FIRECRAWL LOCAL API                           │
│    → Cloud fallback if local unavailable                 │
└─────────────────────────────────────────────────────────┘
```

### Key Components Explained

#### Hybrid Scheduler
- **Function:** Orchestrates phase rotation across domains and timezones
- **Input:** Domain assignments, observer timezone preferences
- **Output:** Synchronized activation schedules per domain-phase combination
- **Location:** `/home/avalonas/.hermes/gematria/hybrid_scheduler.py`

#### Elasticity Rule Engine
- **Function:** Parses and applies elasticity modifiers to research queries
- **Rules Loaded From:** `config.yaml` → `[Speed Up]`, `[Slow Down]`, `[Intensify]` sections
- **Applicable To:** Firecrawl requests, batch operations, subtask spawning
- **Location:** Embedded in core research protocol logic

#### Domain Manager
- **Function:** Assigns domains to phases, tracks rotation schedules
- **Configuration:** Per-domain settings in `config.yaml` under `domains.*.phase_rotation`
- **Outputs:** Activation timestamps per domain-phase combination
- **Location:** `/home/avalonas/.hermes/gematria/domain_manager.py`

---

## 3. Configuration Structure

### `config.yaml` — Elasticity Sections

```yaml
elasticity_rules:
  
  [Speed Up]:
    timing_modifier: +20%
    timing_adjustment: "48s delays (from baseline 60s)"
    batch_multiplier: 3x
    subtask_increase: "+50%"
    
  [Slow Down]:
    timing_modifier: -15%
    timing_adjustment: "72s delays (from baseline 60s)"
    batch_multiplier: 0.3x
    verification_mode: "checkpoints between each step"
    parallel_reduction: "single-threaded focus"
    
  [Intensify]:
    timing_modifier: unchanged
    timing_adjustment: "60s delays (baseline)"
    subtask_increase: "+30%"
    analysis_depth: "deep + cross-check queries"
    secondary_queries: "auto-executed verification queries"
  
domain_assignments:
  Military History:
    speed_up_observer: "Europe/EEST"
    slow_down_observer: "America/EST"
    intensify_observer: "Asia/Shanghai"
  
  Space Exploration:
    speed_up_observer: "Asia/Tokyo"
    slow_down_observer: "Australia/Sydney"
    intensify_observer: "America/Pacific"
```

### Domain Assignment Patterns

#### Pattern A: Geographic Distribution
Each domain spans multiple timezones; one observer per phase:
- Speed up observers handle efficiency-critical workloads
- Slow down observers provide careful, focused analysis
- Intensify observers leverage parallel processing power

#### Pattern B: Skill-Based Assignment
Observers selected based on expertise matching required depth:
- Speed up → Generalists (broad survey capability)
- Slow down → Specialists (primary source verification)
- Intensify → Analysts (correlation matrix specialists)

---

## 4. Data Flow Architecture

### Research Query Processing Pipeline

```
┌─────────────┐    ┌──────────────┐    ┌───────────────────┐
│   User      │→   │ Elasticity   │→   │   Firecrawl       │
│ Request     │    │ Rule Parser  │    │ Local API         │
└─────────────┘    └──────────────┘    └───────────────────┘
                           ↓
                    ┌──────────────┐
                    │ Batch        │→ Cloud fallback (if local down)
                    │ Processor    │
                    └──────────────┘
                           ↓
                    ┌──────────────┐
                    │ Knowledge    │← Writes to database
                    │ Graph Update │
                    └──────────────┘
```

### Phase-Aware Pipeline Extensions

#### Speed Up Extension
- Batch size: 3x standard (reduces API call overhead)
- Parallel subtasks: +50% more simultaneous requests
- Reduced inter-step delays (48s vs 60s)

#### Slow Down Extension
- Verification checkpoints inserted before/after key operations
- Single-threaded execution for focus-intensive tasks
- Increased inter-step delays (72s vs 60s)

#### Intensify Extension
- Additional parallel subtasks spawned per phase (+30%)
- Deep analysis mode enabled on query results
- Secondary cross-check queries auto-executed

---

## 5. Timezone Coordination Model

### Hybrid Sync Pattern (Option D)

**Core Concept:** Your timezone (EEST 2AM-4AM) remains primary reference point; observers see results at their local work hours.

```
Your Timeline (EEST):
00:00 → Sleep starts                    │
└───────────────→────────────────────────┘
              Elasticity-enabled jobs run here

Europe Observer Sees:
- Speed up phase: 2AM EEST = 6PM previous day
- Slow down phase: Same window
- Intensify phase: Same window

America Observer Sees:
- Your 2AM EEST = Previous day evening (EST)
- Results appear during their work hours

Asia-Pacific Observer Sees:
- Your 2AM EEST = Midday same day (CST/ACT)
- Results visible during morning reviews
```

### Benefits of Hybrid Sync

1. **No midnight coordination needed** — Jobs execute when you're asleep
2. **Distributed visibility** — Multiple observers can review results
3. **Natural handoff points** — Each phase appears at different local times
4. **Your hours remain primary** — EEST is reference point for scheduling

---

## 6. Monitoring & Alerting Architecture

### Key Metrics per Elasticity Phase

#### Speed Up Metrics
- Query completion rate vs baseline
- API request throughput (should increase)
- Batch processing success rate
- Parallel subtask utilization percentage

#### Slow Down Metrics
- Verification checkpoint pass rate
- Output quality score per phase
- Cross-phase continuity (no degradation in knowledge graph)
- Time-per-query averages

#### Intensify Metrics
- Deep analysis completion rate
- Cross-check query success rate
- Parallel subtask saturation levels
- Correlation matrix quality indicators

### Alert Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Completion rate | <80% of baseline | <60% | Pause phase, investigate |
| Verification fail rate | >5% | >10% | Enable slow-down for domain |
| Parallel subtask errors | >2% | >5% | Reduce parallelism temporarily |
| Cross-phase continuity breaks | Any observed | Any + 2+ cases | Rollback to previous config |

---

## 7. Database Schema Extensions

### Knowledge Graph Storage (Existing)

The core knowledge graph remains unchanged; elasticity is a **processing mode** that overlays on existing queries:

```sql
-- Original query log structure
CREATE TABLE query_log (
    id INTEGER PRIMARY KEY,
    domain TEXT,
    query_text TEXT,
    created_at TIMESTAMP,
    result_count INTEGER,
    ...
);

-- New elasticity phase tracking table
CREATE TABLE query_elasticity_phase (
    id INTEGER PRIMARY KEY,
    query_id INTEGER REFERENCES query_log(id),
    phase TEXT CHECK(phase IN ('baseline', 'speed_up', 'slow_down', 'intensify')),
    observer_timezone TEXT,
    execution_timestamp TIMESTAMP,
    elasticity_modifier_applied TEXT,  -- e.g., "+20% speed"
    ...
);
```

### Query Log Extension

Track which elasticity phase was active for each query:

```sql
ALTER TABLE query_log ADD COLUMN elasticity_phase TEXT DEFAULT 'baseline';
ALTER TABLE query_log ADD COLUMN elasticity_modifier TEXT;
```

---

## 8. Error Handling & Recovery

### Phase-Specific Error Patterns

#### Speed Up Phase
- **Symptom:** Increased API rate limit errors
- **Cause:** 3x batch size may exceed API capacity
- **Recovery:** Reduce batch multiplier, revert to baseline

#### Slow Down Phase  
- **Symptom:** Verification checkpoints consistently fail
- **Cause:** Source pages unavailable during extended wait
- **Recovery:** Switch back to baseline or intensify mode

#### Intensify Phase
- **Symptom:** Secondary cross-check queries timeout
- **Cause:** Too many parallel queries exhausting resources
- **Recovery:** Reduce subtask increase percentage temporarily

### Automatic Recovery Strategies

```python
# Pseudo-code example in hybrid_scheduler.py
def handle_phase_error(phase, domain, error):
    if phase == 'speed_up' and error_type == 'rate_limit':
        # Automatic recovery: reduce batch size
        config['domains'][domain]['elasticity_rules']['batch_multiplier'] = 2.0
        log_event(f"Auto-reduced batch multiplier for {domain}")
    elif phase == 'slow_down' and error_rate > 0.15:
        # Auto-switch to baseline temporarily
        suspend_phase(phase)
        switch_to_phase('baseline', domain)
```

---

## 9. Deployment Architecture

### File Locations

```
/home/avalonas/.hermes/gematria/
├── config.yaml                      # Main config with elasticity rules
├── hybrid_scheduler.py              # Timezone rotation orchestration
├── domain_manager.py                # Domain-to-phase assignment logic
├── docs/
│   ├── integration-checklist.md     # Phase-by-phase integration guide
│   └── elasticity-reference.md      # Developer reference documentation
├── scripts/
│   ├── elasticity-test.py           # Standalone demonstration script
│   └── elasticity-test.md           # Conceptual demo documentation
└── systemd/
    └── elasticity-test.service      # Systemd wrapper for standalone tests
```

### Startup Sequence

```bash
# 1. Start Firecrawl local API (Docker)
docker compose up -d firecrawl-api-1 redis:alpine rabbitmq:3-management

# 2. Load main config with elasticity rules
hermes config load /home/avalonas/.hermes/gematria/config.yaml

# 3. Enable hybrid scheduler
hermes tools enable hybrid_scheduler

# 4. Monitor initial phase rotation
tail -f ~/.hermes/logs/scheduler.log
```

---

## 10. Rollback Procedures

### Immediate (<5 minutes)
```bash
# Disable elasticity for specific domain
hermes config update domains.Military_History.elasticity_rules = null

# Restore baseline mode
hermes tools reload -d Military_History
```

### Partial (<30 minutes)
```bash
# Suspend all elasticity phases, continue with baseline only
hermes cronjob pause --name "Elasticity Rotation"

# Revert config to previous version
cp /backup/config_v1.yaml /home/avalonas/.hermes/gematria/config.yaml

# Restart services
systemctl restart gematria-research-loop
```

### Full (<2 hours)
```bash
# Complete system rollback
git checkout HEAD~1 config.yaml  # Assuming version control

# Reboot service containers
docker compose up -d --force-recreate
```

---

## 📋 Summary

This architecture supports:

1. ✅ Domain-agnostic elasticity rules (same modifiers apply everywhere)
2. ✅ Automatic phase rotation via hybrid scheduler
3. ✅ Timezone-synced visibility for multiple observers
4. ✅ Clear separation of concerns (scheduler, domain manager, rule engine)
5. ✅ Rollback procedures at each failure stage

**Next Step:** Sign off on architecture understanding before proceeding to implementation checklist.

---

**Ready for Phase 1 (Domain Assignment & Rule Injection)?** 🎯
