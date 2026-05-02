# 🌀 Automated Anomaly Detection System

## Overview

This system continuously monitors your gematria database for emerging patterns, 
symbol convergences, and cross-domain anomalies using local analysis.

## Files Created

- `/home/avalonas/.hermes/gematria/scripts/test_anomaly_detection.py` - Main detection script
- `/home/avalonas/.hermes/gematria/crontab.gematria-anomaly` - Crontab configuration  
- `/home/avalonas/.hermes/gematria/anomaly_reports/` - Output directory for reports

## Installation & Activation

### Option 1: Manual Daily Run (Recommended Starting Point)

```bash
cd /home/avalonas/.hermes/gematria && python3 scripts/test_anomaly_detection.py
```

**When to use:** Testing the system, first-time setup, occasional manual checks.

### Option 2: Install Cron Job (Automatic Execution)

Edit crontab with your preferred schedule:

```bash
crontab -e
```

Add one of these lines (see `/home/avalonas/.hermes/gematria/crontab.gematria-anomaly` for options):

**3 AM daily (recommended):**
```
0 3 * * * cd /home/avalonas/.hermes/gematria && python3 scripts/test_anomaly_detection.py >> ~/.hermes/logs/anomaly-detection.log 2>&1
```

All crontab lines include logging to `~/.hermes/logs/anomaly-detection.log`

## Cron Schedule Options

| Schedule | Frequency | Use Case |
|----------|-----------|----------|
| `0 3 * * *` | Once daily at 3 AM | **Production** - Overnight analysis without interfering with work |
| `0 0 * * *` | Once daily at midnight | Alternative timing preference |
| `0 3,21 * * *` | 3 AM + 9 PM | Twice daily monitoring |
| `*/6 * * * *` | Every 6 hours | Intensive monitoring (high frequency changes) |

### Install Crontab Configuration

```bash
crontab /home/avalonas/.hermes/gematria/crontab.gematria-anomaly
```

Or manually edit:

```bash
crontab -e
```

Then copy desired lines from `/home/avalonas/.hermes/gematria/crontab.gematria-anomaly`

## What Gets Detected

### 1. High-Correlation Symbols
- Symbols exceeding domain-specific thresholds (75%+ correlation)
- Cross-referenced with gematria database structure
- Ranked by correlation strength

### 2. Multi-Domain Convergence
- Patterns appearing across multiple domains simultaneously
- Indicates strong symbolic relationships
- Potential anomaly candidates for deeper analysis

### 3. Biblical Context Matches
- References to prophetic texts, revelations, apocalyptic literature
- Keywords: genesis, exodus, isaias, revelation, apocalypse
- Correlation with numeric convergence patterns

### 4. Geographic Anomalies  
- Border state and regional pattern correlations
- Geopolitical significance detection
- Geographic information system (GIS) data integration

## Report Output

Reports are saved to: `~/.hermes/gematria/anomaly_reports/`

Filename format: `anomaly_{timestamp}.md`

Example report structure:
```markdown
# 🔮 Daily Anomaly Detection Report

**Generated:** 2026-04-27 15:30:00 UTC  
**Detection Cycle:** Automated overnight analysis

## 📊 Summary Statistics

| Metric | Value |
|--------|-------|
| High-Correlation Symbols | 3 |
| Domains Analyzed | 5 |
```

## Verification & Testing

### Test the detection script:

```bash
cd /home/avalonas/.hermes/gematria && python3 scripts/test_anomaly_detection.py
```

Expected output:
```
============================================================
QUICK ANOMALY DETECTION TEST
============================================================

✓ Loaded database
  Keys: ['analyzed_items', 'analyzed_symbols', ...]

📊 Analyzed items by domain:
  1: 5 symbols
  0: 7 symbols
...

High-correlation symbols found: X
```

### Check log files:

```bash
tail -f ~/.hermes/logs/anomaly-detection.log
```

### View latest report:

```bash
ls -lt ~/.hermes/gematria/anomaly_reports/ | head -5
```

## Integration with Other Systems

### Tolaria Verification

The detection system can pipe anomalies to Tolaria for gematria validation:

```python
import subprocess

# After detecting anomalies, verify with Tolaria:
tolaria_check = subprocess.run(['tolaria', 'verify', '--symbols', anomaly_symbols], 
                                capture_output=True, text=True)
print(tolaria_check.stdout)
```

### Obsidian Knowledge Graph Update

Reports can be automatically linked to your Obsidian vault:

```python
obsidian_link_path = Path('/home/avalonas/.hermes/gematria/obsidian_exports/')
latest_report = list(report_dir.glob('*.md'))[-1] if report_dir.exists() else None

if latest_report:
    obsidian_link_path.mkdir(parents=True, exist_ok=True)
    link_name = f"ANOMALY_{latest_report.stem}_{datetime.now():%Y%m%d}".replace(':', '-')
    shutil.copy2(latest_report, obsidian_link_path / link_name)
```

## Troubleshooting

### Script not running automatically?

1. **Check cron syntax:**
   ```bash
   crontab -l  # View current crontab
   ```

2. **Verify Python is in PATH for cron:**
   ```bash
   which python3
   echo $PATH
   ```

3. **Test cron execution manually:**
   ```bash
   sudo -u avalonas bash -c "cd /home/avalonas/.hermes/gematria && python3 scripts/test_anomaly_detection.py"
   ```

4. **Check logs for errors:**
   ```bash
   tail -50 ~/.hermes/logs/anomaly-detection.log
   ```

### No anomalies detected?

This is normal if your database hasn't changed significantly. The system:
- Runs continuously in the background
- Accumulates data over time
- Will detect patterns as more information accumulates

### Database not found error?

```bash
# Verify database location
ls -lh /home/avalonas/.hermes/gematria/gematria_database.json

# If moved, update DB_PATH in crontab:
sudo nano ~/.hermes/gematria/crontab.gematria-anomaly
```

## Next Steps After Deployment

1. **First 24 hours:** Run manually to verify everything works
   ```bash
   cd /home/avalonas/.hermes/gematria && python3 scripts/test_anomaly_detection.py
   ```

2. **Review first automated report** when cron job runs (check log files)

3. **Set up email alerts** (optional) for high-correlation anomalies:
   ```bash
   # Install mail utility if needed
   sudo apt-get install -y mailutils
   
   # Add to crontab:
   0 3 * * * cd /home/avalonas/.hermes/gematria && python3 scripts/test_anomaly_detection.py && \
     find anomaly_reports -name 'anomaly_*.md' -newer /var/log/syslog | head -1 | xargs cat | mail -s "Gematria Anomaly Report" avalon@example.com
   ```

4. **Monitor correlation scores** in the report to identify emerging patterns

5. **Consider Tolaria integration** once baseline is established

## Files Modified/Created

- ✅ `/home/avalonas/.hermes/gematria/scripts/test_anomaly_detection.py` (created)
- ✅ `/home/avalonas/.hermes/gematria/crontab.gematria-anomaly` (created)  
- ✅ `/home/avalonas/.hermes/gematria/anomaly_reports/` (created directory)
- 📝 `~/.hermes/logs/anomaly-detection.log` (log file location)

## System Status

**Current State:** Detection script tested and ready for deployment.

**Next Action:** Install crontab entry OR run manually each day:

```bash
cd /home/avalonas/.hermes/gematria && python3 scripts/test_anomaly_detection.py
```

---
*Generated by Hermes Agent • Automated Anomaly Detection System*
