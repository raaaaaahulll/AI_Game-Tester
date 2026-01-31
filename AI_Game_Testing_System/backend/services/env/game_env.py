"""
Game environment for black-box game testing.
"""
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import cv2
import time

from services.env.screen_capture import ScreenCapture
from services.env.action_executor import ActionExecutor
from services.env.state_processor import StateProcessor
from services.env.reward_engine import RewardEngine
from services.env.racing_reward_engine import RacingRewardEngine, RacingState
from services.env.racing_state_tracker import RacingStateTracker
from services.analytics.coverage_tracker import CoverageTracker
from services.analytics.crash_detector import CrashDetector
from config.settings import settings


class GameEnv(gym.Env):
    """
    Custom OpenAI/Gym Environment for Black-Box Game Testing.
    Features:
    - Real-time Screen Capture (MSS)
    - OS-Level Input Simulation (PyAutoGUI)
    - Automated Reward Calculation based on testing objectives (bugs/coverage)
    """
    metadata = {'render.modes': ['human', 'rgb_array']}

    def __init__(self, config=None):
        super(GameEnv, self).__init__()
        self.config = config or {}
        
        # 1. Initialize Components
        self.screen_capture = ScreenCapture()
        window_hwnd = self.config.get("window_hwnd")
        self.action_executor = ActionExecutor(window_hwnd=window_hwnd)
        self.state_processor = StateProcessor()
        
        # Use racing-specific reward engine for racing games
        self.genre = self.config.get("genre", "platformer")
        if self.genre == "racing":
            self.reward_engine = RacingRewardEngine()
            self.racing_state_tracker = RacingStateTracker()
            self.episode_count = 0
        else:
            self.reward_engine = RewardEngine()
            self.racing_state_tracker = None
        
        self.coverage_tracker = CoverageTracker()
        self.crash_detector = CrashDetector()
        
        # 2. Define Spaces
        # Observation: Stacked Grayscale Frames
        # Note: Stable-Baselines3 CnnPolicy (NatureCNN) expects channel-first format (C, H, W)
        # So we use (FRAME_STACK_SIZE, IMG_HEIGHT, IMG_WIDTH) instead of (IMG_HEIGHT, IMG_WIDTH, FRAME_STACK_SIZE)
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, 
            shape=(settings.FRAME_STACK_SIZE, settings.IMG_HEIGHT, settings.IMG_WIDTH), 
            dtype=np.float32
        )
        
        # Action: Genre dependent (already set above)
        if self.genre == "racing":
            # Continuous: [Steer, Gas/Brake]
            self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(2,), dtype=np.float32)
        elif self.genre == "fps":
            # Discrete: Move + Look combination? Or Complex? 
            # Keeping simple for now: W, A, S, D, Shoot, Jump
            self.action_space = spaces.Discrete(6)
        else: # Platformer / Default
            # Left, Right, Jump, None
            self.action_space = spaces.Discrete(4)
            
        self.current_obs = None
        self.last_hash = None

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        # Reset components
        self.state_processor.reset()
        self.action_executor.reset() # Release keys
        self.reward_engine.reset()
        
        # Reset racing-specific components
        if self.genre == "racing" and self.racing_state_tracker:
            self.racing_state_tracker.reset()
            # Increment episode count for escalating crash penalties
            self.episode_count += 1
            self.reward_engine.reset(episode=self.episode_count)
        
        # Capture initial frame to fill stack
        raw_frame = self.screen_capture.capture()
        self.current_obs = self.state_processor.process(raw_frame)
        
        return self.current_obs, {}

    def step(self, action):
        import numpy as np
        from utils.logging import get_logger
        
        logger = get_logger(__name__)
        
        # 1. Execute Action
        current_action = None  # Store for state tracking
        
        if self.genre == "racing":
            # Convert action to proper format if needed
            if isinstance(action, np.ndarray):
                action = action.flatten()
            elif hasattr(action, '__len__'):
                action = np.array(action).flatten()
            
            # Store action for state tracking (before smoothing)
            current_action = action.copy() if hasattr(action, 'copy') else np.array(action)
            
            # TASK 4: Ensure window is focused before input (handled in action_executor)
            # Action smoothing and clamping happen inside apply_continuous_action
            self.action_executor.apply_continuous_action(action)
        else:
            # Map index to key
            # Simple mapping for Platformer
            key_map = {0: 'nop', 1: 'left', 2: 'right', 3: 'space'}
            if self.genre == "fps":
                 key_map = {0: 'w', 1: 'a', 2: 's', 3: 'd', 4: 'space', 5: 'click'}
                 
            self.action_executor.apply_discrete_action(key_map, int(action))
            
        # 2. Capture New State
        # Small delay to let action have effect in the game
        time.sleep(0.03)
        
        raw_frame = self.screen_capture.capture()
        self.current_obs = self.state_processor.process(raw_frame)
        
        # 3. Analyze State (Coverage & Crash)
        # We need the hash from coverage tracker, or just let it update
        coverage_metrics = self.coverage_tracker.update(raw_frame) # Takes raw frame
        
        # 4. Check Crash/Freeze
        # We need to extract the hash again or CoverageTracker returns it?
        # CoverageTracker refactor: return hash or handle internally?
        # I used CoverageTracker.update to return {is_new...}.
        # I'll rely on CrashDetector using hashes.
        # NOTE: StateProcessor converts to gray. ScreenCapture returns BGR.
        # CoverageTracker computes hash from BGR->Gray.
        # CrashDetector needs hash. I need to expose hash from CoverageTracker or recompute.
        # For efficiency, recomputing hash on small image is cheap.
        
        # Hack: Pass hash logic manually here or trust the metrics.
        # Let's detect freeze via `is_new_state` being false for many steps? 
        # No, `is_new_state`=False just means we visited it before. 
        # Freeze means PIXEL PERFECT match for N seconds.
        # I will let CrashDetector do its own hash on raw frame (cheap).
        
        # Get Frame Hash for crash detector
        gray = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2GRAY)
        small = cv2.resize(gray, (8, 8))
        current_hash = hex(int("".join(['1' if x > small.mean() else '0' for x in (small > small.mean()).flatten()]), 2))
        
        crash_metrics = self.crash_detector.check(current_hash)
        
        # 5. Calculate Reward (racing-specific or generic)
        if self.genre == "racing" and self.racing_state_tracker and current_action is not None:
            # Use racing-specific reward engine
            prev_state = getattr(self, '_prev_racing_state', None)
            current_state = self.racing_state_tracker.update(
                current_action, coverage_metrics, crash_metrics, prev_state
            )
            
            # Compute reward using racing reward engine
            reward = self.reward_engine.compute_reward(
                current_state, prev_state, self.episode_count
            )
            
            # Store state for next step
            self._prev_racing_state = current_state
            
            # TASK 4: Debug logging (speed, delta_progress, reward, steering)
            delta_progress = current_state.track_progress - (prev_state.track_progress if prev_state else 0.0)
            logger.info(
                f"[RACING] Step {self.racing_state_tracker.episode_step} | "
                f"Speed: {current_state.speed:.3f} | "
                f"DeltaProgress: {delta_progress:.3f} | "
                f"Reward: {reward:.3f} | "
                f"Steering: {current_state.steering:.3f} | "
                f"DistCenter: {current_state.distance_from_center:.3f}"
            )
            
            # TASK 1: Immediate termination on collision or off-track
            terminated = current_state.collision or current_state.off_track
            truncated = False
            
            info = {
                "coverage": coverage_metrics,
                "crash": crash_metrics,
                "racing_state": {
                    "speed": current_state.speed,
                    "steering": current_state.steering,
                    "distance_from_center": current_state.distance_from_center,
                    "track_progress": current_state.track_progress,
                    "collision": current_state.collision,
                    "off_track": current_state.off_track,
                    "lap_completed": current_state.lap_completed
                }
            }
        else:
            # Use generic reward engine for non-racing games
            event_flags = {
                "is_new_state": coverage_metrics["is_new"],
                "is_rare_state": coverage_metrics["is_rare"],
                "is_crash": crash_metrics["is_crash"],
                "is_freeze": crash_metrics["is_freeze"],
                "is_death": False,
                "is_idle": False
            }
            
            reward = self.reward_engine.calculate(event_flags)
            
            # 6. Check Done
            terminated = False
            truncated = False
            
            if crash_metrics["is_crash"] or crash_metrics["is_freeze"]:
                terminated = True
            
            info = {
                "coverage": coverage_metrics,
                "crash": crash_metrics
            }
        
        return self.current_obs, reward, terminated, truncated, info

    def render(self, mode='human'):
        # Already capturing screen, maybe show cv2 window?
        pass

    def close(self):
        self.screen_capture.close()
        self.action_executor.reset()

