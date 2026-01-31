"""
Direct test script for SuperTuxKart input.

This script tests keyboard input to SuperTuxKart using different methods
to identify which one works.

Usage:
    python test_super_tuxkart_input.py [window_title]
    
Example:
    python test_super_tuxkart_input.py "SuperTuxKart"
"""
import sys
import time
import platform

# Add parent directory to path
sys.path.insert(0, '.')

try:
    if platform.system() == "Windows":
        import win32gui
        import win32con
        import win32api
        import ctypes
        WIN32_AVAILABLE = True
    else:
        WIN32_AVAILABLE = False
except ImportError:
    WIN32_AVAILABLE = False

import pyautogui

# Virtual key codes
VK_CODES = {
    'a': 0x41, 'd': 0x44, 'w': 0x57, 's': 0x53,
    'up': 0x26, 'down': 0x28, 'left': 0x25, 'right': 0x27
}

def find_window_by_title(title):
    """Find window handle by title."""
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if title.lower() in window_title.lower():
                windows.append((hwnd, window_title))
        return True
    
    windows = []
    win32gui.EnumWindows(callback, windows)
    return windows


def test_sendinput(hwnd, key):
    """Test SendInput method."""
    try:
        PUL = ctypes.POINTER(ctypes.c_ulong)
        
        class KeyBdInput(ctypes.Structure):
            _fields_ = [("wVk", ctypes.c_ushort),
                       ("wScan", ctypes.c_ushort),
                       ("dwFlags", ctypes.c_ulong),
                       ("time", ctypes.c_ulong),
                       ("dwExtraInfo", PUL)]
        
        class Input_I(ctypes.Union):
            _fields_ = [("ki", KeyBdInput)]
        
        class Input(ctypes.Structure):
            _fields_ = [("type", ctypes.c_ulong),
                       ("ii", Input_I)]
        
        send_input = ctypes.windll.user32.SendInput
        send_input.argtypes = [ctypes.c_uint, ctypes.POINTER(Input), ctypes.c_int]
        send_input.restype = ctypes.c_uint
        
        INPUT_KEYBOARD = 1
        KEYEVENTF_KEYUP = 0x0002
        
        vk_code = VK_CODES.get(key.lower())
        if not vk_code:
            return False
        
        # Focus window first
        win32gui.SetForegroundWindow(hwnd)
        win32gui.BringWindowToTop(hwnd)
        time.sleep(0.2)
        
        # Key down
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.ki = KeyBdInput(0, vk_code, 0, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(INPUT_KEYBOARD), ii_)
        result = send_input(1, ctypes.pointer(x), ctypes.sizeof(x))
        
        if result == 0:
            return False
        
        time.sleep(0.3)
        
        # Key up
        ii_.ki = KeyBdInput(0, vk_code, KEYEVENTF_KEYUP, 0, ctypes.pointer(extra))
        send_input(1, ctypes.pointer(x), ctypes.sizeof(x))
        
        return True
    except Exception as e:
        print(f"  ❌ SendInput error: {e}")
        return False


def test_postmessage(hwnd, key):
    """Test PostMessage method."""
    try:
        vk_code = VK_CODES.get(key.lower())
        if not vk_code:
            return False
        
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.2)
        
        win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, vk_code, 0)
        time.sleep(0.3)
        win32api.PostMessage(hwnd, win32con.WM_KEYUP, vk_code, 0)
        
        return True
    except Exception as e:
        print(f"  ❌ PostMessage error: {e}")
        return False


def test_pyautogui(key):
    """Test PyAutoGUI method."""
    try:
        pyautogui.keyDown(key)
        time.sleep(0.3)
        pyautogui.keyUp(key)
        return True
    except Exception as e:
        print(f"  ❌ PyAutoGUI error: {e}")
        return False


def main():
    print("=" * 70)
    print("SUPERTUXKART INPUT TEST")
    print("=" * 70)
    
    window_title = "SuperTuxKart"
    if len(sys.argv) > 1:
        window_title = sys.argv[1]
    
    # Find window
    if not WIN32_AVAILABLE:
        print("❌ Windows API not available. This script requires Windows.")
        return
    
    print(f"\n[1/4] Searching for window: '{window_title}'...")
    windows = find_window_by_title(window_title)
    
    if not windows:
        print(f"❌ Window not found: '{window_title}'")
        print("\nMake sure SuperTuxKart is running!")
        return
    
    hwnd = windows[0][0]
    title = windows[0][1]
    print(f"✅ Found: {title} (HWND: {hwnd})")
    
    # Focus window
    print("\n[2/4] Focusing window...")
    try:
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.2)
        win32gui.SetForegroundWindow(hwnd)
        win32gui.BringWindowToTop(hwnd)
        time.sleep(0.3)
        print("✅ Window focused")
    except Exception as e:
        print(f"⚠️ Focus warning: {e}")
    
    # Test keys
    print("\n[3/4] Testing input methods...")
    print("=" * 70)
    print("⚠️ IMPORTANT: Make sure SuperTuxKart is IN A RACE (not in menu)!")
    print("=" * 70)
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    test_keys = ['up', 'left', 'right', 'down']  # Arrow keys for SuperTuxKart
    
    print("\n🔍 Testing each method:")
    print("-" * 70)
    
    for key in test_keys:
        print(f"\n📌 Testing key: {key.upper()}")
        
        # Test 1: SendInput
        print("  [1] SendInput (most reliable)...")
        if test_sendinput(hwnd, key):
            print("  ✅ SendInput sent successfully")
        else:
            print("  ❌ SendInput failed")
        time.sleep(1)
        
        # Test 2: PostMessage
        print("  [2] PostMessage...")
        if test_postmessage(hwnd, key):
            print("  ✅ PostMessage sent successfully")
        else:
            print("  ❌ PostMessage failed")
        time.sleep(1)
        
        # Test 3: PyAutoGUI
        print("  [3] PyAutoGUI...")
        if test_pyautogui(key):
            print("  ✅ PyAutoGUI sent successfully")
        else:
            print("  ❌ PyAutoGUI failed")
        time.sleep(1)
    
    print("\n" + "=" * 70)
    print("✅ TEST COMPLETE!")
    print("=" * 70)
    print("\nDid the game respond to any of the methods?")
    print("  - If YES: Note which method worked and check backend logs")
    print("  - If NO: Check:")
    print("    1. Is SuperTuxKart in a race? (not in menu)")
    print("    2. Does the game respond to manual arrow key presses?")
    print("    3. Is the correct window selected?")
    print("=" * 70)


if __name__ == "__main__":
    main()
