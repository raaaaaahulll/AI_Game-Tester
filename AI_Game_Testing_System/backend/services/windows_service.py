"""
Windows detection service for OS-level window and process detection.

Provides functionality to:
- Detect active windows/processes
- Check if a window is focused (foreground)
- Track window handles
"""
import platform
from typing import List, Dict, Any, Optional

import psutil

from utils.logging import get_logger

logger = get_logger(__name__)


class WindowsService:
    """
    Service for detecting and managing windows/processes.
    """
    
    def __init__(self):
        """Initialize the windows service."""
        self._win32gui = None
        self._win32process = None
        self._win32con = None
        
        # Try to import Windows-specific modules
        if platform.system() == "Windows":
            try:
                import win32gui
                import win32process
                import win32con
                self._win32gui = win32gui
                self._win32process = win32process
                self._win32con = win32con
                logger.info("Windows API modules loaded successfully")
            except ImportError:
                logger.warning("pywin32 not installed, using basic process detection")
    
    def get_active_windows(self) -> List[Dict[str, Any]]:
        """
        Get list of all active windows/processes.
        
        Returns:
            List of window information with title, process_name, pid, hwnd
        """
        windows = []
        seen_pids = set()  # Track seen PIDs to avoid duplicates
        
        try:
            if platform.system() == "Windows" and self._win32gui:
                # Use Windows API for better detection
                def enum_windows_callback(hwnd, windows_list):
                    """Callback for enumerating windows."""
                    try:
                        # Check if window exists and is valid
                        if not self._win32gui.IsWindow(hwnd):
                            return True
                        
                        # Check if it's a top-level window (has no parent or parent is desktop)
                        parent = self._win32gui.GetParent(hwnd)
                        if parent != 0:
                            # Has a parent, skip child windows
                            return True
                        
                        # Only include visible windows OR minimized windows
                        # Exclude hidden/background windows
                        is_visible = self._win32gui.IsWindowVisible(hwnd)
                        is_minimized = self._win32gui.IsIconic(hwnd)
                        
                        # Skip if window is neither visible nor minimized
                        if not (is_visible or is_minimized):
                            return True
                        
                        window_title = self._win32gui.GetWindowText(hwnd)
                        
                        try:
                            _, pid = self._win32process.GetWindowThreadProcessId(hwnd)
                            
                            # Skip if we've already seen this PID (to avoid duplicates)
                            if pid in seen_pids:
                                return True
                            
                            # Try to get process info
                            try:
                                process = psutil.Process(pid)
                                exe_path = process.exe()
                                process_name = process.name()
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                # If we can't get process info, skip this window
                                return True
                            
                            # Use window title if available, otherwise use process name
                            display_title = window_title.strip() if window_title and window_title.strip() else process_name
                            
                            # Skip if we have neither title nor process name
                            if not display_title:
                                return True
                            
                            seen_pids.add(pid)
                            
                            windows_list.append({
                                "title": display_title,
                                "process_name": process_name,
                                "exe_path": exe_path,
                                "pid": pid,
                                "hwnd": hwnd
                            })
                        except (psutil.NoSuchProcess, psutil.AccessDenied, Exception) as e:
                            logger.debug(f"Skipping window {hwnd}: {e}")
                    except Exception as e:
                        logger.debug(f"Error processing window {hwnd}: {e}")
                    return True
                
                self._win32gui.EnumWindows(enum_windows_callback, windows)
                
                # If no windows found with Windows API, fall through to psutil
                if len(windows) == 0:
                    logger.info("No windows found via Windows API, falling back to psutil")
            
            # Fallback: use psutil for all processes (if Windows API didn't find anything or not on Windows)
            if len(windows) == 0:
                logger.info("Using psutil fallback to get all processes")
                for proc in psutil.process_iter(['pid', 'name', 'exe']):
                    try:
                        proc_info = proc.info
                        pid = proc_info.get('pid')
                        
                        # Skip if already seen
                        if pid in seen_pids:
                            continue
                        seen_pids.add(pid)
                        
                        # Include processes with executables (filter out system processes for cleaner list)
                        exe_path = proc_info.get('exe', '')
                        if exe_path:
                            process_name = proc_info.get('name', 'Unknown')
                            
                            # Filter out common system processes to reduce clutter
                            system_processes = ['svchost.exe', 'dwm.exe', 'winlogon.exe', 'csrss.exe', 
                                              'lsass.exe', 'services.exe', 'smss.exe', 'System', 
                                              'Registry', 'conhost.exe', 'RuntimeBroker.exe']
                            
                            # Include all processes, but you can uncomment to filter:
                            # if process_name.lower() not in [p.lower() for p in system_processes]:
                            windows.append({
                                "title": process_name,
                                "process_name": process_name,
                                "exe_path": exe_path,
                                "pid": pid,
                                "hwnd": None  # Not available without Windows API
                            })
                    except (psutil.NoSuchProcess, psutil.AccessDenied, Exception) as e:
                        logger.debug(f"Skipping process: {e}")
                        
        except Exception as e:
            logger.error(f"Error getting active windows: {e}", exc_info=True)
        
        # Sort by title for better UX
        windows.sort(key=lambda x: x.get("title", "").lower())
        
        logger.info(f"Found {len(windows)} active windows/processes")
        return windows
    
    def is_window_focused(self, hwnd: Optional[int]) -> bool:
        """
        Check if a window is currently focused (foreground).
        
        Args:
            hwnd: Window handle ID (None if not available)
            
        Returns:
            True if window is focused, False otherwise
        """
        if hwnd is None:
            return False
        
        try:
            if platform.system() == "Windows" and self._win32gui:
                # Get the foreground window
                foreground_hwnd = self._win32gui.GetForegroundWindow()
                return foreground_hwnd == hwnd
            else:
                # Cannot determine focus without Windows API
                logger.debug("Cannot check window focus without Windows API")
                return False
        except Exception as e:
            logger.warning(f"Error checking window focus: {e}")
            return False


# Global instance
windows_service = WindowsService()

