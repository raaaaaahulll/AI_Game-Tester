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
        self.action_executor = ActionExecutor()
        self.state_processor = StateProcessor()
        self.reward_engine = RewardEngine()
        self.coverage_tracker = CoverageTracker()
        self.crash_detector = CrashDetector()
        
        # 2. Define Spaces
        # Observation: Stacked Grayscale Frames
        # Note: Stable-Baselines3 CnnPolicy expects channel-last format (H, W, C)
        # So we use (IMG_HEIGHT, IMG_WIDTH, FRAME_STACK_SIZE) instead of (FRAME_STACK_SIZE, IMG_HEIGHT, IMG_WIDTH)
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, 
            shape=(settings.IMG_HEIGHT, settings.IMG_WIDTH, settings.FRAME_STACK_SIZE), 
            dtype=np.float32
        )
        
        # Action: Genre dependent
        self.genre = self.config.get("genre", "platformer")
        
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
        
        # Capture initial frame to fill stack
        raw_frame = self.screen_capture.capture()
        self.current_obs = self.state_processor.process(raw_frame)
        
        return self.current_obs, {}

    def step(self, action):
        # 1. Execute Action
        if self.genre == "racing":
            self.action_executor.apply_continuous_action(action)
        else:
            # Map index to key
            # Simple mapping for Platformer
            key_map = {0: 'nop', 1: 'left', 2: 'right', 3: 'space'}
            if self.genre == "fps":
                 key_map = {0: 'w', 1: 'a', 2: 's', 3: 'd', 4: 'space', 5: 'click'}
                 
            self.action_executor.apply_discrete_action(key_map, int(action))
            
        # 2. Capture New State
        # Wait a small fraction to let action have effect? 
        # Typically Env runs as fast as possible, but real games have lag.
        # time.sleep(0.05) # Optional loop delay
        
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
        
        # 5. Calculate Reward
        # Merge metrics
        event_flags = {
            "is_new_state": coverage_metrics["is_new"],
            "is_rare_state": coverage_metrics["is_rare"],
            "is_crash": crash_metrics["is_crash"],
            "is_freeze": crash_metrics["is_freeze"],
            "is_death": False, # TODO: Optical Character Recognition for "GAME OVER" or Red Screen
            "is_idle": False # TODO: Check if action was NOP
        }
        
        reward = self.reward_engine.calculate(event_flags)
        
        # 6. Check Done
        terminated = False
        truncated = False
        
        if crash_metrics["is_crash"] or crash_metrics["is_freeze"]:
            terminated = True # End episode on crash (Validation success)
            
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

