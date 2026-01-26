import cv2
import numpy as np
from collections import deque
from backend.core.config import IMG_WIDTH, IMG_HEIGHT, FRAME_STACK_SIZE

class StateProcessor:
    """
    Processes raw game frames into RL-ready state representations.
    Includes resizing, grayscale conversion, normalization, and frame stacking.
    """
    def __init__(self, stack_size=FRAME_STACK_SIZE):
        self.stack_size = stack_size
        self.frames = deque(maxlen=stack_size)
    
    def process(self, frame: np.ndarray) -> np.ndarray:
        """
        Process a raw frame and update the stack.
        
        Args:
            frame (np.ndarray): BGR Image from ScreenCapture.
            
        Returns:
            np.ndarray: Stacked frames (C, H, W) or (H, W, C) depending on config.
            Here we return (Stack_Size, Height, Width) normalized to [0, 1].
        """
        if frame is None:
            return np.zeros((self.stack_size, IMG_HEIGHT, IMG_WIDTH), dtype=np.float32)

        # 1. Convert to Grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 2. Resize
        resized = cv2.resize(gray, (IMG_WIDTH, IMG_HEIGHT), interpolation=cv2.INTER_AREA)
        
        # 3. Normalize (0-255 -> 0.0-1.0)
        normalized = resized.astype(np.float32) / 255.0
        
        # 4. Update Stack
        if len(self.frames) == 0:
            # Fill with same frame if empty
            for _ in range(self.stack_size):
                self.frames.append(normalized)
        else:
            self.frames.append(normalized)
            
        # 5. Return Stack
        # Shape: (4, 84, 84)
        return np.array(self.frames, dtype=np.float32)

    def reset(self):
        """Clear the frame stack."""
        self.frames.clear()
