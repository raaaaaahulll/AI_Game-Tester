"""
Racing-specific reward engine for SAC-based racing game agents.

Optimizes for:
1. Forward progress (PRIMARY objective)
2. Stability (penalize steering oscillation)
3. Track centering (penalize distance from center)
4. Speed control (dynamic based on steering)
5. Crash avoidance (escalating penalties)
"""
from utils.logging import get_logger

logger = get_logger(__name__)


class RacingState:
    """Container for racing game state variables."""
    def __init__(self, speed=0.0, steering=0.0, distance_from_center=0.0, 
                 track_progress=0.0, collision=False, off_track=False, 
                 lap_completed=False):
        self.speed = float(speed)
        self.steering = float(steering)
        self.distance_from_center = float(distance_from_center)
        self.track_progress = float(track_progress)
        self.collision = bool(collision)
        self.off_track = bool(off_track)
        self.lap_completed = bool(lap_completed)


class RacingRewardEngine:
    """
    Racing-specific reward engine that prioritizes forward progress and stability.
    
    Reward structure:
    - Forward progress: PRIMARY objective (8.0 * delta_progress)
    - Negative progress penalty: -5.0
    - Dynamic speed control: 0.1 * min(speed, safe_speed)
    - Distance from center penalty: -2.0 * abs(distance_from_center)
    - Steering oscillation penalty: -2.0 * abs(steering_delta)
    - Off-track: -80.0 (immediate termination)
    - Collision: -50 to -200 (escalating with episode)
    - Lap completion: +250.0
    """
    
    def __init__(self):
        self.total_reward = 0.0
        self.prev_state = None
        self.episode_count = 0
        self.low_speed_steps = 0  # Track consecutive low-speed steps
        
    def compute_reward(self, state: RacingState, prev_state: RacingState = None, episode: int = 0) -> float:
        """
        Compute reward based on racing state.
        
        Args:
            state: Current racing state
            prev_state: Previous racing state (for delta calculations)
            episode: Current episode number (for escalating crash penalties)
            
        Returns:
            float: Reward value
        """
        reward = 0.0
        
        # Use provided prev_state or stored one
        if prev_state is None:
            prev_state = self.prev_state
        
        # Initialize prev_state if first step
        if prev_state is None:
            prev_state = RacingState(
                speed=state.speed,
                steering=state.steering,
                distance_from_center=state.distance_from_center,
                track_progress=state.track_progress
            )
        
        # 1. Forward progress (MOST IMPORTANT)
        delta_progress = state.track_progress - prev_state.track_progress
        reward += 8.0 * delta_progress
        
        # Penalize negative or zero progress
        if delta_progress <= 0:
            reward -= 5.0
        
        # 2. Dynamic speed control based on steering
        # Reduce safe speed when steering heavily
        safe_speed = 0.5 if abs(state.steering) > 0.3 else 1.0
        reward += 0.1 * min(state.speed, safe_speed)
        
        # Track low speed for idle detection
        if state.speed < 0.5:
            self.low_speed_steps += 1
            if self.low_speed_steps > 10:  # N steps threshold
                reward -= 0.5  # Small penalty for being stuck
        else:
            self.low_speed_steps = 0
        
        # 3. Stability penalties
        # Penalize distance from track center
        reward -= 2.0 * abs(state.distance_from_center)
        
        # Penalize steering oscillation (difference between steps)
        steering_delta = abs(state.steering - prev_state.steering)
        reward -= 2.0 * steering_delta
        
        # 4. Critical penalties (immediate termination)
        if state.off_track:
            logger.warning(f"Off-track detected! Reward: -80.0")
            return -80.0
        
        if state.collision:
            # Escalate crash penalty with episode count
            crash_penalty = min(200, 50 + episode * 2)
            logger.warning(f"Collision detected! Episode: {episode}, Penalty: -{crash_penalty}")
            return -crash_penalty
        
        # 5. Lap completion bonus
        if state.lap_completed:
            reward += 250.0
            logger.info(f"Lap completed! Bonus: +250.0")
        
        # Store current state as previous for next step
        self.prev_state = RacingState(
            speed=state.speed,
            steering=state.steering,
            distance_from_center=state.distance_from_center,
            track_progress=state.track_progress,
            collision=state.collision,
            off_track=state.off_track,
            lap_completed=state.lap_completed
        )
        
        self.total_reward += reward
        
        # Debug logging
        logger.debug(
            f"Reward: {reward:.3f} | "
            f"Progress: {delta_progress:.3f} | "
            f"Speed: {state.speed:.3f} | "
            f"Steering: {state.steering:.3f} | "
            f"DistCenter: {state.distance_from_center:.3f}"
        )
        
        return reward
    
    def reset(self, episode: int = 0):
        """Reset reward engine for new episode."""
        self.total_reward = 0.0
        self.prev_state = None
        self.episode_count = episode
        self.low_speed_steps = 0
        logger.debug(f"Reward engine reset for episode {episode}")
