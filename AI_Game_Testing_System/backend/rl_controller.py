"""
RL Controller for managing game testing sessions.

Orchestrates the Reinforcement Learning training loop, environment management,
and agent lifecycle.
"""
import threading
import time
from typing import Tuple, Optional
from stable_baselines3.common.callbacks import BaseCallback

from backend.core.strategy_selector import StrategySelector
from backend.env.game_env import GameEnv
from backend.analytics.metrics_collector import metrics_collector
from backend.analytics.test_history import test_history_manager
from backend.core.config import settings
from backend.core.logging_config import get_logger
from backend.core.exceptions import (
    TestingSessionAlreadyRunningError,
    TestingSessionNotRunningError,
    InvalidGenreError,
    EnvironmentError,
    AgentError,
)

logger = get_logger(__name__)


class MetricsCallback(BaseCallback):
    """Callback for updating metrics during training."""
    
    def __init__(self, check_freq: int, stop_event: threading.Event):
        """
        Initialize metrics callback.
        
        Args:
            check_freq: Frequency of metric updates (every N steps)
            stop_event: Threading event to signal stop
        """
        super(MetricsCallback, self).__init__(verbose=0)
        self.check_freq = check_freq
        self.stop_event = stop_event

    def _on_step(self) -> bool:
        """
        Called at each training step.
        
        Returns:
            False to stop training, True to continue
        """
        if self.stop_event.is_set():
            logger.info("Stop event detected, stopping training")
            return False
        
        if self.n_calls % self.check_freq == 0:
            try:
                # Update global metrics from training info
                infos = self.locals.get("infos", [{}])
                if infos:
                    info = infos[0] if isinstance(infos, list) else infos
                    coverage = info.get("coverage", {})
                    crash = info.get("crash", {})
                    
                    if isinstance(coverage, dict):
                        metrics_collector.update(
                            "coverage",
                            coverage.get("unique_states", 0)
                        )
                    
                    if isinstance(crash, dict) and crash.get("is_crash"):
                        current_crashes = metrics_collector.get_all().get("crashes", 0)
                        metrics_collector.update("crashes", current_crashes + 1)
                    
                    metrics_collector.update("total_steps", self.num_timesteps)
            except Exception as e:
                logger.warning(f"Error updating metrics in callback: {e}")
        
        return True


