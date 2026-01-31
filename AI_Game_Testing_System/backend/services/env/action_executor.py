"""
Action executor for OS-level input simulation.
"""
import pyautogui
import time
import platform

# Fail-safe mode (move mouse to corner to abort)
pyautogui.FAILSAFE = True
# Small pause to prevent overwhelming the application
pyautogui.PAUSE = 0.01

# Try to import Windows API for window focus and key sending
_WIN32_AVAILABLE = False
_SENDINPUT_AVAILABLE = False
_SENDINPUT_STRUCTS_READY = False

try:
    if platform.system() == "Windows":
        import win32gui
        import win32con
        import win32api
        _WIN32_AVAILABLE = True
        
        # Try to import ctypes for SendInput
        try:
            import ctypes
            from ctypes import wintypes
            _SENDINPUT_AVAILABLE = True
        except ImportError:
            _SENDINPUT_AVAILABLE = False
except ImportError:
    _WIN32_AVAILABLE = False
    _SENDINPUT_AVAILABLE = False

# SendInput structures for Windows API
if _SENDINPUT_AVAILABLE:
    try:
        # Define INPUT structure for SendInput
        PUL = ctypes.POINTER(ctypes.c_ulong)
        
        class KeyBdInput(ctypes.Structure):
            _fields_ = [("wVk", ctypes.c_ushort),
                       ("wScan", ctypes.c_ushort),
                       ("dwFlags", ctypes.c_ulong),
                       ("time", ctypes.c_ulong),
                       ("dwExtraInfo", PUL)]
        
        class HardwareInput(ctypes.Structure):
            _fields_ = [("uMsg", ctypes.c_ulong),
                       ("wParamL", ctypes.c_short),
                       ("wParamH", ctypes.c_ushort)]
        
        class MouseInput(ctypes.Structure):
            _fields_ = [("dx", ctypes.c_long),
                       ("dy", ctypes.c_long),
                       ("mouseData", ctypes.c_ulong),
                       ("dwFlags", ctypes.c_ulong),
                       ("time", ctypes.c_ulong),
                       ("dwExtraInfo", PUL)]
        
        class Input_I(ctypes.Union):
            _fields_ = [("ki", KeyBdInput),
                       ("mi", MouseInput),
                       ("hi", HardwareInput)]
        
        class Input(ctypes.Structure):
            _fields_ = [("type", ctypes.c_ulong),
                       ("ii", Input_I)]
        
        # Get SendInput function
        _send_input = ctypes.windll.user32.SendInput
        _send_input.argtypes = [ctypes.c_uint, ctypes.POINTER(Input), ctypes.c_int]
        _send_input.restype = ctypes.c_uint
        
        _INPUT_KEYBOARD = 1
        _KEYEVENTF_KEYUP = 0x0002
        _SENDINPUT_STRUCTS_READY = True
    except Exception:
        _SENDINPUT_AVAILABLE = False
        _SENDINPUT_STRUCTS_READY = False
else:
    _SENDINPUT_STRUCTS_READY = False

# Virtual key codes for common keys
_VK_CODES = {
    'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45, 'f': 0x46,
    'g': 0x47, 'h': 0x48, 'i': 0x49, 'j': 0x4A, 'k': 0x4B, 'l': 0x4C,
    'm': 0x4D, 'n': 0x4E, 'o': 0x4F, 'p': 0x50, 'q': 0x51, 'r': 0x52,
    's': 0x53, 't': 0x54, 'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58,
    'y': 0x59, 'z': 0x5A,
    'up': 0x26, 'down': 0x28, 'left': 0x25, 'right': 0x27,
    'space': 0x20, 'enter': 0x0D, 'esc': 0x1B
}


