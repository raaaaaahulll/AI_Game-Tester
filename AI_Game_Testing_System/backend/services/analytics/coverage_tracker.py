"""
Coverage tracker for state coverage analysis.
"""
import cv2
import numpy as np


class CoverageTracker:
    """
    Tracks state coverage using Perceptual Hashing (dHash or Average Hash).
    Identifies new or rare states to guide the Reward Engine.
    """
    def __init__(self):
        self.seen_hashes = {} # hash -> count
        self.total_unique_states = 0

    def _compute_hash(self, frame: np.ndarray) -> str:
        """
        Compute a simple hash of the frame.
        Using Average Hash: specific resize -> compare to mean.
        """
        # Resize to small dimension for hashing (8x8)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        small = cv2.resize(gray, (8, 8))
        avg = small.mean()
        # Create binary string
        diff = small > avg
        # Convert to hex string
        return hex(int("".join(['1' if x else '0' for x in diff.flatten()]), 2))

    def update(self, frame: np.ndarray):
        """
        Update tracker with new frame.
        
        Returns:
            dict: {is_new: bool, is_rare: bool, count: int}
        """
        if frame is None:
            return {"is_new": False, "is_rare": False, "count": 0}

        img_hash = self._compute_hash(frame)
        
        is_new = False
        is_rare = False
        
        if img_hash not in self.seen_hashes:
            self.seen_hashes[img_hash] = 1
            self.total_unique_states += 1
            is_new = True
        else:
            self.seen_hashes[img_hash] += 1
            if self.seen_hashes[img_hash] < 5: # Arbitrary threshold for "rare"
                is_rare = True
                
        return {
            "is_new": is_new,
            "is_rare": is_rare,
            "count": self.seen_hashes[img_hash]
        }

    def get_metrics(self):
        return {
            "unique_states": self.total_unique_states,
            "total_visits": sum(self.seen_hashes.values())
        }

