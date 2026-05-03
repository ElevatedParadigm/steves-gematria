#!/usr/bin/env python3
"""
Visual Archive Export Job Manager v2 - Enhanced
===============================================================================
Advanced parallel export job management with progress tracking, status updates,
and failure handling. Processes symbols in batches of 3-5 and logs all activity
to both database and cron output.

Usage:
    python manage_visual_archive_exports_v2.py run              # Run export jobs
    python manage_visual_archive_exports_v2.py status           # Show job status
    python manage_visual_archive_exports_v2.py retry <symbol_id>  # Retry failed job
    python manage_visual_archive_exports_v2.py cleanup          # Cleanup completed jobs

Integration: Triggered by main export workflow to process pending symbols from symbol_state table.
"""

import sys
import os
import json
import time
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from concurrent.futures import ThreadPoolExecutor, as_completed, Future


# Add parent to path for imports
sys.path.insert(0, str(Path.home() / ".hermes"))

BASE_DIR = Path.home() / ".hermes" / "gematria"
UNIFIED_OUR_DIR = BASE_DIR / "unified_overnight_research"
OUTPUT_DIR = UNIFIED_OUR_DIR / "output"
LOGS_DIR = UNIFIED_OUR_DIR / "logs"
DATABASE_PATH = UNIFIED_OUR_DIR / "database" / "gematria_database.json"

# Cron log path
CRON_LOG_PATH = BASE_DIR / "cron" / "output" / "visual-archive-exports.log"


