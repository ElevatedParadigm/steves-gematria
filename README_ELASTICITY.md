# 🧪 Elasticity Test Protocol: Standalone Demo

**Location:** `/home/avalonas/.hermes/gematria/scripts/elasticity-test.md`

**Purpose:** Demonstrate all three elasticity behaviors (speed up, slow down, intensify) in isolation before integrating into main research loops.

---

## 📋 Quick Start

### Option A: Run Directly
```bash
cd /home/avalonas/.hermes/gematria/scripts
python3 elasticity-test.py
```

### Option B: Via Cron Job
```bash
hermes cronjob create \
  --action run \
  --name "Elasticity Test Standalone" \
  --prompt "Run elasticity test protocol to demonstrate speed up, slow down, and intensify behaviors" \
  --script /home/avalonas/.hermes/gematria/scripts/elasticity-test.md
```

### Option C: Systemd Service
```bash
sudo systemctl enable --now elasticity-test.service
systemctl status elasticity-test.service
```

---

## 🎯 Test Objectives

1. ✅ **Verify elasticity rule parser** correctly reads and applies modifiers
2. ✅ **Confirm timing adjustments** work as expected (+20%, -15%)
3. ✅ **Test batch size modifications** function properly (3x, 0.3x)
4. ✅ **Validate parallel subtask changes** are applied correctly (+50%, -67%)
5. ✅ **Check cross-check queries** execute successfully
6. ✅ **Ensure clear output markers** make debugging easier

---

## 🔬 Three Elasticity Behaviors

### 🚀 Speed Up (`+20%`)
- Inter-step delays: 60s → 48s
- Batch size: 3 → 9 requests (3x standard)
- Parallel subtasks: +50%
- Goal: Demonstrate faster research cycle

### 🐢 Slow Down (`-15%`)
- Inter-step delays: 60s → 72s
- Batch size: 3 → 1 request (0.3x standard)
- Verification checkpoints between steps
- Single-threaded focus mode
- Goal: Demonstrate careful, focused analysis

### 💪 Intensify
- Inter-step delays: 60s (unchanged)
- Parallel subtasks: +30%
- Deeper analysis requests on topics
- Secondary cross-check queries automatically
- Goal: Show parallel processing depth increase

---

## 📊 Expected Output Structure

```
========================================
🧪 ELASTICITY TEST PROTOCOL - STANDALONE DEMO
========================================

⚪ BASELINE PHASE
   → Standard timing (60s delays)
   → Standard batch size
   ✅ Baseline completed

🚀 SPEED UP PHASE
   → Reduced delays to 48s between steps...
   → Batching requests (3x standard size)...
   ✅ Speed up completed

🐢 SLOW DOWN PHASE
   → Increasing delays to 72s between steps...
   → Adding verification checkpoints...
   ✅ Slow down completed

💪 INTENSIFY PHASE
   → Maintaining base timing...
   → Adding extra subtasks (+30%)...
   → Requesting deeper analysis...
   ✅ Intense completed

🎉 ALL PHASES COMPLETED
```

---

## 🎓 Knowledge Gained

After running this standalone test, you'll confirm:

1. ✅ The elasticity configuration system works independently
2. ✅ Each behavioral mode produces distinct output patterns
3. ✅ Timing modifications have real effects (visible delays)
4. ✅ Batch/parallel adjustments are correctly interpreted
5. ✅ Clear markers distinguish which phase is active
6. ✅ No interference with main research loops

---

## 🔧 Customization Options

### Change Test Domain
```python
TEST_DOMAIN = "Military History"  # Or: "Space Exploration", "Climate Science"
```

### Adjust Timing Thresholds
```python
BASE_DELAY = 60  # Standard delay in seconds (adjust for faster/slower demo)
```

### Modify Batch Multipliers
```python
# Speed up multiplier (default: 3x)
SPEED_UP_BATCH_MULTIPLIER = 3  

# Slow down multiplier (default: 0.3x)  
SLOW_DOWN_BATCH_MULTIPLIER = 0.3
```

---

## 🚀 Integration Path

Once standalone testing is confirmed working:

1. ✅ Remove `--script` flag (use direct elasticity rules in prompt)
2. ✅ Update main research loops to include elasticity option
3. ✅ Add monitoring to track which phase is active
4. ✅ Log elasticity metrics to database for analysis

---

## 📁 Related Files

- `/home/avalonas/.hermes/gematria/config.yaml` — Main config with elasticity rules defined
- `/home/avalonas/.hermes/gematria/scripts/elasticity-test.py` — Test script
- `/home/avalonas/.hermes/gematria/systemd/elasticity-test.service` — Systemd wrapper

---

## ✅ Verification Checklist

After running, confirm:

- [ ] All 4 phases completed in order (baseline → speed up → slow down → intensify)
- [ ] Output markers clearly distinguish each phase
- [ ] Timing delays match expected values (48s, 72s, 60s)
- [ ] No errors in stdout/stderr
- [ ] Script completes without interruption

---

## 🎉 Success Criteria

The standalone test is successful if:

1. ✅ Clear output markers for each phase appear
2. ✅ Timing adjustments are visible (delays differ by phase)
3. ✅ All phases complete without errors
4. ✅ Knowledge gained confirms elasticity rules work correctly
5. ✅ Ready to integrate into main research loops

---

**Next Step:** Run the test and confirm all phases execute properly! 🧪
