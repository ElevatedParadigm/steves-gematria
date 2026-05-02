# 🔧 Troubleshooting Guide: Multi-Phase Elasticity Protocol

**Purpose:** Comprehensive troubleshooting procedures for common issues when integrating elasticity into existing research loops.

---

## 1. Quick Reference: Symptom → Root Cause → Solution

### 🚨 Critical Issues (Immediate Action Required)

| Symptom | Root Cause | Solution Command | Risk Level |
|---------|-----------|------------------|------------|
| **No queries executing** | Elasticity rules parser failed | `hermes config validate` + reload service | Medium |
| **All queries timeout** | Batch multiplier too aggressive | Pause phase, reduce batch_multiplier to 1.5x | Low |
| **Knowledge graph corruption** | Cross-phase continuity break | Full rollback to previous config version | High |
| **API rate limit errors cascade** | Speed up phase exceeding capacity | Emergency pause, revert to baseline | Medium |
| **Verification checkpoints all fail** | Slow down mode sources unavailable | Switch to intensify or baseline temporarily | Low |

### ⚠️ Warning Signs (Monitor Closely)

| Symptom | Root Cause | Recommended Action | Risk Level |
|---------|-----------|-------------------|------------|
| Completion rate drops >20% | Elasticity phase mismatched for domain | Pause current phase, adjust domain assignment | Medium |
| Output quality degrades noticeably | Too aggressive timing modifications | Review elasticity_modifier percentages | Low-Medium |
| Phase rotation schedule not executing | Hybrid scheduler not loading config correctly | Re-run hybrid_scheduler initialization | Low |
| Parallel subtask utilization erratic | Resource contention with other processes | Monitor system resources, reduce parallel_factor | Low |

### ✅ Normal Variations (No Action Required)

| Symptom | Interpretation |
|---------|-----------------|
| Minor completion rate fluctuation (<10%) | Natural variability between phases |
| Slightly longer processing for first query of new phase | Phase warm-up period expected |
| Occasional cross-check query timeout in intensify mode | Retry logic handles transient failures |

---

## 2. Detailed Troubleshooting Procedures

### Procedure A: Elasticity Rules Not Applying

**Symptom:** Queries run at baseline speed despite elasticity rules enabled.

#### Step-by-Step Diagnosis:

```bash
# 1. Verify config.yaml syntax and elasticity section
hermes config validate /home/avalonas/.hermes/gematria/config.yaml

# 2. Check if domain has elasticity enabled
grep -A 3 "Military History:" /home/avalonas/.hermes/gematria/config.yaml | grep elasticity_enabled

# Expected output: elasticity_enabled: true
```

**If disabled:**
```bash
# Enable elasticity for this domain
hermes config update domains.Military_History.elasticity_enabled=true

# Reload service to apply changes
systemctl reload gematria-research-loop
```

#### Verify Rules Are Loaded:

```python
# Check in Python REPL or via API
from config import elasticity_rules

print(elasticity_rules['speed_up'])
# Expected: {'timing_adjustment': '48s delays', 'batch_multiplier': 3, ...}
```

**If not in config:**
- Add elasticity rules to `config.yaml` under the domain section
- Use merge strategy (not overwrite) to preserve existing custom rules
- Restart service after configuration change

---

### Procedure B: Batch Size Modulation Not Working

**Symptom:** Speed up phase still processing 3 requests instead of 9.

#### Diagnosis:

```bash
# Check current active configuration for this domain
hermes tools status -d Military_History | grep batch_multiplier
```

**If showing 3x instead of expected 9x:**

```yaml
# In config.yaml, verify correct syntax:
domains:
  Military History:
    elasticity_rules:
      speed_up:
        batch_multiplier: 3  # This means 3x standard (which is 9 requests)
```

#### Common Syntax Error:

```yaml
# ❌ WRONG: Confusing multiplier with absolute value
batch_multiplier: 9   # Would mean 9 requests total, not 3x standard

# ✅ CORRECT: Multiplier relative to baseline
batch_multiplier: 3   # Means 3x the baseline of 3 = 9 requests
```

