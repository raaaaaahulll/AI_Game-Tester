"""
Pytest configuration and fixtures for backend tests.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil
from pathlib import Path

from app import app
from services.metrics_service import metrics_collector
from services.history_service import test_history_manager
from controllers.rl_controller import rl_controller


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def temp_logs_dir():
    """Create a temporary logs directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_metrics_collector():
    """Mock metrics collector with default values."""
    with patch.object(metrics_collector, 'get_all') as mock_get_all:
        mock_get_all.return_value = {
            "coverage": 100.0,
            "crashes": 0,
            "fps": 60.0,
            "current_algorithm": "PPO",
            "status": "Idle",
            "total_steps": 0,
            "reward_mean": 0.0
        }
        yield mock_get_all


@pytest.fixture
def mock_rl_controller():
    """Mock RL controller to prevent actual test execution."""
    with patch.object(rl_controller, 'start_test') as mock_start, \
         patch.object(rl_controller, 'stop_test') as mock_stop, \
         patch.object(rl_controller, 'is_running') as mock_running:
        
        mock_start.return_value = (True, "Test started")
        mock_stop.return_value = (True, "Test stopped")
        mock_running.return_value = False
        
        yield {
            'start': mock_start,
            'stop': mock_stop,
            'is_running': mock_running
        }


@pytest.fixture
def reset_metrics():
    """Reset metrics to default values before each test."""
    metrics_collector.reset()
    yield
    metrics_collector.reset()


@pytest.fixture
def clear_history():
    """Clear test history before and after each test."""
    test_history_manager.clear_history()
    yield
    test_history_manager.clear_history()

