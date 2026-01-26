# Backend Test Suite

Automated tests for the AI Game Testing System backend API.

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
```

### Run specific test
```bash
pytest tests/test_api.py::TestStartTest::test_start_test_success
```

### Run with coverage
```bash
pytest --cov=backend --cov-report=html
```

## Test Structure

- `conftest.py` - Pytest fixtures and configuration
- `test_api.py` - Tests for main API endpoints (start-test, stop-test, metrics, status)
- `test_history_api.py` - Tests for test history endpoints
- `test_validation.py` - Tests for request validation and error handling

## Test Coverage

### Main API Endpoints
- ✅ Health check endpoints (`/`, `/health`)
- ✅ Start test endpoint (`POST /api/start-test`)
- ✅ Stop test endpoint (`POST /api/stop-test`)
- ✅ Metrics endpoint (`GET /api/metrics`)
- ✅ Status endpoint (`GET /api/status`)

### Test History Endpoints
- ✅ List history (`GET /api/history`)
- ✅ Get test details (`GET /api/history/{test_id}`)
- ✅ Get statistics (`GET /api/history/statistics`)
- ✅ Delete test (`DELETE /api/history/{test_id}`)
- ✅ Clear history (`DELETE /api/history`)

### Validation & Error Handling
- ✅ Request validation
- ✅ Error responses
- ✅ 404 handling
- ✅ Method not allowed

## Fixtures

- `client` - FastAPI test client
- `mock_metrics_collector` - Mocked metrics collector
- `mock_rl_controller` - Mocked RL controller
- `reset_metrics` - Reset metrics before/after test
- `clear_history` - Clear test history before/after test

## Notes

- Tests use mocks to prevent actual test execution
- Test history is cleared between tests
- All tests are isolated and can run independently
- No external dependencies required for running tests

