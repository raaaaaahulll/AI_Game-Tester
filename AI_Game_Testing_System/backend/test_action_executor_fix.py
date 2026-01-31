"""
Test script to verify action executor fixes work correctly.

This script tests the action executor with hard-coded inputs to verify
that keys are being sent to the game window correctly.

Usage:
    python test_action_executor_fix.py [window_title]
    
Example:
    python test_action_executor_fix.py "SuperTuxKart"
"""
import sys
import time
import win32gui
import win32con

# Add parent directory to path
sys.path.insert(0, '.')

from services.env.action_executor import ActionExecutor


def find_window_by_title(title):
    """Find window handle by title (partial match)."""
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if title.lower() in window_title.lower():
                windows.append((hwnd, window_title))
        return True
    
    windows = []
    win32gui.EnumWindows(callback, windows)
    return windows


def test_action_executor(window_hwnd=None, window_title=None):
    """
    Test the action executor with hard-coded inputs.
    
    Args:
        window_hwnd: Window handle (if None, will search by title)
        window_title: Window title to search for
    """
    print("=" * 70)
    print("ACTION EXECUTOR FIX VERIFICATION TEST")
    print("=" * 70)
    
    # Find window if handle not provided
    if window_hwnd is None:
        if window_title is None:
            print("\n❌ ERROR: Either window_hwnd or window_title must be provided")
            print("\nUsage: python test_action_executor_fix.py [window_title]")
            return False
        
        print(f"\n[1/5] Searching for window: '{window_title}'...")
        windows = find_window_by_title(window_title)
        
        if not windows:
            print(f"❌ ERROR: No window found with title containing '{window_title}'")
            print("\nAvailable windows:")
            all_windows = []
            def enum_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        windows.append((hwnd, title))
                return True
            win32gui.EnumWindows(enum_callback, all_windows)
            for hwnd, title in all_windows[:10]:  # Show first 10
                print(f"  - {title} (hwnd: {hwnd})")
            return False
        
        if len(windows) > 1:
            print(f"⚠️  Found {len(windows)} matching windows:")
            for i, (hwnd, title) in enumerate(windows):
                print(f"  {i+1}. {title} (hwnd: {hwnd})")
            print(f"\nUsing first match: {windows[0][1]}")
        
        window_hwnd = windows[0][0]
        window_title = windows[0][1]
    
    print(f"✅ Found window: {window_title} (hwnd: {window_hwnd})")
    
    # Initialize action executor
    print("\n[2/5] Initializing ActionExecutor...")
    executor = ActionExecutor(window_hwnd=window_hwnd)
    print("✅ ActionExecutor initialized")
    
    # Focus window
    print("\n[3/5] Focusing game window...")
    try:
        if win32gui.IsIconic(window_hwnd):
            win32gui.ShowWindow(window_hwnd, win32con.SW_RESTORE)
            time.sleep(0.2)
        win32gui.SetForegroundWindow(window_hwnd)
        win32gui.BringWindowToTop(window_hwnd)
        time.sleep(0.3)
        print("✅ Window focused")
    except Exception as e:
        print(f"⚠️  Warning: Could not focus window: {e}")
    
    # Test sequence
    print("\n[4/5] Testing action sequence...")
    print("=" * 70)
    print("IMPORTANT: Make sure your game is in a playable state (in a race, not in menu)!")
    print("=" * 70)
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    test_actions = [
        ("Forward (W)", [0.0, 0.5], "Car should move forward"),
        ("Left + Forward (A+W)", [-0.5, 0.5], "Car should turn left while moving"),
        ("Right + Forward (D+W)", [0.5, 0.5], "Car should turn right while moving"),
        ("Brake (S)", [0.0, -0.5], "Car should brake"),
        ("Stop (release all)", [0.0, 0.0], "Car should stop"),
    ]
    
    for i, (name, action, expected) in enumerate(test_actions, 1):
        print(f"\n[{i}/{len(test_actions)}] {name}")
        print(f"   Action: steering={action[0]:.1f}, throttle={action[1]:.1f}")
        print(f"   Expected: {expected}")
        
        try:
            executor.apply_continuous_action(action)
            time.sleep(2)  # Hold action for 2 seconds
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # Release all keys
    print("\n[5/5] Releasing all keys...")
    executor.reset()
    print("✅ All keys released")
    
    print("\n" + "=" * 70)
    print("✅ TEST COMPLETE!")
    print("=" * 70)
    print("\nDid the game respond to the inputs?")
    print("  - If YES: The fix is working! ✅")
    print("  - If NO: Check the following:")
    print("    1. Is the game in a playable state (in a race)?")
    print("    2. Does the game use WASD keys? (Try arrow keys if not)")
    print("    3. Check backend logs for error messages")
    print("    4. Verify window handle is correct")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    window_title = None
    if len(sys.argv) > 1:
        window_title = sys.argv[1]
    
    success = test_action_executor(window_title=window_title)
    sys.exit(0 if success else 1)
