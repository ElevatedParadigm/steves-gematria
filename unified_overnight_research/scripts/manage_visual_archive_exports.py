#!/usr/bin/env python3
"""
Visual Archive Export Job Manager
===============================================================================
Manages parallel Visual Archive export jobs with progress tracking, status updates,
and failure handling. Processes symbols in batches and logs all activity to both
database and cron output.

Usage:
    python manage_visual_archive_exports.py run                    # Run export jobs
    python manage_visual_archive_exports.py status                 # Show job status
    python manage_visual_archive_exports.py retry <job_id>         # Retry failed job
    python manage_visual_archive_exports.py cleanup                # Cleanup completed jobs

Integration: Triggered by main export workflow to process pending symbols from symbol_state table.
"""

import sys
import os
import json
import time
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed


# Add parent to path for imports
sys.path.insert(0, str(Path.home() / ".hermes"))

BASE_DIR = Path.home() / ".hermes" / "gematria"
UNIFIED_OUR_DIR = BASE_DIR / "unified_overnight_research"
OUTPUT_DIR = UNIFIED_OUR_DIR / "output"
LOGS_DIR = UNIFIED_OUR_DIR / "logs"
DATABASE_PATH = UNIFIED_OUR_DIR / "database" / "gematria_database.json"

# Cron log path
CRON_LOG_PATH = BASE_DIR / "cron" / "output" / "visual-archive-exports.log"


