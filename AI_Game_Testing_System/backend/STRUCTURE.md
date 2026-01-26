# Backend Structure

## Architecture Overview

The backend follows a clean, layered architecture:

```
backend/
├── app.py                 # Application entry point
├── controllers/           # Business logic controllers
├── services/              # Business logic services
│   ├── agents/           # RL agent implementations
│   ├── env/              # Game environment components
│   └── analytics/        # Analytics and tracking
├── models/                # Data models and schemas
├── routes/                # API route definitions
├── utils/                 # Utility functions
├── middlewares/           # Custom middleware
├── config/                # Configuration
└── tests/                 # Test suite
```

## Directory Responsibilities

### `app.py`
- FastAPI application setup
- Middleware configuration
- Route registration
- Exception handlers
- Lifecycle management

### `controllers/`
- Business logic orchestration
- Coordinates between services
- Handles request/response transformation
- Example: `rl_controller.py` - Manages RL training sessions

### `services/`
- Core business logic
- Reusable service components
- **agents/**: RL agent implementations (DQN, PPO, SAC, HRL)
- **env/**: Game environment (screen capture, actions, state processing)
- **analytics/**: Metrics tracking, coverage, crash detection
- Standalone services: metrics, history, strategy selection

### `models/`
- Pydantic models for request/response validation
- Data schemas
- Type definitions

### `routes/`
- API endpoint definitions
- Request/response handling
- Route-specific logic
- **api.py**: Main API endpoints
- **history.py**: Test history endpoints

### `utils/`
- Shared utility functions
- Logging configuration
- Custom exceptions
- Helper functions

### `middlewares/`
- Custom FastAPI middleware
- Request logging
- Security headers
- Cross-cutting concerns

### `config/`
- Application configuration
- Environment settings
- Settings management

### `tests/`
- Test suite
- Unit tests
- Integration tests
- Test fixtures

## Import Patterns

### Absolute Imports (Recommended)
```python
from config.settings import settings
from utils.logging import get_logger
from services.metrics_service import metrics_collector
from controllers.rl_controller import rl_controller
```

### Module Structure
- Each directory has `__init__.py` for package initialization
- Exports are defined in `__init__.py` files
- Clear separation of concerns

## Benefits

1. **Maintainability**: Clear organization makes code easy to find and modify
2. **Scalability**: Easy to add new features without cluttering
3. **Testability**: Services can be easily mocked and tested
4. **Reusability**: Services can be reused across different controllers
5. **Separation of Concerns**: Each layer has a clear responsibility

## Migration Notes

- Old files still exist for reference
- New structure is fully functional
- All imports updated in new files
- Tests updated to work with new structure
- API contract unchanged

