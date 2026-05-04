# Git Lock Monitor for Visual Archive Export

## Overview

This tool monitors the `output/.git/index.lock` file for stale locks that can be left by interrupted Visual Archive export runs. Stale locks can cause subsequent export jobs to fail with "repository is locked" errors.

## Why This Matters

When a Visual Archive export job is interrupted (killed, crashed, or cancelled), it may leave behind `.git/index.lock` files. These are SQLite database locks that prevent further writes to the repository. Without cleanup, every new export attempt will fail until manually cleaned.

## Files Generated

| File | Description |
|------|-------------|
| `git_lock_monitor.py` | Core Python implementation with logging |
| `run_git_lock_monitor.sh` | Shell wrapper for cron/scripting use |
| `run_git_lock_monitor.py` | Main entry point with CLI arguments |
| `gematria-lock-monitor.service` | systemd service unit |
| `git_lock_logger.py` | SQLite database logger module |

## Installation

### 1. Place Files in Output Directory

```bash
cd /data/gematria/outputs
# Files are already created in this directory
chmod +x run_git_lock_monitor.sh run_git_lock_monitor.py
```

### 2. Verify Database Exists

```bash
ls -la output.db  # Should exist if Visual Archive is configured
```

### 3. Test the Monitor

```bash
python3 run_git_lock_monitor.py output --dry-run
# Or
./run_git_lock_monitor.sh output --db /data/gematria/outputs/output.db
```

## Usage

### Manual Check (Dry Run)

```bash
python3 run_git_lock_monitor.py output --db /data/gematria/outputs/output.db -n
```

### Manual Cleanup

```bash
python3 run_git_lock_monitor.py output --db /data/gematria/outputs/output.db
# Exit code 1 means lock was detected and cleaned up
```

### Cron Job (Check Every 5 Minutes)

```bash
# Edit crontab:
crontab -e

# Add this line to run every 5 minutes:
*/5 * * * * /data/gematria/outputs/run_git_lock_monitor.sh output >> /var/log/gematria/lock_monitor.log 2>&1
```

### Cron Job (Before Each Export)

If you control the export job script:

```bash
# In your export script before running Visual Archive export:
python3 run_git_lock_monitor.py output --db /data/gematria/outputs/output.db
EXIT_CODE=$?

if [ $EXIT_CODE -eq 2 ]; then
    echo "ERROR: Failed to clean up git locks" >&2
    exit 1
fi
```

### systemd Service (System-wide)

```bash
# Copy service file and edit paths:
cp output/gematria-lock-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload

# Enable and start:
sudo systemctl enable gematria-lock-monitor
sudo systemctl start gematria-lock-monitor
```

## Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | No lock detected (clean) | Continue normally |
| 1 | Lock was detected and cleaned | Continue (this is expected if cleanup worked) |
| 2 | Error occurred during cleanup | Stop export job and investigate |

## Database Logging

All actions are logged to the SQLite database (`output.db` or custom path via `--db`).

### Query Recent Logs

```bash
sqlite3 /data/gematria/outputs/output.db "SELECT timestamp, status, message FROM lock_monitor_actions ORDER BY timestamp DESC LIMIT 10;"
```

### Database Schema

```sql
CREATE TABLE lock_monitor_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    action_type TEXT NOT NULL CHECK (action_type IN ('check', 'cleanup', 'error')),
    status TEXT NOT NULL CHECK (status IN ('info', 'warning', 'success', 'error')),
    message TEXT NOT NULL,
    details TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Troubleshooting

### Lock Still Exists After Cleanup

Check if another process holds the lock:

```bash
# Check for processes holding the .git directory open
lsof +L1 /path/to/output/.git
# Or check who owns the file
stat -c '%U:%G' /path/to/output/.git/index.lock
```

### Permission Errors

```bash
# Ensure proper permissions on output directory
chown -R gematria_user:gematria_group output
chmod -R 750 output
```

### Database Not Found

If `--db` is not specified, the monitor searches for:
- `output/output.db`
- `db/output.db` (if `output` dir exists)
- `/data/gematria/outputs/output.db`
- Falls back to script's parent directory

Specify explicitly with `--db /full/path/to/output.db` if needed.

## How It Works

1. **Check Phase**: Detects if `output/.git/index.lock` exists and is stale (>60 seconds old)
2. **Git GC Attempt**: Runs `git gc` which may automatically clear the lock
3. **Directory Removal**: If lock persists, removes `.git` directory entirely
4. **Permission Recovery**: Applies `chmod +755` and retries if permission errors occur
5. **Logging**: Logs all actions to SQLite database with timestamps

## Integration Points

### Visual Archive Export Job Template

```bash
#!/bin/bash
# Before running visual_archive_export.py:

export GIT_LOCK_MONITOR_PATH="/data/gematria/outputs/run_git_lock_monitor.py"
export OUTPUT_DIR="${OUTPUT_DIR:-output}"
export DB_PATH="/data/gematria/outputs/output.db"

# Run lock monitor
python3 run_git_lock_monitor.py "$OUTPUT_DIR" --db "$DB_PATH" || true

# Check exit code (skip for expected cleanup)
if [ $? -eq 2 ]; then
    echo "ERROR: Git lock cleanup failed!" >&2
    cat /data/gematria/outputs/output.db >> "${GEMATRIA_LOGS_DIR}/lock_monitor_error.log"
    exit 1
fi

# Now run Visual Archive export
python3 visual_archive_export.py --all-options...
```

## Monitoring Dashboard Query

For monitoring dashboards (Prometheus, Grafana), query the database:

```sql
-- Total cleanup count
SELECT COUNT(*) FROM lock_monitor_actions 
WHERE action_type = 'cleanup' AND status = 'info';

-- Recent errors
SELECT timestamp, message FROM lock_monitor_actions 
WHERE status = 'error' ORDER BY timestamp DESC LIMIT 10;

-- Status distribution
SELECT status, COUNT(*) as cnt FROM lock_monitor_actions GROUP BY status;
```
