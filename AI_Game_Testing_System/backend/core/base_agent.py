from abc import ABC, abstractmethod
import os
import gymnasium as gym

class BaseRLAgent(ABC):
    """
    Abstract Base Class for all Reinforcement Learning Agents.
    Enforces a standard interface for training, action selection, and persistence.
    """

    def __init__(self, env: gym.Env, config: dict):
        """
        Initialize the RL Agent.
        
        Args:
            env (gym.Env): The Game Environment.
            config (dict): Configuration dictionary containing hyperparameters.
        """
        self.env = env
        self.config = config
        self.model = None

    @abstractmethod
    def train(self, timesteps: int):
        """
        Train the agent for a specified number of timesteps.
        
        Args:
            timesteps (int): Total training steps.
        """
        pass

    @abstractmethod
    def act(self, state):
        """
        Select an action based on the current state.
        
        Args:
            state (np.ndarray): The current observation.
            
        Returns:
            action: The selected action.
        """
        pass

    @abstractmethod
    def save(self, path: str):
        """
        Save the agent's model to disk.
        
        Args:
            path (str): File path to save the model.
        """
        pass

    @abstractmethod
    def load(self, path: str):
        """
        Load the agent's model from disk.
        
        Args:
            path (str): File path to load the model from.
        """
        pass

    def get_metrics(self):
        """
        Retrieve current training metrics (optional implementation).
        """
        return {}