#### Fix Command:

```bash
hermes config update \
    domains.Military_History.elasticity_rules.speed_up.batch_multiplier=3

systemctl reload gematria-research-loop
```

---

### Procedure C: Phase Rotation Not Executing

**Symptom:** Domain stays in baseline mode indefinitely, no phase transitions.

#### Step-by-Step Diagnosis:

```bash
# 1. Check hybrid_scheduler service status
systemctl status hybrid_scheduler

# 2. Review scheduler logs for errors
journalctl -u hybrid_scheduler --since "1 hour ago" | grep error

# 3. Verify domain assignments are valid YAML syntax
python3 -c "import yaml; yaml.safe_load(open('/home/avalonas/.hermes/gematria/config.yaml'))"
```

#### Common Causes:

1. **Missing observer timezone assignment:**
   ```yaml
   # ❌ INCOMPLETE - missing slow_down_observer
   domains:
     Military History:
       phase_rotation_schedule:
         speed_up_observer: "Europe/EEST"
         intensify_observer: "Asia/Shanghai"
   
   # ✅ FIXED - all phases assigned
   domains:
     Military History:
       phase_rotation_schedule:
         speed_up_observer: "Europe/EEST"
         slow_down_observer: "America/EST"
         intensify_observer: "Asia/Shanghai"
   ```

2. **Hybrid scheduler not initialized:**
   ```bash
   hermes tools enable hybrid_scheduler --init-domains-from-config
   ```

3. **Timezone name mismatch:**
   ```bash
   # Valid timezone formats for observers:
   - Europe/EEST
   - America/New_York
   - Asia/Shanghai
   - Australia/Sydney
   
   # Invalid (use abbreviation instead):
   - "UTC+8"  ❌ WRONG
   - "China Standard Time"  ❌ WRONG
   ```

---

### Procedure D: Output Quality Degradation in Speed Up Phase

**Symptom:** Queries complete faster but results are incomplete or inaccurate.

#### Diagnosis:

```bash
# Check completion rates and error patterns per phase
hermes tools metrics -d Military_History --phase=baseline > baseline_metrics.txt
hermes tools metrics -d Military_History --phase=speed_up > speedup_metrics.txt

# Compare key metrics
diff baseline_metrics.txt speedup_metrics.txt | grep "completion_rate\|quality_score"
```

**Typical finding:**
```
baseline:  completion_rate=95%, quality_score=0.88
speed_up:  completion_rate=78%, quality_score=0.62
```

#### Solutions:

**Option 1: Reduce speed up aggressiveness**
```bash
hermes config update \
    domains.Military_History.elasticity_rules.speed_up.timing_adjustment="+15%" \
    domains.Military_History.elasticity_rules.speed_up.batch_multiplier=2.5x
```

**Option 2: Remove from speed_up rotation, keep baseline**
```bash
hermes config update \
    domains.Military_History.current_phase=baseline
```

**Option 3: Add additional verification for speed_up phase**
Add to config.yaml:
```yaml
domains:
  Military History:
    elasticity_rules:
      speed_up:
        # Keep fast timing but add lightweight verification
        post_verification_enabled: true
        post_verification_type: "summary_check"  # Lightweight cross-check
```

---

### Procedure E: Verification Checkpoints All Failing in Slow Down Phase

**Symptom:** Every checkpoint fails, progress halts constantly.

#### Diagnosis:

```bash
# Review checkpoint logs
tail -100 ~/.hermes/logs/scheduler_checkpoint.log | grep -A 5 "FAILED"

# Check source availability patterns
curl -s "http://localhost:3002/status/sources/availability" | python3 -m json.tool
```

**Typical finding:** Sources unavailable during slow_down delays (72s wait times)

#### Solutions:

**Option 1: Switch to intensify mode temporarily**
```bash
hermes config update \
    domains.Space_Exploration.current_phase=intensify
systemctl reload gematria-research-loop
```

