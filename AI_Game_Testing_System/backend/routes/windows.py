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
        logger.info("API: Getting active windows")
        windows = windows_service.get_active_windows()
        logger.info(f"API: Returning {len(windows)} windows")
        
        if len(windows) == 0:
            logger.warning("API: No windows returned - check backend logs for details")
        
        return windows
    except Exception as e:
        logger.error(f"Error getting active windows: {e}", exc_info=True)
        # Return empty list instead of raising exception to prevent frontend errors
        logger.error(f"Returning empty list due to error: {e}")
        return []


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


@windows_router.post(
    "/windows/{hwnd}/focus",
    summary="Focus a window",
    description="Bring a window to foreground and focus it.",
    response_model=Dict[str, Any]
)
async def focus_window(hwnd: int) -> Dict[str, Any]:
    """
    Focus a window by bringing it to foreground.
    
    Args:
        hwnd: Window handle ID
        
    Returns:
        Dictionary with success status
    """
    try:
        success = windows_service.focus_window(hwnd)
        return {
            "hwnd": hwnd,
            "success": success
        }
    except Exception as e:
        logger.error(f"Error focusing window: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to focus window")


@windows_router.get(
    "/windows/diagnostic",
    summary="Get window detection diagnostic info",
    description="Get diagnostic information about window detection system.",
    response_model=Dict[str, Any]
)
async def get_diagnostic() -> Dict[str, Any]:
    """
    Get diagnostic information about window detection.
    
    Returns:
        Dictionary with diagnostic information
    """
    import platform
    diagnostic = {
        "platform": platform.system(),
        "pywin32_available": False,
        "windows_api_available": False,
        "psutil_available": False,
        "test_result": None
    }
    
    try:
        import psutil
        diagnostic["psutil_available"] = True
    except ImportError:
        diagnostic["psutil_available"] = False
    
    try:
        import win32gui
        diagnostic["pywin32_available"] = True
        diagnostic["windows_api_available"] = True
    except ImportError:
        diagnostic["pywin32_available"] = False
        diagnostic["windows_api_available"] = False
    
    # Try to get windows
    try:
        windows = windows_service.get_active_windows()
        diagnostic["test_result"] = {
            "success": True,
            "window_count": len(windows),
            "sample_windows": windows[:5] if windows else []
        }
    except Exception as e:
        diagnostic["test_result"] = {
            "success": False,
            "error": str(e),
            "window_count": 0
        }
    
    return diagnostic
