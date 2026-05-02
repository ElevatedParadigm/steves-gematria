# 📖 Usage Examples: Multi-Phase Elasticity Protocol

**Purpose:** Concrete examples demonstrating how to use elasticity rules with existing research loops.

---

## Example 1: Activating Speed Up Phase for Single Domain

### Scenario
Military History domain needs fast information gathering (e.g., broad survey of Operation Overlord sources).

### Configuration Addition

Add to `config.yaml` under the Military History domain section:

```yaml
domains:
  Military History:
    elasticity_enabled: true
    current_phase: speed_up
    phase_rotation_schedule:
      - speed_up_observer: "Europe/EEST"
        activation_time: "02:00-04:00 EEST"
      - slow_down_observer: null  # Not active during this period
      - intensify_observer: null
```

### Expected Behavior

- **Timing:** Standard delays (60s between steps)
- **Batch Size:** 9 requests instead of 3 (3x standard)
- **Parallel Subtasks:** 50% increase in simultaneous queries
- **Output Markers:** 
  ```
  === 🚀 SPEED UP PHASE === 
  → Reducing delays...
  → Batching requests (3x standard)...
  ```

### Usage Command

```bash
hermes cronjob create \
  --action run \
  --name "Military History Speed Up" \
  --prompt "Execute Military History research with speed up elasticity enabled: +20% faster timing, 3x batch size, increased parallelism"
```

---

## Example 2: Activating Slow Down Phase for Deep Analysis

### Scenario
Space Exploration domain requires careful verification of primary source documents (e.g., Soviet space program archives).

### Configuration Addition

```yaml
domains:
  Space Exploration:
    elasticity_enabled: true
    current_phase: slow_down
    phase_rotation_schedule:
      - speed_up_observer: null
      - slow_down_observer: "America/EST"
        activation_time: "02:00-04:00 EEST"
      - intensify_observer: null
```

### Expected Behavior

- **Timing:** 72s delays (increased for careful analysis)
- **Batch Size:** 1 request at a time (0.3x standard)
- **Verification Checkpoints:** Inserted before/after each major step
- **Execution Mode:** Single-threaded focus
- **Output Markers:**
  ```
  === 🐢 SLOW DOWN PHASE ===
  → Increasing delays to 72s...
  → Adding verification checkpoint #1...
  → Switching to single-threaded focus mode...
  ```

### Usage Command

```bash
hermes cronjob create \
  --action run \
  --name "Space Exploration Slow Down" \
  --prompt "Execute Space Exploration research with slow down elasticity enabled: -15% slower timing, verification checkpoints, single-threaded focus mode for careful analysis"
```

---

## Example 3: Activating Intensify Phase for Cross-Domain Correlation

### Scenario
Climate Science domain needs multi-source correlation analysis (e.g., verifying climate patterns across different research papers).

### Configuration Addition

```yaml
domains:
  Climate Science:
    elasticity_enabled: true
    current_phase: intensify
    phase_rotation_schedule:
      - speed_up_observer: null
      - slow_down_observer: null
      - intensify_observer: "Asia/Shanghai"
        activation_time: "02:00-04:00 EEST"
```

### Expected Behavior

- **Timing:** Standard (60s delays unchanged)
- **Parallel Subtasks:** +30% additional parallel queries
- **Analysis Depth:** Deep analysis on each topic
- **Cross-Check Queries:** Secondary verification queries auto-executed
- **Output Markers:**
  ```
  === 💪 INTENSIFY PHASE ===
  → Maintaining base timing...
  → Adding extra subtasks (+30%)...
  → Requesting deeper analysis on topics...
  ```

### Usage Command

```bash
hermes cronjob create \
  --action run \
  --name "Climate Science Intensify" \
  --prompt "Execute Climate Science research with intensify elasticity enabled: +30% extra subtasks, deeper analysis, auto-executed cross-check queries for correlation verification"
```

---

## Example 4: Domain Assignment Rotation (Hybrid Scheduler)

### Scenario
Military History domain spans multiple timezones; each observer handles different phase during their work hours.

### Configuration Setup

```yaml
domains:
  Military History:
    elasticity_enabled: true
    
    # Full rotation schedule covering 24-hour period
    phase_rotation_schedule:
      - Europe_EEST_2AM-4AM:
          current_phase: speed_up
          observer_timezone: "Europe/EEST"
          
      - America_EST_evening:
          current_phase: slow_down  
          observer_timezone: "America/EST"
          
      - Asia_CST_morning:
          current_phase: intensify
          observer_timezone: "Asia/Shanghai"
```

### Expected Behavior

The hybrid scheduler automatically:
1. Activates Europe observer with speed_up phase when it's 2AM EEST
2. Hands off to America observer with slow_down phase when it's evening EST
3. Transitions to Asia observer with intensify phase when it's morning CST

### Output Log Example

```
[02:00 EEST] → Activating speed_up for Military History (Europe observer)
               Batch multiplier set to 3x
               Parallel subtasks increased by 50%
               
[18:00 EST]   → Handoff to slow_down phase (America observer)
               Delays increased to 72s
               Verification checkpoints enabled
               
[12:00 CST]   → Handoff to intensify phase (Asia observer)
               Deep analysis mode enabled
               Cross-check queries auto-executed
```

