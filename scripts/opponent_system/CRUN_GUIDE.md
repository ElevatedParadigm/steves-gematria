# 🎯 Gematria Opponent System - Cron Job Configuration Guide

## ✅ Currently Active

| Job Name | Schedule | Mode | Last Run | Status |
|----------|----------|------|----------|--------|
| `adversarial-research-loop` | Every 45min | Continuous (auto) | — | **Active** ✓ |

---

## 📅 Cron Job Details

**Job ID:** `702469336acd`  
**Schedule:** Every 45 minutes (overnight research pattern)  
**Mode:** Automatic continuous loop

### What it does:
- Runs the adversarial research system continuously in auto-loop mode
- Tests all 6 core symbol hypotheses against domain law axioms
- Provides Bayesian-updating of hypothesis strength via debate loops
- Maintains scientific integrity through falsification engine scrutiny

---

## 🔄 Manual Control Options

### Start Continuous Loop:
```bash
cd /home/avalonas/.hermes/gematria/scripts
python3 opponent_system.py --mode continuous
```

### Run Interactive Mode (one round at a time):
```bash
cd /home/avalonas/.hermes/gematria/scripts
python3 opponent_system.py
# Select "1" for interactive mode
```

### View System Status:
```bash
cd /home/avalonas/.hermes/gematria/scripts  
python3 opponent_system.py
# Select "2" to view heat-scale status overview
```

---

## 🛑 Stopping the Loop

### Stop Current Session:
Press `Ctrl+C` in the terminal running the loop.

### Check if Running:
```bash
ps aux | grep 'opponent_system.py'
```

### Kill Process (if needed):
```bash
pkill -f "python3 opponent_system.py"
# or more specific:
pkill -9 "opponent_system.py"
```

---

## 📊 Logging

All output goes to console. For file logging, add to your script:

```bash
cd /home/avalonas/.hermes/gematria/scripts
python3 opponent_system.py >> /var/log/hermes/gematria-debate.log 2>&1 &
```

---

## 🔧 Configuration Options

### Modify Schedule (Cron Job):
Use the Hermes cronjob interface to change:
- Frequency (e.g., `every 30m`, `every 1h`, `daily at 3AM`)
- Pause/Resume job when needed
- Update prompts or skills

### Change State Persistence:
Edit state file location in `/scripts/state.json` path.

---

## 📈 Monitoring Health

### Check Last Debate Results:
```bash
cd /home/avalonas/.hermes/gematria/scripts
python3 -c "import json; data = json.load(open('state.json')); print(json.dumps(data['hypotheses'], indent=2))"
```

### Review Recent Arbitration Decisions:
Look at `arbitrator_results_count` in state output.

---

## ⚙️ System Service (Future Setup)

For persistent auto-start after reboot, a systemd service file has been created at:
- `/home/avalonas/.hermes/gematria/system/hermes-gematria-opponent.service`

To enable after reboot (requires sudo):
```bash
sudo cp /home/avalonas/.hermes/gematria/system/hermes-gematria-opponent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable hermes-gematria-opponent.service
```

---

## 🎉 Summary

✅ Cron job active: Every 45 minutes in auto-loop mode  
✅ All 6 advocates loaded for core symbols  
✅ Falsification engine ready for meta-level scrutiny  
✅ Arbitrator configured with Bayesian updating  
✅ Domain Law axioms enforced (Conservation, Simplicity, Consistency)  

**The system is running automatically while you heat up those sausages! 🌭**

---

*Self-sustaining opponent system ready for overnight adversarial research.* 🚀
