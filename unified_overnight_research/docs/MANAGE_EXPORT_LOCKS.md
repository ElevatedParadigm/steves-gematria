# 🗄️ Visual Archive Export Lock Manager Documentation

**Location:** `/home/avalonas/.hermes/gematria/unified_overnight_research/scripts/manage_export_locks.py`  
**Wrapper:** `./manage_export_locks.sh`  
**Database:** `database/visual_archive_locks_log.json`  

---

## 📋 Overview

The Visual Archive Export Lock Manager monitors and handles `.git/index.lock` files that can become stale after interrupted Visual Archive export jobs. This prevents corruption and ensures clean git operations across your output directories.

---

## 🔧 Components

### 1. Core Python Script (`manage_export_locks.py`)
   - **Lock file detection** - Scans `output/` directory for `.git/index.lock` files
   - **Safe cleanup** - Removes stale locks with proper git command sequences
   - **Permission handling** - Gracefully handles permission errors
   - **Database logging** - Records all lock operations to JSON database

### 2. Shell Wrapper Script (`manage_export_locks.sh`)
   - Simple CLI interface for common operations
   - Supports specific subdirectory targeting

### 3. Systemd Service (Optional)
   - Automated cleanup on boot/trigger events
   - Located: `systemd/visual-archive-lock-manager.service`

### 4. Database Logging (`database/visual_archive_locks_log.json`)
   - Tracks all lock file operations
   - Stores timestamps, success/failure status
   - Maintains history for troubleshooting

---

## 🚀 Usage

### Quick Commands

```bash
# Check for lock files before export
/home/avalonas/.hermes/gematria/unified_overnight_research/scripts/manage_export_locks.sh check

# Safe cleanup with verification
./manage_export_locks.sh safe-cleanup

# Cleanup specific subdirectory
./manage_export_locks.sh safe-cleanup -s visual_archive

# Run health check
./manage_export_locks.sh health
```

### Python Script Directly

```bash
# Check lock files
python3 manage_export_locks.py check

# Safe cleanup (full mode)
python3 manage_export_locks.py safe-cleanup

# Cleanup with subdirectory
python3 manage_export_locks.py safe-cleanup --subdir visual_archive
```

### Systemd Integration

```bash
# Copy service file to systemd
sudo cp /home/avalonas/.hermes/gematria/unified_overnight_research/systemd/visual-archive-lock-manager.service /etc/systemd/system/

# Reload systemd and enable
sudo systemctl daemon-reload
sudo systemctl enable visual-archive-lock-manager.service

# Run now (one-shot)
sudo systemctl start visual-archive-lock-manager.service

# Check status
sudo systemctl status visual-archive-lock-manager.service
```

### Cron Job Integration

Add to user crontab:

```bash
crontab -e
```

```cron
# Check before export jobs (every 15 mins during export window)
*/15 * * * * /home/avalonas/.hermes/gematria/unified_overnight_research/scripts/manage_export_locks.sh check >> /home/avalonas/.hermes/cron/output/export-locks.log 2>&1

# Health check every 4 hours
0 */4 * * * /home/avalonas/.hermes/gematria/unified_overnight_research/scripts/manage_export_locks.sh health >> /home/avalonas/.hermes/cron/output/export-locks-health.log 2>&1
```

---

## 📊 Database Schema

**File:** `database/visual_archive_locks_log.json`

```json
{
  "version": "1.0",
  "initialized": true,
  "lock_records": [
    {
      "timestamp": "2026-05-01T12:34:56+00:00",
      "operation": "CLEANUP_SUMMARY",
      "status": "success",
      "message": "Cleanup completed: 1/1 locks removed",
      "details": {
        "locks_removed": 1,
        "locks_failed": 0,
        "permission_issues": 0
      }
    }
  ],
  "last_check": null,
  "last_cleanup": null
}
```

---

## 🔍 Troubleshooting

### Permission Denied Errors

**Problem:** Script cannot delete lock files due to incorrect ownership.

**Solution:**
```bash
# Check current permissions
ls -la /path/to/output/.git/index.lock

# Fix ownership (replace with appropriate user)
sudo chown avalonas:avalonas /path/to/output/.git/

# Or fix specific file permissions
chmod 644 /path/to/output/.git/index.lock
```

### Stale Locks After Interrupted Exports

**Problem:** Export job was killed but git lock remains.

