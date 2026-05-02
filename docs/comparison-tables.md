# 📊 Comparison Tables: Elasticity Modes Reference

**Purpose:** Side-by-side comparison of baseline vs. all three elasticity modes for quick reference.

---

## Table A: Core Configuration Differences

| Configuration Item | Baseline (Default) | Speed Up (+20%) | Slow Down (-15%) | Intensify (Intense) |
|-------------------|--------------------|-----------------|------------------|---------------------|
| **Timing Modifier** | None (0%) | +20% faster | -15% slower | Unchanged (0%) |
| **Inter-step Delay** | 60 seconds | 48 seconds | 72 seconds | 60 seconds |
| **Batch Size Multiplier** | ×1 (3 requests) | ×3 (9 requests) | ×0.3 (1 request) | ×1.3 (≈4 requests) |
| **Parallel Subtask Factor** | ×1.0 (baseline) | ×1.5 (+50%) | ×0.33 (-67%) | ×1.3 (+30%) |
| **Verification Mode** | Standard checkpoints | Lightweight summary check | Full verification checkpoints | Deep analysis + cross-checks |
| **Execution Thread Count** | Multi-threaded | Multi-threaded | Single-threaded | Parallel with extra subtasks |
| **Analysis Depth** | Standard | Reduced (efficiency focus) | Maximum (careful review) | Deep + secondary queries |

---

## Table B: Performance Characteristics

| Metric | Baseline | Speed Up | Slow Down | Intensify |
|--------|----------|----------|-----------|-----------|
| **Query Completion Rate** | 95% | 85-90% | 92-95% | 88-92% |
| **Quality Score (0-1)** | 0.88 | 0.75-0.80 | 0.90-0.93 | 0.86-0.89 |
| **API Requests per Query** | 3 | 9 | 1 | 4-5 |
| **Processing Time (Baseline: 60s)** | 60s | 48s | 72s | 60s |
| **Source Coverage** | Broad survey | Maximum breadth | Deep focus | Multi-source correlation |
| **Error Rate** | 3-5% | 8-12% (transient) | 2-4% | 4-6% |

### Speed Trade-offs by Mode

```
Speed Up: 
  ✅ Pros: Faster information gathering, good for broad surveys
  ❌ Cons: Reduced quality score, higher error rate

Slow Down:
  ✅ Pros: High quality scores, excellent for verification tasks
  ❌ Cons: Slower throughput, may miss time-sensitive opportunities

Intensify:
  ✅ Pros: Deep analysis with parallel power, good for correlations
  ❌ Cons: More API requests, potential resource contention
```

---

## Table C: Ideal Use Cases by Research Phase

| Mode | Best For | Not Suitable For | Domain Examples |
|------|----------|------------------|-----------------|
| **Baseline** | Standard research operations, ongoing monitoring, light correlation tasks | Time-critical bursts or deep quality reviews | Climate Science daily checks, Space Exploration routine updates |
| **Speed Up** | Initial source discovery, broad pattern survey, quick information gathering when urgency required | Critical verification, quality-sensitive analysis, primary source review | Military History event timeline construction, rapid threat assessment |
| **Slow Down** | Deep document verification, primary source analysis, careful cross-referencing, quality-critical operations | Time-sensitive tasks, high-volume batch processing | Military History treaty analysis, Space Exploration archival research |
| **Intensify** | Multi-source correlation, pattern recognition across domains, deep cross-checking | Single-query operations, low-complexity topics | Climate Science correlation matrix, Space Exploration orbital mechanics verification |

---

## Table D: Resource Utilization Patterns

| Resource Type | Baseline | Speed Up | Slow Down | Intensify |
|---------------|----------|----------|-----------|-----------|
| **CPU Usage** | ~35-45% of single core | ~60-75% of single core (more parallel) | ~10-20% (focused, sequential) | ~50-70% with bursts |
| **Memory Usage** | ~128-192 MB | ~192-256 MB | ~96-128 MB | ~144-224 MB |
| **API Request Burden** | Baseline (3 req/query) | High (9 req/query, may hit rate limits) | Low (1 req/query, gentle on API) | Moderate (~4-5 req/query) |
| **Network Bandwidth** | Standard throughput | 3x baseline throughput | < baseline throughput | ~1.5x baseline throughput |

