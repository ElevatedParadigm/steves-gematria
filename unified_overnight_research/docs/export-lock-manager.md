# Visual Archive Export Lock Manager - Complete Solution

## Overview

This cron-managed script monitors and handles `.git/index.lock` files during Visual Archive exports to prevent stale locks after interrupted runs.

**Problem:** When git operations or Visual Archive exports are interrupted (e.g., system crash, power loss, manual termination), `.git/index.lock` files can become stale, blocking subsequent export jobs.

**Solution:** Automated monitoring and cleanup with proper permission handling, logging, and verification.

---

## Quick Start

### 1. Install Crontab

```bash
crontab -u avalonas < /home/avalonas/.hermes/gematria/unified_overnight_research/cron_export_locks
```

**OR** edit existing crontab:
```bash
crontab -e  # user: avalonas
# or sudo crontab -e for system-wide
```

### 2. Verify Installation

```bash
/home/avalonas/.hermes/gematria/unified_overnight_research/scripts/manage_export_locks.sh health
```

### 3. Manual Testing

```bash
# Check for existing locks
/home/avalonas/.hermes/gematria/unified_overnight_research/scripts/manage_export_locks.sh check

# Safe cleanup with verification
/home/avalonas/.hermes/gematria/unified_overnight_research/scripts/manage_export_locks.sh safe-cleanup

# Health monitoring
/home/avalonas/.hermes/gematria/unified_overnight_research/scripts/manage_export_locks.sh health
```

---

## Commands Reference

### `check` - Check for Lock Files Before Export

Verifies the output directory for stale `.git/index.lock` files before starting Visual Archive export jobs.

**Cron Usage:** 15 minutes before scheduled exports
```bash
*/15 * * * * scripts/manage_export_locks.sh check >> logs/export-locks-check.log 2>&1
```

**Example Output:**
```
Lock files found: 0
[no locks present - export can proceed]
```

### `cleanup` - Remove Stale Lock Files

Directly removes stale lock files without additional verification. Use for post-export cleanup.

**Cron Usage:** After export jobs complete or on schedule
```bash
*/30 * * * * scripts/manage_export_locks.sh cleanup >> logs/export-locks-cleanup.log 2>&1
```

**Options:**
```bash
scripts/manage_export_locks.sh cleanup -s visual_archive  # Specific subdirectory
```

### `safe-cleanup` - Safe Cleanup with Verification (RECOMMENDED)

Performs a safe, multi-step cleanup process:
1. Checks for lock files
2. Removes stale locks with proper error handling
3. Verifies git repository integrity with `git --full-gc`
4. Reports permission issues and provides recommendations

**Cron Usage:** Regular scheduled maintenance
```bash
0 */4 * * * scripts/manage_export_locks.sh safe-cleanup >> logs/export-locks-safe.log 2>&1
```

### `health` - Health Check

Monitors overall system health for lock management:
- Output directory existence
- Git repository detection
- Lock file staleness analysis
- Database integrity verification

**Cron Usage:** Regular monitoring interval
```bash
0 */4 * * * scripts/manage_export_locks.sh health >> logs/export-locks-health.log 2>&1
```

---

## Manual Intervention Commands

### Quick Cleanup (On-Demand)

Add to personal crontab or run manually:
```bash
# Run every minute during tight loops
* * * * * /home/avalonas/.hermes/gematria/unified_overnight_research/scripts/manage_export_locks.sh check >> /tmp/export-locks-check.log 2>&1

# Immediate cleanup after known interruption
*/5 * * * * /home/avalonas/.hermes/gematria/unified_overnight_research/scripts/manage_export_locks.sh safe-cleanup >> logs/export-locks-immediate.log 2>&1
```

### Visual Archive Specific Monitoring

For heavy-processing subdirectories:
```bash
# Monitor visual_archive every hour
0 * * * * scripts/manage_export_locks.sh check -s visual_archive >> logs/export-locks-visual-archive.log 2>&1
```

---

## Database Structure

Lock operations are logged to:
```
output/database/visual_archive_locks_log.json
```

**Database Fields:**
- `version`: Schema version (currently 1.0)
- `lock_records`: Array of operation records (max 100 kept, older records discarded)
- `git_operations_log`: Parallel log file in `logs/git_operations.log`
- `config`: Configuration parameters

**Log Record Example:**
```json
{
  "timestamp": "2026-05-04T14:30:00Z",
  "operation": "CLEANUP_SUMMARY",
  "status": "success",
  "message": "Cleanup completed: 1/1 locks removed, 0 failed, 0 permission issues",
  "details": {
    "locks_removed": 1,
    "locks_failed": 0,
    "permission_issues": 0
  }
}
```

---

## Handling Permission Issues

If cleanup reports permission issues:

### Option 1: Fix Directory Permissions
```bash
# Add write permissions for group and others
chmod -R ug+wx /home/avalonas/.hermes/gematria/unified_overnight_research/output

# Or fix specific directory
sudo chown avalonas:avalonas /path/to/.git/index.lock
sudo chmod 644 /path/to/.git/index.lock
```

