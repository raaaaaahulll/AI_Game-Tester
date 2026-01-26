"""
Test History API endpoints.

Provides REST API for managing test history and analytics.
All endpoints are separate from the main API to maintain clean separation.
"""
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.analytics.test_history import test_history_manager
from backend.core.logging_config import get_logger

logger = get_logger(__name__)

# Create separate router for history endpoints
history_router = APIRouter(tags=["Test History"])


# Request/Response Models
class TestResultResponse(BaseModel):
    """Test result response model."""
    id: str = Field(..., description="Unique test ID")
    timestamp: str = Field(..., description="Test timestamp (ISO format)")
    genre: str = Field(..., description="Game genre tested")
    algorithm: str = Field(..., description="RL algorithm used")
    status: str = Field(..., description="Test status")
    duration_seconds: Optional[float] = Field(None, description="Test duration in seconds")
    metrics: Dict[str, Any] = Field(..., description="Test metrics")
    notes: str = Field(default="", description="Optional notes")


class TestListResponse(BaseModel):
    """Test list response model."""
    tests: List[TestResultResponse] = Field(..., description="List of test results")
    total: int = Field(..., description="Total number of tests")


class StatisticsResponse(BaseModel):
    """Statistics response model."""
    total_tests: int = Field(..., description="Total number of tests")
    by_genre: Dict[str, int] = Field(..., description="Test count by genre")
    by_algorithm: Dict[str, int] = Field(..., description="Test count by algorithm")
    by_status: Dict[str, int] = Field(..., description="Test count by status")
    average_coverage: float = Field(..., description="Average coverage across all tests")
    average_crashes: float = Field(..., description="Average crashes across all tests")
    total_crashes: int = Field(..., description="Total crashes found")


class DeleteResponse(BaseModel):
    """Delete response model."""
    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Response message")


@history_router.get(
    "/history",
    response_model=TestListResponse,
    summary="List test history",
    description="Retrieve list of past test runs with optional filtering.",
    responses={
        200: {
            "description": "Test history retrieved successfully",
            "model": TestListResponse
        }
    }
)
async def list_tests(
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Maximum number of results"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    algorithm: Optional[str] = Query(None, description="Filter by algorithm"),
    status: Optional[str] = Query(None, description="Filter by status")
) -> Dict[str, Any]:
    """
    List test history with optional filtering.
    
    Args:
        limit: Maximum number of results to return (1-1000)
        genre: Filter by game genre
        algorithm: Filter by RL algorithm
        status: Filter by test status
        
    Returns:
        List of test results with total count
    """
    try:
        tests = test_history_manager.list_tests(
            limit=limit,
            genre=genre,
            algorithm=algorithm,
            status=status
        )
        
        # Get total count without limit
        all_tests = test_history_manager.list_tests(
            genre=genre,
            algorithm=algorithm,
            status=status
        )
        total = len(all_tests)
        
        return {
            "tests": tests,
            "total": total
        }
    except Exception as e:
        logger.error(f"Error listing tests: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve test history")


@history_router.get(
    "/history/{test_id}",
    response_model=TestResultResponse,
    summary="Get test details",
    description="Retrieve detailed information about a specific test run.",
    responses={
        200: {
            "description": "Test details retrieved successfully",
            "model": TestResultResponse
        },
        404: {
            "description": "Test not found"
        }
    }
)
async def get_test(test_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific test.
    
    Args:
        test_id: Unique test ID
        
    Returns:
        Test result details
        
    Raises:
        HTTPException: If test not found
    """
    try:
        test = test_history_manager.get_test(test_id)
        if not test:
            raise HTTPException(status_code=404, detail=f"Test with ID {test_id} not found")
        return test
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving test {test_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve test details")


@history_router.get(
    "/history/statistics",
    response_model=StatisticsResponse,
    summary="Get test statistics",
    description="Get aggregated statistics from all test runs.",
    responses={
        200: {
            "description": "Statistics retrieved successfully",
            "model": StatisticsResponse
        }
    }
)
async def get_statistics() -> Dict[str, Any]:
    """
    Get aggregated statistics from test history.
    
    Returns:
        Statistics including counts, averages, and distributions
    """
    try:
        stats = test_history_manager.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error retrieving statistics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")


@history_router.delete(
    "/history/{test_id}",
    response_model=DeleteResponse,
    summary="Delete test result",
    description="Delete a specific test result from history.",
    responses={
        200: {
            "description": "Test deleted successfully",
            "model": DeleteResponse
        },
        404: {
            "description": "Test not found"
        }
    }
)
async def delete_test(test_id: str) -> Dict[str, str]:
    """
    Delete a test result from history.
    
    Args:
        test_id: Unique test ID to delete
        
    Returns:
        Success response
        
    Raises:
        HTTPException: If test not found
    """
    try:
        success = test_history_manager.delete_test(test_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Test with ID {test_id} not found")
        
        return {
            "success": True,
            "message": f"Test {test_id} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting test {test_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete test")


@history_router.delete(
    "/history",
    response_model=DeleteResponse,
    summary="Clear all test history",
    description="Delete all test history entries.",
    responses={
        200: {
            "description": "History cleared successfully",
            "model": DeleteResponse
        }
    }
)
async def clear_history() -> Dict[str, Any]:
    """
    Clear all test history.
    
    Returns:
        Success response with count of deleted entries
    """
    try:
        count = test_history_manager.clear_history()
        return {
            "success": True,
            "message": f"Cleared {count} test history entries"
        }
    except Exception as e:
        logger.error(f"Error clearing history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to clear history")