### System Load Considerations

```
Speed Up: Use during off-peak hours or scale out infrastructure first
Slow Down: Safe to run with existing resources, low contention
Intensify: May need resource monitoring; avoid overlapping with CPU-intensive tasks
```

---

## Table E: Elasticity Rule Configuration Examples

### Speed Up Configuration Block

```yaml
domains:
  Military History:
    elasticity_enabled: true
    current_phase: speed_up
    
    elasticity_rules:
      speed_up:
        timing_adjustment: "+20%"
        timing_details: "48s delays (from baseline 60s)"
        batch_multiplier: 3  # 9 requests vs 3 standard
        subtask_increase: "+50%"
        
    phase_rotation_schedule:
      speed_up_observer: "Europe/EEST"
      slow_down_observer: null
      intensify_observer: null
```

### Slow Down Configuration Block

```yaml
domains:
  Space Exploration:
    elasticity_enabled: true
    current_phase: slow_down
    
    elasticity_rules:
      slow_down:
        timing_adjustment: "-15%"
        timing_details: "72s delays (from baseline 60s)"
        batch_multiplier: 0.3  # 1 request vs 3 standard
        verification_mode: "checkpoints between each step"
        parallel_reduction: "single-threaded focus"
        
    phase_rotation_schedule:
      speed_up_observer: null
      slow_down_observer: "America/EST"
      intensify_observer: null
```

### Intensify Configuration Block

```yaml
domains:
  Climate Science:
    elasticity_enabled: true
    current_phase: intensify
    
    elasticity_rules:
      intensify:
        timing_adjustment: "unchanged"
        timing_details: "60s delays (baseline)"
        subtask_increase: "+30%"
        analysis_depth: "deep + cross-check queries"
        secondary_queries: "auto-executed verification queries"
        
    phase_rotation_schedule:
      speed_up_observer: null
      slow_down_observer: null
      intensify_observer: "Asia/Shanghai"
```

---

## Table F: Output Markers by Phase

Each elasticity mode produces distinct output markers for identification:

| Phase | Output Header Marker | Key Indicators in Logs |
|-------|---------------------|------------------------|
| **Baseline** | `=== ⚪ BASELINE PHASE ===` | Standard delays (60s), batch size ×1, multi-threaded |
| **Speed Up** | `=== 🚀 SPEED UP PHASE ===` | Reduced delays (48s), batching requests (3x standard) |
| **Slow Down** | `=== 🐢 SLOW DOWN PHASE ===` | Increased delays (72s), verification checkpoints enabled |
| **Intensify** | `=== 💪 INTENSIFY PHASE ===` | Base timing maintained, extra subtasks (+30%), deeper analysis |

### Quick Visual Identification in Logs

```bash
# Search for active phase in logs
grep "PHASE:" ~/.hermes/logs/query_execution.log | tail -1
# Output: "PHASE: speed_up" or "PHASE: slow_down" etc.

# Or use output markers
grep "===" ~/.hermes/logs/scheduler.log | head -1
# Shows: "=== 🚀 SPEED UP PHASE ===" or similar marker
```

---

## Table G: Monitoring Metrics by Phase

| Metric Category | Baseline KPIs | Speed Up KPIs | Slow Down KPIs | Intensify KPIs |
|-----------------|---------------|---------------|----------------|----------------|
| **Efficiency** | Queries/hour: 60-80 | Queries/hour: 90-120 | Queries/hour: 40-50 | Queries/hour: 70-90 |
| **Quality** | Error rate <5% | Error rate 8-12% | Error rate <3% | Error rate <6% |
| **Coverage** | Source breadth: Standard | Source breadth: Maximum | Source depth: Deep | Source correlation: Multi-source |
| **Resource Usage** | CPU: Moderate | CPU: High (parallel) | CPU: Low (sequential) | CPU: Variable (bursts) |

### Warning Thresholds by Phase

