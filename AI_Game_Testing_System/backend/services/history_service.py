"""
Test History Manager for storing and retrieving past test run results.

Uses SQLite database for persistent storage of test results with timestamps, metrics, and metadata.
"""
import sqlite3
import threading
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from uuid import uuid4

from config.settings import settings
from utils.logging import get_logger
from utils.exceptions import MetricsError

logger = get_logger(__name__)


class TestHistoryManager:
    """
    Thread-safe manager for test history storage and retrieval.
    
    Uses SQLite database for storing test results.
    """
    _instance: Optional['TestHistoryManager'] = None
    _lock = threading.Lock()

    def __new__(cls):
        """Create singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(TestHistoryManager, cls).__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initialize the history manager and database."""
        self.db_path = settings.DATABASE_PATH
        self._lock = threading.Lock()
        self._ensure_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn

    def _ensure_database(self) -> None:
        """Ensure database exists with proper schema."""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Create test_history table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS test_history (
                        id TEXT PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        genre TEXT NOT NULL,
                        algorithm TEXT NOT NULL,
                        status TEXT NOT NULL,
                        duration_seconds REAL,
                        coverage REAL DEFAULT 0.0,
                        crashes INTEGER DEFAULT 0,
                        fps REAL DEFAULT 0.0,
                        total_steps INTEGER DEFAULT 0,
                        reward_mean REAL DEFAULT 0.0,
                        notes TEXT DEFAULT '',
                        screenshot_paths TEXT DEFAULT '[]',
                        bug_screenshot_paths TEXT DEFAULT '[]',
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for faster queries
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_timestamp ON test_history(timestamp DESC)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_genre ON test_history(genre)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_algorithm ON test_history(algorithm)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_status ON test_history(status)
                """)
                
                # Add screenshot columns if they don't exist (for existing databases)
                try:
                    cursor.execute("ALTER TABLE test_history ADD COLUMN screenshot_paths TEXT DEFAULT '[]'")
                except sqlite3.OperationalError:
                    pass  # Column already exists
                
                try:
                    cursor.execute("ALTER TABLE test_history ADD COLUMN bug_screenshot_paths TEXT DEFAULT '[]'")
                except sqlite3.OperationalError:
                    pass  # Column already exists
                
                conn.commit()
                logger.info(f"Database initialized: {self.db_path}")
                
                # Migrate existing JSON data if it exists
                self._migrate_json_to_sqlite()
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}", exc_info=True)
            raise MetricsError(f"Failed to initialize database: {e}")

    def _migrate_json_to_sqlite(self) -> None:
        """Migrate existing JSON data to SQLite if JSON file exists."""
        json_file = settings.LOGS_DIR / "test_history.json"
        
        if not json_file.exists():
            return
        
        try:
            logger.info("Found existing JSON file, migrating to SQLite...")
            
            # Check if database already has data
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM test_history")
                count = cursor.fetchone()[0]
                
                if count > 0:
                    logger.info("Database already has data, skipping migration")
                    return
            
            # Load JSON data
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            if not isinstance(json_data, list):
                logger.warning("JSON file is not a list, skipping migration")
                return
            
            # Migrate each entry
            migrated = 0
            for entry in json_data:
                try:
                    metrics = entry.get("metrics", {})
                    self.save_test_result(
                        genre=entry.get("genre", "unknown"),
                        algorithm=entry.get("algorithm", "Unknown"),
                        metrics=metrics,
                        status=entry.get("status", "Unknown"),
                        duration_seconds=entry.get("duration_seconds"),
                        notes=entry.get("notes", ""),
                        test_id=entry.get("id")  # Preserve original ID
                    )
                    migrated += 1
                except Exception as e:
                    logger.warning(f"Failed to migrate entry {entry.get('id')}: {e}")
            
            logger.info(f"Migrated {migrated} entries from JSON to SQLite")
            
            # Backup old JSON file
            backup_file = json_file.with_suffix('.json.backup')
            json_file.rename(backup_file)
            logger.info(f"Backed up JSON file to: {backup_file}")
            
        except Exception as e:
            logger.error(f"Error migrating JSON data: {e}", exc_info=True)

    def save_test_result(
        self,
        genre: str,
        algorithm: str,
        metrics: Dict[str, Any],
        status: str,
        duration_seconds: Optional[float] = None,
        notes: Optional[str] = None,
        test_id: Optional[str] = None,
        screenshot_paths: Optional[List[str]] = None,
        bug_screenshot_paths: Optional[List[str]] = None
    ) -> str:
        """
        Save a test result to database.
        
        Args:
            genre: Game genre tested
            algorithm: RL algorithm used
            metrics: Test metrics dictionary
            status: Final test status
            duration_seconds: Test duration in seconds
            notes: Optional notes about the test
            test_id: Optional test ID (for migration)
            
        Returns:
            Test ID (UUID string)
        """
        if test_id is None:
            test_id = str(uuid4())
        
        timestamp = datetime.utcnow().isoformat()
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Convert lists to JSON strings for storage
                screenshot_paths_json = json.dumps(screenshot_paths or [])
                bug_screenshot_paths_json = json.dumps(bug_screenshot_paths or [])
                
                cursor.execute("""
                    INSERT INTO test_history (
                        id, timestamp, genre, algorithm, status, duration_seconds,
                        coverage, crashes, fps, total_steps, reward_mean, notes,
                        screenshot_paths, bug_screenshot_paths
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    test_id,
                    timestamp,
                    genre,
                    algorithm,
                    status,
                    duration_seconds,
                    metrics.get("coverage", 0.0),
                    metrics.get("crashes", 0),
                    metrics.get("fps", 0.0),
                    metrics.get("total_steps", 0),
                    metrics.get("reward_mean", 0.0),
                    notes or "",
                    screenshot_paths_json,
                    bug_screenshot_paths_json
                ))
                conn.commit()
            
            logger.info(f"Saved test result: {test_id} ({genre}, {algorithm}, {status})")
            return test_id
            
        except Exception as e:
            logger.error(f"Error saving test result: {e}", exc_info=True)
            raise MetricsError(f"Failed to save test result: {e}")

    def get_test(self, test_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific test result by ID.
        
        Args:
            test_id: Test ID to retrieve
            
        Returns:
            Test entry dictionary or None if not found
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM test_history WHERE id = ?
                """, (test_id,))
                
                row = cursor.fetchone()
                if row:
                    return self._row_to_dict(row)
                return None
                
        except Exception as e:
            logger.error(f"Error getting test: {e}", exc_info=True)
            return None

    def list_tests(
        self,
        limit: Optional[int] = None,
        genre: Optional[str] = None,
        algorithm: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List test results with optional filtering.
        
        Args:
            limit: Maximum number of results to return
            genre: Filter by genre
            algorithm: Filter by algorithm
            status: Filter by status
            
        Returns:
            List of test entries (most recent first)
        """
        try:
            query = "SELECT * FROM test_history WHERE 1=1"
            params = []
            
            if genre:
                query += " AND LOWER(genre) = LOWER(?)"
                params.append(genre)
            
            if algorithm:
                query += " AND LOWER(algorithm) = LOWER(?)"
                params.append(algorithm)
            
            if status:
                query += " AND LOWER(status) = LOWER(?)"
                params.append(status)
            
            query += " ORDER BY timestamp DESC"
            
            if limit and limit > 0:
                query += " LIMIT ?"
                params.append(limit)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return [self._row_to_dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error listing tests: {e}", exc_info=True)
            return []

    def delete_test(self, test_id: str) -> bool:
        """
        Delete a test result by ID.
        
        Args:
            test_id: Test ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM test_history WHERE id = ?", (test_id,))
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Deleted test result: {test_id}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error deleting test: {e}", exc_info=True)
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get aggregated statistics from test history.
        
        Returns:
            Dictionary with statistics
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Total tests
                cursor.execute("SELECT COUNT(*) FROM test_history")
                total_tests = cursor.fetchone()[0]
                
                if total_tests == 0:
                    return {
                        "total_tests": 0,
                        "by_genre": {},
                        "by_algorithm": {},
                        "by_status": {},
                        "average_coverage": 0.0,
                        "average_crashes": 0.0,
                        "total_crashes": 0
                    }
                
                # Count by genre
                cursor.execute("""
                    SELECT genre, COUNT(*) as count 
                    FROM test_history 
                    GROUP BY genre
                """)
                by_genre = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Count by algorithm
                cursor.execute("""
                    SELECT algorithm, COUNT(*) as count 
                    FROM test_history 
                    GROUP BY algorithm
                """)
                by_algorithm = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Count by status
                cursor.execute("""
                    SELECT status, COUNT(*) as count 
                    FROM test_history 
                    GROUP BY status
                """)
                by_status = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Average metrics
                cursor.execute("""
                    SELECT 
                        AVG(coverage) as avg_coverage,
                        AVG(crashes) as avg_crashes,
                        SUM(crashes) as total_crashes
                    FROM test_history
                    WHERE coverage IS NOT NULL OR crashes IS NOT NULL
                """)
                metrics_row = cursor.fetchone()
                
                avg_coverage = metrics_row[0] if metrics_row[0] is not None else 0.0
                avg_crashes = metrics_row[1] if metrics_row[1] is not None else 0.0
                total_crashes = metrics_row[2] if metrics_row[2] is not None else 0
                
                return {
                    "total_tests": total_tests,
                    "by_genre": by_genre,
                    "by_algorithm": by_algorithm,
                    "by_status": by_status,
                    "average_coverage": round(avg_coverage, 2),
                    "average_crashes": round(avg_crashes, 2),
                    "total_crashes": total_crashes
                }
                
        except Exception as e:
            logger.error(f"Error getting statistics: {e}", exc_info=True)
            return {
                "total_tests": 0,
                "by_genre": {},
                "by_algorithm": {},
                "by_status": {},
                "average_coverage": 0.0,
                "average_crashes": 0.0,
                "total_crashes": 0
            }

    def clear_history(self) -> int:
        """
        Clear all test history.
        
        Returns:
            Number of entries deleted
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM test_history")
                count = cursor.fetchone()[0]
                
                cursor.execute("DELETE FROM test_history")
                conn.commit()
                
                logger.info(f"Cleared {count} test history entries")
                return count
                
        except Exception as e:
            logger.error(f"Error clearing history: {e}", exc_info=True)
            return 0

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert a database row to dictionary format."""
        # Parse screenshot paths from JSON
        screenshot_paths = []
        bug_screenshot_paths = []
        try:
            if row.get("screenshot_paths"):
                screenshot_paths = json.loads(row["screenshot_paths"])
            if row.get("bug_screenshot_paths"):
                bug_screenshot_paths = json.loads(row["bug_screenshot_paths"])
        except (json.JSONDecodeError, TypeError):
            pass
        
        return {
            "id": row["id"],
            "timestamp": row["timestamp"],
            "genre": row["genre"],
            "algorithm": row["algorithm"],
            "status": row["status"],
            "duration_seconds": row["duration_seconds"],
            "metrics": {
                "coverage": row["coverage"],
                "crashes": row["crashes"],
                "fps": row["fps"],
                "total_steps": row["total_steps"],
                "reward_mean": row["reward_mean"]
            },
            "notes": row["notes"],
            "screenshot_paths": screenshot_paths,
            "bug_screenshot_paths": bug_screenshot_paths
        }


# Global Instance (singleton)
test_history_manager = TestHistoryManager()
