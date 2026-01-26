from backend.agents.dqn_agent import DQNAgent
from backend.agents.ppo_agent import PPOAgent
from backend.agents.sac_agent import SACAgent
from backend.agents.hrl_agent import HRLAgent

class StrategySelector:
    """
    Selects the appropriate RL Strategy (Agent) based on Game Genre.
    """
    
    @staticmethod
    def select_strategy(genre: str):
        """
        Returns the Agent Class and Config needed for the genre.
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
