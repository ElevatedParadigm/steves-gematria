# 📦 Visual Archive Export Job Manager

**Location:** `/home/avalonas/.hermes/gematria/unified_overnight_research/scripts/manage_visual_archive_exports.py`  
**Wrapper:** `./manage_visual_archive_exports.sh`  
**Database:** `database/gematria_database.json` (symbol_state table)

---

## 📋 OVERVIEW

The Visual Archive Export Job Manager handles parallel export processing of symbols from the `symbol_state` queue. It processes exports in batches of 3-5 symbols simultaneously, tracks progress and failures, handles retries automatically, and logs all activity to both the database and cron output files.

### Key Features:

1. **Queue-Based Processing** - Reads pending exports from `symbol_state.exports_queue` table
2. **Parallel Batching** - Processes 4 symbols in parallel (configurable)
3. **Retry Logic** - Automatically retries failed exports up to 3 times
4. **Status Tracking** - Maintains separate queues for completed and failed jobs
5. **Database Logging** - All operations logged to `gematria_database.json` symbol_state section
6. **Cron Integration** - Outputs logged to `cron/output/visual-archive-exports.log`

---

## 🏗️ ARCHITECTURE

### Database Structure:

The script extends the existing database with a `symbol_state` table tracking:

```json
{
  "version": "3.0",
  "symbol_state": {
    "last_updated": "2026-05-02T03:31:45Z",
    "exports_queue": [
      {"symbol_id": 124, "priority": "normal", "added_at": "...", "retry_count": 0},
      {"symbol_id": 666, "priority": "high", "added_at": "...", "retry_count": 0}
    ],
    "exports_in_progress": {
      "124": {"status": "processing", "started_at": "...", "job_id": "exp_124_xxx"}
    },
    "exports_completed": [
      {"symbol_id": 963, "exported_at": "...", "path": "..."}
    ],
    "exports_failed": [
      {"symbol_id": 55, "last_error": "...", "retry_count": 0}
    ],
    "config": {
      "batch_size": 4,
      "max_retries": 3,
      "retry_delay_seconds": 2,
      "timeout_seconds": 600
    }
  }
}
```

### Component Flow:

```
┌─────────────────┐
│ Main Export     │
│ Workflow        │
└──────┬──────────┘
       │ Triggered by export command
       ↓
┌─────────────────────────────────────────────────────────────────┐
│ Visual Archive Export Job Manager                               │
├─────────────────────────────────────────────────────────────────┤
│ 1. Read symbol_state.exports_queue                             │
│ 2. Process batches of 3-5 symbols in parallel                   │
│ 3. Write exports to output/visual_archive/symbol_<id>/          │
│ 4. Update exports_in_progress during processing                 │
│ 5. Move successful → exports_completed                          │
│ 6. Retry failed (up to max_retries)                             │
│ 7. Log all operations to database                               │
│ 8. Log progress to cron output                                  │
└─────────────────────────────────────────────────────────────────┘
       ↓
┌─────────────────┐
│ Cron Output     │ ← /cron/output/visual-archive-exports.log
└─────────────────┘
```

---

## 🛠️ USAGE

### Basic Commands:

```bash
# Run export jobs for all symbols in queue
./manage_visual_archive_exports.sh run

# Check current export status
./manage_visual_archive_exports.sh status

# Retry a failed export job (requires symbol ID)
./manage_visual_archive_exports.sh retry 124

# Archive old exports older than 30 days
./manage_visual_archive_exports.sh cleanup
```

### Direct Python Usage:

```bash
python3 manage_visual_archive_exports.py run
python3 manage_visual_archive_exports.py status
python3 manage_visual_archive_exports.py retry <job_id>
python3 manage_visual_archive_exports.py cleanup
```

---

## 📊 DATABASE INTEGRATION

### Adding Symbols to Queue:

The main export workflow should add symbols to the queue before processing:

```python
# Example: Add symbol to exports queue
symbol_id = 124
priority = "normal"  # or "high" for urgent symbols

from manage_visual_archive_exports import VisualArchiveExportManager

manager = VisualArchiveExportManager()
manager.add_symbol_to_queue(symbol_id, priority)
```

### Reading Queue for Processing:

Before starting export processing, check what's pending:

```python
queue = manager.get_symbols_to_export()
print(f"Queue has {len(queue)} pending exports")
```

---

## 🔄 WORKFLOW INTEGRATION

The script is designed to be triggered by the main export workflow. Here's how to integrate it:

