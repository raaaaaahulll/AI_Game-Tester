# API Contract Documentation

This project includes an OpenAPI 3.0 specification that documents all API endpoints, request/response formats, and schemas.

## Files

- **`openapi.yaml`** - OpenAPI 3.0 specification in YAML format

## Viewing the API Documentation

### Option 1: FastAPI Auto-Generated Docs (Recommended)

FastAPI automatically generates interactive API documentation from your code:

1. Start the backend server:
   ```bash
   cd AI_Game_Testing_System/backend
   python main.py
   ```

2. Open your browser and navigate to:
   - **Swagger UI**: http://localhost:8000/docs
   - **ReDoc**: http://localhost:8000/redoc
   - **OpenAPI JSON**: http://localhost:8000/openapi.json

### Option 2: External Tools

You can import `openapi.yaml` into various tools:

#### Swagger Editor (Online)
1. Go to https://editor.swagger.io/
2. File → Import File → Select `openapi.yaml`
3. View and test the API interactively

#### Postman
1. Open Postman
2. Import → File → Select `openapi.yaml`
3. Generate a collection with all endpoints

#### Insomnia
1. Open Insomnia
2. Application → Preferences → Data → Import Data → From File
3. Select `openapi.yaml`

#### VS Code Extensions
- **OpenAPI (Swagger) Editor**: Provides syntax highlighting and validation
- **REST Client**: Test API endpoints directly from VS Code

## Using the Specification

### Generate Client Code

You can generate client code for various languages using tools like:

- **OpenAPI Generator**: https://openapi-generator.tech/
  ```bash
  openapi-generator generate -i openapi.yaml -g javascript -o ./generated-client
  ```

- **Swagger Codegen**: https://swagger.io/tools/swagger-codegen/

### Validate the Specification

```bash
# Using swagger-cli (npm)
npm install -g @apidevtools/swagger-cli
swagger-cli validate openapi.yaml

# Using openapi-validator (Python)
pip install openapi-validator
openapi-validator openapi.yaml
```

## Specification Details

The OpenAPI specification includes:

- **5 API Endpoints**:
  - `POST /api/start-test` - Start testing session
  - `POST /api/stop-test` - Stop testing session
  - `GET /api/metrics` - Get all metrics
  - `GET /api/status` - Get system status
  - `GET /` - Health check

- **Request/Response Schemas**: Complete type definitions for all endpoints
- **Examples**: Request/response examples for each endpoint
- **Error Responses**: Documented error formats (400, 500)
- **Enums**: Valid values for genre, status, and algorithm fields

## Integration with FastAPI

FastAPI automatically generates OpenAPI documentation from your Python code using:
- Pydantic models for request/response validation
- Type hints for parameter types
- Docstrings for descriptions

The standalone `openapi.yaml` file serves as:
- A design document
- A contract for frontend developers
- A source for client code generation
- Version-controlled API documentation

## Updating the Specification

When adding new endpoints:

1. Add the endpoint to `backend/api.py`
2. Update `openapi.yaml` to reflect the new endpoint
3. Ensure request/response models match the OpenAPI schema
4. Validate the updated specification

## Frontend-Backend Communication

### Architecture

**Backend**:
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Base URL**: `http://localhost:8000`
- **API Prefix**: `/api`
- **CORS**: Enabled for all origins (development mode)

**Frontend**:
- **Framework**: React with Vite
- **HTTP Client**: Axios
- **API Service**: Centralized in `src/services/api.js`

### Communication Flow

1. **Frontend** (`Dashboard.jsx`) imports API functions from `services/api.js`
2. **API Service** (`api.js`) uses Axios to make HTTP requests to `http://localhost:8000/api`
3. **Backend** (`main.py`) receives requests, routes them through `api.py` router
4. **Backend** processes requests using `rl_controller` and `metrics_collector`
5. **Backend** returns JSON responses
6. **Frontend** updates UI state based on responses

## Detailed API Endpoints

### 1. POST `/api/start-test`

**Location**: `backend/api.py:11-16`

**Purpose**: Start the game testing process with a specific genre

**Request Format**:
```json
{
  "genre": "string"
}
```

**Request Headers**:
- `Content-Type: application/json`

**Valid Genre Values**:
- `"platformer"`
- `"fps"`
- `"racing"`
- `"rpg"`

**Response Format** (Success - 200):
```json
{
  "status": "success",
  "message": "string"
}
```

**Response Format** (Error - 400):
```json
{
  "detail": "error message string"
}
```

**Frontend Usage**: `frontend/src/services/api.js:5-12`
```javascript
await startTest(genre)
```

---

### 2. POST `/api/stop-test`

**Location**: `backend/api.py:18-23`

**Purpose**: Stop the currently running game testing process

**Request Format**: No body required

**Response Format** (Success - 200):
```json
{
  "status": "success",
  "message": "string"
}
```

**Response Format** (Error - 400):
```json
{
  "detail": "error message string"
}
```

**Frontend Usage**: `frontend/src/services/api.js:14-21`
```javascript
await stopTest()
```

---

### 3. GET `/api/metrics`

