"""
SQLite Database Logger for Git Lock Monitor
Logs all check, cleanup, and error actions with timestamps.
"""

import sqlite3
from datetime import datetime
from pathlib import Path


class GitLockLogger:
    def __init__(self, db_path: str = None):
        """
        Initialize logger and create database if it doesn't exist.
        
        Args:
            db_path: Path to SQLite database. If None, auto-detect common paths.
        """
        self.db_path = self._find_or_create_db(db_path)
    
    def _find_or_create_db(self, explicit_path: str = None) -> str:
        """Find or create the database path."""
        if explicit_path and os.path.exists(explicit_path):
            return explicit_path
        
        # Try various common locations
        candidates = [
            "output.db",
            Path("output").parent / "db" / "output.db",
            "/data/gematria/outputs/output.db"
        ]
        
        for candidate in candidates:
            if os.path.exists(candidate):
                return str(candidate)
        
        # Default to same directory as script
        return str(Path(__file__).parent / "output.db")
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with proper settings."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        # Enable foreign keys and set pragmas
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        
        return conn
    
    def init_database(self):
        """Initialize database schema if it doesn't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Create actions table for detailed logging
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lock_monitor_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                action_type TEXT NOT NULL CHECK (action_type IN ('check', 'cleanup', 'error')),
                status TEXT NOT NULL CHECK (status IN ('info', 'warning', 'success', 'error')),
                message TEXT NOT NULL,
                details TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_actions_session ON lock_monitor_actions(session_id)
        """)
        
        conn.commit()
        conn.close()
    
    def log_session_start(self, session_id: str):
        """Log the start of a monitor session."""
        self._get_connection()  # Ensure DB exists on first access
        
        action = {
            "session_id": session_id,
            "action_type": "check",
            "status": "info",
            "message": f"Git Lock Monitor started (session: {session_id})",
            "details": None
        }
        self.log_action("check", action["message"], level="INFO", details=action["details"])
    
    def log_session_end(self, session_id: str, result: str):
        """Log the end of a monitor session."""
        self._get_connection()
        
        message = f"Git Lock Monitor finished - {result}"
        status = "warning" if result == "success" else "error"  # Success when lock was found and handled
        
        action = {
            "session_id": session_id,
            "action_type": "check",
            "status": status,
            "message": message,
            "details": None
        }
        self.log_action("check", message, level=status.upper(), details=action["details"])
    
    def log_error(self, action_type: str, message: str, error_details: str = None):
        """Log an error."""
        self._get_connection()
        
        action = {
            "session_id": action_type,  # Use action type as session ID for errors
            "action_type": action_type,
            "status": "error",
            "message": message,
            "details": error_details
        }
        self.log_action(action["action_type"], action["message"], 
                       level="ERROR", details=action["details"])
    
    def log_action(self, action_type: str, message: str, level: str = "INFO", dry_run: bool = False):
        """Log a single action."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Escape special characters in message for SQLite
        escaped_message = self._escape_sql_string(message)
        escaped_details = self._escape_sql_string(None) if dry_run else None
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Millisecond precision
        
        cursor.execute("""
            INSERT INTO lock_monitor_actions 
            (session_id, action_type, status, message, details, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "lock_monitor_session",  # Generic session ID for all actions
            action_type,
            level.lower(),
            escaped_message,
            escaped_details,
            timestamp
        ))
        
        conn.commit()
        row_id = cursor.lastrowid
        
        return {
            "id": row_id,
            "action_type": action_type,
            "status": level,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "escaped_message": escaped_message
        }
    
    def _escape_sql_string(self, text: str) -> str:
        """Escape single quotes for SQLite string literals."""
        if text is None:
            return None
        return text.replace("'", "''")
    
    def get_latest_status(self) -> dict:
        """Get the most recent action status for monitoring dashboards."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT MAX(timestamp) as last_time, status, message 
            FROM lock_monitor_actions 
            ORDER BY timestamp DESC 
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "timestamp": row["last_time"],
                "status": row["status"],
                "message": row["message"]
            }
        return {"timestamp": None, "status": None, "message": None}
    
    def get_recent_actions(self, limit: int = 20) -> list:
        """Get recent actions for display."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, session_id, action_type, status, message, details, timestamp
            FROM lock_monitor_actions 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to list of dicts
        return [dict(row) for row in rows]
    
    def count_by_status(self) -> dict:
        """Get counts of actions by status."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM lock_monitor_actions 
            GROUP BY status
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return {row["status"]: row["count"] for row in rows}


def main():
    """Test the logger."""
    import os
    
    logger = GitLockLogger()
    logger.init_database()
    
    print(f"Database initialized at: {logger.db_path}")
    print("\nTesting logging...")
    
    # Test logging
    for i in range(5):
        logger.log_action("test", f"Test message {i}", level="INFO")
    
    print("Recent actions:")
    for action in logger.get_recent_actions():
        print(f"  [{action['status']}] {action['timestamp']}: {action['message']}")
    
    print("\nStatus counts:", logger.count_by_status())
