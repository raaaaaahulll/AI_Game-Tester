"""
Test History Manager for storing and retrieving past test run results.

Provides persistent storage of test results with timestamps, metrics, and metadata.
"""
import json
import threading
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
    
    Stores test results in JSON format with unique IDs and timestamps.
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
        """Initialize the history manager."""
        self.history_file = settings.LOGS_DIR / "test_history.json"
        self._lock = threading.Lock()
        self._ensure_history_file()

    def _ensure_history_file(self) -> None:
        """Ensure history file exists with empty list."""
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            if not self.history_file.exists():
                with open(self.history_file, 'w', encoding='utf-8') as f:
                    json.dump([], f, indent=2, ensure_ascii=False)
                logger.info(f"Created test history file: {self.history_file}")
        except Exception as e:
            logger.error(f"Error ensuring history file exists: {e}", exc_info=True)

    def _load_history(self) -> List[Dict[str, Any]]:
        """
        Load test history from disk.
        
        Returns:
            List of test history entries
        """
        try:
            if not self.history_file.exists():
                return []
            
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            if not isinstance(history, list):
                logger.warning("History file corrupted, resetting")
                return []
            
            return history
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in history file: {e}", exc_info=True)
            return []
        except Exception as e:
            logger.error(f"Error loading history: {e}", exc_info=True)
            return []

    def _save_history(self, history: List[Dict[str, Any]]) -> None:
        """
        Save test history to disk.
        
        Args:
            history: List of test history entries
        """
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved {len(history)} test history entries")
        except Exception as e:
            logger.error(f"Error saving history: {e}", exc_info=True)
            raise MetricsError(f"Failed to save test history: {e}")

    def save_test_result(
        self,
        genre: str,
        algorithm: str,
        metrics: Dict[str, Any],
        status: str,
        duration_seconds: Optional[float] = None,
        notes: Optional[str] = None
    ) -> str:
        """
        Save a test result to history.
        
        Args:
            genre: Game genre tested
            algorithm: RL algorithm used
            metrics: Test metrics dictionary
            status: Final test status
            duration_seconds: Test duration in seconds
            notes: Optional notes about the test
            
        Returns:
            Test ID (UUID string)
        """
        test_id = str(uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        test_entry = {
            "id": test_id,
            "timestamp": timestamp,
            "genre": genre,
            "algorithm": algorithm,
            "status": status,
            "duration_seconds": duration_seconds,
            "metrics": {
                "coverage": metrics.get("coverage", 0.0),
                "crashes": metrics.get("crashes", 0),
                "fps": metrics.get("fps", 0.0),
                "total_steps": metrics.get("total_steps", 0),
                "reward_mean": metrics.get("reward_mean", 0.0),
            },
            "notes": notes or ""
        }
        
        with self._lock:
            history = self._load_history()
            history.insert(0, test_entry)  # Add to beginning (most recent first)
            self._save_history(history)
        
        logger.info(f"Saved test result: {test_id} ({genre}, {algorithm}, {status})")
        return test_id

    def get_test(self, test_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific test result by ID.
        
        Args:
            test_id: Test ID to retrieve
            
        Returns:
            Test entry dictionary or None if not found
        """
        with self._lock:
            history = self._load_history()
            for entry in history:
                if entry.get("id") == test_id:
                    return entry
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
        with self._lock:
            history = self._load_history()
            
            # Apply filters
            filtered = history
            if genre:
                filtered = [e for e in filtered if e.get("genre", "").lower() == genre.lower()]
            if algorithm:
                filtered = [e for e in filtered if e.get("algorithm", "").lower() == algorithm.lower()]
            if status:
                filtered = [e for e in filtered if e.get("status", "").lower() == status.lower()]
            
            # Apply limit
            if limit and limit > 0:
                filtered = filtered[:limit]
            
            return filtered

    def delete_test(self, test_id: str) -> bool:
        """
        Delete a test result by ID.
        
        Args:
            test_id: Test ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            history = self._load_history()
            original_count = len(history)
            history = [e for e in history if e.get("id") != test_id]
            
            if len(history) < original_count:
                self._save_history(history)
                logger.info(f"Deleted test result: {test_id}")
                return True
            
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get aggregated statistics from test history.
        
        Returns:
            Dictionary with statistics
        """
        with self._lock:
            history = self._load_history()
            
            if not history:
                return {
                    "total_tests": 0,
                    "by_genre": {},
                    "by_algorithm": {},
                    "by_status": {},
                    "average_coverage": 0.0,
                    "average_crashes": 0.0,
                    "total_crashes": 0
                }
            
            # Calculate statistics
            stats = {
                "total_tests": len(history),
                "by_genre": {},
                "by_algorithm": {},
                "by_status": {},
                "total_coverage": 0.0,
                "total_crashes": 0,
                "tests_with_metrics": 0
            }
            
            for entry in history:
                # Count by genre
                genre = entry.get("genre", "Unknown")
                stats["by_genre"][genre] = stats["by_genre"].get(genre, 0) + 1
                
                # Count by algorithm
                algorithm = entry.get("algorithm", "Unknown")
                stats["by_algorithm"][algorithm] = stats["by_algorithm"].get(algorithm, 0) + 1
                
                # Count by status
                status = entry.get("status", "Unknown")
                stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
                
                # Aggregate metrics
                metrics = entry.get("metrics", {})
                if metrics:
                    stats["tests_with_metrics"] += 1
                    stats["total_coverage"] += metrics.get("coverage", 0.0)
                    stats["total_crashes"] += metrics.get("crashes", 0)
            
            # Calculate averages
            if stats["tests_with_metrics"] > 0:
                stats["average_coverage"] = stats["total_coverage"] / stats["tests_with_metrics"]
                stats["average_crashes"] = stats["total_crashes"] / stats["tests_with_metrics"]
            else:
                stats["average_coverage"] = 0.0
                stats["average_crashes"] = 0.0
            
            # Remove temporary fields
            del stats["total_coverage"]
            del stats["tests_with_metrics"]
            stats["total_crashes"] = stats["total_crashes"]
            
            return stats

    def clear_history(self) -> int:
        """
        Clear all test history.
        
        Returns:
            Number of entries deleted
        """
        with self._lock:
            history = self._load_history()
            count = len(history)
            self._save_history([])
            logger.info(f"Cleared {count} test history entries")
            return count


# Global Instance (singleton)
test_history_manager = TestHistoryManager()

