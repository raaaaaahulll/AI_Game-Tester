"""
Racing state tracker for black-box game testing.

Estimates racing state variables from:
- Actions (steering, throttle)
- Coverage metrics (progress estimation)
- Crash detection (collision, off-track)
"""
from services.env.racing_reward_engine import RacingState
from utils.logging import get_logger

logger = get_logger(__name__)


class RacingStateTracker:
    """
    Tracks racing game state from black-box observations.
    
    Since we don't have direct access to game state, we estimate:
    - Speed: from throttle input and coverage changes
    - Steering: from action directly
    - Distance from center: estimated from steering oscillation
    - Track progress: from coverage metrics (unique states visited)
    - Collision: from crash detector
    - Off-track: from crash detector or freeze detection
    - Lap completed: from significant progress reset
    """
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset state tracker for new episode."""
        self.initial_coverage = 0
        self.total_unique_states = 0
        self.last_coverage_count = 0
        self.episode_step = 0
        self.estimated_speed = 0.0
        self.estimated_progress = 0.0
        self.last_progress = 0.0
        self.lap_completed = False
        
    def update(self, action, coverage_metrics, crash_metrics, prev_state=None):
        """
        Update racing state from current observations.
        
        Args:
            action: [steering, throttle] action vector
            coverage_metrics: Dict with 'is_new', 'is_rare', 'count', etc.
            crash_metrics: Dict with 'is_crash', 'is_freeze'
            prev_state: Previous RacingState (optional)
            
        Returns:
            RacingState: Current racing state
        """
        self.episode_step += 1
        
        # Extract action values
        steering = float(action[0]) if len(action) > 0 else 0.0
        throttle = float(action[1]) if len(action) > 1 else 0.0
        
        # Estimate speed from throttle (simplified model)
        # Positive throttle increases speed, negative decreases
        if throttle > 0:
            self.estimated_speed = min(1.0, self.estimated_speed + 0.1 * throttle)
        elif throttle < 0:
            self.estimated_speed = max(0.0, self.estimated_speed + 0.2 * throttle)  # Brake faster
        
        # Apply friction (speed decays over time)
        self.estimated_speed *= 0.95
        
        # Estimate progress from coverage (unique states visited)
        current_coverage = coverage_metrics.get("count", 0)
        if self.episode_step == 1:
            self.initial_coverage = current_coverage
            self.last_coverage_count = current_coverage
        
        # Progress = increase in unique states
        delta_coverage = current_coverage - self.last_coverage_count
        self.estimated_progress += max(0, delta_coverage * 0.01)  # Scale coverage to progress
        self.last_coverage_count = current_coverage
        
        # Estimate distance from center from steering magnitude
        # More steering = further from center (simplified)
        distance_from_center = abs(steering) * 0.5
        
        # Detect collision and off-track
        collision = crash_metrics.get("is_crash", False)
        off_track = crash_metrics.get("is_freeze", False) or collision
        
        # Detect lap completion (progress reset or significant milestone)
        # This is a heuristic - in real implementation, would need game state
        if prev_state and self.estimated_progress > 100 and prev_state.track_progress > 50:
            # Significant progress suggests lap completion
            self.lap_completed = True
        else:
            self.lap_completed = False
        
        # Create racing state
        state = RacingState(
            speed=self.estimated_speed,
            steering=steering,
            distance_from_center=distance_from_center,
            track_progress=self.estimated_progress,
            collision=collision,
            off_track=off_track,
            lap_completed=self.lap_completed
        )
        
        return state
