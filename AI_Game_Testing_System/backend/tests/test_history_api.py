"""
Tests for test history API endpoints.
"""
import pytest
from fastapi import status
from services.history_service import test_history_manager


class TestListHistory:
    """Tests for list history endpoint."""
    
    def test_list_history_empty(self, client, clear_history):
        """Test listing history when empty."""
        response = client.get("/api/history")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "tests" in data
        assert "total" in data
        assert data["total"] == 0
        assert len(data["tests"]) == 0
    
    def test_list_history_with_data(self, client, clear_history):
        """Test listing history with test data."""
        # Create a test entry
        test_id = test_history_manager.save_test_result(
            genre="platformer",
            algorithm="DQN",
            metrics={"coverage": 100.0, "crashes": 0, "fps": 60.0, "total_steps": 1000, "reward_mean": 0.5},
            status="Completed"
        )
        
        response = client.get("/api/history")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert len(data["tests"]) == 1
        assert data["tests"][0]["id"] == test_id
    
    def test_list_history_with_limit(self, client, clear_history):
        """Test listing history with limit parameter."""
        # Create multiple test entries
        for i in range(5):
            test_history_manager.save_test_result(
                genre="platformer",
                algorithm="DQN",
                metrics={"coverage": 100.0 + i, "crashes": 0, "fps": 60.0, "total_steps": 1000, "reward_mean": 0.5},
                status="Completed"
            )
        
        response = client.get("/api/history?limit=3")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 5
        assert len(data["tests"]) == 3
    
    def test_list_history_filter_by_genre(self, client, clear_history):
        """Test filtering history by genre."""
        # Create tests with different genres
        test_history_manager.save_test_result(
            genre="platformer",
            algorithm="DQN",
            metrics={"coverage": 100.0, "crashes": 0, "fps": 60.0, "total_steps": 1000, "reward_mean": 0.5},
            status="Completed"
        )
        test_history_manager.save_test_result(
            genre="fps",
            algorithm="PPO",
            metrics={"coverage": 200.0, "crashes": 1, "fps": 60.0, "total_steps": 2000, "reward_mean": 0.6},
            status="Completed"
        )
        
        response = client.get("/api/history?genre=platformer")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["tests"][0]["genre"] == "platformer"
    
    def test_list_history_filter_by_algorithm(self, client, clear_history):
        """Test filtering history by algorithm."""
        test_history_manager.save_test_result(
            genre="platformer",
            algorithm="DQN",
            metrics={"coverage": 100.0, "crashes": 0, "fps": 60.0, "total_steps": 1000, "reward_mean": 0.5},
            status="Completed"
        )
        test_history_manager.save_test_result(
            genre="fps",
            algorithm="PPO",
            metrics={"coverage": 200.0, "crashes": 1, "fps": 60.0, "total_steps": 2000, "reward_mean": 0.6},
            status="Completed"
        )
        
        response = client.get("/api/history?algorithm=PPO")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["tests"][0]["algorithm"] == "PPO"
    
    def test_list_history_filter_by_status(self, client, clear_history):
        """Test filtering history by status."""
        test_history_manager.save_test_result(
            genre="platformer",
            algorithm="DQN",
            metrics={"coverage": 100.0, "crashes": 0, "fps": 60.0, "total_steps": 1000, "reward_mean": 0.5},
            status="Completed"
        )
        test_history_manager.save_test_result(
            genre="fps",
            algorithm="PPO",
            metrics={"coverage": 200.0, "crashes": 1, "fps": 60.0, "total_steps": 2000, "reward_mean": 0.6},
            status="Error"
        )
        
        response = client.get("/api/history?status=Completed")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["tests"][0]["status"] == "Completed"


class TestGetTest:
    """Tests for get test endpoint."""
    
    def test_get_test_success(self, client, clear_history):
        """Test getting a specific test."""
        test_id = test_history_manager.save_test_result(
            genre="platformer",
            algorithm="DQN",
            metrics={"coverage": 100.0, "crashes": 0, "fps": 60.0, "total_steps": 1000, "reward_mean": 0.5},
            status="Completed"
        )
        
        response = client.get(f"/api/history/{test_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_id
        assert data["genre"] == "platformer"
        assert data["algorithm"] == "DQN"
        assert data["status"] == "Completed"
        assert "timestamp" in data
        assert "metrics" in data
    
    def test_get_test_not_found(self, client, clear_history):
        """Test getting a non-existent test."""
        response = client.get("/api/history/non-existent-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()


class TestStatistics:
    """Tests for statistics endpoint."""
    
    def test_get_statistics_empty(self, client, clear_history):
        """Test statistics when no tests exist."""
        response = client.get("/api/history/statistics")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_tests"] == 0
        assert data["average_coverage"] == 0.0
        assert data["average_crashes"] == 0.0
        assert data["total_crashes"] == 0
    
    def test_get_statistics_with_data(self, client, clear_history):
        """Test statistics with test data."""
        # Create multiple tests
        test_history_manager.save_test_result(
            genre="platformer",
            algorithm="DQN",
            metrics={"coverage": 100.0, "crashes": 2, "fps": 60.0, "total_steps": 1000, "reward_mean": 0.5},
            status="Completed"
        )
        test_history_manager.save_test_result(
            genre="fps",
            algorithm="PPO",
            metrics={"coverage": 200.0, "crashes": 1, "fps": 60.0, "total_steps": 2000, "reward_mean": 0.6},
            status="Completed"
        )
        
        response = client.get("/api/history/statistics")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_tests"] == 2
        assert data["average_coverage"] == 150.0
        assert data["average_crashes"] == 1.5
        assert data["total_crashes"] == 3
        assert "platformer" in data["by_genre"]
        assert "fps" in data["by_genre"]
        assert "DQN" in data["by_algorithm"]
        assert "PPO" in data["by_algorithm"]


class TestDeleteTest:
    """Tests for delete test endpoint."""
    
    def test_delete_test_success(self, client, clear_history):
        """Test deleting a specific test."""
        test_id = test_history_manager.save_test_result(
            genre="platformer",
            algorithm="DQN",
            metrics={"coverage": 100.0, "crashes": 0, "fps": 60.0, "total_steps": 1000, "reward_mean": 0.5},
            status="Completed"
        )
        
        response = client.delete(f"/api/history/{test_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "deleted" in data["message"].lower()
        
        # Verify test is deleted
        get_response = client.get(f"/api/history/{test_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_test_not_found(self, client, clear_history):
        """Test deleting a non-existent test."""
        response = client.delete("/api/history/non-existent-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestClearHistory:
    """Tests for clear history endpoint."""
    
    def test_clear_history_success(self, client, clear_history):
        """Test clearing all history."""
        # Create some tests
        for i in range(3):
            test_history_manager.save_test_result(
                genre="platformer",
                algorithm="DQN",
                metrics={"coverage": 100.0 + i, "crashes": 0, "fps": 60.0, "total_steps": 1000, "reward_mean": 0.5},
                status="Completed"
            )
        
        response = client.delete("/api/history")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "3" in data["message"] or "cleared" in data["message"].lower()
        
        # Verify history is empty
        list_response = client.get("/api/history")
        assert list_response.json()["total"] == 0

