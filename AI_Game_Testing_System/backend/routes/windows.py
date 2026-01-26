"""
Windows detection API routes.

Provides endpoints for detecting active windows and checking window focus.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException

from services.windows_service import windows_service
from utils.logging import get_logger

logger = get_logger(__name__)

windows_router = APIRouter(tags=["Windows"])


@windows_router.get(
    "/windows",
    summary="Get active windows",
    description="Retrieve list of all currently active windows/processes.",
    response_model=List[Dict[str, Any]]
)
async def get_active_windows() -> List[Dict[str, Any]]:
    """
    Get list of active windows/processes.
    
    Returns:
        List of active windows with title, process name, pid, and hwnd
    """
    try:
        windows = windows_service.get_active_windows()
        return windows
    except Exception as e:
        logger.error(f"Error getting active windows: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve active windows")


@windows_router.get(
    "/windows/{hwnd}/focused",
    summary="Check if window is focused",
    description="Check if a specific window is currently focused (foreground).",
    response_model=Dict[str, Any]
)
async def check_window_focused(hwnd: int) -> Dict[str, Any]:
    """
    Check if a window is currently focused.
    
    Args:
        hwnd: Window handle ID
        
    Returns:
        Dictionary with focused status
    """
    try:
        is_focused = windows_service.is_window_focused(hwnd)
        return {
            "hwnd": hwnd,
            "focused": is_focused
        }
    except Exception as e:
        logger.error(f"Error checking window focus: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to check window focus")