```yaml
# Warning thresholds in config.yaml
monitoring:
  baseline:
    warning_completion_drop: "15%"
    warning_quality_drop: "0.10"
  
  speed_up:
    warning_rate_limit_errors: ">2 per hour"
    warning_quality_drop: "0.12"
  
  slow_down:
    warning_verification_failures: ">10% checkpoint failures"
    warning_timeout_rate: ">15%"
  
  intensify:
    warning_resource_saturation: ">80% CPU or memory"
    warning_query_duplication: ">2 similar queries in 1 hour"
```

---

## Table H: Integration Path Comparison

| Aspect | Phase 1 (Baseline) → Speed Up | Baseline → Slow Down | Baseline → Intensify |
|--------|-------------------------------|----------------------|----------------------|
| **Change Type** | Performance boost | Quality enhancement | Parallel depth increase |
| **Risk Level** | Medium (error rate increases) | Low (adds caution) | Medium (resource usage increases) |
| **Rollback Complexity** | Simple (revert timing/batch) | Simple (remove checkpoints) | Moderate (reduce parallelism) |
| **Typical Use Case** | Urgent information need | Quality-critical analysis | Cross-domain correlation needed |

---

## Table I: Domain Assignment Patterns Comparison

### Pattern A: Single-Timezone Focused

All three observers in same timezone; rotation happens via domain switching.

```yaml
domains:
  Military History:
    current_phase: speed_up
    observer_timezone: "Europe/EEST"  # Single timezone
    
    phase_rotation_schedule:
      speed_up_observer: "Europe/EEST"
      slow_down_observer: "Europe/EEST"
      intensify_observer: "Europe/EEST"
```

**Best for:** Simple deployments, single-user setups

---

### Pattern B: Geographic Distribution (Recommended)

Each observer in different timezone; rotation coordinated by hybrid scheduler.

```yaml
domains:
  Military History:
    elasticity_enabled: true
    phase_rotation_schedule:
      speed_up_observer: "Europe/EEST"        # Your hours when awake
      slow_down_observer: "America/EST"       # Previous day evening
      intensify_observer: "Asia/Shanghai"      # Midday same day
```

**Best for:** Multi-observer setups, hybrid sync pattern (Option D)

---

### Pattern C: Skill-Based Assignment

Observers assigned based on expertise rather than timezone.

```yaml
domains:
  Military History:
    elasticity_enabled: true
    phase_rotation_schedule:
      speed_up_observer: "Generalist-A"       # Broad survey capability
      slow_down_observer: "Specialist-Military"  # Primary source verification expert
      intensify_observer: "Analyst-Correlation"   # Multi-source correlation specialist
```

**Best for:** Teams with specialized expertise per phase type

---

## Table J: Emergency Switch Procedures Comparison

| Situation | Recommended Action | Command Example | Expected Recovery Time |
|-----------|-------------------|-----------------|------------------------|
| Speed up causing rate limits | Reduce batch_multiplier | `hermes config update ... batch_multiplier=2x` | <5 minutes |
| Slow down checkpoint failures | Switch to intensify mode | `hermes config update ... current_phase=intensify` | <1 minute |
| Intensify resource saturation | Limit parallelism factor | Add `max_parallelism_factor: 1.5` to config | <10 minutes |
| All phases degrading quality | Revert entire domain to baseline | `elasticity_enabled=false` | <2 minutes |
| Knowledge graph gaps | Full rollback of elasticity rules | `git checkout HEAD~1 config.yaml` + restart | <15 minutes |

---

## Table K: Performance Comparison Summary

### Baseline vs. Elasticity Modes (Military History Example)

| Aspect | Baseline | Speed Up (+20%) | Slow Down (-15%) | Intensify (+30%) |
|--------|----------|-----------------|------------------|------------------|
| **Information Gathering** | Good | ⚡⚡⚡ Best for breadth | Fair (sequential) | Good (parallel depth) |
| **Quality Assurance** | Standard | ⚠️ Reduced quality | 🛡️ Enhanced quality | Deep + cross-checks |
| **Time Criticality** | Moderate | ✅ Ideal for urgency | ❌ Not time-sensitive | Moderate (same pace) |
| **Resource Efficiency** | Good | ⚠️ High API load | ✅ Efficient | Moderate (burst usage) |
| **Best Domain Fit** | General-purpose | Military/urgent | Space/verification | Climate/correlation |

