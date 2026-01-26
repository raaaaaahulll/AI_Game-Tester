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

## Notes

- All tests use mocks to prevent actual test execution
- Test history is automatically cleared between tests
- Metrics are reset between tests
- No external dependencies required
- Tests are fast and can run in parallel