class VisualArchiveExportManagerV2:
    """Enhanced manager for Visual Archive export jobs with parallel processing and retry logic."""
    
    # Default configuration
    DEFAULT_CONFIG = {
        "batch_size": 4,           # Process 3-5 symbols per batch
        "max_retries": 3,          # Maximum retry attempts for failed exports
        "retry_delay_seconds": 2,  # Delay between retries
        "timeout_seconds": 600,    # Timeout for individual exports
        "max_workers": 4,          # Max parallel workers (adjust based on CPU/RAM)
        "export_dir": "visual_archive",  # Subdirectory in output/
        "log_interval": 1          # Log progress every N completed jobs
    }
    
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
        
        # Export configuration (can be updated dynamically)
        self.config = self.DEFAULT_CONFIG.copy()
        self._load_config_from_database()
    
    def _get_current_utc(self) -> str:
        """Get current UTC timestamp in ISO format."""
        now = datetime.now(timezone.utc)
        return now.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    
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
                        "exports_in_progress": {},  # Currently running exports
                        "exports_completed": [],   # Successfully completed exports
                        "exports_failed": [],     # Failed exports with retry info
                        "exports_metadata": {},    # Additional metadata per symbol_id
                        "config": self.DEFAULT_CONFIG.copy()
                    }
                
                with open(self.db_file, 'w') as f:
                    json.dump(db, f, indent=2)
                    
            else:
                # Create new database with symbol_state tracking
                self.db_file.parent.mkdir(parents=True, exist_ok=True)
                db = {
                    "version": "4.0",
                    "initialized": True,
                    "symbol_state": {
                        "last_updated": self._get_current_utc(),
                        "exports_queue": [],
                        "exports_in_progress": {},
                        "exports_completed": [],
                        "exports_failed": [],
                        "exports_metadata": {},
                        "config": self.DEFAULT_CONFIG.copy()
                    },
                }
                with open(self.db_file, 'w') as f:
                    json.dump(db, f, indent=2)
                    
        except Exception as e:
            print(f"Warning: Database initialization had issue: {e}")
    
    def _load_config_from_database(self):
        """Load export configuration from database (if present)."""
        try:
            if self.db_file.exists():
                with open(self.db_file, 'r') as f:
                    db = json.load(f)
                
                if "symbol_state" in db and "config" in db["symbol_state"]:
                    self.config = db["symbol_state"]["config"].copy()
        except Exception:
            pass
    
    def _log_to_cron(self, message):
        """Log message to cron output file."""
        try:
            timestamp = self._get_current_utc()
            log_entry = f"[{timestamp}] {message}\n"
            
            # Ensure parent directory exists
            Path(self.cron_log_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.cron_log_path, 'a') as f:
                f.write(log_entry)
                
        except Exception as e:
            print(f"Warning: Failed to write to cron log: {e}")
    
    def _log_to_database(self, operation, status, message, details=None, update_queue=True):
        """Log operation to database symbol_state."""
        try:
            if self.db_file.exists():
                with open(self.db_file, 'r') as f:
                    db = json.load(f)
                
                if "symbol_state" in db:
                    state = db["symbol_state"]
                    current_time = self._get_current_utc()
                    
                    # Create log entry
                    extra_details = details.copy() if details else {}
                    log_entry = {
                        "timestamp": current_time,
                        "operation": operation,
                        "status": status,  # success, warning, error, info
                        "message": message,
                        "details": extra_details
                    }
                    
                    state["last_updated"] = current_time
                    
                    # Update queue and metadata based on status
                    if update_queue:
                        if status == "success" and "exports_completed" in state:
                            # Remove from failed if present, add to completed
                            sym_id = extra_details.get("symbol_id")
                            if sym_id and "exports_failed" in state:
                                state["exports_failed"] = [
                                    e for e in state["exports_failed"]
                                    if str(e.get("symbol_id", "")) != str(sym_id)
                                ]
                            
                            # Add to completed
                            completed_entry = {
                                "timestamp": current_time,
                                "symbol_id": sym_id,
                                "path": extra_details.get("path", "")
                            }
                            if len(state["exports_completed"]) > 100:
                                state["exports_completed"] = state["exports_completed"][-100:]
                            state["exports_completed"].append(completed_entry)
                        
                        elif status in ("error", "warning") and "exports_failed" in state:
                            # Add to failed list
                            sym_id = extra_details.get("symbol_id")
                            if sym_id:
                                failed_entry = {
                                    "timestamp": current_time,
                                    "symbol_id": sym_id,
                                    "error": extra_details.get("error", "")
                                }
                                if len(state["exports_failed"]) > 100:
                                    state["exports_failed"] = state["exports_failed"][:-101]
                                state["exports_failed"].append(failed_entry)
                        
                        # Remove from processing and queue
                        sym_id = extra_details.get("symbol_id")
                        if sym_id and str(sym_id) in state.get("exports_in_progress", {}):
                            del state["exports_in_progress"][str(sym_id)]
                        
                        if update_queue:
                            queue = state.get("exports_queue", [])
                            state["exports_queue"] = [
                                s for s in queue
                                if str(s.get("symbol_id", "")) != str(sym_id)
                            ]
                    
                    with open(self.db_file, 'w') as f:
                        json.dump(db, f, indent=2)
                        
        except Exception as e:
            print(f"Warning: Failed to log to database: {e}")
    
    def get_symbols_to_export(self):
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
            print(f"Warning: Error reading exports queue: {e}")
            return []
    
    def add_symbols_to_queue(self, symbol_ids, priority="normal"):
        """Add multiple symbols to the exports queue."""
        try:
            if self.db_file.exists():
                with open(self.db_file, 'r') as f:
                    db = json.load(f)
                
                if "symbol_state" in db:
                    state = db["symbol_state"]
                    queue = state.get("exports_queue", [])
                    
                    for symbol_id in symbol_ids:
                        # Avoid duplicates
                        if not any(str(s["symbol_id"]) == str(symbol_id) for s in queue):
                            queue.append({
                                "symbol_id": symbol_id,
                                "priority": priority,
                                "added_at": self._get_current_utc(),
                                "retry_count": 0
                            })
                    
                    with open(self.db_file, 'w') as f:
                        json.dump(db, f, indent=2)
                        
            self._log_to_database("ADD", "info", 
                               f"Added {len(symbol_ids)} symbols to export queue",
                               {"symbol_ids": symbol_ids[:5], "total": len(symbol_ids)})
            
        except Exception as e:
            print(f"Warning: Failed to add symbols to queue: {e}")
    
    def mark_symbol_processing(self, symbol_id):
        """Mark a symbol as being processed (acquire lock)."""
        try:
            if self.db_file.exists():
                with open(self.db_file, 'r') as f:
                    db = json.load(f)
                
                if "symbol_state" in db:
                    state = db["symbol_state"]
                    
                    # Add to in_progress
                    if "exports_in_progress" not in state:
                        state["exports_in_progress"] = {}
                    
                    job_id = f"exp_{symbol_id}_{int(time.time())}"
                    state["exports_in_progress"][str(symbol_id)] = {
                        "status": "processing",
                        "started_at": self._get_current_utc(),
                        "job_id": job_id,
                        "retry_count": 0,
                        "last_error": None
                    }
                    
                    with open(self.db_file, 'w') as f:
                        json.dump(db, f, indent=2)
                        
        except Exception as e:
            print(f"Warning: Failed to mark symbol as processing: {e}")
    
    def _is_processing(self, symbol_id):
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
    
    def _compute_checksum(self, data):
        """Compute simple checksum of export data."""
        content = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def process_export(self, symbol_data):
        """
        Process a single symbol export job with timeout and error handling.

        Args:
            symbol_data: Dictionary containing symbol_id and other metadata
            
        Returns:
            Dictionary with export result status and details
        """
        symbol_id = symbol_data.get("symbol_id")
        if not symbol_id:
            return {"success": False, "error": "Missing symbol_id"}
        
        try:
            print(f"\nProcessing export for symbol #{symbol_id}...")
            
            # Create output path for this symbol's Visual Archive export
            export_dir = OUTPUT_DIR / self.config.get("export_dir", "visual_archive")
            output_path = export_dir / f"symbol_{symbol_id}"
            
            # Ensure output directory exists
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Generate unique file name based on symbol and timestamp
            timestamp = self._get_current_utc()
            export_file = output_path / f"export_{symbol_id}_{timestamp}.json"
            
            # Create export data structure (placeholder - replace with actual export logic)
            export_data = {
                "symbol_id": symbol_id,
                "exported_at": timestamp,
                "status": "completed",
                "content_type": "visual_archive_export",
                "path": str(export_file),
                "checksum": self._compute_checksum(export_data)
            }
            
            # Write export file (placeholder - replace with actual export logic)
            with open(export_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"   Export saved to: {export_file}")
            
            # Log success to database and cron
            self._log_to_database("EXPORT", "success", 
                               f"Export completed for symbol #{symbol_id}",
                               {"path": str(export_file), "symbol_id": symbol_id})
            self._log_to_cron(f"Export completed: symbol #{symbol_id} -> {export_file}")
            
            return {"success": True, "path": str(export_file), "symbol_id": symbol_id}
            
        except Exception as e:
            error_msg = f"Export failed for symbol #{symbol_id}: {str(e)}"
            print(f"   Error: {error_msg}")
            
            # Log failure to database and cron
            self._log_to_database("EXPORT", "error", error_msg, 
                               {"symbol_id": symbol_id, "error": str(e)})
            self._log_to_cron(f"Export failed for symbol #{symbol_id}: {str(e)}")
            
            return {"success": False, "error": str(e), "symbol_id": symbol_id}
    
    def process_exports_parallel(self, symbols, batch_size=None):
        """
        Process exports in parallel batches using ThreadPoolExecutor.

        Args:
            symbols: List of symbol dictionaries to export
            batch_size: Number of items per batch (None = use config default)
            
        Returns:
            Dictionary with batch results summary
        """
        # Determine batch size
        actual_batch_size = min(
            batch_size or self.config.get("batch_size", 4),
            len(symbols)
        )
        
        if not symbols:
            return {
                "status": "no_jobs",
                "symbols_processed": 0,
                "symbols_in_queue": 0
            }
        
        # Filter out already processing jobs
        available_symbols = [s for s in symbols 
                          if not self._is_processing(s["symbol_id"])]
        
        if not available_symbols:
            print("All available jobs are currently being processed")
            return {
                "status": "jobs_in_progress",
                "symbols_available": len(available_symbols),
                "total_queue_size": len(symbols)
            }
        
        print(f"\nProcessing {len(available_symbols)} symbols with batch size {actual_batch_size}...")
        
        results = {
            "status": "processing",
            "batch_size": actual_batch_size,
            "total_processed": 0,
            "successful": [],
            "failed": [],
            "retry_attempts": {},
            "symbols_by_job": {}
        }
        
        # Process in parallel batches using ThreadPoolExecutor
        max_workers = min(self.config.get("max_workers", self.max_workers), 
                         len(available_symbols))
        
        print(f"   Workers: {max_workers} | Batch size: {actual_batch_size}")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit jobs to executor
            future_to_symbol = {}
            
            for s in available_symbols:
                if str(s["symbol_id"]) not in self.config.get("exports_in_progress", {}):
                    # Mark as processing (handle duplicate handling)
                    try:
                        symbol_data = {"symbol_id": s["symbol_id"]}
                        
                        future = executor.submit(
                            self.process_export, 
                            symbol_data
                        )
                        
                        # Track which symbols are associated with each future
                        if future not in future_to_symbol:
                            future_to_symbol[future] = []
                        future_to_symbol[future].append(s)
                        
                    except Exception as e:
                        print(f"Warning: Failed to submit job for symbol #{s['symbol_id']}: {e}")
            
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
                            
                        # Update symbols_by_job mapping
                        symbol_id = result.get("symbol_id")
                        if symbol_id and str(symbol_id) in results["symbols_by_job"]:
                            for s in future_to_symbol.pop(future, []):
                                results["symbols_by_job"][s["symbol_id"]] = f"success" if result.get("success") else f"failed"
                            
                        completed += 1
                        
                    except Exception as e:
                        # Handle unexpected exceptions
                        error_result = {
                            "success": False,
                            "error": f"Unexpected error: {str(e)}",
                            "symbol_id": None
                        }
                        batch_results.append(error_result)
                        results["failed"].append(error_result)
                        
                        # Update symbols_by_job mapping
                        for s in future_to_symbol.pop(future, []):
                            results["symbols_by_job"][s["symbol_id"]] = f"error: {str(e)}"
                        
                        completed += 1
                
                # Wait a moment between batches if jobs completed (for log_interval)
                if completed > 0 and completed % self.config.get("log_interval", 1) == 0:
                    print(f"\n   Completed {completed} exports in this batch")
                    time.sleep(0.5)
        
        # Process retry queue - attempt failed exports with retry logic
        self._process_failed_exports_with_retry(batch_results, actual_batch_size)
        
        results["total_processed"] = sum(len(r.get("successful", [])) for r in batch_results) if batch_results else 0
        
        # Summary logging
        success_count = len(results["successful"])
        fail_count = len(results["failed"])
        
        print(f"\n{'=' * 70}")
        print(f"Batch COMPLETE - {success_count} successful, {fail_count} failed")
        print(f"{'=' * 70}\n")
        
        self._log_to_cron("=" * 70)
        self._log_to_cron(f"Batch complete: {success_count} successful, {fail_count} failed")
        
        return results
    
    def _process_failed_exports_with_retry(self, batch_results, batch_size=None):
        """Retry failed exports up to max_retries times with backoff."""
        try:
            if self.db_file.exists():
                with open(self.db_file, 'r') as f:
                    db = json.load(f)
                
                if "symbol_state" in db:
                    state = db["symbol_state"]
                    config = state.get("config", {})
                    max_retries = config.get("max_retries", 3)
                    retry_delay = config.get("retry_delay_seconds", 2)
                    
                    # Collect all failed exports from this batch
                    failed_exports = []
                    for result in batch_results:
                        if not result.get("success") and result.get("symbol_id"):
                            failed_exports.append({
                                "result": result,
                                "retry_count": config.get("max_retries", 3) - 1
                            })
                    
                    if not failed_exports:
                        return
                    
                    print(f"\nFound {len(failed_exports)} failed exports for retry processing")
                    
                    # Process each failed export for retries
                    for item in failed_exports:
                        result = item["result"]
                        symbol_id = result.get("symbol_id")
                        
                        if not symbol_id or self._is_processing(symbol_id):
                            continue
                        
                        attempt = 1
                        
                        # Determine if we should retry based on error type
                        error = result.get("error", "")
                        
                        # Only retry certain types of errors (not permission issues, etc.)
                        can_retry = not any(x in error.lower() for x in [
                            "permission", "denied", "access denied", 
                            "file exists", "already exists",
                            "no such file"
                        ]) if error else True
                        
                        if can_retry and attempt < max_retries:
                            print(f"   Retry {attempt}/{max_retries} for symbol #{symbol_id}")
                            
                            try:
                                # Attempt export again
                                result = self.process_export({
                                    "symbol_id": symbol_id,
                                    "retry_attempt": attempt
                                })
                                
                                if result.get("success"):
                                    # Remove from failed
                                    if str(symbol_id) in state.get("exports_failed", []):
                                        state["exports_failed"] = [
                                            e for e in state["exports_failed"]
                                            if str(e.get("symbol_id", "")) != str(symbol_id)
                                        ]
                                    
                                    print(f"      Retry {attempt} succeeded!")
                                
                                else:
                                    # Increment retry count and update metadata
                                    existing_metadata = state.get("exports_metadata", {}).get(str(symbol_id), {})
                                    state["exports_metadata"][str(symbol_id)] = existing_metadata.copy()
                                    state["exports_metadata"][str(symbol_id)].update({
                                        "retry_count": attempt,
                                        "last_error": result.get("error"),
                                        "status": "failed"
                                    })
                                    
                            except Exception as e:
                                print(f"      Retry {attempt} error: {str(e)}")
                        
                        elif not can_retry or attempt >= max_retries:
                            print(f"   Symbol #{symbol_id} exhausted retries (attempts={attempt})")
                            
                            # Update metadata to mark as permanently failed
                            existing_metadata = state.get("exports_metadata", {}).get(str(symbol_id), {})
                            state["exports_metadata"][str(symbol_id)] = existing_metadata.copy()
                            state["exports_metadata"][str(symbol_id)].update({
                                "last_error": result.get("error", str(e)) if error else str(e),
                                "status": "failed_permanently"
                            })
                            
        except Exception as e:
            print(f"Warning: Failed to process retries: {e}")
    
    def show_status(self):
        """Show current export job status."""
        try:
            if self.db_file.exists():
                with open(self.db_file, 'r') as f:
                    db = json.load(f)
                
                if "symbol_state" in db:
                    state = db["symbol_state"]
                    
                    print("\n" + "=" * 70)
                    print("VISUAL ARCHIVE EXPORT STATUS (V2)")
                    print("=" * 70)
                    print(f"\nQueue size:          {len(state.get('exports_queue', []))}")
                    print(f"In progress:         {len(state.get('exports_in_progress', {}))}")
                    print(f"Completed:           {len(state.get('exports_completed', []))}")
                    print(f"Failed (retryable):  {len(state.get('exports_failed', []))}")
                    
                    # Show detailed in-progress jobs
                    if state.get("exports_in_progress"):
                        print("\nIn Progress:")
                        for job_id, info in list(state['exports_in_progress'].items())[:10]:
                            print(f"  - Symbol #{info.get('symbol_id', 'unknown')}: {job_id} (started {info.get('started_at', 'N/A')})")
                    
                    if state.get("exports_queue"):
                        print("\nPending Exports:")
                        for item in state['exports_queue'][:10]:
                            print(f"  - Symbol #{item.get('symbol_id')} [{item.get('priority', 'normal')}]")
                    
                    print(f"\nLast updated: {state.get('last_updated', 'N/A')}")
                    
                    # Show recent history
                    if state.get("exports_completed"):
                        recent = state["exports_completed"][-5:]
                        print("\nRecent Completions:")
                        for entry in reversed(recent):
                            ts = entry.get("timestamp", "unknown")[:19]  # Short timestamp
                            sid = entry.get("symbol_id", "unknown")
                            print(f"  - #{sid} @ {ts}")
                    
        except Exception as e:
            print(f"Warning: Error showing status: {e}")
    
    def retry_job(self, symbol_id):
        """Retry a failed export job."""
        try:
            print(f"\nRetrying export for symbol #{symbol_id}...")
            
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
                            if str(e.get("symbol_id", "")) != str(symbol_id)
                        ]
                        
                        # Add to completed
                        completed_entry = {
                            "symbol_id": symbol_id,
                            "recovered_at": self._get_current_utc(),
                            "recovered_from_retry": True
                        }
                        state["exports_completed"].append(completed_entry)
                        if len(state["exports_completed"]) > 100:
                            state["exports_completed"] = state["exports_completed"][-100:]
                        
                        # Remove from queue
                        state["exports_queue"] = [
                            s for s in state.get("exports_queue", [])
                            if str(s.get("symbol_id", "")) != str(symbol_id)
                        ]
                        
                        with open(self.db_file, 'w') as f:
                            json.dump(db, f, indent=2)
                        
                        print(f"Recovery successful! Export recovered.")
            
            return result
            
        except Exception as e:
            print(f"Retry failed: {e}")
            return {"success": False, "error": str(e)}
    
    def cleanup(self):
        """Cleanup completed exports (optional archival)."""
        print("\nStarting cleanup of completed exports...")
        self._log_to_cron("Starting cleanup of completed exports")
        
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
                            print(f"   Archived: {export_file} -> {archive_path}")
                            
                            # Remove from completed list in database
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
                            print(f"   Warning: Failed to archive {export_file}: {e}")
                    else:
                        remaining_count += 1
                
                if archived_count > 0:
                    print(f"\nArchived {archived_count} exports")
                    print(f"Remaining in output: {remaining_count} exports")
                    
                    self._log_to_cron(f"Cleanup complete: archived {archived_count}, remaining {remaining_count}")
                
        except Exception as e:
            print(f"Cleanup error: {e}")


