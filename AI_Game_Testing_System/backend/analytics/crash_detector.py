import time

class CrashDetector:
    """
    Detects application crashes or freezes.
    """
    def __init__(self, freeze_threshold=5.0):
        self.freeze_threshold = freeze_threshold # seconds
        self.last_change_time = time.time()
        self.last_hash = None

    def check(self, current_hash: str, is_process_running: bool = True):
        """
        Check for freeze or crash.
        
        Args:
            current_hash (str): Hash of current frame.
            is_process_running (bool): External check if process is alive.
            
        Returns:
            dict: {is_crash: bool, is_freeze: bool}
        """
        if not is_process_running:
            return {"is_crash": True, "is_freeze": False}
        
        is_freeze = False
        now = time.time()
        
        if current_hash == self.last_hash:
            if (now - self.last_change_time) > self.freeze_threshold:
                is_freeze = True
        else:
            self.last_hash = current_hash
            self.last_change_time = now
            
        return {"is_crash": False, "is_freeze": is_freeze}