**Option 2: Reduce slow_down timing aggressiveness**
```bash
hermes config update \
    domains.Space_Exploration.elasticity_rules.slow_down.timing_adjustment="+10%"
```

**Option 3: Add source availability check before checkpoint**
```yaml
# In config.yaml under slow_down:
skip_unavailable_sources: true  # Don't wait if source is down
retry_after_short_delay: "5s"  # Short retry instead of full delay
```

---

### Procedure F: Knowledge Graph Showing Gaps After Slow Down Phase

**Symptom:** Queries complete but new facts not persisted to knowledge graph.

#### Diagnosis:

```bash
# Check query execution logs for persistence failures
grep -E "persist|save|write" ~/.hermes/logs/query_execution.log | tail -50

# Verify database connectivity
python3 -c "from gematria_db import Database; db = Database(); print(db.health_check())"
```

#### Common Cause: Extended delays causing timeout before persistence

**Fix:** Increase database connection pool size temporarily

```bash
# Edit ~/.hermes/gematria/database_config.yaml
connection_pool_size: 20  # Increase from default 10
```

Then reload service and verify knowledge graph updates.

---

### Procedure G: Parallel Subtask Saturation in Intensify Phase

**Symptom:** System CPU/Memory usage spikes during intensify phase, causing slowdowns.

#### Diagnosis:

```bash
# Check resource utilization during intensify phase
watch -n 1 'echo "CPU:"; top -bn1 | head -3' &
watch -n 1 'echo "MEM:"; free -m' &

# Monitor parallel subtask count per phase
hermes tools metrics --phase=intensify --metric=parallel_subtasks_used
```

**Typical finding:** Parallelism exceeds system capacity

#### Solutions:

**Option 1: Reduce intensify aggressiveness**
```bash
hermes config update \
    domains.Climate_Science.elasticity_rules.intensify.subtask_increase="+25%"
```

**Option 2: Limit intensify to off-peak hours only**
Add to phase_rotation_schedule:
```yaml
phase_rotation_schedule:
  - intensify_observer: "Asia/Shanghai"
    activation_time: "01:00-03:00"  # Restricted window
```

**Option 3: Implement dynamic scaling based on system load**
Add to config.yaml:
```yaml
domains:
  Climate Science:
    elasticity_rules:
      intensify:
        max_parallelism_factor: 1.5  # Limit to 1.5x baseline regardless of rule
```

---

## 3. Rollback Procedures by Risk Level

### Immediate (<5 minutes) — Critical Failure

**Symptom:** System unresponsive or severe data corruption

```bash
# 1. Pause all elasticity-enabled loops
hermes cronjob pause --name "Elasticity Rotation"

# 2. Revert to last known good config (from version control)
git checkout HEAD~1 /home/avalonas/.hermes/gematria/config.yaml

# 3. Reload service
systemctl restart gematria-research-loop

# 4. Verify baseline-only operation restored
hermes tools status -all | grep elasticity_enabled
# Expected: All showing false or null
```

### Partial (<30 minutes) — Performance Degradation

**Symptom:** Slower than normal but not critical failure

```bash
# 1. Disable elasticity for affected domain only
hermes config update \
    domains.Military_History.elasticity_enabled=false

# 2. Revert phase to baseline
hermes config update \
    domains.Military_History.current_phase=baseline

# 3. Verify restored normal operation
hermes tools metrics -d Military_History --since="15 minutes ago" | grep completion_rate
```

### Extended (<2 hours) — Quality Issues Detected

**Symptom:** Output quality degraded but system operational

```bash
# 1. Pause phase rotation schedule (keep single-phase baseline)
hermes cronjob pause --name "Elasticity Rotation Military_History"

# 2. Document issue for future iteration
echo "Issue: Speed up phase causing quality degradation in Military History domain" \
    >> ~/.hermes/gematria/issues/speed_up_quality_issues.md

# 3. Resume with baseline-only operation
hermes cronjob resume --name "Baseline Rotation Military_History"
```

---

## 4. Monitoring Commands for Health Checks