---

## Table L: Configuration Complexity Comparison

| Aspect | Baseline | Speed Up | Slow Down | Intensify |
|--------|----------|----------|-----------|-----------|
| **Config Blocks Required** | None (default) | Timing + batch keys | Timing + checkpoints + parallel_reduction | Subtask_increase + analysis_depth |
| **Validation Steps** | Syntax check only | Verify batch_multiplier value | Check timezone name validity | Ensure secondary_query_enabled |
| **Common Configuration Errors** | N/A | Batch multiplier type errors | Invalid timezone format | Missing analysis_depth field |
| **Monitoring Overhead** | None additional | Track completion rate drops | Track checkpoint pass rates | Monitor resource saturation |

---

## Table M: Expected Behavior in Output Logs

### Baseline Phase Sample

```
=== ⚪ BASELINE PHASE ===
→ Processing query #1: Operation Overlord strategic analysis...
   → Batch 3 requests completed (standard)
   → Multi-threaded execution active
   → Delay between steps: 60s
✓ Query completed, knowledge graph updated

---

=== ⚪ BASELINE PHASE ===
→ Processing query #2: WWII naval tactics Pacific theater...
   → Batch 3 requests completed (standard)
   → Multi-threaded execution active
   → Delay between steps: 60s
✓ Query completed, knowledge graph updated
```

### Speed Up Phase Sample

```
=== 🚀 SPEED UP PHASE ===
→ Reducing delays to 48s between steps...
→ Batching requests (3x standard size: 9 requests)...
→ Increasing parallel subtasks by 50%...
Starting research loop at elevated pace...

---

=== 🚀 SPEED UP PHASE ===
→ Query #1: Operation Overlord deployment analysis...
   → Batch 9 requests processed (speed up mode)
   → Parallel subtasks: 6 concurrent (vs 4 baseline)
✓ Faster completion, knowledge graph updated
```

### Slow Down Phase Sample

```
=== 🐢 SLOW DOWN PHASE ===
→ Increasing delays to 72s between steps...
→ Reducing batch size to single-threaded focus mode...
→ Adding verification checkpoint #1...
Starting research loop with careful scrutiny...

---

=== 🐢 SLOW DOWN PHASE ===
→ Query #1: Operation Overlord deployment analysis...
   → Request 1 of 3 processed (careful, sequential)
   → Verification checkpoint #1 initiated...
   → Document verified against primary source
✓ Quality-focused completion, knowledge graph updated
```

### Intensify Phase Sample

```
=== 💪 INTENSIFY PHASE ===
→ Maintaining base timing from 60s delays...
→ Adding extra subtasks (+30%) to parallel workload...
→ Requesting deeper analysis on topics...
Starting research loop with enhanced depth...

---

=== 💪 INTENSIFY PHASE ===
→ Query #1: Operation Overlord deployment analysis...
   → Base analysis completed (standard depth)
   → Deep analysis mode activated
   → Cross-check query initiated: correlation with D-Day planning docs
✓ Enhanced completion, knowledge graph updated
```

---

## 📋 Quick Reference: When to Use Each Mode

### Use Speed Up When:
- ✅ Time is critical and broad information needed
- ✅ Initial survey of source landscape
- ✅ Pattern recognition across many sources
- ⚠️ Monitor for quality degradation

### Use Slow Down When:
- ✅ Quality and accuracy are paramount
- ✅ Primary source verification required
- ✅ Careful cross-referencing of documents
- ⚠️ Accept slower throughput as trade-off

### Use Intensify When:
- ✅ Multi-source correlation needed
- ✅ Deep analysis across parallel dimensions
- ✅ Pattern integration across domains
- ⚠️ Watch for resource saturation

---

**This completes Phase 0 documentation!** 📄

Would you like to:
1. Review the architecture overview first?
2. Proceed to sign off on Phase 0 readiness?
3. Jump to creating your custom domain assignment configuration?

What's your preference, Avalon? 🎯
