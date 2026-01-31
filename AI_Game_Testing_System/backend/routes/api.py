"""
Main API routes for the AI Game Testing System.

All endpoints maintain backward compatibility with the existing API contract.
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException

from controllers.rl_controller import rl_controller
from services.metrics_service import metrics_collector
from models.schemas import StartRequest, SuccessResponse, StatusResponse
from utils.exceptions import (
    TestingSessionAlreadyRunningError,
    TestingSessionNotRunningError,
    InvalidGenreError,
    MetricsError,
)
from utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/start-test",
    response_model=SuccessResponse,
    summary="Start game testing session",
    description="Initiates a new game testing session with the specified game genre.",
    responses={
        200: {
            "description": "Testing session started successfully",
            "model": SuccessResponse
        },
        400: {
            "description": "Bad request - Invalid genre or testing already in progress"
        }
    }
)
async def start_test(request: StartRequest) -> Dict[str, str]:
    """
    Start a game testing session.
    
    Args:
        request: Start request containing the game genre and optional window_hwnd
        
    Returns:
        Success response with status and message
        
    Raises:
        HTTPException: If test cannot be started (already running or invalid genre)
    """
    logger.info(
        f"Starting test for genre: {request.genre}",
        extra={"extra_fields": {"genre": request.genre, "window_hwnd": getattr(request, 'window_hwnd', None)}}
    )
    
    try:
        window_hwnd = request.window_hwnd
        success, msg = rl_controller.start_test(request.genre, window_hwnd=window_hwnd)
        if not success:
            logger.warning(f"Failed to start test: {msg}")
            raise HTTPException(status_code=400, detail=msg)
        
        logger.info(f"Test started successfully: {msg}")
        return {"status": "success", "message": msg}
        
    except InvalidGenreError as e:
        logger.warning(f"Invalid genre: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    except TestingSessionAlreadyRunningError as e:
        logger.warning(f"Test already running: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error starting test: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/stop-test",
    response_model=SuccessResponse,
    summary="Stop game testing session",
    description="Stops the currently running game testing session.",
    responses={
        200: {
            "description": "Testing session stopped successfully",
            "model": SuccessResponse
        },
        400: {
            "description": "Bad request - No active testing session"
        }
    }
)
async def stop_test() -> Dict[str, str]:
    """
    Stop the current game testing session.
    
    Returns:
        Success response with status and message
        
    Raises:
        HTTPException: If no test is currently running
    """
    logger.info("Stopping test session")
    
    try:
        success, msg = rl_controller.stop_test()
        if success:
            logger.info(f"Test stopped successfully: {msg}")
            return {"status": "success", "message": msg}
        else:
            # Even if stop_test returns False, we still return success
            # because the stop signal was sent and cleanup was attempted
            logger.warning(f"Stop request sent but cleanup had issues: {msg}")
            return {"status": "success", "message": f"Stop signal sent. {msg}"}
        
    except TestingSessionNotRunningError as e:
        logger.warning(f"No test running: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error stopping test: {e}", exc_info=True)
        # Don't raise 500 - just return success with warning
        return {"status": "success", "message": "Stop signal sent. Check logs for details."}


@router.get(
    "/metrics",
    summary="Get all testing metrics",
    description="Retrieves comprehensive metrics for the current testing session.",
    responses={
        200: {
            "description": "Metrics retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "coverage": 1250.5,
                        "crashes": 3,
                        "fps": 60.0,
                        "current_algorithm": "PPO",
                        "status": "Training",
                        "total_steps": 15420,
                        "reward_mean": 0.85
                    }
                }
            }
        },
        500: {
            "description": "Internal server error"
        }
    }
)
async def get_metrics() -> Dict[str, Any]:
    """
    Get all current testing metrics.
    
    Returns:
        Dictionary containing all metrics (coverage, crashes, fps, etc.)
        
    Raises:
        HTTPException: If metrics cannot be retrieved
    """
    try:
        metrics = metrics_collector.get_all()
        return metrics
    except Exception as e:
        logger.error(f"Error retrieving metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")


@router.get(
    "/status",
    response_model=StatusResponse,
    summary="Get system status",
    description="Retrieves only the current status of the testing system.",
    responses={
        200: {
            "description": "Status retrieved successfully",
            "model": StatusResponse
        },
        500: {
            "description": "Internal server error"
        }
    }
)
async def get_status() -> Dict[str, str]:
    """
    Get the current system status.
    
    Returns:
        Dictionary with current status
        
    Raises:
        HTTPException: If status cannot be retrieved
    """
    try:
        metrics = metrics_collector.get_all()
        status = metrics.get("status", "Unknown")
        return {"status": status}
    except Exception as e:
        logger.error(f"Error retrieving status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve status")


@router.post(
    "/reset-status",
    response_model=SuccessResponse,
    summary="Reset system status",
    description="Resets the system status to Idle. Useful for clearing error states.",
    responses={
        200: {
            "description": "Status reset successfully",
            "model": SuccessResponse
        },
        400: {
            "description": "Cannot reset status while test is running"
        }
    }
)
async def reset_status() -> Dict[str, str]:
    """
    Reset the system status to Idle.
    
    This is useful for clearing error states when no test is running.
    
    Returns:
        Success response
        
    Raises:
        HTTPException: If test is currently running or reset fails
    """
    try:
        # Check if test is running
        if rl_controller.is_running():
            raise HTTPException(
                status_code=400,
                detail="Cannot reset status while test is running. Stop the test first."
            )
        
        # Reset status to Idle
        metrics_collector.update("status", "Idle")
        # Clear error log if exists
        all_metrics = metrics_collector.get_all()
        if "error_log" in all_metrics:
            metrics_collector.update("error_log", "")
        
        logger.info("Status reset to Idle")
        return {"status": "success", "message": "Status reset to Idle"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to reset status")

