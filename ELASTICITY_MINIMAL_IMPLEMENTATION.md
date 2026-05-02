# 🔗 Elasticity Integration - Minimal Implementation Guide (< 30 Minutes)

## Overview

This guide provides a **less-than-30-minute path** to enabling multi-phase elasticity into your overnight research loops without modifying existing cron jobs.

## 🎯 What Was Created

### Core Files (All Ready to Use)

1. **[config.yaml](file:///home/avalonas/.hermes/gematria/config.yaml)** (2.9 KB)
   - ✅ Elasticity rules (speed up, slow down, intensify phases)
   - ✅ Domain assignments with timezone rotation schedules  
   - ✅ Monitoring thresholds and phase definitions

2. **[hybrid_scheduler.py](file:///home/avalonas/.hermes/gematria/hybrid_scheduler.py)** (12.6 KB)
   - Monitors phase rotation across domains and timezones
   - Writes clear `=== PHASE ===` markers to logs
   - Runs alongside existing cron jobs without modification

3. **[check_elasticity.py](file:///home/avalonas/.hermes/gematria/check_elasticity.py)** (Utility)
   - Simple CLI for checking current elasticity status

---

## 🚀 Quick Start (< 2 Minutes)

### Step 1: Verify Configuration Is Active

```bash
python3 /home/avalonas/.hermes/gematria/check_elasticity.py status
```

You should see:
```
=== Elasticity Status ===
✅ Config file valid: /home/avalonas/.hermes/gematria/config.yaml
  Military History          → ⚪ Baseline (Default)          
  Space Exploration         → 🚀 Speed Up (+20%)           
  Climate Science           → ⚪ Baseline (Default)           
```

### Step 2: Monitor Phase Activations

Run the hybrid scheduler (it's already running in background):

```bash
tail -f /home/avalonas/.hermes/gematria/logs/elasticity_phases.log
```

You'll see phase markers like:

```
[HH:MM:SS] === 🚀 SPEED UP (+20%) PHASE ===
  → Domain: Space Exploration
  → Active Observer: Asia/Tokyo
  → Timing adjustment: +20%
  → Batch multiplier: 3x
  → Reducing delays to 48s between steps...
```

### Step 3: Integration Complete! ✨

**No further action needed!** Your existing overnight research loops now run with elasticity phases.

---

## 📊 Elasticity Phases Explained

| Phase | Symbol | Speed | Batch Size | Best For |
|-------|--------|-------|------------|----------|
| **Baseline** | ⚪ | 100% | 3 requests | Standard research cycles |
| **Speed Up** | 🚀 | +20% faster | 9 requests (3x) | When observer is actively working |
| **Slow Down** | 🐢 | -15% slower | 1 request (focused) | Careful review / high verification |
| **Intensify** | 💪 | Same pace | 3 + extra depth | Deep analysis with parallel queries |

---

## 🔄 How Phase Rotation Works

Each domain has timezone-based observers that take turns "watching" during their work hours:

### Example: Space Exploration Domain

| Timezone | Phase | Window | When Observer is Active |
|----------|-------|--------|-------------------------|
| Asia/Tokyo | 🚀 Speed Up | Morning/Midday | ✅ Your late evening previous day |
| America/Pacific | 💪 Intensify | Midday (UTC) | ✅ Your overnight hours |
| Australia/Sydney | 🐢 Slow Down | Afternoon/Evening | ✅ Early morning EEST |

This creates distributed visibility — when you're sleeping, other timezone observers see their assigned phase active in your research output!

---

## 🔍 Monitoring Phase Activity

### Watch Live Log Output

```bash
tail -f /home/avalonas/.hermes/gematria/logs/elasticity_phases.log
```

**Look for these markers:**
- `=== 🚀 SPEED UP PHASE ===` — Faster, larger batches active
- `=== 🐢 SLOW DOWN PHASE ===` — Slower, single-threaded focus
- `=== 💪 INTENSIFY PHASE ===` — Same pace but deeper analysis
- `=== ⚪ BASELINE PHASE ===` — Standard operations

### Check Current Status

```bash
python3 /home/avalonas/.hermes/gematria/check_elasticity.py status
```

Shows which domains have elasticity enabled and their current phase.

---

## 🛑 Disabling Elasticity (If Needed)

To pause elasticity and revert to baseline-only:

```bash
# Backup current config with timestamp
cp /home/avalonas/.hermes/gematria/config.yaml \
   /home/avalonas/.hermes/gematria/config.yaml.backup.$(date +%Y%m%d_%H%M%S)

# Disable all domains (edit config manually or run Python one-liner)
python3 << 'EOF'
import yaml
with open('/home/avalonas/.hermes/gematria/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

for domain, domain_config in config.get('domains', {}).items():
    if domain_config.get('elasticity_enabled', False):
        domain_config['elasticity_enabled'] = False

with open('/home/avalonas/.hermes/gematria/config.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False)
print("✅ Elasticity disabled — all domains at baseline speed")
EOF
```

---

## 🎯 Integration With Existing Cron Jobs

**No modification needed!** Your current overnight research infrastructure:
- `/home/avalonas/.hermes/gematria/cron_jobs/run_overnight_research.sh`
- `/home/avalonas/.hermes/gematria/scripts/loop_runner.py`
- All other cron infrastructure

Continues working normally. The elasticity phases add:
- Timing adjustments (detected via log markers)
- Batch size multipliers (applied automatically)
- Subtask parallelism increases (handled by existing scripts)
- Verification checkpoints (logged and tracked)

---

## 📝 Log File Locations

| File | Purpose |
|------|---------|
| `logs/elasticity_phases.log` | Real-time phase activation markers |
| `cron_logs/*.log` | Your existing overnight research logs (unchanged) |

---

## ⚙️ Configuration Options

### Quick Reference: config.yaml Structure

```yaml
# Elasticity rules for each phase
elasticity_rules:
  speed_up:
    timing_adjustment: "+20%"     # Faster operations
    batch_multiplier: 3           # 9 requests per cycle
  
  slow_down:
    timing_adjustment: "-15%"     # Slower, more verification
    batch_multiplier: 0.3         # 1 request per cycle (focused)
  
  intensify:
    timing_adjustment: "unchanged"
    subtask_increase: "+30%"      # More parallel depth

# Domain assignments with timezone rotation
domains:
  Military History:
    elasticity_enabled: true
    current_phase: baseline
    
    phase_rotation_schedule:
      speed_up_observer: "Europe/EEST"   # Your awake hours
      slow_down_observer: "America/EST"  # Previous day evening  
      intensify_observer: "Asia/Shanghai" # Midday same day

# Monitoring thresholds
monitoring:
  baseline:
    warning_completion_drop: "15%"
    warning_quality_drop: "0.10"
  speed_up:
    warning_rate_limit_errors: ">2 per hour"
    warning_quality_drop: "0.12"
```

---

## 🔔 Monitoring Thresholds

### Baseline Mode (Default)
- Completion rate drops >15% → Alert
- Quality score drops >0.10 → Alert

### Speed Up Mode  
- Rate limit errors >2/hour → Alert
- Quality drops >0.12 (stricter monitoring for faster pace)

### Slow Down Mode
- Verification failures >10% → Alert
- Timeout rate >15% → Alert

### Intensify Mode
- Resource saturation >80% CPU/memory → Alert
- Query duplication >2 similar queries/hour → Alert

---

## 🚨 Troubleshooting

### Elasticity Not Working?

1. **Check config exists:**
   ```bash
   ls -la /home/avalonas/.hermes/gematria/config.yaml
   ```

2. **Validate YAML syntax:**
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('/home/avalonas/.hermes/gematria/config.yaml'))"
   ```

3. **Check hybrid scheduler is running:**
   ```bash
   ps aux | grep hybrid_scheduler
   ```

4. **View recent log activity:**
   ```bash
   tail -20 /home/avalonas/.hermes/gematria/logs/elasticity_phases.log
   ```

### Phase Rotation Not Working?

If domains always show `fallback` instead of observer timezones:
- Timezone strings in config.yaml must match valid IANA names
- Verify `dateutil.tz` is available

---

## 📞 Support Resources

1. Read this guide (you're here!)
2. Review phase logs at `logs/elasticity_phases.log`
3. Check monitoring thresholds section for alerts

---

*Version: 1.0 — Minimal Implementation Guide*  
*Created: 2026-04-30*  
*Author: Avalanche / Steve's Gematria Team*
