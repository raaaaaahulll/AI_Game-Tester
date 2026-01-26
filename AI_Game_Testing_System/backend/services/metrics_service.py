"""
Metrics collector for tracking game testing metrics.

Thread-safe singleton that collects and serves metrics for the testing system.
"""
import json
import threading
from typing import Any, Dict, Optional
from pathlib import Path

from config.settings import settings
from utils.logging import get_logger
from utils.exceptions import MetricsError

logger = get_logger(__name__)


class MetricsCollector:
    """
    Thread-safe Singleton to collect and serve metrics.
    
    Provides centralized metrics storage and retrieval for the testing system.
    """
    _instance: Optional['MetricsCollector'] = None
    _lock = threading.Lock()

    def __new__(cls):
        """Create singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MetricsCollector, cls).__new__(cls)
                    cls._instance._initialize_metrics()
        return cls._instance

    def _initialize_metrics(self) -> None:
        """Initialize default metrics."""
        self.metrics: Dict[str, Any] = {
            "coverage": 0.0,
            "crashes": 0,
            "fps": 0.0,
            "current_algorithm": "None",
            "status": "Idle",
            "total_steps": 0,
            "reward_mean": 0.0,
            "window_focused": False
        }
        self._lock = threading.Lock()

    def update(self, key: str, value: Any) -> None:
        """
        Update a metric value.
        
        Args:
            key: Metric key
            value: Metric value
        """
        with self._lock:
            self.metrics[key] = value
            logger.debug(f"Updated metric: {key} = {value}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a specific metric value.
        
        Args:
            key: Metric key
            default: Default value if key doesn't exist
            
        Returns:
            Metric value or default
        """
        with self._lock:
            return self.metrics.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        """
        Get all metrics.
        
        Returns:
            Copy of all metrics dictionary
            
        Raises:
            MetricsError: If metrics cannot be retrieved
        """
        try:
            with self._lock:
                return self.metrics.copy()
        except Exception as e:
            logger.error(f"Error retrieving metrics: {e}", exc_info=True)
            raise MetricsError(f"Failed to retrieve metrics: {e}")

    def reset(self) -> None:
        """Reset all metrics to default values."""
        with self._lock:
            self._initialize_metrics()
            logger.info("Metrics reset to default values")

    def save_to_disk(self) -> None:
        """
        Save metrics to disk.
        
        Raises:
            MetricsError: If metrics cannot be saved
        """
        try:
            with self._lock:
                metrics_file = settings.METRICS_FILE
                metrics_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(metrics_file, 'w', encoding='utf-8') as f:
                    json.dump(self.metrics, f, indent=4, ensure_ascii=False)
                
                logger.debug(f"Metrics saved to {metrics_file}")
        except Exception as e:
            logger.error(f"Error saving metrics to disk: {e}", exc_info=True)
            raise MetricsError(f"Failed to save metrics: {e}")

    def load_from_disk(self) -> None:
        """
        Load metrics from disk.
        
        Raises:
            MetricsError: If metrics cannot be loaded
        """
        try:
            metrics_file = settings.METRICS_FILE
            if not metrics_file.exists():
                logger.warning(f"Metrics file not found: {metrics_file}")
                return
            
            with open(metrics_file, 'r', encoding='utf-8') as f:
                loaded_metrics = json.load(f)
            
            with self._lock:
                self.metrics.update(loaded_metrics)
            
            logger.info(f"Metrics loaded from {metrics_file}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in metrics file: {e}", exc_info=True)
            raise MetricsError(f"Invalid metrics file format: {e}")
        except Exception as e:
            logger.error(f"Error loading metrics from disk: {e}", exc_info=True)
            raise MetricsError(f"Failed to load metrics: {e}")


# Global Instance (singleton)
metrics_collector = MetricsCollector()

