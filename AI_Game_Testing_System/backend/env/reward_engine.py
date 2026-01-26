class RewardEngine:
    """
    Calculates rewards for the RL agent.
    Unlike traditional RL, this engine optimizes for:
    1. Coverage (New Exploration)
    2. Edge Case Discovery (Crashes/Freezes)
    3. Game Progression (optional, to reach deeper states)
    """
    def __init__(self):
        self.total_reward = 0.0

    def calculate(self, event_flags: dict) -> float:
        """
        Compute reward based on events detected in the current step.
        
        Args:
            event_flags (dict):
                - is_new_state (bool): Captured frame hash indicates new state.
                - is_rare_state (bool): State visited very few times.
                - is_crash (bool): Process crashed.
                - is_freeze (bool): Screen didn't change for N frames.
                - is_idle (bool): Agent output no effective action.
                - is_death (bool): Game over detected (negative).
                
        Returns:
            float: The reward value.
        """
        reward = 0.0

        if event_flags.get("is_crash"):
            # Jackpot! Objective of testing is to find bugs.
            reward += 10.0
        
        if event_flags.get("is_freeze"):
            # Also good, indicates performance issue or hang.
            reward += 5.0
            
        if event_flags.get("is_new_state"):
            # Encourages exploration of map/menus.
            reward += 1.0
            
        if event_flags.get("is_rare_state"):
            reward += 2.0
            
        if event_flags.get("is_death"):
            # Failure to survive might prevent finding deeper bugs.
            reward -= 1.0
            
        if event_flags.get("is_idle"):
            # Penalize doing nothing.
            reward -= 0.1
            
        self.total_reward += reward
        return reward

    def reset(self):
        self.total_reward = 0.0
