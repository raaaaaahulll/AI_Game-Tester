"""
Screenshot service for saving game screenshots and bug/issue images.
"""
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from uuid import uuid4

from config.settings import settings
from utils.logging import get_logger

logger = get_logger(__name__)


class ScreenshotService:
    """
    Service for managing screenshot storage.
    
    Organizes screenshots into:
    - Game screenshots: Regular gameplay screenshots
    - Bug screenshots: Screenshots of detected bugs/issues/crashes
    """
    
    def __init__(self):
        """Initialize screenshot service and create directories."""
        self.screenshots_dir = settings.SCREENSHOTS_DIR
        self.bugs_dir = settings.BUGS_DIR
        self.game_dir = settings.GAME_SCREENSHOTS_DIR
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Ensure all screenshot directories exist."""
        try:
            self.screenshots_dir.mkdir(parents=True, exist_ok=True)
            self.bugs_dir.mkdir(parents=True, exist_ok=True)
            self.game_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Screenshot directories initialized: {self.screenshots_dir}")
        except Exception as e:
            logger.error(f"Error creating screenshot directories: {e}", exc_info=True)
    
    def save_game_screenshot(
        self,
        frame: np.ndarray,
        test_id: Optional[str] = None,
        step: Optional[int] = None,
        prefix: Optional[str] = None
    ) -> Optional[Path]:
        """
        Save a game screenshot.
        
        Args:
            frame: Image frame (numpy array, BGR format)
            test_id: Optional test ID to organize screenshots
            step: Optional step number
            prefix: Optional filename prefix
            
        Returns:
            Path to saved screenshot or None if failed
        """
        try:
            if frame is None:
                logger.warning("Cannot save screenshot: frame is None")
                return None
            
            # Create subdirectory for test if test_id provided
            if test_id:
                test_dir = self.game_dir / test_id
                test_dir.mkdir(parents=True, exist_ok=True)
                save_dir = test_dir
            else:
                save_dir = self.game_dir
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_parts = []
            
            if prefix:
                filename_parts.append(prefix)
            
            if step is not None:
                filename_parts.append(f"step_{step}")
            
            filename_parts.append(timestamp)
            filename_parts.append(str(uuid4())[:8])  # Short UUID for uniqueness
            
            filename = "_".join(filename_parts) + ".png"
            filepath = save_dir / filename
            
            # Save image
            cv2.imwrite(str(filepath), frame)
            
            logger.debug(f"Saved game screenshot: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving game screenshot: {e}", exc_info=True)
            return None
    
    def save_bug_screenshot(
        self,
        frame: np.ndarray,
        test_id: str,
        bug_type: str = "crash",
        description: Optional[str] = None,
        step: Optional[int] = None
    ) -> Optional[Path]:
        """
        Save a bug/issue screenshot.
        
        Args:
            frame: Image frame (numpy array, BGR format)
            test_id: Test ID where bug occurred
            bug_type: Type of bug (crash, freeze, error, etc.)
            description: Optional description of the bug
            step: Optional step number when bug occurred
            
        Returns:
            Path to saved screenshot or None if failed
        """
        try:
            if frame is None:
                logger.warning("Cannot save bug screenshot: frame is None")
                return None
            
            # Create subdirectory for test
            test_dir = self.bugs_dir / test_id
            test_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_parts = [bug_type]
            
            if step is not None:
                filename_parts.append(f"step_{step}")
            
            filename_parts.append(timestamp)
            filename_parts.append(str(uuid4())[:8])
            
            filename = "_".join(filename_parts) + ".png"
            filepath = test_dir / filename
            
            # Save image
            cv2.imwrite(str(filepath), frame)
            
            # Save metadata file
            metadata = {
                "test_id": test_id,
                "bug_type": bug_type,
                "timestamp": timestamp,
                "step": step,
                "description": description or "",
                "screenshot_path": str(filepath)
            }
            self._save_metadata(filepath, metadata)
            
            logger.info(f"Saved bug screenshot: {filepath} (type: {bug_type})")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving bug screenshot: {e}", exc_info=True)
            return None
    
    def _save_metadata(self, screenshot_path: Path, metadata: Dict[str, Any]) -> None:
        """Save metadata JSON file alongside screenshot."""
        try:
            import json
            metadata_path = screenshot_path.with_suffix('.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Failed to save metadata for {screenshot_path}: {e}")
    
    def get_screenshots_for_test(self, test_id: str) -> Dict[str, list]:
        """
        Get all screenshots for a specific test.
        
        Args:
            test_id: Test ID
            
        Returns:
            Dictionary with 'game' and 'bugs' lists of screenshot paths
        """
        screenshots = {
            "game": [],
            "bugs": []
        }
        
        try:
            # Get game screenshots
            game_test_dir = self.game_dir / test_id
            if game_test_dir.exists():
                screenshots["game"] = [
                    str(p) for p in game_test_dir.glob("*.png")
                ]
            
            # Get bug screenshots
            bug_test_dir = self.bugs_dir / test_id
            if bug_test_dir.exists():
                screenshots["bugs"] = [
                    str(p) for p in bug_test_dir.glob("*.png")
                ]
            
        except Exception as e:
            logger.error(f"Error getting screenshots for test {test_id}: {e}", exc_info=True)
        
        return screenshots
    
    def cleanup_old_screenshots(self, days: int = 30) -> int:
        """
        Clean up screenshots older than specified days.
        
        Args:
            days: Number of days to keep screenshots
            
        Returns:
            Number of files deleted
        """
        import time
        deleted_count = 0
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        try:
            for directory in [self.game_dir, self.bugs_dir]:
                for filepath in directory.rglob("*.png"):
                    if filepath.stat().st_mtime < cutoff_time:
                        try:
                            filepath.unlink()
                            # Also delete metadata if exists
                            metadata_path = filepath.with_suffix('.json')
                            if metadata_path.exists():
                                metadata_path.unlink()
                            deleted_count += 1
                        except Exception as e:
                            logger.warning(f"Failed to delete {filepath}: {e}")
            
            logger.info(f"Cleaned up {deleted_count} old screenshots")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up screenshots: {e}", exc_info=True)
            return deleted_count


# Global instance
screenshot_service = ScreenshotService()
