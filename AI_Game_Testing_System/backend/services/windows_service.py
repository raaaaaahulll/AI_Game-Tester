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
                logger.warning("For better window detection, install: pip install pywin32")
    
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
                        
                        # Check if it's a top-level window (has no parent)
                        parent = self._win32gui.GetParent(hwnd)
                        if parent != 0:
                            # Has a parent, skip child windows
                            return True
                        
                        # Check visibility - be more lenient
                        is_visible = self._win32gui.IsWindowVisible(hwnd)
                        is_minimized = self._win32gui.IsIconic(hwnd)
                        
                        # Include visible, minimized, or any window with a title
                        # This is more lenient to catch more windows
                        window_title = self._win32gui.GetWindowText(hwnd)
                        
                        # Skip completely invisible windows without titles
                        if not is_visible and not is_minimized and (not window_title or not window_title.strip()):
                            return True
                        
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
                            
                            # Skip only if we have absolutely no way to identify the window
                            if not display_title or display_title.strip() == '':
                                return True
                            
                            # Skip very small/system windows (likely not user-facing)
                            # Very lenient threshold - only skip tiny windows
                            try:
                                rect = self._win32gui.GetWindowRect(hwnd)
                                width = rect[2] - rect[0]
                                height = rect[3] - rect[1]
                                # Skip windows smaller than 30x30 pixels (very small)
                                if width < 30 or height < 30:
                                    return True
                            except:
                                pass  # If we can't get size, include it anyway
                            
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
                logger.info(f"Windows API found {len(windows)} windows")
                
                # If no windows found with Windows API, fall through to psutil
                if len(windows) == 0:
                    logger.warning("No windows found via Windows API, falling back to psutil")
            
            # Fallback: use psutil for all processes (if Windows API didn't find anything or not on Windows)
            if len(windows) == 0:
                logger.warning("No windows found via Windows API, using psutil fallback")
                logger.info("Using psutil fallback to get all processes")
                
                # Try to get window titles using Windows API even in fallback mode
                window_titles_by_pid = {}
                if platform.system() == "Windows" and self._win32gui:
                    try:
                        def collect_titles(hwnd, titles_dict):
                            try:
                                if self._win32gui.IsWindowVisible(hwnd):
                                    title = self._win32gui.GetWindowText(hwnd)
                                    if title and title.strip():
                                        _, pid = self._win32process.GetWindowThreadProcessId(hwnd)
                                        if pid not in titles_dict or not titles_dict[pid]:
                                            titles_dict[pid] = title.strip()
                            except:
                                pass
                            return True
                        self._win32gui.EnumWindows(collect_titles, window_titles_by_pid)
                    except Exception as e:
                        logger.debug(f"Could not collect window titles: {e}")
                
                for proc in psutil.process_iter(['pid', 'name', 'exe']):
                    try:
                        proc_info = proc.info
                        pid = proc_info.get('pid')
                        
                        # Skip if already seen
                        if pid in seen_pids:
                            continue
                        seen_pids.add(pid)
                        
                        # Include processes with executables
                        exe_path = proc_info.get('exe', '')
                        if exe_path:
                            process_name = proc_info.get('name', 'Unknown')
                            
                            # Filter out common system processes to reduce clutter
                            system_processes = ['svchost.exe', 'dwm.exe', 'winlogon.exe', 'csrss.exe', 
                                              'lsass.exe', 'services.exe', 'smss.exe', 'System', 
                                              'Registry', 'conhost.exe', 'RuntimeBroker.exe', 
                                              'wininit.exe', 'csrss.exe', 'services.exe']
                            
                            # Skip system processes
                            if process_name.lower() in [p.lower() for p in system_processes]:
                                continue
                            
                            # Use window title if available, otherwise process name
                            display_title = window_titles_by_pid.get(pid, process_name)
                            
                            windows.append({
                                "title": display_title,
                                "process_name": process_name,
                                "exe_path": exe_path,
                                "pid": pid,
                                "hwnd": None  # Not available without Windows API
                            })
                    except (psutil.NoSuchProcess, psutil.AccessDenied, Exception) as e:
                        logger.debug(f"Skipping process: {e}")
                        
        except Exception as e:
            logger.error(f"Error getting active windows: {e}", exc_info=True)
            # Return empty list on error, but log it
            return []
        
        # Sort by title for better UX
        windows.sort(key=lambda x: x.get("title", "").lower())
        
        logger.info(f"Found {len(windows)} active windows/processes")
        
        # If still no windows, log warning
        if len(windows) == 0:
            logger.warning("No windows detected! Possible issues:")
            logger.warning("  1. pywin32 not installed (run: pip install pywin32)")
            logger.warning("  2. No visible/minimized windows open")
            logger.warning("  3. All windows filtered out by size/title checks")
            logger.warning("  4. Permission issues accessing processes")
        
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
    
    def focus_window(self, hwnd: Optional[int]) -> bool:
        """
        Bring a window to foreground and focus it.
        
        Args:
            hwnd: Window handle ID (None if not available)
            
        Returns:
            True if successful, False otherwise
        """
        if hwnd is None:
            return False
        
        try:
            if platform.system() == "Windows" and self._win32gui:
                # Restore window if minimized
                if self._win32gui.IsIconic(hwnd):
                    self._win32gui.ShowWindow(hwnd, self._win32con.SW_RESTORE)
                
                # Bring window to foreground
                self._win32gui.SetForegroundWindow(hwnd)
                self._win32gui.BringWindowToTop(hwnd)
                logger.info(f"Focused window {hwnd}")
                return True
            else:
                logger.debug("Cannot focus window without Windows API")
                return False
        except Exception as e:
            logger.warning(f"Error focusing window: {e}")
            return False


# Global instance
windows_service = WindowsService()

