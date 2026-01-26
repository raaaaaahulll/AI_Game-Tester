"""
Action executor for OS-level input simulation.
"""
import pyautogui
import time

# Fail-safe mode (move mouse to corner to abort)
pyautogui.FAILSAFE = True
# Small pause to prevent overwhelming the application
pyautogui.PAUSE = 0.01


class ActionExecutor:
    """
    Executes actions via generic OS input (Keyboard/Mouse).
    Maintains state of keys to allow 'holding' keys across steps.
    """
    def __init__(self):
        self.held_keys = set()

    def reset(self):
        """Release all currently held keys."""
        for key in list(self.held_keys):
            pyautogui.keyUp(key)
        self.held_keys.clear()

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

    def apply_continuous_action(self, action_vector):
        """
        Apply continuous action (e.g. mouse movement).
        Implementation depends on specific game needs.
        
        Args:
            action_vector: [steering, throttle] or [dx, dy]
        """
        # Example for mouse
        # pyautogui.moveRel(x, y)
        pass

    def text_input(self, text):
        pyautogui.write(text)

    def click(self, x, y):
        pyautogui.click(x, y)

