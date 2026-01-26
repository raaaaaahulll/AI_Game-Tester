from backend.core.base_agent import BaseRLAgent
from stable_baselines3 import SAC
import os

class SACAgent(BaseRLAgent):
    """
    Soft Actor-Critic (SAC) Agent.
    Off-policy, entropy-regularized. Best for Continuous Control (Racing).
    """
    def __init__(self, env, config):
        super().__init__(env, config)
        # SAC requires Continuous Action Space
        self.model = SAC(
            "CnnPolicy", 
            env, 
            verbose=1,
            learning_rate=3e-4,
            buffer_size=50000,
            learning_starts=1000,
            batch_size=64,
            tau=0.005,
            gamma=0.99,
            train_freq=1,
            gradient_steps=1,
            ent_coef='auto',
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
