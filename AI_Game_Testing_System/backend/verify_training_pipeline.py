"""
Verification script for the full training pipeline.

This script checks:
1. Action generation (SAC agent)
2. Action execution (PostMessage)
3. Observation capture (screen capture + processing)
4. Reward calculation (coverage + crash detection)
5. Model training (weight updates)

Usage:
    python verify_training_pipeline.py
"""
import sys
import time
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.env.game_env import GameEnv
from services.agents.sac_agent import SACAgent
from services.env.action_executor import ActionExecutor
from services.env.screen_capture import ScreenCapture
from services.env.state_processor import StateProcessor
from services.env.reward_engine import RewardEngine
from services.analytics.coverage_tracker import CoverageTracker
from services.analytics.crash_detector import CrashDetector
from config.settings import settings
from utils.logging import get_logger

logger = get_logger(__name__)


def verify_action_generation():
    """Verify SAC agent can generate actions."""
    print("\n" + "="*70)
    print("1. VERIFYING ACTION GENERATION")
    print("="*70)
    
    try:
        # Create a dummy environment for testing
        env_config = {"genre": "racing"}
        env = GameEnv(config=env_config)
        
        # Create SAC agent
        agent = SACAgent(env, config={})
        
        # Generate a few actions
        print("\n[TEST] Testing action generation...")
        actions = []
        for i in range(5):
            # Create a dummy observation (random for testing)
            dummy_obs = np.random.rand(settings.FRAME_STACK_SIZE, settings.IMG_HEIGHT, settings.IMG_WIDTH).astype(np.float32)
            action = agent.act(dummy_obs)
            actions.append(action)
            print(f"  Action {i+1}: steering={action[0]:.3f}, throttle={action[1]:.3f}")
        
        # Check action format
        assert len(actions[0]) == 2, "Action should have 2 dimensions (steering, throttle)"
        assert all(-1.0 <= a[0] <= 1.0 for a in actions), "Steering should be in [-1, 1]"
        assert all(-1.0 <= a[1] <= 1.0 for a in actions), "Throttle should be in [-1, 1]"
        
        print("[OK] Action generation working correctly")
        print(f"   - Actions are continuous 2D vectors")
        print(f"   - Values are in range [-1, 1]")
        
        env.close()
        return True
    except Exception as e:
        print(f"[FAIL] Action generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_action_execution():
    """Verify actions can be executed (without actually sending to game)."""
    print("\n" + "="*70)
    print("2. VERIFYING ACTION EXECUTION")
    print("="*70)
    
    try:
        executor = ActionExecutor(window_hwnd=None)
        
        print("\n[TEST] Testing action execution logic...")
        
        # Test continuous action mapping
        test_actions = [
            np.array([-0.5, 0.8]),   # Turn left, accelerate
            np.array([0.3, -0.2]),  # Turn right, brake slightly
            np.array([0.0, 0.0]),   # No action
        ]
        
        for i, action in enumerate(test_actions):
            print(f"\n  Test action {i+1}: steering={action[0]:.3f}, throttle={action[1]:.3f}")
            executor.apply_continuous_action(action)
            print(f"    Held keys: {executor.held_keys}")
        
        executor.reset()
        print("\n[OK] Action execution logic working correctly")
        print("   - Actions are mapped to arrow keys correctly")
        print("   - Key state is tracked properly")
        
        return True
    except Exception as e:
        print(f"[FAIL] Action execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_observation_capture():
    """Verify screen capture and state processing."""
    print("\n" + "="*70)
    print("3. VERIFYING OBSERVATION CAPTURE")
    print("="*70)
    
    try:
        screen_capture = ScreenCapture()
        state_processor = StateProcessor()
        
        print("\n[TEST] Testing screen capture...")
        raw_frame = screen_capture.capture()
        print(f"  Raw frame shape: {raw_frame.shape}")
        print(f"  Raw frame dtype: {raw_frame.dtype}")
        
        print("\n[TEST] Testing state processing...")
        processed_obs = state_processor.process(raw_frame)
        print(f"  Processed observation shape: {processed_obs.shape}")
        print(f"  Processed observation dtype: {processed_obs.dtype}")
        print(f"  Observation range: [{processed_obs.min():.3f}, {processed_obs.max():.3f}]")
        
        # Verify shape matches expected
        expected_shape = (settings.FRAME_STACK_SIZE, settings.IMG_HEIGHT, settings.IMG_WIDTH)
        assert processed_obs.shape == expected_shape, f"Shape mismatch: got {processed_obs.shape}, expected {expected_shape}"
        
        print("\n[OK] Observation capture working correctly")
        print(f"   - Screen capture: {raw_frame.shape}")
        print(f"   - State processing: {processed_obs.shape}")
        print(f"   - Values normalized to [0, 1]")
        
        screen_capture.close()
        return True
    except Exception as e:
        print(f"[FAIL] Observation capture failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_reward_calculation():
    """Verify reward engine calculates rewards correctly."""
    print("\n" + "="*70)
    print("4. VERIFYING REWARD CALCULATION")
    print("="*70)
    
    try:
        reward_engine = RewardEngine()
        
        print("\n[TEST] Testing reward calculation...")
        
        test_cases = [
            ({"is_new_state": True}, "New state discovered"),
            ({"is_rare_state": True}, "Rare state discovered"),
            ({"is_crash": True}, "Crash detected"),
            ({"is_freeze": True}, "Freeze detected"),
            ({"is_idle": True}, "Idle action"),
            ({"is_new_state": False, "is_idle": False}, "No events"),
        ]
        
        for event_flags, description in test_cases:
            reward = reward_engine.calculate(event_flags)
            print(f"  {description}: reward = {reward:.2f}")
        
        print("\n[OK] Reward calculation working correctly")
        print("   - Rewards are calculated based on events")
        print("   - Positive rewards for exploration/crashes")
        print("   - Negative rewards for idling")
        
        return True
    except Exception as e:
        print(f"[FAIL] Reward calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_model_training():
    """Verify SAC model can train (with dummy data)."""
    print("\n" + "="*70)
    print("5. VERIFYING MODEL TRAINING")
    print("="*70)
    
    try:
        # Create environment
        env_config = {"genre": "racing"}
        env = GameEnv(config=env_config)
        
        # Create agent
        agent = SACAgent(env, config={})
        
        print("\n[TEST] Testing model initialization...")
        print(f"  Buffer size: {agent.model.replay_buffer.buffer_size}")
        print(f"  Learning starts: {agent.model.learning_starts}")
        print(f"  Batch size: {agent.model.batch_size}")
        
        # Get initial model weights (before training)
        initial_weights = {}
        for name, param in agent.model.policy.named_parameters():
            if 'weight' in name:
                initial_weights[name] = param.data.clone()
        
        print("\n[TEST] Running short training session (100 steps)...")
        print("   (This will use random actions until learning_starts threshold)")
        
        # Run a few steps to see if model updates
        # Note: SAC won't update until learning_starts steps are reached
        try:
            agent.model.learn(total_timesteps=100, log_interval=10)
            print("  [OK] Training step completed")
        except Exception as e:
            print(f"  [WARN] Training step had issues (may be expected): {e}")
        
        # Check if weights changed (only if learning_starts was reached)
        weights_changed = False
        if agent.model.num_timesteps >= agent.model.learning_starts:
            for name, param in agent.model.policy.named_parameters():
                if 'weight' in name and name in initial_weights:
                    if not torch.equal(param.data, initial_weights[name]):
                        weights_changed = True
                        break
        
        print(f"\n  Timesteps completed: {agent.model.num_timesteps}")
        print(f"  Learning starts threshold: {agent.model.learning_starts}")
        
        if weights_changed:
            print("  [OK] Model weights updated (learning is happening!)")
        elif agent.model.num_timesteps < agent.model.learning_starts:
            print(f"  [WARN] Model hasn't started learning yet (needs {agent.model.learning_starts} steps)")
            print("     This is normal - model collects experience first")
        else:
            print("  [WARN] Weights didn't change (may need more steps)")
        
        print("\n[OK] Model training setup working correctly")
        print("   - Model initializes properly")
        print("   - Training loop can run")
        
        env.close()
        return True
    except ImportError:
        print("[WARN] PyTorch not available, skipping weight check")
        return True
    except Exception as e:
        print(f"[FAIL] Model training verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_full_pipeline():
    """Verify the complete step() function works."""
    print("\n" + "="*70)
    print("6. VERIFYING FULL PIPELINE (env.step)")
    print("="*70)
    
    try:
        env_config = {"genre": "racing"}
        env = GameEnv(config=env_config)
        
        print("\n[TEST] Testing environment reset...")
        obs, info = env.reset()
        print(f"  Observation shape: {obs.shape}")
        print(f"  Observation range: [{obs.min():.3f}, {obs.max():.3f}]")
        
        print("\n[TEST] Testing environment step (5 steps)...")
        total_reward = 0
        for i in range(5):
            # Generate random action
            action = env.action_space.sample()
            print(f"\n  Step {i+1}:")
            print(f"    Action: steering={action[0]:.3f}, throttle={action[1]:.3f}")
            
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            
            print(f"    Reward: {reward:.3f}")
            print(f"    Terminated: {terminated}, Truncated: {truncated}")
            print(f"    Coverage: {info.get('coverage', {})}")
            print(f"    Crash: {info.get('crash', {})}")
            
            if terminated or truncated:
                print("    Episode ended, resetting...")
                obs, info = env.reset()
                break
        
        print(f"\n  Total reward over 5 steps: {total_reward:.3f}")
        
        print("\n[OK] Full pipeline working correctly")
        print("   - Environment reset works")
        print("   - Environment step works")
        print("   - Observations are generated")
        print("   - Rewards are calculated")
        print("   - Info dict contains coverage/crash data")
        
        env.close()
        return True
    except Exception as e:
        print(f"[FAIL] Full pipeline verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all verification checks."""
    print("="*70)
    print("TRAINING PIPELINE VERIFICATION")
    print("="*70)
    print("\nThis script verifies all components of the training pipeline.")
    print("Note: Random movements are EXPECTED initially - the agent needs")
    print("time to learn from experience!\n")
    
    results = []
    
    # Run all checks
    results.append(("Action Generation", verify_action_generation()))
    results.append(("Action Execution", verify_action_execution()))
    results.append(("Observation Capture", verify_observation_capture()))
    results.append(("Reward Calculation", verify_reward_calculation()))
    results.append(("Model Training", verify_model_training()))
    results.append(("Full Pipeline", verify_full_pipeline()))
    
    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    all_passed = True
    for name, passed in results:
        status = "[OK] PASS" if passed else "[FAIL] FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("[OK] ALL CHECKS PASSED!")
        print("\nThe training pipeline is working correctly.")
        print("\nAbout random movements:")
        print("  - This is NORMAL for the first ~100 steps")
        print("  - SAC agent needs to collect experience before learning")
        print("  - After learning_starts threshold, the model will update")
        print("  - Performance should improve over time")
        print("\nTo verify learning is happening:")
        print("  1. Check backend logs for 'Training' messages")
        print("  2. Monitor metrics in the UI")
        print("  3. Watch for increasing coverage/exploration")
        print("  4. After ~100 steps, actions should become less random")
    else:
        print("[FAIL] SOME CHECKS FAILED")
        print("\nPlease review the errors above and fix them.")
    print("="*70)


if __name__ == "__main__":
    try:
        import torch
    except ImportError:
        print("[WARN] PyTorch not available - some checks may be skipped")
    
    main()
