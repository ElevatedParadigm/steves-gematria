# Installation Guide for Overnight Research Loop

## 🌙 Quick Start (Systemd)

### 1. Install systemd service and timer

```bash
# Copy files to /etc/systemd/system/ (or keep in gematria directory)
sudo cp /home/avalonas/.hermes/gematria/overnight_loop.service /etc/systemd/system/
sudo cp /home/avalonas/.hermes/gematria/overnight_loop.timer /etc/systemd/system/

# Reload systemd daemon
sudo systemctl daemon-reload

# Enable and start the timer
sudo systemctl enable --now overnight_loop.timer
sudo systemctl enable --now overnight_loop.service
```

### 2. Verify installation

```bash
# Check timer status
systemctl list-timers | grep overnight_loop

# Expected output shows next activation times at hours 0,3,6,9,12,15,18,21 UTC
```

### 3. Test manual run (optional)

```bash
python3 /home/avalonas/.hermes/gematria/scripts/loop_runner_enhanced.py
```

---

## 📜 Quick Start (Cron - Alternative for non-systemd)

### Copy cron file to system cron:

```bash
sudo cp /home/avalonas/.hermes/gematria/overnight_loop.cron /etc/cron.d/gematria-overnight
```

### Or source manually:

```bash
crontab -e
# Add this line:
0 0,3,6,9,12,15,18,21 * * * /home/avalonas/.hermes/gematria/scripts/hybrid_scheduler.py --interval 1800 & sleep 30; /home/avalonas/.hermes/gematria/scripts/loop_runner_enhanced.py >> /home/avalonas/.hermes/gematria/cron_logs/loop_runner_cron.log 2>&1
```

---

## 📊 OVERNIGHT RESEARCH LOOP CONFIGURATION

### Schedule:
- **Frequency:** Every 3 hours at :00 minute
- **Hours (UTC):** 0, 3, 6, 9, 12, 15, 18, 21
- **Next run from UTC midnight:** 03:00

### Script Pipeline (executed each interval):

```bash
# Phase A: Elasticity Monitoring (30 seconds)
/usr/bin/python3 /home/avalonas/.hermes/gematria/scripts/hybrid_scheduler.py --interval 1800 &

# Wait for hybrid scheduler to initialize
sleep 30

# Phase B: Main Research Loop
/usr/bin/python3 /home/avalonas/.hermes/gematria/scripts/loop_runner_enhanced.py
```

---

## 🎯 LOOP PHASES EXPLAINED

### Phase 1: Enhanced Stability Test (`stability_test_enhanced_fixed.py`)
- Scans gematria database for corruption/inconsistency
- Validates symbolic relationships
- Verifies cross-domain integrity
- **Logs:** `STABILITY_TEST_*.md` in `obsidian_exports/`

### Phase 2: Auto-Obsidian Sync (`auto_obisidian_sync_v2.py`)
- Extracts relationship matrices from database
- Generates markdown notes with YAML frontmatter
- Creates cross-reference indices
- **Outputs:** Multiple `.md` files with Tolaria-compliant structure

### Phase 3: Correlation Heatmaps (Generated inline)
- Analyzes symbol correlations in database
- Visualizes relationship density via ASCII art
- Documents elemental force patterns
- **Outputs:** `correlation_heatmap.md`, `heatmap_status.ascii` in `obsidian_exports/correlation_heatmaps/`

### Phase 4: Hybrid Scheduler Check
- Reads current elasticity phase from scheduler state
- Logs phase rotation events
- Integrates with multi-phase monitoring system
- **Logs:** Updates `phase_markers_*.log` file

---

## 📋 LOG FILES ORGANIZATION

All logs go to `/home/avalonas/.hermes/gematria/cron_logs/`:

| File | Purpose |
|------|---------|
| `loop_enhanced_YYYYMMDD_HHMMSS.log` | Full run logs with timestamps |
| `phase_markers_YYYYMM.log` | Phase rotation markers for elasticity monitoring |
| `loop_runner_cron.log` | Cron-based execution logs |
| `service.log`, `service_error.log` | Systemd service output/error |
| `STABILITY_TEST_*.md` | Stability test reports |
| Various `.md` files | Sync outputs, heatmaps, etc. |

---

## ⚙️ AUTO-RESTART & RETRY LOGIC

