# Cron Installation Guide for Steve's Gematria Overnight Research Protocol
# ================================================================

## Option A: Direct crontab Edit (Recommended)

1. Create/edit the crontab file:
   ```bash
   crontab -e gematria-overnight
   ```
   
2. Add this line at the end of the file:
   ```bash
   0 3 * * * /home/avalonas/.hermes/gematria/scripts/auto_obisidian_sync_v2.py >> /home/avalonas/.hermes/gematria/logs/sync.log 2>&1
   ```

3. Save and exit (in vim: :wq, in nano: Ctrl+O then Enter, Ctrl+X)

---

## Option B: Copy from Template File

1. Copy the template crontab file:
   ```bash
   cp /home/avalonas/.hermes/gematria/crontab.gematria-overnight-v2 ~/.crontab/gematria-overnight 2>/dev/null || \
   echo "# Paste below into your crontab:" > /tmp/cron-template.txt && \
   tail -n +3 /home/avalonas/.hermes/gematria/crontab.gematria-overnight-v2 >> /tmp/cron-template.txt
   ```

2. Edit the generated file if needed, then run:
   ```bash
   crontab -e gematria-overnight
   ```

3. Add the line from above and save.

---

## Option C: Quick Copy-Paste

Simply add this single line to your crontab (`crontab -e`):

```bash
0 3 * * * /home/avalonas/.hermes/gematria/scripts/auto_obisidian_sync_v2.py >> /home/avalonas/.hermes/gematria/logs/sync.log 2>&1
```

---

## Verification After Installation:

```bash
# List installed cron jobs for gematria:
grep gematria ~/.crontab/gematria-overnight 2>/dev/null || crontab -l | grep gematria

# Test the script manually first (optional):
python /home/avalonas/.hermes/gematria/scripts/auto_obisidian_sync_v2.py

# Check logs after next run:
tail -f /home/avalonas/.hermes/gematria/logs/sync.log
```

---

## Next Run Time:

Cron jobs run at **3:00 AM** daily. The next execution will be:
- Within 24 hours from any time (e.g., if set up at 2 PM today, runs tomorrow at 3:00 AM)

---

## Logs Location:

Output appears in:
- `/home/avalonas/.hermes/gematria/logs/sync.log`

Check progress with:
```bash
tail -50 /home/avalonas/.hermes/gematria/logs/sync.log
```

---

## Troubleshooting:

If the job doesn't run:
1. Check crontab syntax: `crontab -l | grep gematria`
2. Verify script is executable: `ls -la /home/avalonas/.hermes/gematria/scripts/auto_obisidian_sync_v2.py`
3. Check PATH in crontab (shebang usually handles this)
4. Look at logs for errors: `cat /home/avalonas/.hermes/gematria/logs/sync.log | grep -i error`

---

## Alternative: Manual Running

If cron isn't working or you want to run manually:

```bash
cd /home/avalonas/.hermes/gematria && python scripts/auto_obisidian_sync_v2.py
```

---

**Ready to install? Run: `crontab -e gematria-overnight`** ✨