class RLController:
    """
    Main Controller that orchestrates the RL Service.
    
    Manages the Game Environment, Agent, and Training Loop.
    Thread-safe for concurrent API requests.
    """
    
    def __init__(self):
        """Initialize the RL controller."""
        self._lock = threading.Lock()
        self.thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.env: Optional[GameEnv] = None
        self.agent = None
        self._current_genre: Optional[str] = None
        self._start_time: Optional[float] = None
        self._algorithm_name: Optional[str] = None

    def _training_loop(self, genre: str) -> None:
        """
        Background training loop executed in a separate thread.
        
        Args:
            genre: Game genre to test
        """
        logger.info(f"Starting training loop for genre: {genre}")
        self._start_time = time.time()
        final_status = "Error"  # Default to error, will be updated on success
        
        try:
            # Update status
            metrics_collector.update("status", "Initializing Environment")
            metrics_collector.update("current_algorithm", genre)
            
            # Initialize Environment
            logger.info(f"Initializing game environment for genre: {genre}")
            try:
                self.env = GameEnv(config={"genre": genre})
                logger.info("Game environment initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize environment: {e}", exc_info=True)
                raise EnvironmentError(f"Failed to initialize game environment: {e}")
            
            # Select and initialize Agent
            logger.info(f"Selecting strategy for genre: {genre}")
            try:
                agent_cls = StrategySelector.select_strategy(genre)
                self._algorithm_name = agent_cls.__name__
                logger.info(f"Selected agent: {self._algorithm_name}")
                self.agent = agent_cls(self.env, config={})
                metrics_collector.update("status", f"Training {self._algorithm_name}")
                metrics_collector.update("current_algorithm", self._algorithm_name)
            except Exception as e:
                logger.error(f"Failed to initialize agent: {e}", exc_info=True)
                raise AgentError(f"Failed to initialize RL agent: {e}")

            # Start training with callback
            logger.info(f"Starting training for {settings.TIMESTEPS} timesteps")
            callback = MetricsCallback(check_freq=10, stop_event=self.stop_event)
            
            try:
                self.agent.model.learn(
                    total_timesteps=settings.TIMESTEPS,
                    callback=callback
                )
                logger.info("Training completed successfully")
                metrics_collector.update("status", "Completed")
                final_status = "Completed"
            except Exception as e:
                if self.stop_event.is_set():
                    logger.info("Training stopped by user request")
                    metrics_collector.update("status", "Stopped")
                    final_status = "Stopped"
                else:
                    logger.error(f"Training failed: {e}", exc_info=True)
                    final_status = "Error"
                    raise
            
        except Exception as e:
            logger.error(f"Error in training loop: {e}", exc_info=True)
            final_status = "Error"
            metrics_collector.update("status", final_status)
            metrics_collector.update("error_log", str(e))
        finally:
            # Save test result to history
            try:
                duration = None
                if self._start_time:
                    duration = time.time() - self._start_time
                
                final_metrics = metrics_collector.get_all()
                # final_status is set in the try/except blocks above
                
                algorithm = self._algorithm_name or final_metrics.get("current_algorithm", "Unknown")
                
                # Only save if test actually ran (not just initialization error)
                if self._start_time and (final_status in ["Completed", "Stopped", "Error"]):
                    error_note = None
                    if final_status == "Error":
                        error_note = final_metrics.get("error_log", "Unknown error")
                    
                    test_history_manager.save_test_result(
                        genre=genre,
                        algorithm=algorithm,
                        metrics=final_metrics,
                        status=final_status,
                        duration_seconds=duration,
                        notes=error_note
                    )
            except Exception as e:
                logger.warning(f"Failed to save test result to history: {e}", exc_info=True)
            
            # Cleanup
            logger.info("Cleaning up training resources")
            if self.env:
                try:
                    self.env.close()
                except Exception as e:
                    logger.warning(f"Error closing environment: {e}")
            
            with self._lock:
                self.env = None
                self.agent = None
                self._current_genre = None
                self._start_time = None
                self._algorithm_name = None

    def start_test(self, genre: str) -> Tuple[bool, str]:
        """
        Start a new testing session.
        
        Args:
            genre: Game genre to test (must be valid)
            
        Returns:
            Tuple of (success: bool, message: str)
            
        Raises:
            TestingSessionAlreadyRunningError: If a test is already running
            InvalidGenreError: If genre is invalid
        """
        with self._lock:
            if self.thread and self.thread.is_alive():
                error_msg = "Test already running"
                logger.warning(error_msg)
                raise TestingSessionAlreadyRunningError(error_msg)
            
            # Validate genre
            genre_lower = genre.lower()
            valid_genres = {"platformer", "fps", "racing", "rpg"}
            if genre_lower not in valid_genres:
                error_msg = f"Invalid genre: {genre}. Must be one of {valid_genres}"
                logger.warning(error_msg)
                raise InvalidGenreError(error_msg)
            
            # Start training thread
            self.stop_event.clear()
            self._current_genre = genre_lower
            
            # Clear any previous error status
            current_status = metrics_collector.get("status", "Idle")
            if current_status == "Error":
                metrics_collector.update("status", "Initializing")
                # Clear error log
                if "error_log" in metrics_collector.get_all():
                    metrics_collector.update("error_log", "")
            
            self.thread = threading.Thread(
                target=self._training_loop,
                args=(genre_lower,),
                daemon=True,
                name=f"TrainingThread-{genre_lower}"
            )
            self.thread.start()
            
            logger.info(f"Test started for genre: {genre_lower}")
            return True, f"Testing started for genre: {genre_lower}"

    def stop_test(self) -> Tuple[bool, str]:
        """
        Stop the current testing session.
        
        Returns:
            Tuple of (success: bool, message: str)
            
        Raises:
            TestingSessionNotRunningError: If no test is running
        """
        with self._lock:
            if not self.thread or not self.thread.is_alive():
                error_msg = "No active testing session to stop"
                logger.warning(error_msg)
                raise TestingSessionNotRunningError(error_msg)
            
            # Signal stop
            logger.info("Stopping test session")
            self.stop_event.set()
            
            # Wait for thread to finish (with timeout)
            self.thread.join(timeout=10.0)
            
            if self.thread.is_alive():
                logger.warning("Training thread did not stop within timeout")
                return False, "Stop request sent, but thread is still running"
            
            # Reset status to Idle after successful stop
            metrics_collector.update("status", "Idle")
            logger.info("Test stopped successfully")
            return True, "Testing stopped successfully"
    
    def is_running(self) -> bool:
        """
        Check if a test is currently running.
        
        Returns:
            True if test is running, False otherwise
        """
        with self._lock:
            return self.thread is not None and self.thread.is_alive()
    
    def get_current_genre(self) -> Optional[str]:
        """
        Get the genre of the currently running test.
        
        Returns:
            Genre string or None if no test is running
        """
        with self._lock:
            if self.is_running():
                return self._current_genre
            return None


# Global Instance (singleton pattern)
rl_controller = RLController()