class ActionExecutor:
    """
    Executes actions via generic OS input (Keyboard/Mouse).
    Maintains state of keys to allow 'holding' keys across steps.
    """
    def __init__(self, window_hwnd=None):
        self.held_keys = set()
        self.window_hwnd = window_hwnd
        # Action smoothing state (for racing games)
        self.prev_steering = 0.0
        self.prev_throttle = 0.0
        self.smoothing_alpha = 0.8  # Exponential smoothing factor

    def reset(self):
        """Release all currently held keys and reset smoothing state."""
        for key in list(self.held_keys):
            self._release_key(key)
        self.held_keys.clear()
        # Reset smoothing state on episode reset
        self.prev_steering = 0.0
        self.prev_throttle = 0.0

    def apply_discrete_action(self, action_map: dict, action_idx: int):
        """
        Apply a discrete action (e.g., press specific key).
        Unpresses keys not in the new action set (unless multi-press logic used).
        
        Args:
            action_map (dict): Mapping from index to key name (e.g. {0: 'a', 1: 'd'}).
            action_idx (int): The selected action index.
        """
        target_key = action_map.get(action_idx)
        
        # Simple Logic: Release all previous, press new. 
        # (Improvement: Only release different keys)
        self.reset()
        
        if target_key and target_key != "nop":
            pyautogui.keyDown(target_key)
            self.held_keys.add(target_key)

    def _ensure_window_focused(self):
        """Ensure the target window is focused before sending keys."""
        if self.window_hwnd and _WIN32_AVAILABLE:
            try:
                # Check if window is already focused (optimization)
                foreground_hwnd = win32gui.GetForegroundWindow()
                if foreground_hwnd == self.window_hwnd:
                    return  # Already focused, skip
                
                # Restore if minimized
                if win32gui.IsIconic(self.window_hwnd):
                    win32gui.ShowWindow(self.window_hwnd, win32con.SW_RESTORE)
                    time.sleep(0.2)
                
                # Bring to foreground and focus - try multiple methods
                win32gui.SetForegroundWindow(self.window_hwnd)
                win32gui.BringWindowToTop(self.window_hwnd)
                # Try SetFocus if available (may not exist in all win32gui versions)
                try:
                    if hasattr(win32gui, 'SetFocus'):
                        win32gui.SetFocus(self.window_hwnd)
                except:
                    pass
                time.sleep(0.2)  # Increased delay to ensure focus is set
                
                # Verify focus was set
                new_foreground = win32gui.GetForegroundWindow()
                if new_foreground != self.window_hwnd:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"⚠️ Window focus may have failed. Expected {self.window_hwnd}, got {new_foreground}")
                    logger.warning(f"   This may cause inputs to not reach the game!")
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to focus window {self.window_hwnd}: {e}")
                # Fall back to pyautogui if Windows API fails
    
    def apply_continuous_action(self, action_vector):
        """
        Apply continuous action for racing games.
        Maps continuous action vector to keyboard inputs.
        
        Args:
            action_vector: [steering, throttle/brake]
                - steering: -1.0 (left) to 1.0 (right)
                - throttle/brake: -1.0 (brake) to 1.0 (throttle)
        """
        import numpy as np
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Convert to numpy array if needed and ensure it's a flat array
        if hasattr(action_vector, '__len__'):
            action_array = np.array(action_vector).flatten()
        else:
            return
        
        if len(action_array) < 2:
            return
        
        steering_raw, throttle_raw = float(action_array[0]), float(action_array[1])
        
        # TASK 3: Safety constraints - clamp actions to safe ranges
        # Steering: [-0.5, 0.5] to prevent excessive turning
        steering = max(-0.5, min(0.5, steering_raw))
        # Throttle/Brake: [-1.0, 1.0] where negative = brake, positive = throttle
        # Clamp to [0.0, 1.0] for throttle, [0.0, 1.0] for brake
        throttle = max(-1.0, min(1.0, throttle_raw))
        
        # TASK 2: Action smoothing layer (exponential smoothing)
        # Smooth steering and throttle to reduce oscillation
        # Do NOT smooth brake aggressively - if switching to brake, apply immediately
        if throttle < 0 and self.prev_throttle >= 0:
            # Switching to brake - apply immediately (no smoothing)
            pass  # Keep throttle as-is (negative = brake)
        else:
            # Normal smoothing for steering and throttle
            steering = self.smoothing_alpha * self.prev_steering + (1 - self.smoothing_alpha) * steering
            throttle = self.smoothing_alpha * self.prev_throttle + (1 - self.smoothing_alpha) * throttle
        
        # Store smoothed values for next step
        self.prev_steering = steering
        self.prev_throttle = throttle
        
        # Ensure window is focused before sending keys
        self._ensure_window_focused()
        
        # Define thresholds (FIXED: THROTTLE_THRESHOLD was undefined!)
        STEERING_THRESHOLD = 0.15
        THROTTLE_THRESHOLD = 0.15  # CRITICAL FIX: This was missing!
        
        # Determine which keys should be pressed based on action
        keys_to_press = set()
        
        # CRITICAL: SuperTuxKart and most racing games use ARROW KEYS, not WASD!
        # Set to False if your game uses WASD instead
        USE_ARROW_KEYS = True  # Changed to True - most racing games use arrow keys
        
        if USE_ARROW_KEYS:
            # Use arrow keys for steering
            if steering < -STEERING_THRESHOLD:
                keys_to_press.add('left')
            elif steering > STEERING_THRESHOLD:
                keys_to_press.add('right')
            
            # Use arrow keys for throttle/brake
            if throttle > THROTTLE_THRESHOLD:
                keys_to_press.add('up')
            elif throttle < -THROTTLE_THRESHOLD:
                keys_to_press.add('down')
        else:
            # Use WASD keys (default)
            if steering < -STEERING_THRESHOLD:
                keys_to_press.add('a')  # Turn left
            elif steering > STEERING_THRESHOLD:
                keys_to_press.add('d')  # Turn right
            
            # Throttle/Brake: Map to W (throttle) and S (brake) keys
            if throttle > THROTTLE_THRESHOLD:
                keys_to_press.add('w')  # Accelerate
            elif throttle < -THROTTLE_THRESHOLD:
                keys_to_press.add('s')  # Brake
        
        # CRITICAL FIX: Only release keys that are no longer needed
        # This prevents unnecessary key release/press cycles
        keys_to_release = self.held_keys - keys_to_press
        
        # Release keys that are no longer needed
        for key in keys_to_release:
            self._release_key(key)
        
        # Press new keys that aren't already held
        keys_to_press_new = keys_to_press - self.held_keys
        
        # Log action for debugging (more verbose for troubleshooting)
        if keys_to_press:
            if not hasattr(self, '_key_log_count'):
                self._key_log_count = 0
            if self._key_log_count < 30:  # Increased logging for debugging
                logger.info(f"🎮 Action: keys={list(keys_to_press)} (steering={steering:.3f}, throttle={throttle:.3f})")
                logger.info(f"   Window HWND: {self.window_hwnd}, Arrow keys: {USE_ARROW_KEYS}")
                # Log which keys will be pressed vs already held
                logger.info(f"   Keys to press NEW: {list(keys_to_press_new)}, Already held: {list(self.held_keys)}")
                self._key_log_count += 1
        
        # Press new keys
        for key in keys_to_press_new:
            self._press_key(key)
            # Small delay between key presses
            time.sleep(0.01)
        
        # Small delay to ensure keys are registered
        time.sleep(0.05)  # Increased delay for better reliability
    
    def _press_key(self, key):
        """
        Press a key using SendInput (most reliable), PostMessage, or PyAutoGUI fallback.
        
        Args:
            key: Key name (e.g., 'w', 'a', 'left', 'up')
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            vk_code = _VK_CODES.get(key.lower())
            if not vk_code:
                # Key not in VK_CODES, use PyAutoGUI
                pyautogui.keyDown(key)
                self.held_keys.add(key)
                return
            
            # Method 1: Try PostMessage/SendMessage FIRST (diagnostic confirmed this works!)
            # Since diagnostic test showed PostMessage works for SuperTuxKart, use it as primary method
            if _WIN32_AVAILABLE and self.window_hwnd:
                try:
                    # Ensure window is focused
                    self._ensure_window_focused()
                    time.sleep(0.03)
                    
                    # Send key messages directly to window (diagnostic confirmed this works!)
                    win32api.PostMessage(self.window_hwnd, win32con.WM_KEYDOWN, vk_code, 0)
                    win32api.SendMessage(self.window_hwnd, win32con.WM_KEYDOWN, vk_code, 0)
                    self.held_keys.add(key)
                    if not hasattr(self, '_win32_success_logged'):
                        logger.info("✅ Using Windows API PostMessage/SendMessage for key sending")
                        logger.info(f"   Window handle: {self.window_hwnd}")
                        logger.info(f"   Method: PostMessage (diagnostic test confirmed this works for SuperTuxKart!)")
                        self._win32_success_logged = True
                    return
                except Exception as e:
                    logger.warning(f"PostMessage failed for {key}: {e}, trying PyAutoGUI")
            
            # Note: SendInput is skipped for SuperTuxKart (diagnostic test showed it fails)
            # Going directly to PyAutoGUI fallback which also works
            
            # Method 2: Fallback to PyAutoGUI (diagnostic confirmed this also works!)
            self._ensure_window_focused()
            time.sleep(0.03)
            pyautogui.keyDown(key)
            self.held_keys.add(key)
            if not hasattr(self, '_pyautogui_success_logged'):
                logger.info("✅ Using PyAutoGUI for key sending (fallback - diagnostic confirmed this works!)")
                self._pyautogui_success_logged = True
        except Exception as e:
            logger.warning(f"Failed to press key {key}: {e}")
    
    def _release_key(self, key):
        """
        Release a key using SendInput, PostMessage, or PyAutoGUI fallback.
        
        Args:
            key: Key name (e.g., 'w', 'a', 'left', 'up')
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            vk_code = _VK_CODES.get(key.lower())
            if not vk_code:
                # Key not in VK_CODES, use PyAutoGUI
                pyautogui.keyUp(key)
                self.held_keys.discard(key)
                return
            
            # Method 1: Try PostMessage/SendMessage FIRST (primary method)
            if _WIN32_AVAILABLE and self.window_hwnd:
                try:
                    win32api.PostMessage(self.window_hwnd, win32con.WM_KEYUP, vk_code, 0)
                    win32api.SendMessage(self.window_hwnd, win32con.WM_KEYUP, vk_code, 0)
                    self.held_keys.discard(key)
                    return
                except Exception as e:
                    logger.debug(f"PostMessage key release failed for {key}, trying PyAutoGUI: {e}")
            
            # Note: SendInput is skipped for SuperTuxKart (diagnostic test showed it fails)
            
            # Method 2: Fallback to PyAutoGUI
            self._ensure_window_focused()
            pyautogui.keyUp(key)
            self.held_keys.discard(key)
        except Exception as e:
            logger.warning(f"Failed to release key {key}: {e}")
            # Ensure key is removed from held_keys even if release fails
            self.held_keys.discard(key)

    def text_input(self, text):
        pyautogui.write(text)

    def click(self, x, y):
        pyautogui.click(x, y)

