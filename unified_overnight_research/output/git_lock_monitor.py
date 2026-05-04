#!/usr/bin/env python3
"""
Git Lock Monitor for Visual Archive Export
Prevents stale .git/index.lock files from interrupted runs.
Usage: python git_lock_monitor.py [path]
"""

import os
import sys
import sqlite3
import subprocess
import shutil
from datetime import datetime
from pathlib import Path


class GitLockMonitor:
    def __init__(self, output_dir: str = "output", db_path: str = None):
        self.output_dir = Path(output_dir)
        self.git_dir = self.output_dir / ".git"
        self.lock_file = self.git_dir / "index.lock"
        
        # Database path - defaults to the gematria repository's SQLite DB
        if not db_path:
            # Try common locations for the database
            for candidate in ["output.db", "db/output.db", "/data/gematria/outputs/output.db"]:
                if os.path.exists(candidate):
                    self.db_path = candidate
                    break
            else:
                # Fallback to same directory as script
                script_dir = Path(__file__).parent
                self.db_path = script_dir / "output.db"
        
        self.logger = GitLockLogger(self.db_path)
    
    def check_for_locks(self) -> dict:
        """Check if .git/index.lock exists and is stale."""
        result = {
            "timestamp": datetime.now().isoformat(),
            "lock_exists": False,
            "lock_age_seconds": 0,
            "actions_taken": [],
            "errors": []
        }
        
        # Check if .git directory exists
        if not self.git_dir.exists():
            result["actions_taken"].append(f"INFO: {self.git_dir} does not exist (not a git repository)")
            return result
        
        # Check for lock file
        if self.lock_file.exists():
            result["lock_exists"] = True
            
            # Calculate lock age
            lock_mtime = self.lock_file.stat().st_mtime
            now = datetime.now()
            lock_time = datetime.fromtimestamp(lock_mtime)
            result["lock_age_seconds"] = (now - lock_time).total_seconds()
            
            result["actions_taken"].append(
                f"LOCK DETECTED: {self.lock_file} (age: {result['lock_age_seconds']:.0f}s, created: {lock_time.strftime('%Y-%m-%d %H:%M:%S')})"
            )
        
        return result
    
    def cleanup_lock(self) -> dict:
        """Clean up stale lock file with proper git commands and error handling."""
        result = self.check_for_locks()
        
        if not result["lock_exists"]:
            result["actions_taken"].append("ACTION: No lock to clean up")
            return result
        
        # Step 1: Try git gc first (may clear the lock automatically)
        result["actions_taken"].append("ACTION: Attempting git gc...")
        self._run_git_command(["gc"])
        
        # Check if lock still exists after gc
        if self.lock_file.exists():
            result["actions_taken"].append("ACTION: Lock persists after git gc, proceeding with manual cleanup")
            
            # Step 2: Remove .git directory to clear all state including lock
            try:
                if self.git_dir.is_dir():
                    result["actions_taken"].append(f"ACTION: Removing {self.git_dir} directory...")
                    shutil.rmtree(self.git_dir)
                elif self.git_dir.is_file():
                    result["actions_taken"].append("ACTION: Removing .git file...")
                    os.remove(self.git_dir)
            except PermissionError as e:
                error_result = self._handle_permission_error(str(e))
                result["errors"].extend(error_result)
            except Exception as e:
                result["errors"].append(f"ERROR: Failed to remove .git directory: {e}")
        else:
            result["actions_taken"].append("ACTION: Lock cleared by git gc")
        
        return result
    
    def _run_git_command(self, args: list[str]) -> dict:
        """Run a git command with proper error handling."""
        try:
            # Run in output directory to avoid needing to cd
            cmd = ["git"] + args
            output = subprocess.run(
                cmd,
                cwd=str(self.output_dir),
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout for git operations
            )
            
            if output.returncode == 0:
                return {"success": True, "stdout": output.stdout, "stderr": output.stderr}
            else:
                return {
                    "success": False, 
                    "returncode": output.returncode,
                    "stdout": output.stdout,
                    "stderr": output.stderr
                }
        except subprocess.TimeoutExpired as e:
            return {"error": f"Git command timed out after 120 seconds", "command": cmd}
        except Exception as e:
            return {"error": str(e)}
    
    def _handle_permission_error(self, error_msg: str) -> list[str]:
        """Attempt to fix permission errors and retry cleanup."""
        actions = []
        
        # Try chmod +755 on .git directory if it exists as a directory
        if self.git_dir.exists():
            try:
                os.chmod(self.git_dir, 0o755)
                actions.append("FIXED: Applied chmod +755 to .git directory")
                
                # Retry removing the lock file directly
                try:
                    shutil.rmtree(self.git_dir)
                    actions.append("SUCCESS: Successfully removed .git directory after chmod")
                except Exception as e2:
                    actions.append(f"AFTER CHMOD: Still failed to remove .git: {e2}")
            except PermissionError:
                actions.append("FAILED: Could not apply chmod - still owned by another user/process")
        else:
            actions.append(f"PERMISSION ISSUE: Lock file {self.lock_file} but .git not a directory")
        
        return actions
    
    def run(self, dry_run: bool = False) -> int:
        """
        Run the lock monitor and cleanup.
        
        Args:
            dry_run: If True, only check for locks without performing cleanup
            
        Returns:
            Exit code: 0 if OK/clean, 1 if lock detected (dry-run or cleaned), 2 on error
        """
        self.logger.log_session_start("git_lock_monitor")
        
        try:
            # Step 1: Check for locks
            result = self.check_for_locks()
            
            # Log check result
            self.logger.log_action(
                "check",
                f"output/.git/index.lock {'exists' if result['lock_exists'] else 'does not exist'}",
                level="WARNING" if result["lock_exists"] else "INFO",
                dry_run=dry_run
            )
            
            # Step 2: If lock exists and not dry-run, clean it up
            if result["lock_exists"] and not dry_run:
                cleanup_result = self.cleanup_lock()
                
                # Log cleanup actions
                for action in cleanup_result["actions_taken"]:
                    level = "INFO"
                    if "ERROR" in action or "FAILED" in action:
                        level = "ERROR"
                    self.logger.log_action(
                        "cleanup",
                        action,
                        level=level
                    )
                
                # Log errors
                for error in cleanup_result["errors"]:
                    self.logger.log_action(
                        "cleanup",
                        f"{error}",
                        level="ERROR"
                    )
            elif result["lock_exists"] and dry_run:
                # Dry-run with lock detected
                self.logger.log_action(
                    "check",
                    f"Dry run: Would clean up lock (detected but not cleaned)",
                    level="WARNING"
                )
            
            # Step 3: Final result logging
            if result["lock_exists"]:
                if dry_run or not result["errors"]:
                    self.logger.log_session_end("success", 
                        f"Lock {'would be' if dry_run else 'was'} detected and handled")
                    return 1  # Lock was present (exit 1 is expected for monitor)
                else:
                    self.logger.log_session_end("error", "Lock cleanup failed with errors")
                    return 2
            else:
                self.logger.log_session_end("success", "No lock detected")
                return 0
        
        except Exception as e:
            self.logger.log_error(f"Unexpected error: {e}", str(e))
            self.logger.log_session_end("error", f"Unexpected error: {e}")
            return 2


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Git Lock Monitor for Visual Archive Export"
    )
    parser.add_argument(
        "output_dir", 
        nargs="?",
        default="output",
        help="Output directory to check (default: output)"
    )
    parser.add_argument(
        "--db", 
        default=None,
        help="Path to SQLite database for logging"
    )
    parser.add_argument(
        "-n", "--dry-run",
        action="store_true",
        help="Check only, do not perform cleanup"
    )
    
    args = parser.parse_args()
    
    monitor = GitLockMonitor(
        output_dir=args.output_dir,
        db_path=args.db
    )
    
    exit_code = monitor.run(dry_run=args.dry_run)
    
    if exit_code == 1 and not args.dry_run:
        print("WARNING: Stale lock was detected and cleaned up")
        sys.stdout.flush()
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
