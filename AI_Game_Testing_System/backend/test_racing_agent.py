"""
Quick test script to verify the racing RL agent is working correctly.

Run this to check:
1. Environment initialization
2. SAC agent initialization
3. Action space compatibility
4. Observation space compatibility
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.env.game_env import GameEnv
from services.agents.sac_agent import SACAgent
from services.strategy_selector import StrategySelector
from utils.logging import get_logger

logger = get_logger(__name__)


def test_racing_agent():
    """Test the racing game RL agent setup."""
    print("=" * 60)
    print("RACING RL AGENT VERIFICATION TEST")
    print("=" * 60)
    
    # Test 1: Strategy Selection
    print("\n[1] Testing Strategy Selection...")
    try:
        agent_cls = StrategySelector.select_strategy("racing")
        print(f"✅ Strategy selected: {agent_cls.__name__}")
        assert agent_cls.__name__ == "SACAgent", "Wrong agent selected!"
    except Exception as e:
        print(f"❌ Strategy selection failed: {e}")
        return False
    
    # Test 2: Environment Initialization
    print("\n[2] Testing Environment Initialization...")
    try:
        env = GameEnv(config={"genre": "racing"})
        print(f"✅ Environment created successfully")
        print(f"   - Genre: {env.genre}")
        print(f"   - Action Space: {env.action_space}")
        print(f"   - Observation Space: {env.observation_space}")
        
        # Verify action space
        assert hasattr(env.action_space, 'shape'), "Action space should be Box"
        assert env.action_space.shape == (2,), f"Expected shape (2,), got {env.action_space.shape}"
        print(f"   ✅ Action space correct: {env.action_space.shape}")
        
        # Verify observation space
        expected_obs_shape = (84, 84, 4)  # (H, W, C)
        assert env.observation_space.shape == expected_obs_shape, \
            f"Expected {expected_obs_shape}, got {env.observation_space.shape}"
        print(f"   ✅ Observation space correct: {env.observation_space.shape}")
        
    except Exception as e:
        print(f"❌ Environment initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Agent Initialization
    print("\n[3] Testing SAC Agent Initialization...")
    try:
        agent = agent_cls(env, config={})
        print(f"✅ SAC Agent initialized successfully")
        print(f"   - Agent type: {type(agent).__name__}")
        print(f"   - Model type: {type(agent.model).__name__}")
        
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        print("\nPossible issues:")
        print("  - Memory allocation error (check buffer_size)")
        print("  - Observation space mismatch")
        print("  - Missing dependencies")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Environment Reset
    print("\n[4] Testing Environment Reset...")
    try:
        obs, info = env.reset()
        print(f"✅ Environment reset successful")
        print(f"   - Observation shape: {obs.shape}")
        print(f"   - Observation dtype: {obs.dtype}")
        print(f"   - Observation range: [{obs.min():.3f}, {obs.max():.3f}]")
        
        assert obs.shape == expected_obs_shape, f"Wrong observation shape: {obs.shape}"
        print(f"   ✅ Observation shape matches expected: {expected_obs_shape}")
        
    except Exception as e:
        print(f"❌ Environment reset failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 5: Action Execution
    print("\n[5] Testing Action Execution...")
    try:
        # Test continuous action
        test_action = [0.5, 0.8]  # [steering right, throttle]
        print(f"   Testing action: {test_action}")
        
        obs, reward, terminated, truncated, info = env.step(test_action)
        print(f"✅ Action executed successfully")
        print(f"   - Reward: {reward}")
        print(f"   - Terminated: {terminated}")
        print(f"   - Info keys: {list(info.keys())}")
        
    except Exception as e:
        print(f"❌ Action execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 6: Agent Prediction
    print("\n[6] Testing Agent Prediction...")
    try:
        action = agent.act(obs)
        print(f"✅ Agent prediction successful")
        print(f"   - Action: {action}")
        print(f"   - Action shape: {action.shape if hasattr(action, 'shape') else 'scalar'}")
        print(f"   - Action type: {type(action)}")
        
        # Verify action is in valid range
        if hasattr(action, '__len__') and len(action) == 2:
            assert -1.0 <= action[0] <= 1.0, f"Steering out of range: {action[0]}"
            assert -1.0 <= action[1] <= 1.0, f"Throttle out of range: {action[1]}"
            print(f"   ✅ Action values in valid range [-1.0, 1.0]")
        
    except Exception as e:
        print(f"❌ Agent prediction failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Cleanup
    print("\n[7] Cleaning up...")
    try:
        env.close()
        print("✅ Environment closed successfully")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - Racing Agent is Working!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_racing_agent()
    sys.exit(0 if success else 1)
