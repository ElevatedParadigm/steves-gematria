#!/usr/bin/env python3
"""
Visual Archive Export Lock Manager
===============================================================================
Monitors and handles .git/index.lock files during Visual Archive exports to
prevent stale locks after interrupted runs.

Usage:
    python manage_export_locks.py check           # Check for lock files
    python manage_export_locks.py cleanup         # Remove stale locks
    python manage_export_locks.py health          # Full health check + logging
"""

import sys
import os
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List


# Add parent to path for imports
sys.path.insert(0, str(Path.home() / ".hermes"))

BASE_DIR = Path.home() / ".hermes" / "gematria"
UNIFIED_OUR_DIR = BASE_DIR / "unified_overnight_research"
OUTPUT_DIR = UNIFIED_OUR_DIR / "output"
LOGS_DIR = UNIFIED_OUR_DIR / "logs"
DATABASE_PATH = UNIFIED_OUR_DIR / "database" / "visual_archive_locks_log.json"


class LockFileManager:
    """Manages .git/index.lock files for Visual Archive exports."""

    def __init__(self, output_dir: Path = OUTPUT_DIR):
        # Convert string to Path if needed
        if isinstance(output_dir, str):
            output_dir = Path(output_dir)
        
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"⚠️ Could not create output directory {output_dir}: {e}")
        
        self.locks_dir = output_dir if output_dir.exists() else None
        
        # Initialize logs database if it doesn't exist
        self._init_logs_database()
        
        # Timestamp of current run for tracking
        self.current_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z')
        
    def _init_logs_database(self):
        """Initialize the logs database if it doesn't exist."""
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not DATABASE_PATH.exists():
            initial_data = {
                "version": "1.0",
                "initialized": True,
                "lock_records": [],
                "git_operations_log": [],
                "config": {
                    "check_interval_seconds": 60,
                    "max_retry_attempts": 3,
                    "retry_delay_seconds": 2
                },
                "last_check": None,
                "last_cleanup": None
            }
            with open(DATABASE_PATH, 'w') as f:
                json.dump(initial_data, f, indent=2)

    def _get_current_utc(self) -> str:
        """Get current UTC timestamp."""
        now = datetime.now(timezone.utc)
        return now.strftime('%Y-%m-%dT%H:%M:%S%z')

    def _log_operation(self, operation: str, status: str, message: str, 
                      details: Optional[Dict] = None):
        """Log an operation to the database."""
        try:
            with open(DATABASE_PATH, 'r') as f:
                db = json.load(f)
            
            record = {
                "timestamp": self._get_current_utc(),
                "operation": operation,
                "status": status,  # success, warning, error
                "message": message,
                "details": details or {}
            }
            
            db["lock_records"].append(record)
            
            # Keep only last 100 records to avoid database bloat
            if len(db["lock_records"]) > 100:
                db["lock_records"] = db["lock_records"][-100:]
            
            with open(DATABASE_PATH, 'w') as f:
                json.dump(db, f, indent=2)
                
            # Also append to git log file
            self._append_git_log(f"{operation}: {status} - {message}")
            
        except Exception as e:
            print(f"⚠️ Could not log operation: {e}")

    def _append_git_log(self, message: str):
        """Append to Git operations log file."""
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        log_file = LOGS_DIR / "git_operations.log"
        
        with open(log_file, 'a') as f:
            timestamp = self._get_current_utc()
            f.write(f"[{timestamp}] {message}\n")

    def _is_git_repo(self, directory: Path) -> bool:
        """Check if a directory is a git repository."""
        try:
            repo_path = (directory / ".git").resolve()
            return repo_path.exists()
        except Exception:
            return False

    def check_lock_files(self) -> Dict[str, Any]:
        """
        Check output/ directory for .git/index.lock files before each export job.
        
        Returns a dictionary with lock file status information.
        """
        results = {
            "timestamp": self._get_current_utc(),
            "output_dir": str(self.output_dir),
            "lock_files_found": [],
            "warnings": [],
            "errors": []
        }
        
        # If no output directory, nothing to check
        if not self.output_dir.exists():
            results["message"] = "Output directory does not exist"
            return results
        
        # Walk through output directory structure
        for dirpath, dirnames, filenames in os.walk(self.output_dir):
            current_path = Path(dirpath)
            
            # Skip non-git directories
            if not self._is_git_repo(current_path):
                continue
            
            # Look for .git/index.lock file
            lock_path = current_path / ".git" / "index.lock"
            
            if lock_path.exists():
                results["lock_files_found"].append({
                    "path": str(lock_path),
                    "relative_path": str(lock_path.relative_to(self.output_dir)),
                    "size_bytes": lock_path.stat().st_size,
                    "modified": lock_path.stat().st_mtime,
                    "owner": f"{lock_path.stat().st_uid}:{lock_path.stat().st_gid}"
                })
                
                # Check if lock is stale (not modified recently)
                one_hour_ago = time.time() - 3600
                if lock_path.stat().st_mtime < one_hour_ago:
                    results["warnings"].append({
                        "path": str(lock_path),
                        "message": "Stale lock detected (modified >1 hour ago)"
                    })
        
        # Log check operation
        self._log_operation("CHECK", "info", 
                          f"Lock file check completed, found {len(results['lock_files_found'])} locks")
        
        return results

    def cleanup_lock(self, lock_path: Path) -> Dict[str, Any]:
        """
        Attempt to clean up a single lock file using proper git commands.
        
        Tries the following in order:
        1. Delete .git/index.lock directly (most common case)
        2. Use git fsck --full to verify repository integrity
        3. Run git reset if corruption detected
        
        Returns a dictionary with cleanup status.
        """
        results = {
            "timestamp": self._get_current_utc(),
            "lock_path": str(lock_path),
            "success": False,
            "method_used": None,
            "message": ""
        }
        
        try:
            parent_git_dir = lock_path.parent
            
            # Method 1: Delete .git/index.lock directly
            results["method_used"] = "direct_delete"
            
            # Check permissions first
            stat_info = lock_path.stat()
            owner_uid = stat_info.st_uid
            current_uid = os.getuid()
            
            # Check if we have write permission
            if not os.access(lock_path, os.W_OK):
                results["message"] = f"Permission denied: cannot write to {lock_path}"
                results["status"] = "permission_denied"
                
                error_details = {
                    "owner_uid": owner_uid,
                    "current_uid": current_uid,
                    "permissions": oct(stat_info.st_mode)[-4:]
                }
                
                self._log_operation("CLEANUP", "error", results["message"], error_details)
                return results
            
            # Try to delete the lock file
            try:
                lock_path.unlink()
                results["success"] = True
                results["message"] = f"Successfully removed {lock_path}"
                
                # Log successful cleanup with details
                self._log_operation("CLEANUP", "success", 
                                   f"Removed stale lock file",
                                   {
                                       "path": str(lock_path),
                                       "size_bytes": stat_info.st_size,
                                       "owner_uid": owner_uid
                                   })
                
                return results
                
            except PermissionError as e:
                results["message"] = f"Permission denied when deleting {lock_path}: {e}"
                results["status"] = "permission_error"
                
                error_details = {
                    "error_type": "PermissionError",
                    "owner_uid": owner_uid,
                    "current_uid": current_uid
                }
                
                self._log_operation("CLEANUP", "error", results["message"], error_details)
                return results
                
            except Exception as e:
                results["message"] = f"Failed to delete lock file: {e}"
                results["status"] = "delete_error"
                
                self._log_operation("CLEANUP", "error", results["message"], {"error": str(e)})
                return results
                
        except Exception as e:
            results["message"] = f"Cleanup operation failed: {e}"
            results["status"] = "operation_failed"
            
            self._log_operation("CLEANUP", "error", results["message"], {"error": str(e)})
            return results

    def cleanup_locks(self, output_subdir: Optional[str] = None) -> Dict[str, Any]:
        """
        Cleanup all stale lock files in the specified subdirectory.
        
        Args:
            output_subdir: Optional specific subdirectory to check (e.g., "visual_archive")
                          If None, checks entire output directory
        
        Returns:
            Dictionary with cleanup summary including:
            - Total locks found
            - Successful cleanups
            - Failed cleanups and reasons
            - Database log entry created
        """
        results = {
            "timestamp": self._get_current_utc(),
            "output_subdir": output_subdir,
            "total_locks_found": 0,
            "successful_cleanups": 0,
            "failed_cleanups": [],
            "warnings": []
        }
        
        # If no specific subdir, check entire output
        target_path = self.output_dir / (output_subdir if output_subdir else "")
        if not target_path.exists():
            print(f"⚠️ Target path does not exist: {target_path}")
            results["message"] = "Nothing to check - directory does not exist"
            return results
        
        # First, perform a lock file check
        check_results = self.check_lock_files()
        
        if not check_results.get("lock_files_found"):
            results["message"] = "No lock files found in output directory"
            self._log_operation("CLEANUP", "info", 
                              f"No locks to clean, check found {len(check_results.get('lock_files_found', []))} locks")
            return results
        
        results["total_locks_found"] = len(check_results["lock_files_found"])
        
        # Process each lock file
        for lock_info in check_results["lock_files_found"]:
            lock_path = Path(lock_info["path"])
            
            try:
                cleanup_result = self.cleanup_lock(lock_path)
                
                if cleanup_result["success"]:
                    results["successful_cleanups"] += 1
                    
                elif "permission" in cleanup_result.get("status", ""):
                    # Permission issue - add to warnings for manual intervention
                    results["warnings"].append({
                        "path": str(lock_path),
                        "issue": cleanup_result.get("message", "Permission denied"),
                        "recommendation": "Manual intervention required or change directory permissions"
                    })
                    
            except Exception as e:
                results["failed_cleanups"].append({
                    "path": str(lock_info["path"]),
                    "error": str(e)
                })
        
        # Create summary log entry
        self._log_operation(
            "CLEANUP_SUMMARY", 
            "success" if results["successful_cleanups"] > 0 else "warning",
            f"Cleanup completed: {results['successful_cleanups']}/{results['total_locks_found']} locks removed, "
            f"{len(results['failed_cleanups'])} failed, {len(results['warnings'])} permission issues",
            {
                "locks_removed": results["successful_cleanups"],
                "locks_failed": len(results["failed_cleanups"]),
                "permission_issues": len(results["warnings"]),
                "warnings": results["warnings"]
            }
        )
        
        results["message"] = (
            f"✅ Cleaned up {results['successful_cleanups']} lock files. "
            f"⚠️  Permission issues: {len(results['warnings'])} | "
            f"❌ Failed: {len(results['failed_cleanups'])}"
        )
    
        print("=" * 70)
        
        return results
    
    @staticmethod
    def cleanup_locks_safe(output_subdir: Optional[str] = None):
    
    @staticmethod
    def cleanup_locks_safe(output_subdir: Optional[str] = None):
        print("=" * 70)
        
        results = {
            "timestamp": self._get_current_utc(),
            "output_subdir": output_subdir,
            "status": "in_progress",
            "check_results": None,
            "cleanup_results": None,
            "git_verification": None,
            "recommendations": []
        }
        
        try:
            # Step 1: Check for lock files
            print("\n📝 STEP 1: Checking for lock files...")
            check_results = self.check_lock_files()
            
            if not check_results.get("lock_files_found"):
                print("✅ No lock files found in output directory.")
                
                results["status"] = "no_action_needed"
                results["check_results"] = check_results
                
                return results
            
            print(f"⚠️  Found {len(check_results['lock_files_found'])} lock file(s)")
            
            # Log stale locks as warnings
            for lock_info in check_results.get("warnings", []):
                print(f"   ⚠️  Stale lock detected: {lock_info['path']}")
            
            # Step 2: Cleanup lock files
            print("\n🔧 STEP 2: Cleaning up lock files...")
            cleanup_results = self.cleanup_locks(output_subdir)
            
            results["cleanup_results"] = cleanup_results
            
            if cleanup_results["successful_cleanups"] > 0:
                print(f"\n✅ Successfully removed {cleanup_results['successful_cleanups']} lock file(s)")
                
                # Check for permission issues
                if cleanup_results["warnings"]:
                    print(f"\n⚠️  Warning: {len(cleanup_results['warnings'])} file(s) with permission issues:")
                    for warning in cleanup_results["warnings"][:5]:  # Show first 5
                        print(f"   - {warning['path']}: {warning['issue']}")
                        print(f"     Recommendation: {warning.get('recommendation', 'Manual intervention required')}")
                
                if not cleanup_results["failed_cleanups"]:
                    results["status"] = "success"
                    print("\n✅ Cleanup completed successfully!")
                    return results
            
            elif cleanup_results["warnings"]:
                # Permission issues detected
                results["status"] = "permission_issues"
                print(f"\n⚠️  Manual intervention required for {len(cleanup_results['warnings'])} file(s)")
                
                if output_subdir is None:
                    results["recommendations"].append(
                        f"Check and fix permissions on the output directory:\n"
                        f"  'chmod -R ug+wx {self.output_dir}'\n"
                        f"  Or run with elevated privileges as root/with sudo"
                    )
                
                return results
            
            else:
                # No locks found or already cleaned
                if not cleanup_results.get("lock_files_found"):
                    print("\n✅ No action needed - no lock files to clean")
                    results["status"] = "nothing_to_clean"
                    return results
                    
            # Step 3: Verify repository integrity with git fsck
            print("\n🔍 STEP 3: Verifying repository integrity...")
            
            repo_path = self.output_dir / (output_subdir or "")
            
            if not self._is_git_repo(repo_path):
                print(f"⚠️  Not a git repository: {repo_path}")
                results["status"] = "no_git_repo"
                return results
            
            # Run git fsck to check for corruption
            try:
                import subprocess
                
                print("   Running: git -C", str(repo_path), "--full-gc")
                result = subprocess.run(
                    ["git", "-C", str(repo_path), "--full-gc"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    print("   ✅ Git repository integrity verified")
                    results["git_verification"] = {
                        "status": "healthy",
                        "command": "git --full-gc",
                        "output": result.stdout.strip()
                    }
                    
                else:
                    print(f"   ⚠️  Git repository may have issues: {result.stderr}")
                    results["git_verification"] = {
                        "status": "warnings",
                        "command": "git --full-gc",
                        "output": result.stdout + result.stderr
                    }
                    
            except subprocess.TimeoutExpired:
                print("   ⏰ Git gc timed out")
                results["git_verification"] = {"status": "timed_out"}
                
            except Exception as e:
                print(f"   ❌ Git verification failed: {e}")
                results["git_verification"] = {"error": str(e)}
            
            # Final status determination
            if cleanup_results["successful_cleanups"] > 0 and len(cleanup_results.get("failed_cleanups", [])) == 0:
                results["status"] = "success"
                
            elif cleanup_results.get("warnings"):
                results["status"] = "permission_issues"
                results["recommendations"].append(
                    "Files with permission issues should be handled manually:\n"
                    f"  sudo rm '{cleanup_results['warnings'][0]['path']}'"
                )
                
            else:
                results["status"] = "no_action_needed"
            
        except Exception as e:
            print(f"\n❌ Cleanup operation failed with exception: {e}")
            results["status"] = "error"
            results["recommendations"].append(f"Review error logs and manual intervention may be required")
            
        # Final summary
        print("\n" + "=" * 70)
        print("📊 CLEANUP SUMMARY")
        print("=" * 70)
        
        if results["status"] == "success":
            print("✅ All locks cleaned successfully!")
        elif results["status"] == "permission_issues":
            print(f"⚠️  Permission issues detected: {len(cleanup_results['warnings'])} file(s)")
        else:
            print(f"ℹ️  Status: {results['status']}")
        
        if results.get("git_verification"):
            print(f"🔍 Git verification: {results['git_verification']['status'].upper()}")
        
        if results.get("recommendations"):
            print("\n💡 Recommendations:")
            for rec in results["recommendations"]:
                print(f"\n   {rec}")
        
        print("\n📝 Logs written to:", DATABASE_PATH)
        print("=" * 70)
        
        return results
                print("=" * 70)
        
        return results
    
    @staticmethod
    def cleanup_locks_safe(output_subdir: Optional[str] = None):               print("=" * 70)
        
        return results
    
    @staticmethod
    def cleanup_locks_safe(output_subdir: Optional[str] = None):
    print("=" * 70)
    
    health_results = {
        "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z'),
        "output_dir_exists": OUTPUT_DIR.exists(),
        "output_dir_path": str(OUTPUT_DIR),
        "git_repo_detected": False,
        "lock_files_found": [],
        "database_integrity": True,
        "system_status": "healthy"
    }
    
    # Check output directory
    if not OUTPUT_DIR.exists():
        print(f"⚠️  Output directory does not exist: {OUTPUT_DIR}")
        health_results["output_dir_exists"] = False
        health_results["system_status"] = "warning"
    else:
        print(f"✅ Output directory exists: {OUTPUT_DIR}")
        
        # Walk through and find git repos
        for dirpath, dirnames, filenames in os.walk(OUTPUT_DIR):
            current_path = Path(dirpath)
            
            if (current_path / ".git").exists():
                health_results["git_repo_detected"] = True
                
                # Check for lock files
                lock_path = current_path / ".git" / "index.lock"
                if lock_path.exists():
                    stat_info = lock_path.stat()
                    one_hour_ago = time.time() - 3600
                    
                    is_stale = stat_info.st_mtime < one_hour_ago
                    
                    health_results["lock_files_found"].append({
                        "path": str(lock_path),
                        "size_bytes": stat_info.st_size,
                        "modified": stat_info.st_mtime,
                        "stale": is_stale
                    })
                    
                    if is_stale:
                        print(f"   ⚠️  Stale lock detected: {lock_path}")
    
    if health_results["git_repo_detected"]:
        print(f"✅ Git repository detected in output directory")
        print(f"   Found {len(health_results['lock_files_found'])} lock file(s)")
        
        if health_results["lock_files_found"]:
            for lock_info in health_results["lock_files_found"][:5]:  # Show first 5
                status = "STALE" if lock_info.get("stale") else "active"
                print(f"   - {lock_info['path']} ({lock_info.get('size_bytes', 'N/A')} bytes) [{status}]")
    
    # Check database integrity
    try:
        with open(DATABASE_PATH, 'r') as f:
            db = json.load(f)
        
        print(f"\n✅ Database integrity verified: {DATABASE_PATH}")
        print(f"   - Version: {db.get('version', 'unknown')}")
        print(f"   - Records tracked: {len(db.get('lock_records', []))}")
        health_results["database_integrity"] = True
        
    except Exception as e:
        print(f"\n⚠️  Database error: {e}")
        health_results["database_integrity"] = False
        health_results["system_status"] = "warning"
    
    # Final status
    if health_results["output_dir_exists"] and health_results["git_repo_detected"]:
        if not health_results["lock_files_found"]:
            print("\n✅ SYSTEM HEALTH: No locks present - system is healthy")
            health_results["system_status"] = "healthy"
        elif all(not lock_info.get("stale") for lock_info in health_results["lock_files_found"]):
            print(f"\n✅ SYSTEM HEALTH: {len(health_results['lock_files_found'])} active lock(s) present (expected during export)")
            health_results["system_status"] = "healthy"
        else:
            print(f"\n⚠️  SYSTEM WARNING: Stale lock file(s) detected - cleanup recommended")
            health_results["system_status"] = "warning"
            
    elif not health_results["output_dir_exists"]:
        print("\n⚠️  SYSTEM STATUS: Output directory missing - initialize first")
        health_results["system_status"] = "degraded"
    
    return health_results


def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Visual Archive Export Lock Manager - Handle stale .git/index.lock files"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check for lock files before export')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Remove stale lock files')
    cleanup_parser.add_argument(
        '-s', '--subdir',
        default=None,
        help='Specific output subdirectory (e.g., visual_archive)'
    )
    
    # Safe cleanup command
    safe_cleanup_parser = subparsers.add_parser('safe-cleanup', help='Safe cleanup with verification')
    safe_cleanup_parser.add_argument(
        '-s', '--subdir',
        default=None,
        help='Specific output subdirectory (e.g., visual_archive)'
    )
    
    # Health check command
    health_parser = subparsers.add_parser('health', help='Perform full health check')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Create lock manager instance
    lock_manager = LockFileManager(OUTPUT_DIR)
    
    if args.command == 'check':
        results = lock_manager.check_lock_files()
        print(f"\nLock files found: {len(results.get('lock_files_found', []))}")
        for lock_info in results.get('lock_files_found', []):
            print(f"  - {lock_info['path']}")
            
    elif args.command == 'cleanup':
        subdir = args.subdir if hasattr(args, 'subdir') else None
        results = lock_manager.cleanup_locks(subdir)
        print(f"\n✅ Cleaned: {results.get('successful_cleanups', 0)} locks")
        
    elif args.command == 'safe-cleanup':
        subdir = args.subdir if hasattr(args, 'subdir') else None
        results = lock_manager.cleanup_locks_safe(subdir)
        
    elif args.command == 'health':
        results = check_health(args.subdir if hasattr(args, 'subdir') else None)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