**Location**: `backend/api.py:25-27`

**Purpose**: Retrieve all current testing metrics

**Request Format**: No parameters required

**Response Format** (Success - 200):
```json
{
  "coverage": 0.0,
  "crashes": 0,
  "fps": 0.0,
  "current_algorithm": "string",
  "status": "string",
  "total_steps": 0,
  "reward_mean": 0.0
}
```

**Response Fields**:
- `coverage` (float): State coverage percentage
- `crashes` (int): Number of crashes/freezes detected
- `fps` (float): Frames per second
- `current_algorithm` (string): Active RL algorithm name (e.g., "PPO", "DQN", "SAC", "None")
- `status` (string): Current system status (e.g., "Idle", "Training", etc.)
- `total_steps` (int): Total training steps executed
- `reward_mean` (float): Mean reward value

**Frontend Usage**: `frontend/src/services/api.js:23-31`
- Called every 1 second via `useEffect` interval in `Dashboard.jsx:42-56`
- Used to update metrics cards and status display

---

### 4. GET `/api/status`

**Location**: `backend/api.py:29-32`

**Purpose**: Get only the current status of the testing system

**Request Format**: No parameters required

**Response Format** (Success - 200):
```json
{
  "status": "string"
}
```

**Response Fields**:
- `status` (string): Current system status (e.g., "Idle", "Training", "Unknown")

**Frontend Usage**: Not currently used in the frontend (metrics endpoint provides status)

---

### 5. GET `/`

**Location**: `backend/main.py:20-22`

**Purpose**: Root endpoint to verify backend is running

**Request Format**: No parameters required

**Response Format** (Success - 200):
```json
{
  "message": "AI Game Testing System Backend is Running"
}
```

**Frontend Usage**: Not used in the frontend

---

## File Locations

### Backend API Definition
- **Main Application**: `AI_Game_Testing_System/backend/main.py`
- **API Routes**: `AI_Game_Testing_System/backend/api.py`
- **Configuration**: `AI_Game_Testing_System/backend/core/config.py`
- **Metrics Collector**: `AI_Game_Testing_System/backend/analytics/metrics_collector.py`
- **RL Controller**: `AI_Game_Testing_System/backend/rl_controller.py`

### Frontend API Integration
- **API Service**: `AI_Game_Testing_System/frontend/src/services/api.js`
- **Dashboard Component**: `AI_Game_Testing_System/frontend/src/components/Dashboard.jsx`
- **Main App**: `AI_Game_Testing_System/frontend/src/App.jsx`

## Request/Response Patterns

### Error Handling

**Backend**:
- Uses FastAPI's `HTTPException` for error responses
- Returns 400 status code for client errors
- Error response format: `{"detail": "error message"}`

**Frontend**:
- Axios catches errors and extracts `error.response.data`
- Errors are displayed via `alert()` in the Dashboard component
- Metrics endpoint errors are caught and return `null` to prevent UI crashes

### Data Flow Example

1. User clicks "Start Testing" button
2. `Dashboard.jsx` calls `handleStart()` → `startTest(genre)`
3. `api.js` makes `POST /api/start-test` with `{genre: "platformer"}`
4. Backend `rl_controller.start_test()` processes the request
5. Backend returns `{"status": "success", "message": "..."}`
6. Frontend receives response (or error)
7. Every 1 second, `getMetrics()` polls `/api/metrics`
8. Metrics update the dashboard UI in real-time

## CORS Configuration

**Location**: `backend/main.py:10-16`

The backend is configured with CORS middleware to allow:
- All origins (`allow_origins=["*"]`)
- All methods (`allow_methods=["*"]`)
- All headers (`allow_headers=["*"]`)
- Credentials (`allow_credentials=True`)

**Note**: This is configured for development. In production, you should restrict origins to your frontend domain.

## Server Configuration

**Location**: `backend/core/config.py:35-36`

- **Host**: `0.0.0.0` (listens on all interfaces)
- **Port**: `8000`
- **Reload**: Enabled for development (`reload=True`)

## Real-time Updates

The frontend implements a polling mechanism:
- **Interval**: 1 second (1000ms)
- **Endpoint**: `/api/metrics`
- **Implementation**: `useEffect` hook with `setInterval` in `Dashboard.jsx:41-56`
- **Purpose**: Continuously update metrics cards and status display

## API Summary Table

| Endpoint | Method | Purpose | Request Body | Response |
|----------|--------|---------|--------------|----------|
| `/api/start-test` | POST | Start testing | `{genre: string}` | `{status, message}` |
| `/api/stop-test` | POST | Stop testing | None | `{status, message}` |
| `/api/metrics` | GET | Get all metrics | None | Full metrics object |
| `/api/status` | GET | Get status only | None | `{status}` |
| `/` | GET | Health check | None | `{message}` |

All API endpoints are defined in `backend/api.py` and consumed via `frontend/src/services/api.js`.

## Notes

- The API currently has no authentication (security section is prepared but commented out)
- CORS is enabled for all origins in development mode
- All endpoints return JSON
- Error responses follow FastAPI's standard format: `{"detail": "error message"}`

