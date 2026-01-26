from backend.core.base_agent import BaseRLAgent
from stable_baselines3 import PPO
import os

class PPOAgent(BaseRLAgent):
    """
    Proximal Policy Optimization (PPO) Agent.
    Robust baseline for both Discrete and Continuous tasks.
    """
    def __init__(self, env, config):
        super().__init__(env, config)
        self.model = PPO(
            "CnnPolicy", 
            env, 
            verbose=1,
            learning_rate=3e-4,
            n_steps=2048,
            batch_size=64,
            n_epochs=10,
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.2,
            ent_coef=0.01, # Encourage exploration
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
            self.model = PPO.load(path, env=self.env)
