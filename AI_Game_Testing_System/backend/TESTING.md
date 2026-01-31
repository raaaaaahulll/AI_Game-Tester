# Backend Testing Guide

## Overview

The backend includes a comprehensive test suite using pytest for automated testing of all API endpoints.

## Installation

Install test dependencies:

```bash
pip install -r requirements.txt
```

This includes:
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `httpx` - HTTP client for testing (used by FastAPI TestClient)

## Running Tests

### Run all tests
```bash
pytest
```

### Run with verbose output
```bash
pytest -v
```

### Run specific test file
```bash
pytest tests/test_api.py
pytest tests/test_history_api.py
pytest tests/test_validation.py
```

### Run specific test class
```bash
pytest tests/test_api.py::TestStartTest
```

### Run specific test
```bash
pytest tests/test_api.py::TestStartTest::test_start_test_success
```

### Run with coverage report
```bash
pytest --cov=backend --cov-report=html
```

Coverage report will be generated in `htmlcov/index.html`

## Test Structure

```
tests/
├── __init__.py          # Package initialization
├── conftest.py          # Pytest fixtures and configuration
├── test_api.py          # Main API endpoint tests
├── test_history_api.py  # Test history API tests
├── test_validation.py   # Validation and error handling tests
└── README.md           # Test documentation
```

## Test Coverage

### Main API Endpoints (`test_api.py`)

#### Health Endpoints
- ✅ Root endpoint (`GET /`)
- ✅ Health check (`GET /health`)

#### Start Test
- ✅ Successful test start
- ✅ Invalid genre validation
- ✅ Missing genre field
- ✅ All valid genres
- ✅ Already running error

#### Stop Test
- ✅ Successful test stop
- ✅ Not running error

#### Metrics
- ✅ Successful metrics retrieval
- ✅ Metrics structure validation

#### Status
- ✅ Successful status retrieval
- ✅ Status value validation

### Test History API (`test_history_api.py`)

#### List History
- ✅ Empty history
- ✅ History with data
- ✅ Limit parameter
- ✅ Filter by genre
- ✅ Filter by algorithm
- ✅ Filter by status

#### Get Test
- ✅ Successful test retrieval
- ✅ Test not found (404)

#### Statistics
- ✅ Empty statistics
- ✅ Statistics with data
- ✅ Aggregated calculations

#### Delete Test
- ✅ Successful deletion
- ✅ Test not found (404)

#### Clear History
- ✅ Clear all history

### Validation & Error Handling (`test_validation.py`)

#### Request Validation
- ✅ Invalid JSON
- ✅ Empty body
- ✅ Wrong data types
- ✅ Parameter validation (limits, etc.)

#### Error Handling
- ✅ 404 on invalid endpoints
- ✅ Method not allowed (405)

## Fixtures

### `client`
FastAPI TestClient instance for making HTTP requests.

```python
def test_example(client):
    response = client.get("/api/metrics")
    assert response.status_code == 200
```

### `mock_metrics_collector`
Mocks the metrics collector to return predictable values.

```python
def test_metrics(mock_metrics_collector):
    # Metrics collector is mocked
    response = client.get("/api/metrics")
    assert response.json()["status"] == "Idle"
```

### `mock_rl_controller`
Mocks the RL controller to prevent actual test execution.

```python
def test_start(mock_rl_controller):
    # RL controller is mocked
    response = client.post("/api/start-test", json={"genre": "platformer"})
    assert response.status_code == 200
```

### `reset_metrics`
Resets metrics before and after each test.

### `clear_history`
Clears test history before and after each test.

## Writing New Tests

### Example Test Structure

```python
class TestNewFeature:
    """Tests for new feature."""
    
    def test_feature_success(self, client):
        """Test successful feature operation."""
        response = client.get("/api/new-feature")
        assert response.status_code == 200
        assert "expected_field" in response.json()
    
    def test_feature_error(self, client):
        """Test feature error handling."""
        response = client.get("/api/new-feature/invalid")
        assert response.status_code == 404
```

### Best Practices

1. **Use descriptive test names**: `test_start_test_success` not `test1`
2. **One assertion per test**: Focus on one behavior
3. **Use fixtures**: Leverage existing fixtures for common setup
4. **Mock external dependencies**: Don't run actual RL training in tests
5. **Test both success and error cases**: Cover happy path and edge cases
6. **Isolate tests**: Each test should be independent

## Continuous Integration

Tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest --cov=backend --cov-report=xml
```

## Test Statistics

Run tests with statistics:

```bash
pytest --tb=short -v
```

This shows:
- Number of tests run
- Pass/fail status
- Execution time
- Coverage percentage

## Troubleshooting

### Tests fail with import errors
- Ensure you're in the backend directory
- Check that all dependencies are installed
- Verify Python path includes the backend directory

### Tests fail with database/file errors
- Tests use mocks - no actual files should be created
- Check that fixtures are properly cleaning up

### Slow test execution
- Use `-x` flag to stop on first failure: `pytest -x`
- Use `-k` to filter tests: `pytest -k "test_start"`

## Racing Agent Testing

### Overview

This section provides specific testing and verification guidance for the SAC (Soft Actor-Critic) agent used for racing games.

### Agent Configuration

**Algorithm**: SAC (Soft Actor-Critic)
- **Type**: Off-policy, actor-critic
- **Best For**: Continuous control tasks (racing games)
- **Action Space**: Continuous [Steering, Throttle/Brake]
  - Steering: -1.0 (left) to 1.0 (right)
  - Throttle: -1.0 (brake) to 1.0 (accelerate)

**Environment Setup**:
- **Observation Space**: (84, 84, 4) - Stacked grayscale frames
- **Action Space**: Box(-1.0, 1.0, shape=(2,)) - Continuous 2D actions

### Key Components

#### 1. Action Executor (`action_executor.py`)
**Status**: ✅ **FIXED** - Now implements continuous actions

**Mapping**:
- Steering < -0.15 → Press 'A' (left)
- Steering > 0.15 → Press 'D' (right)
- Throttle > 0.15 → Press 'W' (accelerate)
- Throttle < -0.15 → Press 'S' (brake)

#### 2. SAC Agent (`sac_agent.py`)
**Configuration**:
- Policy: CnnPolicy (for image inputs)
- Buffer Size: 2,000 (reduced to save memory)
- Learning Rate: 3e-4
- Batch Size: 16

#### 3. Game Environment (`game_env.py`)
**Racing Configuration**:
- Action Space: `Box(low=-1.0, high=1.0, shape=(2,))`
- Observation: Stacked frames (84x84x4)

### How to Test Racing Agent

#### Step 1: Start Backend
```bash
cd backend
python app.py
```

#### Step 2: Start Frontend
```bash
cd frontend
npm run dev
```

#### Step 3: Test Racing Agent
1. Open the dashboard at `http://localhost:5173`
2. Login/Register
3. Select **Genre: Racing**
4. Select a game window (or use auto-detect)
5. Click **"Start Testing"**

#### Step 4: Monitor Status
- Check the status indicator - should show "Training SACAgent"
- Watch metrics:
  - **State Coverage**: Should increase as agent explores
  - **Total Steps**: Should increment
  - **Active Model**: Should show "SACAgent"

### Expected Behavior

#### ✅ Working Correctly If:
1. Status changes to "Training SACAgent"
2. Metrics start updating (coverage, steps)
3. No error messages appear
4. Game window receives keyboard inputs (W, A, S, D keys)
5. Agent explores the game (coverage increases)

#### ❌ Issues to Watch For:

1. **Memory Error**:
   - Error: "Unable to allocate X GiB"
   - **Solution**: Already fixed - buffer_size reduced to 2,000
   - If still occurs, check if old code is running

2. **No Actions Executed**:
   - Game doesn't respond to inputs
   - **Check**: `apply_continuous_action` implementation
   - **Verify**: Game window is focused

3. **Observation Space Mismatch**:
   - Error about observation shape
   - **Status**: Should be fixed - using (C, H, W) format

### Verification Checklist

- [ ] Backend starts without errors
- [ ] Frontend connects to backend
- [ ] Racing genre is selectable
- [ ] SACAgent is selected automatically
- [ ] Training starts (status = "Training SACAgent")
- [ ] Metrics update in real-time
- [ ] Game window receives keyboard inputs
- [ ] Coverage increases over time
- [ ] No crashes or errors in logs

### Debugging Racing Agent

#### Check Backend Logs
```bash
tail -f backend/logs/app.log
```

Look for:
- "Selected agent: SACAgent" ✅
- "Starting training for X timesteps" ✅
- "Using Windows API PostMessage/SendMessage for key sending" ✅
- Any error messages ❌

#### Check Frontend Console
- Open browser DevTools (F12)
- Check Console tab for errors
- Check Network tab for API calls

#### Test Action Execution
1. Manually test keyboard inputs in the game
2. Verify W, A, S, D keys work
3. Check if game responds to continuous key presses

### Common Issues & Solutions

#### Issue 1: Agent Not Initializing
**Symptoms**: Status shows "Error" immediately
**Check**:
- Memory available (need at least 2GB free)
- PyTorch installed correctly
- Stable-Baselines3 version compatible

#### Issue 2: Actions Not Working
**Symptoms**: Game doesn't respond
**Check**:
- Game window is focused
- Game accepts keyboard input
- Action executor is being called (check logs)
- Game is in playable state (not in menu)

#### Issue 3: Low Coverage
**Symptoms**: Coverage stays at 0 or very low
**Possible Causes**:
- Agent not exploring (stuck in one state)
- Reward function not encouraging exploration
- Game not responding to actions

### Performance Metrics

#### Expected Values (After Training)
- **Coverage**: Should increase steadily
- **Steps**: Should reach thousands
- **Crashes**: May detect crashes (this is good - means testing works!)

### For Project Review

#### What to Demonstrate:
1. ✅ **Agent Selection**: Show that SACAgent is automatically selected for racing
2. ✅ **Action Execution**: Show that continuous actions are being executed
3. ✅ **Learning Progress**: Show metrics improving over time
4. ✅ **State Coverage**: Demonstrate that agent explores different game states
5. ✅ **Crash Detection**: Show that bugs are detected (if any occur)

#### Key Points to Explain:
- **Why SAC?**: Best for continuous control (steering, throttle)
- **Action Space**: Continuous 2D vector vs discrete actions
- **Observation**: Visual input (stacked frames)
- **Learning**: Agent learns from experience to maximize coverage

### Code Locations

- **SAC Agent**: `backend/services/agents/sac_agent.py`
- **Action Executor**: `backend/services/env/action_executor.py`
- **Game Environment**: `backend/services/env/game_env.py`
- **Strategy Selector**: `backend/services/strategy_selector.py`
- **RL Controller**: `backend/controllers/rl_controller.py`

## Notes

- All tests use mocks to prevent actual test execution
- Test history is automatically cleared between tests
- Metrics are reset between tests
- No external dependencies required
- Tests are fast and can run in parallel