def run_exports(max_workers=4):
    """Main entry point for running export jobs."""
    manager = VisualArchiveExportManagerV2(max_workers=max_workers)
    return manager.run_exports_batch()


def run_exports_batch(max_workers=4, batch_size=None):
    """Run exports with optional custom batch size."""
    manager = VisualArchiveExportManagerV2(max_workers=max_workers)
    queue = manager.get_symbols_to_export()
    
    if not queue:
        print("No exports in queue - nothing to process")
        return {
            "status": "no_jobs",
            "symbols_processed": 0,
            "symbols_in_queue": len(queue)
        }
    
    # Determine batch size (3-5 as specified)
    actual_batch_size = min(batch_size or manager.config.get("batch_size", 4), 5)
    
    return manager.process_exports_parallel(queue, batch_size=actual_batch_size)


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Visual Archive Export Job Manager v2"
    )
    parser.add_argument(
        "command",
        choices=["run", "status", "retry", "cleanup"],
        help="Command to execute"
    )
    parser.add_argument(
        "job_id", 
        nargs="?",
        help="Job ID (symbol_id) for retry command"
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Maximum parallel workers (default: 4)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        choices=[3, 4, 5],
        default=None,
        help="Batch size for parallel processing (3-5). Default uses config."
    )
    
    args = parser.parse_args()
    
    manager = VisualArchiveExportManagerV2(max_workers=args.max_workers)
    
    if args.command == "run":
        if args.batch_size:
            print(f"Running with batch size {args.batch_size}...")
        result = run_exports_batch(max_workers=args.max_workers, batch_size=args.batch_size)
        return result
    elif args.command == "status":
        manager.show_status()
        return {"status": "status_shown"}
    elif args.command == "retry":
        if not args.job_id:
            print("Job ID (symbol_id) required for retry command")
            return {"success": False, "error": "job_id_required"}
        
        try:
            symbol_id = int(args.job_id)
            return manager.retry_job(symbol_id)
        except ValueError:
            print(f"Invalid job ID: {args.job_id}")
            return {"success": False, "error": "invalid_job_id"}
    elif args.command == "cleanup":
        manager.cleanup()
        return {"status": "cleanup_complete"}


if __name__ == "__main__":
    result = main()
    
    if result and isinstance(result, dict):
        status = result.get("status", "unknown")
        
        # Print final summary for run commands
        if status != "no_jobs" and status != "jobs_in_progress":
            success = result.get("successful", [])
            failed = result.get("failed", [])
            
            print(f"\n{'=' * 70}")
            print("FINAL REPORT")
            print(f"{'=' * 70}")
            print(f"Successful:   {len(success)} exports completed")
            print(f"Failed:        {len(failed)} exports failed")
            
            if failed:
                print("\nFailed exports:")
                for f in failed[:5]:
                    sym_id = f.get("symbol_id", "unknown")
                    err = f.get("error", "Unknown error")[:60]
                    print(f"  - Symbol #{sym_id}: {err}")
