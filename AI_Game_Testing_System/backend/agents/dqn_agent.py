"""
Deep Q-Network (DQN) Agent implementation.

Best for Discrete, Low-Dimensional action spaces (e.g. Platformers).
"""
import os
from stable_baselines3 import DQN

from backend.core.base_agent import BaseRLAgent
from backend.core.logging_config import get_logger

logger = get_logger(__name__)


class DQNAgent(BaseRLAgent):
    """
    Deep Q-Network (DQN) Agent.
    Best for Discrete, Low-Dimensional action spaces (e.g. Platformers).
    """
    def __init__(self, env, config):
        super().__init__(env, config)
        # Initialize SB3 DQN
        # CnnPolicy is used for image-based observations
        self.model = DQN(
            "CnnPolicy", 
            env, 
            verbose=1,
            learning_rate=1e-4,
            buffer_size=10000,
            learning_starts=1000,
            batch_size=32,
            tau=1.0,
            gamma=0.99,
            train_freq=4,
            gradient_steps=1,
            target_update_interval=1000,
            exploration_fraction=0.1,
            exploration_final_eps=0.02,
            tensorboard_log=self.config.get("log_dir")
        )

    def train(self, timesteps):
        logger.info(f"Training DQN for {timesteps} steps...")
        self.model.learn(total_timesteps=timesteps)

    def act(self, state):
        # State processing is handled by Env, but predict expects standardized input
        # SB3 predict handles the wrapping usually if env is vectorized
        action, _ = self.model.predict(state, deterministic=True)
        return action

    def save(self, path):
        self.model.save(path)

    def load(self, path):
        if os.path.exists(path):
            self.model = DQN.load(path, env=self.env)
        else:
            logger.warning(f"Model path not found: {path}")