**Solution:**
```bash
# Run safe cleanup (recommended first step)
./manage_export_locks.sh safe-cleanup

# If that fails, try direct removal
rm /path/to/output/.git/index.lock

# Verify repository integrity
cd /path/to/output && git fsck --full
```

### Database Logging Issues

**Problem:** Operations are not being logged.

**Solution:**
```bash
# Check if database file exists and is writable
ls -la /home/avalonas/.hermes/gematria/unified_overnight_research/database/visual_archive_locks_log.json

# Verify directory permissions
chmod 644 /home/avalonas/.hermes/gematria/unified_overnight_research/database/
```

---

## 📈 Monitoring

### Check Recent Lock Operations

```bash
# View last 20 records from database
cat database/visual_archive_locks_log.json | python3 -c "import sys,json; d=json.load(sys.stdin); print('\n'.join([json.dumps(r, indent=2) for r in d.get('lock_records',[])[-20:]]))"
```

### Health Check Output Example

```
======================================================================
🏥 Health Check: Visual Archive Lock Management System
======================================================================
✅ Output directory exists: /home/avalonas/.hermes/gematria/unified_overnight_research/output
✅ Git repository detected in output directory
   Found 0 lock file(s)

✅ SYSTEM HEALTH: No locks present - system is healthy
```

### Permission Issues Detected

When permission issues are found, you'll see:

```
⚠️  Warning: 1 file(s) with permission issues:
   - /output/visual_archive/.git/index.lock
     Recommendation: Manual intervention required or change directory permissions

💡 Recommendations:
   
   Check and fix permissions on the output directory:
     chmod -R ug+wx /home/avalonas/.hermes/gematria/unified_overnight_research/output
     Or run with elevated privileges as root/with sudo
```

---

## 🔧 Integration with Export Jobs

Add to your Visual Archive export script/hook:

```bash
#!/bin/bash

# Before export: Check for existing locks
/home/avalonas/.hermes/gematria/unified_overnight_research/scripts/manage_export_locks.sh check

# Run the export job
# ... export commands ...

# After export: Safe cleanup
/home/avalonas/.hermes/gematria/unified_overnight_research/scripts/manage_export_locks.sh safe-cleanup
```

Or as a post-job hook in cron:

```cron
# Example cron entry for export cleanup (adjust time based on your workflow)
30 2,8,14 * * * /home/avalonas/.hermes/gematria/unified_overnight_research/scripts/manage_export_locks.sh safe-cleanup -s visual_archive >> /home/avalonas/.hermes/cron/output/export-locks.log 2>&1
```

---

## 📝 Log File Locations

| Log | Location |
|-----|----------|
| Check operations | `/home/avalonas/.hermes/cron/output/export-locks-check.log` |
| Safe cleanup | `/home/avalonas/.hermes/cron/output/export-locks-safe.log` |
| Health checks | `/home/avalonas/.hermes/cron/output/export-locks-health.log` |
| Git operations | `/home/avalonas/.hermes/gematria/unified_overnight_research/logs/git_operations.log` |
| Database history | `database/visual_archive_locks_log.json` |

---

## 🛡️ Best Practices

1. **Run after exports:** Always call `safe-cleanup` after export jobs complete
2. **Permission ownership:** Ensure output directories are owned by the user running exports
3. **Database monitoring:** Regularly review `visual_archive_locks_log.json` for failed operations
4. **Health checks:** Use health command during maintenance windows
5. **Cron integration:** Add cleanup steps to your export workflow cron jobs

---

## 🔗 Related Files

- **Main script:** `scripts/manage_export_locks.py`
- **Shell wrapper:** `scripts/manage_export_locks.sh`
- **Systemd service:** `systemd/visual-archive-lock-manager.service`
- **Cron config template:** `cron_export_locks`
- **Database log:** `database/visual_archive_locks_log.json`

---

## 📖 License & Credits

Part of Steve's Gematria Unified Overnight Research Pipeline  
Version: 1.0  
Author: Hermes Agent (Auto-generated based on project conventions)  

---

**Quick Start:**

```bash
# Run your first lock management operation
/home/avalonas/.hermes/gematria/unified_overnight_research/scripts/manage_export_locks.sh health

# Add to crontab for automated maintenance
echo "*/30 * * * * /home/avalonas/.hermes/gematria/unified_overnight_research/scripts/manage_export_locks.sh check >> /home/avalonas/.hermes/cron/output/export-locks.log 2>&1" | crontab -

# Verify installation
ls -la /home/avalonas/.hermes/gematria/unified_overnight_research/scripts/manage_export_locks.*
```