### Quick Health Check (1 command)

```bash
hermes tools health-check \
    domains=all \
    metrics=completion_rate,quality_score,error_rate \
    phases=all
```

**Expected output:**
```json
{
  "Military_History": {
    "baseline": {"completion_rate": 95%, "quality_score": 0.88, "error_rate": 2%},
    "speed_up": {"completion_rate": 78%, "quality_score": 0.62, "error_rate": 15%},
    "slow_down": {"completion_rate": 92%, "quality_score": 0.91, "error_rate": 3%},
    "intensify": {"completion_rate": 88%, "quality_score": 0.89, "error_rate": 4%}
  }
}
```

### Detailed Status Report

```bash
hermes tools status -d Military_History \
    --elasticity-details \
    --resource-utilization \
    --phase-rotation-timeline
```

**Expected output:** Shows current phase, active observer, resource usage, and rotation timeline

---

## 5. Common Configuration Errors & Fixes

### Error: "Unknown elasticity phase"

**Cause:** Typo in phase name or using invalid phase name

**Fix:**
```yaml
# ❌ WRONG: Invalid phase name
domains:
  Military History:
    current_phase: fast_mode  # Should be speed_up
    
# ✅ CORRECT
domains:
  Military History:
    current_phase: speed_up  # Valid phase names: baseline, speed_up, slow_down, intensify
```

### Error: "Missing batch_multiplier key"

**Cause:** Incomplete elasticity_rules section in config.yaml

**Fix:**
```yaml
# Add missing keys
domains:
  Military History:
    elasticity_rules:
      speed_up:
        timing_adjustment: "+20%"
        batch_multiplier: 3  # ← Was missing this
```

### Error: "Phase rotation schedule not valid"

**Cause:** Missing required observer timezone for current phase

**Fix:**
```yaml
# All three observers must be assigned (even if one is null)
domains:
  Military History:
    phase_rotation_schedule:
      speed_up_observer: "Europe/EEST"
      slow_down_observer: null  # Valid: explicitly null
      intensify_observer: "Asia/Shanghai"
```

---

## 6. Performance Baselines for Comparison

### Expected Metrics by Phase (Military History Domain)

| Metric | Baseline | Speed Up (+20%) | Slow Down (-15%) | Intensify (+30%) |
|--------|----------|-----------------|------------------|------------------|
| Query completion rate | 95% | 85% | 92% | 88% |
| Quality score | 0.88 | 0.75 | 0.91 | 0.89 |
| Time per query | 60s | 48s | 72s | 60s |
| API request count | 3 req/query | 9 req/query | 1 req/query | 4 req/query |

### Performance Acceptability Thresholds

- ✅ **Green:** Within ±10% of baseline metrics
- ⚠️ **Yellow:** 10-20% degradation, monitor closely
- 🔴 **Red:** >20% degradation or critical errors — pause immediately

---

## 7. Contact Information for Escalation

### Level 1: Self-Service (Documented Here)
- Use quick reference tables above
- Follow troubleshooting procedures A-G
- Run health check commands

### Level 2: Configuration Review (5-minute wait)
```bash
# Request config review via cronjob message queue
hermes tools request-review --domain=Military_History \
    --issue-type="Elasticity phase not applying"
```

### Level 3: Architecture Team (Critical only)
- Contact via webhook to architecture monitoring channel
- Escalate only for knowledge graph corruption or data loss

---

## 📞 Support Resources

1. **Configuration Docs:** `/home/avalonas/.hermes/gematria/docs/architecture-overview.md`
2. **Usage Examples:** `/home/avalonas/.hermes/gematria/docs/usage-examples.md`
3. **Elasticity Reference:** `/home/avalonas/.hermes/gematria/config.yaml`
4. **Test Script Demo:** `scripts/elasticity-test.py`

**Remember:** Most issues resolve with simple configuration corrections or phase reassignment!

---

**Phase 0 documentation complete!** Would you like to proceed to Phase 1 (Domain Assignment) or review any specific troubleshooting scenario? 🔧
