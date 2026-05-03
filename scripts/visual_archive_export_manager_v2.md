# Visual Archive Export Manager v2 - Documentation

## Overview
This script manages Visual Archive export jobs with parallel processing, progress tracking, and failure handling. It processes symbols from the `symbol_state` table in batches of 3-5 symbols at once.

## Features
- ✅ Parallel batch processing (3-5 symbols per batch)
- ✅ Database-driven queue management via `symbol_state` table
- ✅ Graceful error handling with retry logic
- ✅ Comprehensive logging to both database and cron output
- ✅ Job status tracking (in progress, completed, failed)
- ✅ Cleanup and archival of old exports

## File Location
```bash
/home/avalonas/.hermes/gematria/scripts/manage_visual_archive_exports_v2.py
```

## Database Schema
The script reads from and writes to the `symbol_state` table in `gematria_database.json`:

```json
{
  "symbol_state": {
    "last_updated": "ISO timestamp",
    "exports_queue": [                     // Symbols pending export
      {
        "symbol_id": <int>,
        "priority": "normal"|"high",
        "added_at": "<timestamp>",
        "retry_count": 0
      }
    ],
    "exports_in_progress": {               // Currently processing exports
      "<symbol_id>": {
        "status": "processing",
        "started_at": "<timestamp>",
        "job_id": "<unique_job_id>"
      }
    },
    "exports_completed": [                 // Successfully completed exports
      {
        "symbol_id": <int>,
        "timestamp": "<iso_timestamp>",
        "path": "<export_file_path>"
      }
    ],
    "exports_failed": [                    // Failed exports (retryable)
      {
        "symbol_id": <int>,
        "timestamp": "<iso_timestamp>",
        "error": "<error_message>"
      }
    ],
    "exports_metadata": {                  // Additional metadata per symbol
      "<symbol_id>": {
        "retry_count": <int>,
        "last_error": "<string>",
        "status": "failed"|"recovered",
        ...
      }
    },
    "config": {                            // Runtime configuration
      "batch_size": 4,
      "max_retries": 3,
      "retry_delay_seconds": 2,
      "max_workers": 4,
      "log_interval": 1
    }
  }
}
```

## Usage Commands

### Run Export Jobs (Default: batch size 4)
```bash
python manage_visual_archive_exports_v2.py run --max-workers 4
```

### Run with Custom Batch Size (3-5 symbols)
```bash
python manage_visual_archive_exports_v2.py run --batch-size 3 --max-workers 4
python manage_visual_archive_exports_v2.py run --batch-size 5 --max-workers 8
```

### Show Current Status
```bash
python manage_visual_archive_exports_v2.py status
```

### Retry a Failed Job
```bash
python manage_visual_archive_exports_v2.py retry <symbol_id>
```

### Cleanup Old Exports (Archive older than 30 days)
```bash
python manage_visual_archive_exports_v2.py cleanup
```

## Integration with Main Export Workflow

The script should be triggered as part of your main export workflow. Here are typical integration patterns:

### Pattern 1: Direct Cron Job Trigger
Add to your cron schedule (e.g., `/etc/cron.d/gematria-exports`):
```bash
# Run exports every 30 minutes
*/30 * * * * /usr/bin/python3 /home/avalonas/.hermes/gematria/scripts/manage_visual_archive_exports_v2.py run --batch-size 4 >> /var/log/gematria-exports.log 2>&1
```

### Pattern 2: Workflow Orchestrator Call
If you're using a workflow orchestrator (like Airflow, Prefect, or custom Python):
```python
from scripts.manage_visual_archive_exports_v2 import run_exports_batch

# Fetch symbols needing export from upstream process
symbols_to_export = fetch_symbols_for_export()

# Add them to queue
manager.add_symbols_to_queue(symbols_to_export["symbol_ids"])

# Run exports in parallel batches
result = run_exports_batch(max_workers=4, batch_size=5)
```

### Pattern 3: Response from Upstream Symbol Processing
When symbols are processed by your main workflow and determined to need Visual Archive export:
```python
# Example pseudo-code from main export workflow
def on_symbol_export_ready(symbol_id, export_data):
    """Callback when a symbol is ready for Visual Archive export"""
    
    # Add to exports queue in database
    manager.add_symbols_to_queue([symbol_id], priority="high")
    
    # Or trigger immediate processing
    run_exports_batch(max_workers=4)
```

### Pattern 4: Database-Driven Batch Processing (Recommended)
For reliable, idempotent processing:
```python
# In your main export workflow's post-processing phase:
symbols_needing_export = db.query(
    "SELECT symbol_id FROM symbol_state WHERE status IN ('ready', 'export_pending')",
    limit=100
)

# Add to queue
manager.add_symbols_to_queue([s["symbol_id"] for s in symbols_needing_export])

# Run exports
result = run_exports_batch(max_workers=4, batch_size=5)
```

## How It Works

### 1. Queue Reading
The script reads pending symbols from `exports_queue` in the `symbol_state` table. Symbols are added to this queue when they become ready for export.

### 2. Parallel Processing
Using Python's `ThreadPoolExecutor`, the script processes exports in parallel:
- Configurable batch size (default: 4)
- Maximum workers based on CPU/RAM (configurable)
- Each worker handles one symbol at a time

### 3. Status Updates
As each export completes:
- ✅ **Success**: Moved from queue → `exports_completed`
- ⏳ **In Progress**: Added to `exports_in_progress` with job ID lock
- ❌ **Error**: Added to `exports_failed` with error details