class VisualArchiveExportManager:
    """Manages Visual Archive export jobs with progress tracking and error handling."""
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize the export manager.
        
        Args:
            max_workers: Maximum number of parallel export workers (default: 4)
        """
        self.max_workers = max_workers
        self.db_file = DATABASE_PATH
        self.cron_log_path = CRON_LOG_PATH
        
        # Create directories if needed
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        (BASE_DIR / "cron" / "output").mkdir(parents=True, exist_ok=True)
        
        # Initialize database structure if it doesn't exist
        self._init_database()
        
        # Track current session for locking
        self.session_id = None
        
    def _get_current_utc(self) -> str:
        """Get current UTC timestamp."""
        now = datetime.now(timezone.utc)
        return now.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    def _init_database(self):
        """Initialize the database with symbol_state tracking if needed."""
        try:
            if self.db_file.exists():
                with open(self.db_file, 'r') as f:
                    db = json.load(f)
                
                # Add symbol_state tracking if not present
                if "symbol_state" not in db:
                    db["symbol_state"] = {
                        "last_updated": self._get_current_utc(),
                        "exports_queue": [],      # Symbols pending export
                        "exports_in_progress": {}, # Currently running exports
                        "exports_completed": [],  # Successfully completed exports
                        "exports_failed": [],    # Failed exports with retry info
                        "config": {
                            "batch_size": 4,
                            "max_retries": 3,
                            "retry_delay_seconds": 2,
                            "timeout_seconds": 600
                        }
                    }
                
                with open(self.db_file, 'w') as f:
                    json.dump(db, f, indent=2)
                    
            else:
                # Create new database with symbol_state tracking
                self.db_file.parent.mkdir(parents=True, exist_ok=True)
                db = {
                    "version": "3.0",
                    "initialized": True,
                    "symbol_state": {
                        "last_updated": self._get_current_utc(),
                        "exports_queue": [],
                        "exports_in_progress": {},
                        "exports_completed": [],
                        "exports_failed": [],
                        "config": {
                            "batch_size": 4,
                            "max_retries": 3,
                            "retry_delay_seconds": 2,
                            "timeout_seconds": 600
                        }
                    },
                }
                with open(self.db_file, 'w') as f:
                    json.dump(db, f, indent=2)
                    
        except Exception as e:
            print(f"⚠️ Database initialization warning: {e}")
    
    def _log_to_cron(self, message: str):
        """Log message to cron output file."""
        try:
            timestamp = self._get_current_utc()
            log_entry = f"[{timestamp}] {message}\n"
            
            with open(self.cron_log_path, 'a') as f:
                f.write(log_entry)
                
        except Exception as e:
            print(f"⚠️ Failed to write to cron log: {e}")
    
    def _log_to_database(self, operation: str, status: str, message: str, 
                        details: Optional[Dict] = None):
        """Log operation to database symbol_state."""
        try:
            if self.db_file.exists():
                with open(self.db_file, 'r') as f:
                    db = json.load(f)
                
                if "symbol_state" in db:
                    state = db["symbol_state"]
                    current_time = self._get_current_utc()
                    
                    log_entry = {
                        "timestamp": current_time,
                        "operation": operation,
                        "status": status,  # success, warning, error
                        "message": message,
                        "details": details or {}
                    }
                    
                    state["last_updated"] = current_time
                    
                    # Add to appropriate queue based on status
                    if status == "success" and "exports_completed" in state:
                        state["exports_completed"].append(log_entry)
                        # Keep only last 100 completed entries
                        if len(state["exports_completed"]) > 100:
                            state["exports_completed"] = state["exports_completed"][-100:]
                    elif status == "error" and "exports_failed" in state:
                        state["exports_failed"].append(log_entry)
                        
                    with open(self.db_file, 'w') as f:
                        json.dump(db, f, indent=2)
        
        except Exception as e:
            print(f"⚠️ Failed to log to database: {e}")
    
    def get_symbols_to_export(self) -> List[Dict]:
        """Get list of symbols that need exporting from the queue."""
        try:
            if self.db_file.exists():
                with open(self.db_file, 'r') as f:
                    db = json.load(f)
                
                if "symbol_state" in db:
                    queue = db["symbol_state"].get("exports_queue", [])
                    return queue
                    
            return []
            
        except Exception as e:
            print(f"⚠️ Error reading exports queue: {e}")
            return []
    
    def add_symbol_to_queue(self, symbol_id: int, priority: str = "normal"):
        """Add a symbol to the exports queue."""
        try:
            if self.db_file.exists():
                with open(self.db_file, 'r') as f:
                    db = json.load(f)
                
                if "symbol_state" in db:
                    queue = db["symbol_state"].get("exports_queue", [])
                    
                    # Avoid duplicates
                    if not any(s["symbol_id"] == symbol_id for s in queue):
                        queue.append({
                            "symbol_id": symbol_id,
                            "priority": priority,
                            "added_at": self._get_current_utc(),
                            "retry_count": 0
                        })
                    
                    with open(self.db_file, 'w') as f:
                        json.dump(db, f, indent=2)
                        
            self._log_to_database("ADD", "info", 
                               f"Added symbol #{symbol_id} to export queue",
                               {"priority": priority})
            
        except Exception as e:
            print(f"⚠️ Failed to add symbol to queue: {e}")
    
    def process_export(self, symbol_data: Dict) -> Dict:
        """
        Process a single symbol export job.
        
        Args:
            symbol_data: Dictionary containing symbol_id and other metadata
            
        Returns:
            Dictionary with export result status and details
        """
        symbol_id = symbol_data.get("symbol_id")
        if not symbol_id:
            return {"success": False, "error": "Missing symbol_id"}
        
        try:
            print(f"\n📦 Processing export for symbol #{symbol_id}...")
            
            # Create output path for this symbol's Visual Archive export
            output_path = OUTPUT_DIR / f"visual_archive/symbol_{symbol_id}"
            
            # Ensure output directory exists
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Generate unique file name based on symbol and timestamp
            timestamp = self._get_current_utc()
            export_file = output_path / f"export_{symbol_id}_{timestamp}.json"
            
            # Create export data structure
            export_data = {
                "symbol_id": symbol_id,
                "exported_at": timestamp,
                "status": "completed",
                "content": f"# Visual Archive Export for Symbol #{symbol_id}\n\n" +
                          f"**Export Timestamp**: {timestamp}\n",
                "file_path": str(export_file),
                "checksum": self._compute_checksum(export_data)
            }
            
            # Write export file
            with open(export_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"   ✅ Export saved to: {export_file}")
            
            # Log success to database and cron
            self._log_to_database("EXPORT", "success", 
                               f"Export completed for symbol #{symbol_id}",
                               {"path": str(export_file), "symbol_id": symbol_id})
            self._log_to_cron(f"✅ Export completed: symbol #{symbol_id} → {export_file}")
            
            return {"success": True, "path": str(export_file), "symbol_id": symbol_id}
            
        except Exception as e:
            error_msg = f"Export failed for symbol #{symbol_id}: {str(e)}"
            print(f"   ❌ Error: {error_msg}")
            
            # Log failure to database and cron
            self._log_to_database("EXPORT", "error", error_msg, 
                               {"symbol_id": symbol_id, "error": str(e)})
            self._log_to_cron(f"❌ Export failed for symbol #{symbol_id}: {str(e)}")
            
            return {"success": False, "error": str(e), "symbol_id": symbol_id}
    
    def _compute_checksum(self, data: Dict) -> str:
        """Compute simple checksum of export data."""
        content = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def run_exports_batch(self) -> Dict[str, Any]:
        """
        Process exports in parallel batches.
        
        Returns:
            Summary dictionary with batch results
        """
        print("\n" + "=" * 70)
        print("🚀 STARTING VISUAL ARCHIVE EXPORT JOB MANAGER")
        print("=" * 70)
        
        self._log_to_cron("=" * 70)
        self._log_to_cron("🚀 STARTING VISUAL ARCHIVE EXPORT BATCH PROCESSING")
        
        try:
            # Get symbols to export from queue
            queue = self.get_symbols_to_export()
            
            if not queue:
                print("\nℹ️ No exports in queue - nothing to process")
                self._log_to_cron("ℹ️ No exports in queue - nothing to process")
                return {
                    "status": "no_jobs",
                    "symbols_processed": 0,
                    "symbols_in_queue": len(queue)
                }
            
            print(f"\n📋 Found {len(queue)} symbols in export queue")
            self._log_to_cron(f"📦 Queue has {len(queue)} pending exports")
            
            # Filter out already processing jobs
            available_symbols = [s for s in queue 
                              if not self._is_processing(s["symbol_id"])]
            
            print(f"   Available for processing: {len(available_symbols)} symbols")
            
            if not available_symbols:
                print("ℹ️ All available jobs are currently being processed")
                return {
                    "status": "jobs_in_progress",
                    "symbols_available": len(available_symbols),
                    "total_queue_size": len(queue)
                }
            
            # Define batch size (3-5 as specified)
            batch_size = min(len(available_symbols), 4)  # Use 4 for this implementation
            
            print(f"\n📦 Processing {batch_size} symbols in parallel batches...")
            
            results = {
                "status": "processing",
                "batch_size": batch_size,
                "total_processed": 0,
                "successful": [],
                "failed": [],
                "retry_attempts": {}
            }
            
            # Process in parallel batches using ThreadPoolExecutor
            max_workers = min(self.max_workers, len(available_symbols))
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit jobs to executor
                future_to_symbol = {
                    executor.submit(self.process_export, s): s 
                    for s in available_symbols
                }
                
                # Track completion and handle retries
                completed = 0
                batch_results = []
                
                while future_to_symbol:
                    # Get completed futures
                    done_futures = []
                    for future in list(future_to_symbol.keys()):
                        try:
                            if future.done():
                                done_futures.append(future)
                        except Exception:
                            pass
                    
                    # Process completed futures
                    for future in done_futures:
                        try:
                            result = future.result()
                            batch_results.append(result)
                            
                            if result.get("success"):
                                results["successful"].append(result)
                            else:
                                results["failed"].append(result)
                                
                            # Remove from pending
                            symbol_id = future_to_symbol.pop(future, {}).get("symbol_id")
                            if symbol_id:
                                completed += 1
                                
                        except Exception as e:
                            # Handle unexpected exceptions
                            error_result = {
                                "success": False,
                                "error": f"Unexpected error: {str(e)}",
                                "symbol_id": future_to_symbol.pop(future, {}).get("symbol_id", None)
                            }
                            batch_results.append(error_result)
                            results["failed"].append(error_result)
                            completed += 1
                    
                    # Wait a moment between batches if jobs completed
                    if completed % max_workers == 0 and completed < len(available_symbols):
                        time.sleep(1)
                
            # Process retry queue - attempt failed exports with retry logic
            self._process_failed_exports_with_retry(queue, batch_results)
            
            results["total_processed"] = sum(len(r.get("successful", [])) for r in batch_results)
            
            # Summary logging
            success_count = len(results["successful"])
            fail_count = len(results["failed"])
            
            print(f"\n{'=' * 70}")
            print(f"📊 BATCH COMPLETE - {success_count} successful, {fail_count} failed")
            print(f"{'=' * 70}\n")
            
            self._log_to_cron("=" * 70)
            self._log_to_cron(f"📊 Batch complete: {success_count} successful, {fail_count} failed")
            
            return results
            
        except Exception as e:
            print(f"\n❌ Batch processing error: {str(e)}")
            self._log_to_database("BATCH", "error", 
                               f"Batch processing failed: {str(e)}",
                               {"error": str(e)})
            self._log_to_cron(f"❌ Batch processing error: {str(e)}")
            
            return {
                "status": "error",
                "error": str(e),
                "symbols_processed": 0
            }
    
    def _is_processing(self, symbol_id: int) -> bool:
        """Check if a symbol is currently being processed."""
        try:
            if self.db_file.exists():
                with open(self.db_file, 'r') as f:
                    db = json.load(f)
                
                if "symbol_state" in db:
                    in_progress = db["symbol_state"].get("exports_in_progress", {})
                    return str(symbol_id) in in_progress
                    
        except Exception:
            pass
        
        return False
    
    def _mark_processing(self, symbol_id: int):
        """Mark a symbol as being processed."""
        try:
            if self.db_file.exists():
                with open(self.db_file, 'r') as f:
                    db = json.load(f)
                
                if "symbol_state" in db:
                    state = db["symbol_state"]
                    
                    # Add to in_progress
                    if "exports_in_progress" not in state:
                        state["exports_in_progress"] = {}
                    
                    state["exports_in_progress"][str(symbol_id)] = {
                        "status": "processing",
                        "started_at": self._get_current_utc(),
                        "job_id": f"exp_{symbol_id}_{int(time.time())}"
                    }
                    
                    with open(self.db_file, 'w') as f:
                        json.dump(db, f, indent=2)
                        
        except Exception as e:
            print(f"⚠️ Failed to mark symbol as processing: {e}")
    
    def _mark_completed(self, symbol_id: int, result: Dict):
        """Mark a symbol export as completed."""
        try:
            if self.db_file.exists():
                with open(self.db_file, 'r') as f:
                    db = json.load(f)
                
                if "symbol_state" in db:
                    state = db["symbol_state"]
                    
                    # Remove from queue and in_progress
                    queue = state.get("exports_queue", [])
                    state["exports_queue"] = [s for s in queue 
                                             if s.get("symbol_id") != symbol_id]
                    
                    if str(symbol_id) in state.get("exports_in_progress", {}):
                        del state["exports_in_progress"][str(symbol_id)]
                    
                    with open(self.db_file, 'w') as f:
                        json.dump(db, f, indent=2)
                        
        except Exception as e:
            print(f"⚠️ Failed to mark symbol as completed: {e}")
    
    def _process_failed_exports_with_retry(self, queue: List[Dict], 
                                         batch_results: List[Dict]):
        """Retry failed exports up to max_retries times."""
        try:
            if self.db_file.exists():
                with open(self.db_file, 'r') as f:
                    db = json.load(f)
                
                if "symbol_state" in db:
                    state = db["symbol_state"]
                    config = state.get("config", {})
                    max_retries = config.get("max_retries", 3)
                    retry_delay = config.get("retry_delay_seconds", 2)
                    
                    failed_exports = state.get("exports_failed", [])
                    completed_count = len(state.get("exports_completed", []))
                    
                    # Process each failed export for retries
                    for failed_export in failed_exports:
                        symbol_id = failed_export.get("symbol_id")
                        retry_count = failed_export.get("retry_count", 0)
                        
                        if retry_count < max_retries:
                            attempt = retry_count + 1
                            print(f"   🔄 Retry {attempt}/{max_retries} for symbol #{symbol_id}")
                            
                            try:
                                # Attempt export again
                                result = self.process_export({
                                    "symbol_id": symbol_id,
                                    "retry_attempt": attempt
                                })
                                
                                if result.get("success"):
                                    # Add to completed
                                    state["exports_completed"].append(failed_export)
                                    if len(state["exports_completed"]) > 100:
                                        state["exports_completed"] = \
                                            state["exports_completed"][-100:]
                                    
                                    # Remove from failed queue
                                    state["exports_failed"] = [
                                        e for e in state["exports_failed"]
                                        if e.get("symbol_id") != symbol_id
                                    ]
                                    print(f"      ✅ Retry {attempt} succeeded!")
                                else:
                                    # Increment retry count and update error info
                                    failed_export["retry_count"] = retry_count + 1
                                    failed_export["last_error"] = result.get("error") or failed_export.get("error")
                                    
                            except Exception as e:
                                print(f"      ⚠️ Retry {attempt} error: {str(e)}")
                        
                        else:
                            print(f"      ❌ Symbol #{symbol_id} gave up after {max_retries} attempts")
                            
        except Exception as e:
            print(f"⚠️ Failed to process retries: {e}")
    
    def show_status(self):
        """Show current export job status."""
        try:
            if self.db_file.exists():
                with open(self.db_file, 'r') as f:
                    db = json.load(f)
                
                if "symbol_state" in db:
                    state = db["symbol_state"]
                    
                    print("\n" + "=" * 70)
                    print("📊 VISUAL ARCHIVE EXPORT STATUS")
                    print("=" * 70)
                    print(f"\nQueue size:        {len(state.get('exports_queue', []))}")
                    print(f"In progress:        {len(state.get('exports_in_progress', {}))}")
                    print(f"Completed:          {len(state.get('exports_completed', []))}")
                    print(f"Failed (retryable): {len(state.get('exports_failed', []))}")
                    
                    if state.get('exports_queue'):
                        print("\nPending Exports:")
                        for item in state['exports_queue'][:10]:
                            print(f"  - Symbol #{item.get('symbol_id')} [{item.get('priority', 'normal')}]")
                    
                    if state.get('exports_in_progress'):
                        print("\nIn Progress:")
                        for job_id, info in list(state['exports_in_progress'].items())[:5]:
                            print(f"  - {job_id}: started {info.get('started_at', 'N/A')}")
                    
                    print(f"\nLast updated: {state.get('last_updated', 'N/A')}")
                    
        except Exception as e:
            print(f"⚠️ Error showing status: {e}")
    
    def retry_job(self, symbol_id: int) -> Dict[str, Any]:
        """Retry a failed export job."""
        try:
            print(f"\n🔄 Retrying export for symbol #{symbol_id}...")
            
            result = self.process_export({"symbol_id": symbol_id})
            
            if result.get("success"):
                # Remove from failed and add to completed
                if self.db_file.exists():
                    with open(self.db_file, 'r') as f:
                        db = json.load(f)
                    
                    if "symbol_state" in db:
                        state = db["symbol_state"]
                        
                        # Remove from failed
                        state["exports_failed"] = [
                            e for e in state.get("exports_failed", [])
                            if e.get("symbol_id") != symbol_id
                        ]
                        
                        # Add to completed
                        state["exports_completed"].append({
                            "symbol_id": symbol_id,
                            "recovered_at": self._get_current_utc()
                        })
                        if len(state["exports_completed"]) > 100:
                            state["exports_completed"] = state["exports_completed"][-100:]
                        
                        with open(self.db_file, 'w') as f:
                            json.dump(db, f, indent=2)
                        
                        print(f"✅ Recovery successful! Export recovered.")
            
            return result
            
        except Exception as e:
            print(f"❌ Retry failed: {e}")
            return {"success": False, "error": str(e)}
    
    def cleanup(self):
        """Cleanup completed exports (optional archival)."""
        print("\n🧹 Starting cleanup of completed exports...")
        self._log_to_cron("🧹 Starting cleanup of completed exports")
        
        try:
            # Archive old exports older than 30 days
            thirty_days_ago = datetime.now(timezone.utc) - __import__('datetime').timedelta(days=30)
            
            if OUTPUT_DIR.exists():
                archived_count = 0
                remaining_count = 0
                
                for export_file in OUTPUT_DIR.glob("visual_archive/symbol_*"):
                    file_stat = export_file.stat()
                    file_time = datetime.fromtimestamp(file_stat.st_mtime, timezone.utc)
                    
                    if file_time < thirty_days_ago:
                        # Archive to history directory
                        archive_dir = OUTPUT_DIR / "visual_archive_history"
                        archive_dir.mkdir(parents=True, exist_ok=True)
                        
                        archived_name = export_file.name.replace(".json", f"_archived_{file_time.strftime('%Y%m%d')}.json")
                        archive_path = archive_dir / archived_name
                        
                        try:
                            export_file.rename(archive_path)
                            archived_count += 1
                            print(f"   Archived: {export_file} → {archive_path}")
                            
                            # Remove original from queue
                            if self.db_file.exists():
                                with open(self.db_file, 'r') as f:
                                    db = json.load(f)
                                
                                if "symbol_state" in db:
                                    state = db["symbol_state"]
                                    
                                    # Clean from completed list
                                    state["exports_completed"] = [
                                        c for c in state.get("exports_completed", [])
                                        if c.get("path", "").replace("/", "") != export_file.name.replace(".json", "")
                                    ]
                                    
                                    with open(self.db_file, 'w') as f:
                                        json.dump(db, f, indent=2)
                        
                        except Exception as e:
                            print(f"   ⚠️ Failed to archive {export_file}: {e}")
                    else:
                        remaining_count += 1
                
                if archived_count > 0:
                    print(f"\n✅ Archived {archived_count} exports")
                    print(f"📁 Remaining in output: {remaining_count} exports")
                    
                    self._log_to_cron(f"🧹 Cleanup complete: archived {archived_count}, remaining {remaining_count}")
                
        except Exception as e:
            print(f"❌ Cleanup error: {e}")


def run_exports():
    """Main entry point for running export jobs."""
    manager = VisualArchiveExportManager(max_workers=4)
    return manager.run_exports_batch()


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Visual Archive Export Job Manager"
    )
    parser.add_argument(
        "command",
        choices=["run", "status", "retry", "cleanup"],
        help="Command to execute"
    )
    parser.add_argument(
        "job_id", 
        nargs="?",
        help="Job ID for retry command (symbol_id)"
    )
    
    args = parser.parse_args()
    
    manager = VisualArchiveExportManager(max_workers=4)
    
    if args.command == "run":
        return run_exports()
    elif args.command == "status":
        manager.show_status()
    elif args.command == "retry":
        if not args.job_id:
            print("❌ Job ID required for retry command")
            return {"success": False, "error": "job_id_required"}
        
        try:
            symbol_id = int(args.job_id)
            return manager.retry_job(symbol_id)
        except ValueError:
            print(f"❌ Invalid job ID: {args.job_id}")
            return {"success": False, "error": "invalid_job_id"}
    elif args.command == "cleanup":
        manager.cleanup()


if __name__ == "__main__":
    result = main()
    
    if result and isinstance(result, dict):
        status = result.get("status", "unknown")
        if status != "no_jobs" and status != "jobs_in_progress":
            success = result.get("successful", [])
            failed = result.get("failed", [])
            
            print(f"\n{'=' * 70}")
            print(f"FINAL REPORT")
            print(f"{'=' * 70}")
            print(f"Successful:   {len(success)} exports completed")
            print(f"Failed:        {len(failed)} exports failed")
            
            if failed:
                print("\nFailed exports:")
                for f in failed[:5]:
                    print(f"  - Symbol #{f.get('symbol_id')}: {f.get('error', 'Unknown error')}")
