"""
State processor for converting raw frames to RL-ready states.
"""
import cv2
import numpy as np
from collections import deque

from config.settings import settings


class StateProcessor:
    """
    Processes raw game frames into RL-ready state representations.
    Includes resizing, grayscale conversion, normalization, and frame stacking.
    """
    def __init__(self, stack_size=None):
        self.stack_size = stack_size or settings.FRAME_STACK_SIZE
        self.frames = deque(maxlen=self.stack_size)
    
    def process(self, frame: np.ndarray) -> np.ndarray:
        """
        Process a raw frame and update the stack.
        
        Args:
            frame (np.ndarray): BGR Image from ScreenCapture.
            
        Returns:
            np.ndarray: Stacked frames in channel-last format (H, W, C).
            Returns (Height, Width, Stack_Size) normalized to [0, 1].
            This format is required by Stable-Baselines3 CnnPolicy.
        """
        if frame is None:
            return np.zeros((settings.IMG_HEIGHT, settings.IMG_WIDTH, self.stack_size), dtype=np.float32)

        # 1. Convert to Grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 2. Resize
        resized = cv2.resize(gray, (settings.IMG_WIDTH, settings.IMG_HEIGHT), interpolation=cv2.INTER_AREA)
        
        # 3. Normalize (0-255 -> 0.0-1.0)
        normalized = resized.astype(np.float32) / 255.0
        
        # 4. Update Stack
        if len(self.frames) == 0:
            # Fill with same frame if empty
            for _ in range(self.stack_size):
                self.frames.append(normalized)
        else:
            self.frames.append(normalized)
            
        # 5. Return Stack in channel-last format (H, W, C)
        # Convert from (stack_size, height, width) to (height, width, stack_size)
        stacked = np.array(self.frames, dtype=np.float32)  # Shape: (stack_size, height, width)
        # Transpose to (height, width, stack_size)
        return np.transpose(stacked, (1, 2, 0))

    def reset(self):
        """Clear the frame stack."""
        self.frames.clear()