### 4. Retry Logic
Failed exports are retried automatically:
- Maximum retries: 3 (configurable)
- Backoff delay: 2 seconds between attempts
- Certain errors skipped (permission, file exists, etc.)
- Each retry logged to both database and cron output

### 5. Cleanup & Archival
The `cleanup` command archives exports older than 30 days:
- Original files renamed with date stamp
- Removed from `exports_completed` list
- Preserves historical data in `visual_archive_history/`

## Output Files

### Database Location
```bash
/home/avalonas/.hermes/gematria/unified_overnight_research/database/gematria_database.json
```

### Cron Log (Real-time Progress)
```bash
/home/avalonas/.hermes/gematria/cron/output/visual-archive-exports.log
```

### Export Output Directory
```bash
/home/avalonas/.hermes/gematria/unified_overnight_research/output/visual_archive/
# Format: symbol_<symbol_id>/export_<symbol_id>_<timestamp>.json
```

### History Archive (30-day retention)
```bash
/home/avalonas/.hermes/gematria/unified_overnight_research/output/visual_archive_history/
# Format: symbol_<symbol_id>_archived_<date>.json
```

## Configuration

Configuration can be set via command line or stored in the database's `config` field:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `batch_size` | 4 | Symbols per batch (max 5) |
| `max_retries` | 3 | Retry attempts for failed exports |
| `retry_delay_seconds` | 2 | Delay between retry attempts |
| `max_workers` | 4 | Maximum parallel workers |
| `log_interval` | 1 | Log every N completed jobs |

## Error Handling

The script handles the following error types gracefully:

### Retryable Errors (Will be retried)
- Network failures
- Temporary I/O errors
- Rate limit errors
- Unknown exceptions

### Non-Retryable Errors (Skipped permanently)
- Permission denied
- Access denied
- File already exists
- No such file/directory

All failed exports are logged with:
1. Timestamp of failure
2. Error message
3. Retry count
4. Final status after all retries exhausted

## Monitoring & Observability

### Check Job Status
```bash
python manage_visual_archive_exports_v2.py status
```

### View Cron Log (in real-time)
```bash
tail -f /home/avalonas/.hermes/gematria/cron/output/visual-archive-exports.log
```

### Parse Database State
```python
import json
with open('/home/avalonas/.hermes/gematria/unified_overnight_research/database/gematria_database.json') as f:
    db = json.load(f)
state = db["symbol_state"]

print(f"Queue: {len(state['exports_queue'])}")
print(f"In Progress: {len(state['exports_in_progress'])}")
print(f"Completed: {len(state['exports_completed'])}")
print(f"Failed: {len(state['exports_failed'])}")
```

## Extending the Export Logic

The script includes a placeholder in `process_export()`. To implement your actual export logic, modify this section:

```python
# IN process_export(), around line 275-300:

export_data = {
    "symbol_id": symbol_id,
    "exported_at": timestamp,
    "status": "completed",
    "content_type": "visual_archive_export",
    "path": str(export_file),
    "checksum": self._compute_checksum(export_data)
}

with open(export_file, 'w') as f:
    json.dump(export_data, f, indent=2)
```

Replace the placeholder content with your actual Visual Archive export logic. The script will automatically log successes and failures to both database and cron output regardless of your implementation details.

## Troubleshooting

### No exports processing
**Symptom**: "All available jobs are currently being processed" message persists

**Solution**: Check if workers are hanging:
```bash
python manage_visual_archive_exports_v2.py status
# Look for stuck jobs in exports_in_progress
```

### Stuck on retries
**Symptom**: Same symbol_id repeatedly failing and retrying

**Solution**: Investigate the actual export logic - there may be a bug in your export function. Check cron log for detailed error messages.

### Database file locked/permissions
**Symptom**: "Failed to write to database" errors

**Solution**: 
```bash
ls -la /home/avalonas/.hermes/gematria/unified_overnight_research/database/
chown $USER:$USER /home/avalonas/.hermes/gematria/unified_overnight_research/database/
chmod 644 /home/avalonas/.hermes/gematria/unified_overnight_research/database/*.json
```

### Need to clear all exports queue
**Symptom**: Accidentally queued wrong symbols, need fresh start

**Solution**: 
```python
import json
db_path = "/home/avalonas/.hermes/gematria/unified_overnight_research/database/gematria_database.json"
with open(db_path) as f:
    db = json.load(f)
db["symbol_state"]["exports_queue"] = []
with open(db_path, 'w') as f:
    json.dump(db, f, indent=2)
```

## Best Practices

1. **Add symbols to queue immediately** after they become export-ready (don't let them accumulate indefinitely in memory)

2. **Use batch_size 4-5** for typical CPU cores; increase if you have many-core machines

3. **Set max_workers = min(cpu_cores, 8)** - don't oversubscribe threads

4. **Monitor failed exports** regularly with `status` command

5. **Run cleanup periodically** to keep output directory manageable (e.g., via cron every week)

6. **Always check error logs** in the cron output file for detailed failure reasons

7. **Keep retry_count reasonable** - 3 retries handles transient errors without stalling indefinitely

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v2 (Current) | 2026-05-03 | Enhanced parallel processing, retry logic, comprehensive logging |
| v1 | Earlier | Basic sequential export with single-threaded processing |

## Author/Contact
For questions or issues, check the cron output logs or contact your infrastructure team.
