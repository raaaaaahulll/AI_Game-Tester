"""
Screen capture module using MSS for high-performance screen grabbing.
"""
import mss
import numpy as np
import cv2

from backend.core.config import SCREEN_SETTINGS
from backend.core.logging_config import get_logger

logger = get_logger(__name__)


class ScreenCapture:
    """
    Handles screen capturing using MSS.
    Optimized for high-speed capture.
    """
    def __init__(self):
        self.sct = mss.mss()
        # Define the monitor region
        self.monitor = {
            "top": SCREEN_SETTINGS["top"],
            "left": SCREEN_SETTINGS["left"],
            "width": SCREEN_SETTINGS["width"],
            "height": SCREEN_SETTINGS["height"],
            "mon": SCREEN_SETTINGS["monitor"],
        }

    def capture(self) -> np.ndarray:
        """
        Captures the defined screen region.
        
        Returns:
            np.ndarray: The raw screen image (BGRA) or None if failed.
        """
        try:
            # Grab the screen
            sct_img = self.sct.grab(self.monitor)
            # Convert to numpy array
            img = np.array(sct_img)
            # Drop the alpha channel to get BGR
            img = img[:, :, :3]
            return img
        except Exception as e:
            logger.error(f"Screen capture failed: {e}", exc_info=True)
            return None

    def close(self):
        """Close the screen capture instance."""
        self.sct.close()

if __name__ == "__main__":
    # Test block
    cap = ScreenCapture()
    frame = cap.capture()
    if frame is not None:
        logger.info(f"Captured frame shape: {frame.shape}")
    else:
        logger.error("Failed to capture frame")
