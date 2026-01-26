# Test History Feature

## Overview

The Test History feature provides a comprehensive REST API for tracking, retrieving, and analyzing past game testing runs. All test results are automatically saved when tests complete, allowing you to review historical performance, compare metrics, and analyze trends.

## Features

- ✅ **Automatic Test Result Saving**: Test results are automatically saved when tests complete
- ✅ **Test History Retrieval**: List and filter past test runs
- ✅ **Detailed Test Information**: Get complete details for any test run
- ✅ **Statistics & Analytics**: Aggregate statistics across all test runs
- ✅ **Test Management**: Delete individual tests or clear all history
- ✅ **Filtering & Search**: Filter by genre, algorithm, or status

## API Endpoints

All endpoints are prefixed with `/api` and are separate from existing endpoints.

### 1. List Test History

**GET** `/api/history`

Retrieve list of past test runs with optional filtering.

**Query Parameters:**
- `limit` (optional): Maximum number of results (1-1000)
- `genre` (optional): Filter by game genre (platformer, fps, racing, rpg)
- `algorithm` (optional): Filter by RL algorithm (PPO, DQN, SAC, HRL)
- `status` (optional): Filter by status (Completed, Stopped, Error)

**Response:**
```json
{
  "tests": [
    {
      "id": "uuid-string",
      "timestamp": "2024-01-15T10:30:00",
      "genre": "platformer",
      "algorithm": "DQN",
      "status": "Completed",
      "duration_seconds": 1250.5,
      "metrics": {
        "coverage": 1250.5,
        "crashes": 3,
        "fps": 60.0,
        "total_steps": 15420,
        "reward_mean": 0.85
      },
      "notes": ""
    }
  ],
  "total": 10
}
```

**Example:**
```bash
# Get last 10 tests
GET /api/history?limit=10

# Get all platformer tests
GET /api/history?genre=platformer

# Get all completed PPO tests
GET /api/history?algorithm=PPO&status=Completed
```

---

### 2. Get Test Details

**GET** `/api/history/{test_id}`

Retrieve detailed information about a specific test run.

**Path Parameters:**
- `test_id`: Unique test ID (UUID)

**Response:**
```json
{
  "id": "uuid-string",
  "timestamp": "2024-01-15T10:30:00",
  "genre": "platformer",
  "algorithm": "DQN",
  "status": "Completed",
  "duration_seconds": 1250.5,
  "metrics": {
    "coverage": 1250.5,
    "crashes": 3,
    "fps": 60.0,
    "total_steps": 15420,
    "reward_mean": 0.85
  },
  "notes": ""
}
```

**Example:**
```bash
GET /api/history/123e4567-e89b-12d3-a456-426614174000
```

---

### 3. Get Statistics

**GET** `/api/history/statistics`

Get aggregated statistics from all test runs.

**Response:**
```json
{
  "total_tests": 25,
  "by_genre": {
    "platformer": 10,
    "fps": 8,
    "racing": 5,
    "rpg": 2
  },
  "by_algorithm": {
    "DQN": 10,
    "PPO": 8,
    "SAC": 5,
    "HRL": 2
  },
  "by_status": {
    "Completed": 20,
    "Stopped": 3,
    "Error": 2
  },
  "average_coverage": 1150.5,
  "average_crashes": 2.5,
  "total_crashes": 62
}
```

**Example:**
```bash
GET /api/history/statistics
```

---

### 4. Delete Test

**DELETE** `/api/history/{test_id}`

Delete a specific test result from history.

**Path Parameters:**
- `test_id`: Unique test ID (UUID)

**Response:**
```json
{
  "success": true,
  "message": "Test 123e4567-e89b-12d3-a456-426614174000 deleted successfully"
}
```

**Example:**
```bash
DELETE /api/history/123e4567-e89b-12d3-a456-426614174000
```

---

### 5. Clear All History

**DELETE** `/api/history`

Delete all test history entries.

**Response:**
```json
{
  "success": true,
  "message": "Cleared 25 test history entries"
}
```

**Example:**
```bash
DELETE /api/history
```

## Automatic Saving

Test results are automatically saved when:
- ✅ Test completes successfully (`status: "Completed"`)
- ✅ Test is stopped by user (`status: "Stopped"`)
- ✅ Test encounters an error (`status: "Error"`)

Each saved test includes:
- Unique ID (UUID)
- Timestamp (ISO format)
- Game genre
- RL algorithm used
- Final status
- Duration in seconds
- Complete metrics snapshot
- Error notes (if applicable)

## Storage

Test history is stored in:
- **File**: `logs/test_history.json`
- **Format**: JSON array (most recent first)
- **Location**: Configured via `LOGS_DIR` in settings

## Integration

The feature is fully integrated with the existing system:
- ✅ No changes to existing endpoints
- ✅ Automatic saving in RL controller
- ✅ Uses existing logging and error handling
- ✅ Follows production-grade patterns

## Usage Examples

### Frontend Integration

```javascript
// List recent tests
const response = await fetch('http://localhost:8000/api/history?limit=10');
const data = await response.json();
console.log(data.tests);

// Get statistics
const stats = await fetch('http://localhost:8000/api/history/statistics');
const statsData = await stats.json();
console.log(statsData);

// Get specific test
const test = await fetch(`http://localhost:8000/api/history/${testId}`);
const testData = await test.json();
console.log(testData);
```

### Filtering Examples

```javascript
// Get all platformer tests
const platformerTests = await fetch(
  'http://localhost:8000/api/history?genre=platformer'
);

// Get all completed PPO tests
const completedPPO = await fetch(
  'http://localhost:8000/api/history?algorithm=PPO&status=Completed'
);

// Get last 5 tests
const recent = await fetch(
  'http://localhost:8000/api/history?limit=5'
);
```

## Error Handling

All endpoints follow the same error handling patterns:
- **404**: Test not found
- **500**: Internal server error
- **422**: Validation error (for query parameters)

Error responses follow the standard format:
```json
{
  "detail": "Error message"
}
```

## Notes

- Test history persists across server restarts
- History file is automatically created if it doesn't exist
- Invalid JSON in history file is automatically handled
- Thread-safe operations for concurrent access
- All timestamps are in UTC ISO format