### Option 1: Manual Trigger After Data Collection

```bash
# After collecting research data for a batch of symbols
./manage_visual_archive_exports.sh run
```

### Option 2: Automated in Cron Job

Add to your cron schedule (e.g., every hour during business hours):

```bash
# Edit crontab: crontab -e
0 * * * * cd /home/avalonas/.hermes/gematria/unified_overnight_research && \
  ./scripts/manage_visual_archive_exports.sh run >> /home/avalonas/.hermes/cron/output/export-jobs.log 2>&1
```

### Option 3: Scheduled Retry for Failed Jobs

```bash
# Every 5 minutes, retry failed exports (optional)
*/5 * * * * cd /home/avalonas/.hermes/gematria/unified_overnight_research && \
  python3 scripts/manage_visual_archive_exports.py status >> /home/avalonas/.hermes/cron/output/export-status.log 2>&1
```

---

## 📁 OUTPUT STRUCTURE

Exports are saved to:

```
/home/avalonas/.hermes/gematria/unified_overnight_research/output/visual_archive/symbol_<id>/
├── export_<symbol_id>_<timestamp>.json    # Main export file
└── ...                                    # Additional export artifacts
```

Example export file content:

```json
{
  "symbol_id": 124,
  "exported_at": "2026-05-02T03:31:45Z",
  "status": "completed",
  "content": "# Visual Archive Export for Symbol #124\n...",
  "file_path": "/home/avalonas/.../output/visual_archive/symbol_124/export_124_xxx.json",
  "checksum": "a1b2c3d4e5f6..."
}
```

---

## 🎮 COMMAND-LEVEL DETAILS

### `run` - Process Queue

- Reads symbols from `symbol_state.exports_queue`
- Filters out currently processing jobs
- Processes in parallel batches (default: 4 concurrent workers)
- Automatically retries failed exports up to 3 times
- Moves successful exports to `exports_completed`
- Logs progress to database and cron output

### `status` - Check Status

Shows:
- Queue size (pending exports)
- Jobs currently in progress
- Total completed exports
- Failed exports (retryable)
- Last update timestamp

### `retry <job_id>` - Retry Failed Job

Manually retry a specific failed export by symbol ID. Useful for:
- One-off manual intervention
- Resolving transient errors
- Testing retry behavior

### `cleanup` - Archive Old Exports

Archives exports older than 30 days to avoid database bloat:
- Moves completed exports to `visual_archive_history/`
- Cleans up old entries from tracking tables
- Keeps recent exports for quick access

---

## ⚙️ CONFIGURATION

All configuration is stored in the database's `symbol_state.config`:

```json
{
  "batch_size": 4,          // Number of parallel workers (3-5)
  "max_retries": 3,         // Max retry attempts for failed jobs
  "retry_delay_seconds": 2, // Delay between retries
  "timeout_seconds": 600    // Per-job timeout (10 minutes)
}
```

To modify defaults, edit the database or create a configuration override.

---

## 📝 LOG FORMAT

### Cron Output Format:

```
[2026-05-02T03:31:45Z] 🚀 STARTING VISUAL ARCHIVE EXPORT BATCH PROCESSING
[2026-05-02T03:31:46Z] 📋 Queue has 6 pending exports
[2026-05-02T03:31:47Z] Processing 4 symbols in parallel batches...
[2026-05-02T03:32:00Z] ✅ Export completed: symbol #124 → /output/visual_archive/symbol_124/export_xxx.json
[2026-05-02T03:32:15Z] ✅ Export completed: symbol #666 → /output/visual_archive/symbol_666/export_xxx.json
[2026-05-02T03:35:00Z] 📊 Batch complete: 4 successful, 0 failed
```

### Database Log Format:

```json
{
  "timestamp": "2026-05-02T03:31:47Z",
  "operation": "EXPORT",
  "status": "success",
  "message": "Export completed for symbol #124",
  "details": {
    "path": "/output/visual_archive/symbol_124/export_xxx.json",
    "symbol_id": 124
  }
}
```

---

## 🐛 ERROR HANDLING

### Retry Logic:

1. **First Failure:** Export marked as failed, added to `exports_failed` queue
2. **Retry Attempts:** System automatically retries failed exports up to `max_retries` times
3. **Failure After Retries:** Job remains in failed queue with error details for manual review

### Common Errors:

