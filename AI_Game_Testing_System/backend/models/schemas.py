"""
Pydantic models and schemas for API requests and responses.
"""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, field_validator


# Valid genre values
VALID_GENRES = {"platformer", "fps", "racing", "rpg"}


class StartRequest(BaseModel):
    """Request model for starting a test session."""
    
    genre: str = Field(
        ...,
        description="Game genre to test",
        examples=["platformer", "fps", "racing", "rpg"]
    )
    
    window_hwnd: Optional[int] = Field(
        None,
        description="Optional window handle ID to track during testing"
    )
    
    @field_validator("genre")
    @classmethod
    def validate_genre(cls, v: str) -> str:
        """Validate genre value."""
        genre_lower = v.lower()
        if genre_lower not in VALID_GENRES:
            raise ValueError(
                f"Invalid genre '{v}'. Must be one of: {', '.join(VALID_GENRES)}"
            )
        return genre_lower


class SuccessResponse(BaseModel):
    """Standard success response model."""
    
    status: str = Field(default="success", description="Response status")
    message: str = Field(..., description="Human-readable message")


class StatusResponse(BaseModel):
    """Status response model."""
    
    status: str = Field(..., description="Current system status")


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