### Option 2: Run with Elevated Privileges
```bash
# For cron jobs requiring sudo access (use caution)
sudo -u avalonas /home/avalonas/.hermes/gematria/unified_overnight_research/scripts/manage_export_locks.sh safe-cleanup
```

---

## Log Files Reference

| Log File | Purpose | Check Interval |
|----------|---------|----------------|
| `export-locks-check.log` | Lock file detection before exports | Every 15 min |
| `export-locks-cleanup.log` | Cleanup operations | Every 30 min |
| `export-locks-safe.log` | Safe cleanup with verification | Every 4 hours |
| `export-locks-health.log` | System health monitoring | Every 4 hours |
| `git_operations.log` | All git lock operations (append-only) | Continuous |

**Log Rotation:** See crontab configuration for automatic log compression.

---

## Troubleshooting

### Stale Lock After Export Interruption

1. **Run health check to diagnose:**
   ```bash
   scripts/manage_export_locks.sh health
   ```

2. **If stale locks detected, run safe-cleanup:**
   ```bash
   scripts/manage_export_locks.sh safe-cleanup -s visual_archive
   ```

3. **Review recommendations in output** for permission issues

### Permission Denied Errors

**Cause:** Lock file owned by different user/group

**Solution:**
```bash
# Check current ownership
ls -la /path/to/.git/index.lock

# Fix ownership
sudo chown avalonas:avalonas /path/to/.git/index.lock

# Or temporarily add write permission for testing
chmod 644 /path/to/.git/index.lock
```

### Git Repository Corruption After Lock Removal

**Symptom:** Errors after lock cleanup

**Solution:**
```bash
# Run git gc to repair repository
cd /home/avalonas/.hermes/gematria/unified_overnight_research/output
git --full-gc

# If still corrupted, check for loose objects
git fsck --full
```

---

## Best Practices

### 1. Always Use `safe-cleanup` in Production

The safe-cleanup mode provides:
- ✅ Multiple-step verification
- ✅ Git integrity checks after removal
- ✅ Permission issue reporting
- ✅ Detailed recommendations

### 2. Monitor Health Regularly

Health checks every 4 hours provide ongoing visibility into:
- Lock file presence during active exports
- Staleness indicators
- Database integrity
- System status

### 3. Log Rotation is Critical

Crontab includes automatic log compression for files >50MB to prevent GitHub push failures (see skill: hermes-cron-job-management).

### 4. Use Specific Subdirectories When Possible

```bash
scripts/manage_export_locks.sh check -s visual_archive
```

Reduces noise in logs and focuses on relevant subdirectories.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Visual Archive Export                     │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   Cron Scheduler                      │   │
│  │               (*/15 * * * *)                         │   │
│  └─────────────────────┬─────────────────────────────────┘   │
│                        │                                       │
│                        ▼                                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Check Command (before export start)           │   │
│  │         - scans output/.git/                          │   │
│  │         - identifies stale locks (>1hr old)           │   │
│  └─────────────────────┬─────────────────────────────────┘   │
│                        │                                       │
│                        ▼                                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               Cleanup Command                         │   │
│  │         - direct deletion of .git/index.lock          │   │
│  │         - permission checking                         │   │
│  │         - git --full-gc verification                  │   │
│  └─────────────────────┬─────────────────────────────────┘   │
│                        │                                       │
│                        ▼                                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │        Logging & Database Recording                   │   │
│  │         - JSON database (visual_archive_locks_log.json) │
│  │         - Git operations log file                      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Testing the System

### 1. Create a Test Lock File

```bash
# Simulate stale lock
touch /home/avalonas/.hermes/gematria/unified_overnight_research/output/.git/index.lock
echo "test" > /home/avalonas/.hermes/gematria/unified_overnight_research/output/.git/index.lock
# Modify old to simulate staleness
stat -c %Y /home/avalonas/.hermes/gematria/unified_overnight_research/output/.git/index.lock  # get mtime
touch -d "2026-05-01 12:00:00" \
    /home/avalonas/.hermes/gematria/unified_overnight_research/output/.git/index.lock

# Verify stale status
ls -la /home/avalonas/.hermes/gematria/unified_overnight_research/output/.git/index.lock
```

### 2. Test Cleanup

```bash
/home/avalonas/.hermes/gematria/unified_overnight_research/scripts/manage_export_locks.sh safe-cleanup
```

Should report: "✅ Successfully removed X lock file(s)"

### 3. Verify Database Logging

```bash
cat /home/avalonas/.hermes/gematria/unified_overnight_research/output/database/visual_archive_locks_log.json | python3 -m json.tool
```

---

## References

- **Main Script:** `scripts/manage_export_locks.py`
- **Shell Wrapper:** `scripts/manage_export_locks.sh`
- **Crontab Config:** `cron_export_locks`
- **Database:** `output/database/visual_archive_locks_log.json`
- **AGENTS.md:** `/home/avalonas/.hermes/gematria/unified_overnight_research/AGENTS.md`

## Support

For additional help:
- Review log files in `/home/avalonas/.hermes/cron/output/`
- Check git operations log in `logs/git_operations.log`
- See crontab configuration comments for options