| Error Type | Cause | Resolution |
|------------|-------|------------|
| Permission denied | Output directory not writable | Run with elevated privileges or fix permissions |
| No output directory | Missing `/output/visual_archive/` path | Script auto-creates on first run |
| Database lock | Previous run didn't complete cleanly | Manual cleanup or restart of export workflow |

---

## 🔍 MONITORING & DEBUGGING

### Check Queue Size:

```bash
python3 manage_visual_archive_exports.py status | grep "Queue size"
```

### View Recent Activity:

```bash
tail -100 /home/avalonas/.hermes/cron/output/visual-archive-exports.log
```

### Inspect Failed Exports:

```bash
python3 -c "
import json
with open('/home/avalonas/.hermes/gematria/database/gematria_database.json') as f:
    db = json.load(f)
failed = db['symbol_state']['exports_failed']
for f in failed[-5:]:
    print(json.dumps(f, indent=2))
"
```

---

## 📚 EXAMPLES

### Process All Pending Exports:

```bash
./manage_visual_archive_exports.sh run
```

Expected output:
```
╔════════════════════════════════════════════════════════╗
║  📦 VISUAL ARCHIVE EXPORT JOB MANAGER                  ║
╚════════════════════════════════════════════════════════╝

📋 Found 6 symbols in export queue

📦 Processing 4 symbols in parallel batches...
📦 Processing export for symbol #124...
   ✅ Export saved to: /output/visual_archive/symbol_124/export_xxx.json
📦 Processing export for symbol #666...
   ✅ Export saved to: /output/visual_archive/symbol_666/export_xxx.json
[Parallel processing continues...]

======================================================================
📊 BATCH COMPLETE - 4 successful, 0 failed
======================================================================

FINAL REPORT
======================================================================
Successful:   4 exports completed
Failed:        0 exports failed
```

---

## 🚨 LIMITATIONS & NOTES

1. **Queue Size:** Maximum concurrent exports limited to 4 (configurable)
2. **Database Format:** Uses JSON database, no SQL migrations needed
3. **Atomic Operations:** All queue updates use file locking patterns for safety
4. **Cleanup Policy:** Default archival removes exports older than 30 days

---

## 📈 METRICS & MONITORING

Track export throughput:

```bash
# Count completed exports today
python3 -c "
import json
from datetime import datetime, timezone
with open('/home/avalonas/.hermes/gematria/database/gematria_database.json') as f:
    db = json.load(f)
today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
completed = [c for c in db['symbol_state']['exports_completed'] 
             if c['exported_at'].startswith(today)]
print(f'Today's exports: {len(completed)}')
"
```

---

## 📦 RELATED TOOLS

- `/scripts/manage_export_locks.py` - Handles `.git/index.lock` cleanup
- `/docs/MANAGE_EXPORT_LOCKS.md` - Lock file management documentation

---

## 🧪 TESTING

### Test Queue Management:

```bash
# Add a test symbol to queue
python3 manage_visual_archive_exports.py run  # Will show "No exports in queue"

# Manually add to queue and verify
python3 -c "
import json
with open('/home/avalonas/.hermes/gematria/database/gematria_database.json') as f:
    db = json.load(f)
db['symbol_state']['exports_queue'].append({'symbol_id': 999, 'priority': 'test'})
with open('/home/avalonas/.hermes/gematria/database/gematria_database.json', 'w') as f:
    json.dump(db, f, indent=2)
print('Test symbol added to queue')
"

./manage_visual_archive_exports.sh run  # Will process symbol 999
```

---

## 📞 SUPPORT & TROUBLESHOOTING

### Issue: Exports not processing

1. Check queue has items: `./manage_visual_archive_exports.sh status`
2. Verify output directory permissions: `ls -la /home/avalonas/.hermes/gematria/unified_overnight_research/output/`
3. Check cron logs for errors: `tail -50 /home/avalonas/.hermes/cron/output/visual-archive-exports.log`

### Issue: Stuck in retry loop

Check if exports are succeeding after retries:
```bash
python3 manage_visual_archive_exports.py status | grep "Failed"
```

If stuck, manually retry or increase `max_retries`:
```python
# Edit database directly (not recommended for production)
import json
with open('/home/avalonas/.hermes/gematria/database/gematria_database.json') as f:
    db = json.load(f)
db['symbol_state']['config']['max_retries'] = 5
with open('/home/avalonas/.hermes/gematria/database/gematria_database.json', 'w') as f:
    json.dump(db, f, indent=2)
```

---

**Version:** 1.0  
**Last Updated:** 2026-05-02  
**Author:** Hermes Agent (Visual Archive Export Module)
