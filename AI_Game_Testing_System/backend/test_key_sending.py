"""
Test script to verify key sending to game window.
Run this to test if keys are being sent correctly.
"""
import time
import pyautogui
import platform

# Try to import Windows API
try:
    if platform.system() == "Windows":
        import win32gui
        import win32con
        import win32api
        WIN32_AVAILABLE = True
    else:
        WIN32_AVAILABLE = False
except ImportError:
    WIN32_AVAILABLE = False

# Virtual key codes
VK_CODES = {
    'a': 0x41, 'd': 0x44, 'w': 0x57, 's': 0x53,
    'up': 0x26, 'down': 0x28, 'left': 0x25, 'right': 0x27
}

def test_key_sending(window_hwnd=None):
    """Test sending keys to a specific window."""
    print("=" * 60)
    print("KEY SENDING TEST")
    print("=" * 60)
    
    if window_hwnd and WIN32_AVAILABLE:
        print(f"Testing with window handle: {window_hwnd}")
        
        # Focus the window
        try:
            if win32gui.IsIconic(window_hwnd):
                win32gui.ShowWindow(window_hwnd, win32con.SW_RESTORE)
                time.sleep(0.2)
            
            win32gui.SetForegroundWindow(window_hwnd)
            win32gui.BringWindowToTop(window_hwnd)
            time.sleep(0.3)
            
            foreground = win32gui.GetForegroundWindow()
            if foreground == window_hwnd:
                print("✅ Window is focused")
            else:
                print(f"⚠️  Window focus check: Expected {window_hwnd}, got {foreground}")
        except Exception as e:
            print(f"❌ Failed to focus window: {e}")
    
    print("\nSending test keys (W, A, S, D) in sequence...")
    print("Watch your game window - you should see movement!")
    print("Starting in 3 seconds...")
    time.sleep(3)
    
    test_keys = ['w', 'a', 's', 'd']
    print("\nTrying Windows API first, then PyAutoGUI...")
    
    for key in test_keys:
        print(f"Pressing {key.upper()}...")
        
        # Try Windows API first
        if window_hwnd and WIN32_AVAILABLE:
            try:
                vk_code = VK_CODES.get(key.lower())
                if vk_code:
                    print(f"  → Using Windows API (VK code: 0x{vk_code:02X})")
                    win32api.PostMessage(window_hwnd, win32con.WM_KEYDOWN, vk_code, 0)
                    time.sleep(0.3)
                    win32api.PostMessage(window_hwnd, win32con.WM_KEYUP, vk_code, 0)
                    time.sleep(0.2)
                    continue
            except Exception as e:
                print(f"  → Windows API failed: {e}, trying PyAutoGUI...")
        
        # Fallback to PyAutoGUI
        print(f"  → Using PyAutoGUI")
        pyautogui.keyDown(key)
        time.sleep(0.3)
        pyautogui.keyUp(key)
        time.sleep(0.2)
    
    print("\n✅ Test complete!")
    print("If you didn't see any movement in the game:")
    print("1. Make sure the game is running and in a playable state (not in menu)")
    print("2. Make sure the game window is visible and not minimized")
    print("3. Check if the game uses different keys (arrow keys, etc.)")

if __name__ == "__main__":
    import sys
    hwnd = None
    if len(sys.argv) > 1:
        try:
            hwnd = int(sys.argv[1])
        except ValueError:
            print(f"Invalid window handle: {sys.argv[1]}")
            sys.exit(1)
    
    test_key_sending(hwnd)
