"""
Strategy selector for choosing RL agents based on game genre.
"""
from services.agents.dqn_agent import DQNAgent
from services.agents.ppo_agent import PPOAgent
from services.agents.sac_agent import SACAgent
from services.agents.hrl_agent import HRLAgent


class StrategySelector:
    """
    Selects the appropriate RL Strategy (Agent) based on Game Genre.
    """
    
    @staticmethod
    def select_strategy(genre: str):
        """
        Returns the Agent Class and Config needed for the genre.
        
        Args:
            genre: Game genre string
            
        Returns:
            Agent class
        """
        genre = genre.lower()
        
        if genre == 'platformer':
            return DQNAgent
        elif genre == 'fps':
            return PPOAgent
        elif genre == 'racing':
            return SACAgent
        elif genre == 'rpg':
            return HRLAgent
        else:
            # Default to PPO as it is robust
            return PPOAgent