---

## Example 5: On-Demand Phase Switching

### Scenario
Need to manually switch from speed_up to slow_down mid-cycle for urgent deep analysis.

### Usage Command

```bash
hermes tools update -d Military_History elasticity.current_phase=slow_down \
                     elasticity.phase_rotation_schedule.active_observer=America/EST
```

### Expected Behavior

- Immediate phase switch (no waiting for scheduled rotation)
- Old phase completes current operation before switching
- New phase begins with verification of transition

---

## Example 6: Monitoring Active Elasticity Phase

### Check Current Phase Status

```bash
hermes tools status -d Military_History | grep elasticity
```

Expected output:
```
Domain: Military History
Elasticity Phase: speed_up
Observer Timezone: Europe/EEST
Phase Start Time: 2026-04-29 18:30:00 EEST
Active Elasticity Modifier: +20% speed
Batch Multiplier: 3x
Parallel Subtasks Increase: +50%
```

### Check Phase History (Last 24 Hours)

```bash
hermes tools history -d Military_History --elasticity
```

Expected output:
```
2026-04-29 18:30 → Phase switch: baseline → speed_up
               Observer: Europe/EEST
               Elasticity modifier applied: +20% speed
               
2026-04-29 06:00 → Phase switch: intensify → baseline
               Observer handoff complete
```

---

## Example 7: Creating Custom Elasticity Preset

### Scenario
You want a permanent "Intensify" mode for Climate Science domain.

### Create Custom Configuration Block

```yaml
domains:
  Climate Science:
    elasticity_preset: intensify  # Always use intensify for this domain
    
    # Override with phase_rotation_schedule if you want rotation instead
    # phase_rotation_schedule: ...
    
    custom_evidence_rules:
      - type: correlation
        min_queries: 10
        confidence_threshold: 0.85
```

### Usage Command

```bash
hermes config load /home/avalonas/.hermes/gematria/config.yaml
hermes tools update preset=Climate_Science_intensify
```

---

## Example 8: Emergency Stop & Recovery

### Scenario
Speed up phase causing too many rate limit errors; need immediate pause.

### Usage Commands

```bash
# Pause elasticity for this domain
hermes cronjob pause --name "Elasticity Rotation Military_History"

# Revert to baseline mode only
hermes tools update -d Military_History \
                     elasticity_enabled=false \
                     elasticity.current_phase=baseline

# Resume after fix confirmed
hermes cronjob resume --name "Elasticity Rotation Military_History"
```

---

## 🎓 Best Practices

### When to Use Each Phase

| Phase | Ideal For | Not Suitable For |
|-------|-----------|------------------|
| **Speed Up** | Broad surveys, quick information gathering, initial source discovery | Critical verification, complex correlation analysis |
| **Slow Down** | Deep document verification, primary source analysis, quality-sensitive research | Time-critical operations, batch processing tasks |
| **Intensify** | Multi-source correlation, pattern recognition, cross-domain integration | Single-query operations, low-complexity topics |

### Phase Selection Guidelines

1. **Start with baseline** — Establish normal performance reference
2. **Rotate through phases** — Let each phase run for its scheduled window
3. **Monitor metrics** — Track completion rates and output quality per phase
4. **Adjust observer assignments** — If certain domains need more focus time
5. **Document patterns** — Note which phases work best for which domain types

### Common Pitfalls to Avoid

- ❌ Activating multiple observers simultaneously without rotation logic
- ❌ Using slow_down for high-throughput tasks (causes bottlenecks)
- ❌ Ignoring verification checkpoint failures during slow_down phase
- ❌ Running speed_up on quality-critical domains without monitoring
- ❌ Not checking API rate limits when increasing batch size

---

## 🔍 Troubleshooting Quick Reference

### Speed Up Issues

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Rate limit errors | 3x batch too large | Reduce batch_multiplier to 2x temporarily |
| API timeouts | Too many parallel requests | Reduce subtask_increase to +30% |
| Quality degradation | Rushed processing | Pause, revert to baseline, review verification needs |

### Slow Down Issues

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Checkpoint failures | Sources unavailable during extended wait | Switch to baseline or intensify mode |
| Progress stalls too slow | Delays too aggressive | Reduce timing_modifier from -15% to -10% |
| Knowledge graph gaps | Missing verification checkpoints | Enable checkpoint logging, adjust thresholds |

### Intensify Issues

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Cross-check timeouts | Too many secondary queries | Reduce subtask_increase to +20% |
| Resource exhaustion | Parallelism too high for current load | Lower parallel_factor temporarily |
| Query duplication | Same topic analyzed multiple times | Enable deduplication in config |

---

## 📞 Support Contacts & Resources

- **Full Architecture Docs:** `/home/avalonas/.hermes/gematria/docs/architecture-overview.md`
- **Integration Checklist:** `/home/avalonas/.hermes/gematria/docs/integration-checklist.md`
- **Elasticity Reference:** `/home/avalonas/.hermes/gematria/config.yaml` (elasticity_rules section)
- **Test Script Demo:** `/home/avalonas/.hermes/gematria/scripts/elasticity-test.py`

---

**Ready for Phase 2 (Configuration Validation) or would you like more examples first?** 🎯
