"""
Tests for request validation and error handling.
"""
import pytest
from fastapi import status


class TestRequestValidation:
    """Tests for request validation."""
    
    def test_start_test_invalid_json(self, client):
        """Test start test with invalid JSON."""
        response = client.post(
            "/api/start-test",
            json={"invalid_field": "value"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_start_test_empty_body(self, client):
        """Test start test with empty body."""
        response = client.post("/api/start-test", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_start_test_wrong_type(self, client):
        """Test start test with wrong data type."""
        response = client.post(
            "/api/start-test",
            json={"genre": 123}
        )
        # Should still validate as string, but might fail genre validation
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_400_BAD_REQUEST]
    
    def test_history_limit_validation(self, client):
        """Test history limit parameter validation."""
        # Test negative limit
        response = client.get("/api/history?limit=-1")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test zero limit
        response = client.get("/api/history?limit=0")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test too large limit
        response = client.get("/api/history?limit=1001")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_404_on_invalid_endpoint(self, client):
        """Test 404 for non-existent endpoint."""
        response = client.get("/api/non-existent")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_method_not_allowed(self, client):
        """Test method not allowed errors."""
        # GET on POST endpoint
        response = client.get("/api/start-test")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        
        # POST on GET endpoint
        response = client.post("/api/metrics")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

