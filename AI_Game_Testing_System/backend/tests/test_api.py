"""
Tests for main API endpoints (start-test, stop-test, metrics, status).
"""
import pytest
from fastapi import status


class TestHealthEndpoints:
    """Tests for health check endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root health check endpoint."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "environment" in data
        assert data["version"] == "1.0.0"
    
    def test_health_endpoint(self, client, mock_metrics_collector):
        """Test detailed health check endpoint."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "metrics_available" in data
        assert "current_status" in data


class TestStartTest:
    """Tests for start-test endpoint."""
    
    def test_start_test_success(self, client, mock_rl_controller):
        """Test successful test start."""
        response = client.post(
            "/api/start-test",
            json={"genre": "platformer"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert "message" in data
        mock_rl_controller['start'].assert_called_once()
    
    def test_start_test_invalid_genre(self, client, mock_rl_controller):
        """Test start test with invalid genre."""
        response = client.post(
            "/api/start-test",
            json={"genre": "invalid_genre"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_start_test_missing_genre(self, client):
        """Test start test without genre field."""
        response = client.post(
            "/api/start-test",
            json={}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_start_test_all_valid_genres(self, client, mock_rl_controller):
        """Test start test with all valid genres."""
        valid_genres = ["platformer", "fps", "racing", "rpg"]
        for genre in valid_genres:
            response = client.post(
                "/api/start-test",
                json={"genre": genre}
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["status"] == "success"
    
    def test_start_test_already_running(self, client, mock_rl_controller):
        """Test start test when already running."""
        mock_rl_controller['start'].return_value = (False, "Test already running")
        response = client.post(
            "/api/start-test",
            json={"genre": "platformer"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already running" in response.json()["detail"].lower()


class TestStopTest:
    """Tests for stop-test endpoint."""
    
    def test_stop_test_success(self, client, mock_rl_controller):
        """Test successful test stop."""
        mock_rl_controller['is_running'].return_value = True
        response = client.post("/api/stop-test")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert "message" in data
        mock_rl_controller['stop'].assert_called_once()
    
    def test_stop_test_not_running(self, client, mock_rl_controller):
        """Test stop test when no test is running."""
        mock_rl_controller['stop'].return_value = (False, "Not running")
        response = client.post("/api/stop-test")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "not running" in response.json()["detail"].lower()


class TestMetrics:
    """Tests for metrics endpoint."""
    
    def test_get_metrics_success(self, client, mock_metrics_collector):
        """Test successful metrics retrieval."""
        response = client.get("/api/metrics")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "coverage" in data
        assert "crashes" in data
        assert "fps" in data
        assert "current_algorithm" in data
        assert "status" in data
        assert "total_steps" in data
        assert "reward_mean" in data
    
    def test_get_metrics_structure(self, client, mock_metrics_collector):
        """Test metrics response structure."""
        response = client.get("/api/metrics")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check types
        assert isinstance(data["coverage"], (int, float))
        assert isinstance(data["crashes"], int)
        assert isinstance(data["fps"], (int, float))
        assert isinstance(data["total_steps"], int)
        assert isinstance(data["reward_mean"], (int, float))
        assert isinstance(data["status"], str)
        assert isinstance(data["current_algorithm"], str)


class TestStatus:
    """Tests for status endpoint."""
    
    def test_get_status_success(self, client, mock_metrics_collector):
        """Test successful status retrieval."""
        response = client.get("/api/status")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert isinstance(data["status"], str)
    
    def test_get_status_value(self, client, mock_metrics_collector):
        """Test status value matches metrics."""
        response = client.get("/api/status")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Status should be a valid status value
        assert data["status"] in ["Idle", "Training", "Completed", "Stopped", "Error", "Unknown"]

