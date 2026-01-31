"""
Soft Actor-Critic (SAC) Agent implementation.

Off-policy, entropy-regularized. Best for Continuous Control (Racing).
"""
import os
from stable_baselines3 import SAC

from services.agents.base_agent import BaseRLAgent


class SACAgent(BaseRLAgent):
    """
    Soft Actor-Critic (SAC) Agent.
    Off-policy, entropy-regularized. Best for Continuous Control (Racing).
    """
    def __init__(self, env, config):
        super().__init__(env, config)
        # SAC requires Continuous Action Space
        # Memory-optimized configuration for systems with limited RAM
        self.model = SAC(
            "CnnPolicy", 
            env, 
            verbose=1,
            learning_rate=3e-4,
            buffer_size=2000,  # Significantly reduced to ~200 MB (from 1.05 GiB)
            learning_starts=100,  # Reduced proportionally
            batch_size=16,  # Smaller batch size to save memory
            tau=0.005,
            gamma=0.99,
            train_freq=1,
            gradient_steps=1,
            ent_coef='auto',
            policy_kwargs=dict(normalize_images=False),  # Images are already normalized to [0, 1] in StateProcessor
            tensorboard_log=self.config.get("log_dir")
        )

    def train(self, timesteps):
        self.model.learn(total_timesteps=timesteps)

    def act(self, state):
        action, _ = self.model.predict(state, deterministic=True)
        return action

    def save(self, path):
        self.model.save(path)

    def load(self, path):
        if os.path.exists(path):
            self.model = SAC.load(path, env=self.env)

