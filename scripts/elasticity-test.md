# 🧪 Elasticity Test Protocol: Standalone Demo

**Purpose:** Demonstrate all three elasticity behaviors (speed up, slow down, intensify) in isolation before integrating into main research loops.

---

## 📋 Test Objectives

1. **Speed Up Phase** — Execute research tasks 3x faster than normal (reduced delays between steps)
2. **Slow Down Phase** — Execute research tasks at 0.5x speed (increased delays for careful analysis)  
3. **Intensify Phase** — Run additional parallel subtasks while maintaining base pace

---

## 🎯 Elasticity Rules Implementation

The job will apply the following elasticity modifiers to the overnight research protocol:

### Speed Up (`+20%`)
- Reduce inter-step delays from 60s → 48s
- Batch requests where possible (3x normal batch size)
- Increase parallel subtask count by 50%

### Slow Down (`-15%`)
- Increase inter-step delays from 60s → 72s  
- Add verification checkpoints between each major step
- Reduce parallel subtasks to single-threaded execution for focus

### Intensify (Intense)
- Maintain base timing but add 30% additional subtasks per phase
- Request deeper analysis on each topic
- Run secondary cross-check queries automatically

---

## 🔬 Test Workflow

```
┌─────────────────────────────────────────────────────────┐
│ PHASE 1: BASELINE                                    │
│ - Single domain (Military History)                     │
│ - Standard timing                                      │
│ - 5-minute duration                                    │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ PHASE 2: SPEED UP                                    │
│ - Same domain                                         │
│ - +20% speed (48s delays)                              │
│ - Larger batches                                       │
│ - 5-minute duration                                    │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ PHASE 3: SLOW DOWN                                   │
│ - Same domain                                          │
│ - -15% speed (72s delays)                              │
│ - Verification checkpoints                              │
│ - Single-threaded                                      │
│ - 10-minute duration                                   │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ PHASE 4: INTENSIFY                                   │
│ - Same domain                                          │
│ - Base timing + extra subtasks (30%)                   │
│ - Deeper analysis requests                              │
│ - Cross-check queries                                  │
│ - 15-minute duration                                    │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Expected Output Markers

The test will output clear markers showing which elasticity rule is active:

```
=== 🚀 SPEED UP PHASE === 
→ Reducing delays to 48s between steps...
→ Batching requests (3x standard size)...
→ Starting research loop at elevated pace...

=== 🐢 SLOW DOWN PHASE ===
→ Increasing delays to 72s between steps...
→ Adding verification checkpoint #1...
→ Switching to single-threaded focus mode...

=== 💪 INTENSIFY PHASE ===
→ Maintaining base timing...
→ Adding extra subtasks (+30%)...
→ Requesting deeper analysis on topics...
```

---

## 🎓 Knowledge Gained

By running this standalone test, we'll verify:

1. ✅ The elasticity rule parser correctly reads and applies modifiers
2. ✅ Timing adjustments work as expected  
3. ✅ Batch size modifications function properly
4. ✅ Parallel subtask count changes are applied
5. ✅ Additional cross-check queries execute successfully
6. ✅ Clear output markers make debugging easier

---

## 🚀 Execution Command

Once this script is complete, run with:

```bash
hermes cronjob create \
  --action run \
  --prompt "Execute Elasticity Test Protocol with all phases" \
  --script /home/avalonas/.hermes/gematria/scripts/elasticity-test.md
```

This will demonstrate the full elasticity behavior without affecting any existing research loops.