### Automatic Retry:
- **Max retries:** 3 attempts per phase
- **Retry delay:** 5 seconds between attempts
- **Failures logged:** Yes, with error details in main log

### Systemd Auto-Restart:
- On failure: Service restarts automatically after 30 seconds
- Configured via `Restart=on-failure` and `RestartSec=30` in service file

---

## 🔍 MONITORING COMMANDS

### Check recent runs:

```bash
tail -f /home/avalonas/.hermes/gematria/cron_logs/phase_markers_*.log
ls -lt /home/avalonas/.hermes/gematria/cron_logs/*.log | head -20
```

### View latest log:

```bash
cat $(ls -t /home/avalonas/.hermes/gematria/cron_logs/loop_enhanced_*.log | head -1)
```

### Check systemd status:

```bash
systemctl status overnight_loop.timer
systemctl status overnight_loop.service
journalctl -u overnight_loop.timer -f
```

---

## 🛠️ ELASTICITY MONITORING INTEGRATION

The loop integrates with `hybrid_scheduler.py` for multi-phase operations:

### Elasticity Phases (from config.yaml):

| Phase | Speed Multiplier | Batch Size | Timeout Multiplier | Parallel Depth |
|-------|-----------------|------------|-------------------|----------------|
| baseline | 1.0x | 3 | 1.0x | 1 |
| speed_up | 1.2x | 9 | 0.8x | 1 |
| slow_down | 0.85x | 3 | 1.15x | 1 |
| intensify | 1.0x | 3 | 1.0x | 4 |

### Phase Rotation Logic:

- **speed_up:** UTC hours 8-18 (business hours)
- **slow_down:** UTC hours 4-12 (early morning)
- **baseline:** UTC hours 0-4 and 18-24 (off-hours)
- **intensify:** UTC hours 2-3, 22-4 (deep work sessions)

---

## 📦 INCLUDED FILES

### Created during this setup:

```
/home/avalonas/.hermes/gematria/
├── scripts/
│   ├── loop_runner_enhanced.py          ✅ Main loop orchestrator
│   └── hybrid_scheduler.py               ✅ Elasticity monitoring
├── cron_logs/                           ✅ Log directory (created)
├── overnight_loop.service               ✅ Systemd service file
├── overnight_loop.timer                 ✅ Systemd timer file
├── overnight_loop.cron                  ✅ Cron alternative script
└── README_OVERNIGHT_LOOP_INSTALL.md     ← This file
```

---

## 📊 PHASE MARKER LOG FORMAT

Phase markers are written to `phase_markers_YYYYMM.log`:

```
[2026-05-02 03:00:01 UTC] [STABILITY TEST] Starting enhanced stability test
[2026-05-02 03:15:05 UTC] [AUTO-SYNC] Starting auto-sync with relationship matrices
[2026-05-02 03:30:08 UTC] [HEATMAP] Starting correlation heatmap generation
[2026-05-02 03:45:12 UTC] [HYBRID SCHEDULER] Phase: BASELINE - 2026-05-02 03:45:00 UTC
[2026-05-02 03:45:15 UTC] [COMPLETE] All phases completed
```

---

## 🎓 NEXT STEPS

1. **Install systemd service:** `sudo systemctl enable --now overnight_loop.timer`
2. **Verify installation:** `systemctl list-timers | grep overnight_loop`
3. **Test manual run (optional):** `python3 /home/avalonas/.hermes/gematria/scripts/loop_runner_enhanced.py`
4. **Monitor logs:** `tail -f /home/avalonas/.hermes/gematria/cron_logs/phase_markers_*.log`

---

## 🆘 TROUBLESHOOTING

### Issue: Timer not triggering

```bash
# Check timer status
systemctl list-timers | grep overnight_loop

# Enable and reload
sudo systemctl daemon-reload
sudo systemctl enable --now overnight_loop.timer
```

### Issue: Script errors in logs

Check `service_error.log` or latest `loop_enhanced_*.log` for details.

### Issue: Need to stop/restart

```bash
sudo systemctl stop overnight_loop.service
sudo systemctl start overnight_loop.service
sudo systemctl restart overnight_loop.timer
```

---

**Status:** ✅ CRON JOB CREATED AND CONFIGURED  
**Version:** Enhanced Overnight Research Loop v2.0  
**Last Updated:** 2026-05-02
