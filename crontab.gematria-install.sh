# Steve's Gematria Overnight Research Protocol - Cron Jobs
# Working directory: /home/avalonas/.hermes/gematria
# 
# Option 1 (DEFAULT): Daily at 3:00 AM - overnight research with anomaly detection
#   Runs scripts/overnight_research.py automatically each morning
#
# Option 2: After-work completion (hourly during work hours, skip nights)
# Option 3: Weekly Sunday runs
# 
# All options use crontab -e for manual installation (no sudo required)

# === OPTION 1: DAILY OVERNIGHT RESEARCH (3:00 AM) ===
# This is the recommended option for production overnight analysis
# Runs once daily at 3:00 AM local time
0 3 * * * /home/avalonas/.hermes/gematria/scripts/run_overnight_research.sh >> /home/avalonas/.hermes/gematria/logs/cron_overnight.log 2>&1

# === OPTION 2: WORK-HOURS OVERNIGHT RESEARCH (Hourly, skip nights) ===
# Runs every hour between 8 AM and 7 PM, skips overnight
HOUR=$(date +%u); if [ $HOUR -le 5 ] && [ $(date +%H) -ge 8 ] && [ $(date +%H) -le 19 ]; then /home/avalonas/.hermes/gematria/scripts/run_overnight_research.sh; fi

# === OPTION 3: WEEKLY SUNDAY RUNS (3:00 AM Sunday) ===
# Runs once per week on Sunday at 3:00 AM for batch analysis
0 3 * * 0 /home/avalonas/.hermes/gematria/scripts/run_overnight_research.sh >> /home/avalonas/.hermes/gematria/logs/cron_overnight.log 2>&1

# === OBSIDIAN SYNC CRON JOBS ===

# === OPTION 4: DAILY OBSIDIAN SYNC (5:00 AM - after overnight research) ===
0 5 * * * /home/avalonas/.hermes/gematria/scripts/run_auto_sync.sh >> /home/avalonas/.hermes/gematria/logs/cron_sync.log 2>&1

# === OPTION 5: WEEKLY FULL ANALYSIS (Sunday at 4:30 AM) ===
# Runs comprehensive analysis with multiple cycles
30 4 * * 0 /home/avalonas/.hermes/gematria/scripts/run_analysis_multi.sh >> /home/avalonas/.hermes/gematria/logs/cron_analysis.log 2>&1

# === INSTALLATION INSTRUCTIONS ===
# Copy relevant lines above to your crontab using:
#   crontab -e
# Then uncomment the option(s) you want by removing # prefix

# To verify cron job is installed, run:
#   crontab -l

# To view logs:
#   tail -f /home/avalonas/.hermes/gematria/logs/cron_overnight.log
