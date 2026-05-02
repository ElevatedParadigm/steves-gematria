# 🤖 STEVE'S GEMATRIA — Automation Guide

---

## **📋 Quick Start**

Choose your automation method below:

### **1. Manual Testing** (Best for development)
```bash
cd /home/avalonas/.hermes/gematria && python scripts/scheduler.py --immediate
# Runs all tasks immediately!
```

### **2. Background Scheduler** (Recommended - runs continuously)
```bash
cd /home/avalonas/.hermes/gematria && python scripts/scheduler.py &
# Starts scheduler in background, CTRL+C to stop
```

### **3. Simple Command Runner** (Quick one-liners)
```bash
cd /home/avalonas/.hermes/gematria && bash run_scheduler.sh overnight
# Run overnight research manually
```

### **4. Python Scheduler Script** (All tasks at intervals)
```bash
cd /home/avalonas/.hermes/gematria && python scripts/scheduler.py --all
# Background mode - runs all scheduled jobs
```

---

## **⏰ Default Schedule (3 AM overnight)**

| Task | Frequency | Command | Purpose |
|------|-----------|---------|---------|
| **Overnight Research** | Daily @ 3:00 AM | `scheduler.py --mode overnight` | Full gematria analysis |
| **Hourly Sync** | Every hour at :30 | `scheduler.py --mode hourly` | Relationship tracking |
| **Pattern Scan** | Every 6 hours | `scheduler.py --mode pattern` | Pattern convergence |
| **Health Check** | Every 30 minutes | `scheduler.py --health` | System monitoring |

---

## **🎯 Usage Examples**

### **Run overnight research right now:**
```bash
cd /home/avalonas/.hermes/gematria && python scripts/scheduler.py --mode overnight
```

### **Start the scheduler in background (recommended):**
```bash
cd /home/avalonas/.hermes/gematria && python scripts/scheduler.py
# Runs all jobs at their scheduled intervals
```

### **Run all tasks immediately (for testing):**
```bash
cd /home/avalonas/.hermes/gematria && python scripts/scheduler.py --immediate
```

### **Show scheduler job status:**
```bash
cd /home/avalonas/.hermes/gematria && python scripts/scheduler.py --status
```

---

## **📂 Output & Logs**

### **Generated Reports (Obsidian-compatible):**
- `/obsidian_exports/overnight_report_YYYY-MM-DD.md` - Daily overnight research
- `/obsidian_reports/CORE_SYMBOLS_SUMMARY.md` - Core symbol definitions
- `/obsidian_reports/DOMAIN_CONVERGENCE_REPORT.md` - Multi-domain analysis
- `/obsidian_reports/RELATIONSHIP_MATRIX.md` - Full relationship network
- `/obsidian_reports/CROSS_REFERENCE_INDEX.md` - Top cross-references

### **Log Files:**
- `/cron_logs/overnight.log` - Overnight research logs
- `/cron_logs/hourly.log` - Hourly sync logs  
- `/cron_logs/pattern.log` - Pattern scan logs
- `/cron_logs/health.log` - Health check logs

---

## **🔧 Configuration**

Edit `scheduler.py` to change schedules:

```python
# In /home/avalonas/.hermes/gematria/scripts/scheduler.py

# Change overnight research time (currently 3 AM)
CronTrigger(hour=3, minute=0)  # Change hour as needed

# Change hourly sync frequency (currently every hour)
CronTrigger(minute=30)  # Every hour at :30

# Change pattern scan frequency (currently every 6 hours)
CronTrigger(minute=0, hour=[0, 6, 12, 18])  # Midnight, noon, etc.
```

---

## **🐍 Python Scheduler Options**

### **Start background scheduler:**
```bash
python scripts/scheduler.py --all
# or just:
python scripts/scheduler.py
```

### **Stop scheduler:**
```bash
# Press Ctrl+C in the terminal running the scheduler
kill <process_id>  # If it keeps running
```

### **Check installed dependencies:**
```bash
pip list | grep -i apscheduler
# Should show: APScheduler [installed]
```

**Install scheduler if needed:**
```bash
pip install apscheduler
```

---

## **✅ System Status**

| Component | Status | Path |
|-----------|--------|------|
| Database | ✅ Ready | `database/gematria_database.json` |
| Scripts | ✅ Ready | `scripts/` (50 Python files) |
| Exports | ✅ Active | `obsidian_exports/` (27 markdown files) |
| Scheduler | ⏳ Background mode | Use `python scripts/scheduler.py` |

---

## **🎯 Core Symbols Tracked**

The overnight pipeline monitors these core symbols:
- **124** - Universal Threshold/Bridge
- **666** - Completion/Wholeness (→9)
- **963** - Cycle Turning/Harmony
- **55** - Resonance/Foundation
- **111** - Activation/Manifestation  
- **279** - Alternative cycle turning variant

---

## **🌉 Multi-Agent Domains**

| Domain | Status | Convergence Score |
|--------|--------|-------------------|
| Political Events | 🔴 Active | 0.99 |
| Religious Themes | 🟢 Monitoring | N/A |
| Economic Indicators | 🟡 Historical | 0.99 |
| Military Coups | 🔴 Active | 0.99 |
| Elemental Forces | 🟢 Monitoring | All domains |

---

## **📊 System Features**

- ✅ **Overnight Research**: Full gematria analysis at 3 AM daily
- ✅ **Auto-sync Engine**: Maintains relationship tracking (117 connections)
- ✅ **Health Monitoring**: Verifies database, scripts, exports every 30 min
- ✅ **Pattern Scans**: Detects convergence patterns every 6 hours
- ✅ **Firecrawl Integration**: Uses local Firecrawl at localhost:3002
- ✅ **Obsidian Format**: All reports in markdown for vault integration

---

## **🎮 Next Steps**

1. **Test the scheduler:** `python scripts/scheduler.py --immediate`
2. **Start background mode:** `python scripts/scheduler.py &`
3. **Verify overnight report generated:** Check `obsidian_exports/` folder
4. **Monitor logs:** `tail -f cron_logs/overnight.log`

---

## **📚 Additional Documentation**

- `AUTOMATION_README.md` — Quick reference commands
- `ARCHITECTURE.md` — Multi-agent system design
- `SETUP_COMPLETE_README.md` — Initial setup guide

---

## **🌙 Ready for Overnight Runs!**

Your multi-agent gematria system is ready for automatic overnight execution. Choose your preferred method above and start the scheduler! 🌉✨

---

*Generated by Steve's Gematria Multi-Agent System*  
*Obsidian-compatible format for knowledge graph integration*
