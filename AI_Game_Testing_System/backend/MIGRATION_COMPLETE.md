# Backend Restructuring - Migration Instructions

## ✅ Completed Files

The following new structure has been created:

### New Structure Created:
- ✅ `models/schemas.py` - All Pydantic models
- ✅ `routes/api.py` - Main API routes  
- ✅ `routes/history.py` - History routes
- ✅ `utils/logging.py` - Logging utilities
- ✅ `utils/exceptions.py` - Custom exceptions
- ✅ `config/settings.py` - Configuration
- ✅ `middlewares/middleware.py` - Custom middleware
- ✅ `app.py` - Main application entry point

## 🔄 Files That Need to Be Moved

### 1. Move Controllers
```bash
# Move RL controller
mv backend/rl_controller.py backend/controllers/rl_controller.py
```

Then update imports in `controllers/rl_controller.py`:
```python
# Old
from backend.core.strategy_selector import StrategySelector
from backend.env.game_env import GameEnv
from backend.analytics.metrics_collector import metrics_collector
from backend.analytics.test_history import test_history_manager
from backend.core.config import settings
from backend.core.logging_config import get_logger
from backend.core.exceptions import (...)

# New
from services.strategy_selector import StrategySelector
from services.env.game_env import GameEnv
from services.metrics_service import metrics_collector
from services.history_service import test_history_manager
from config.settings import settings
from utils.logging import get_logger
from utils.exceptions import (...)
```

### 2. Move Services

#### Analytics Services
```bash
# Create services directory structure
mkdir -p backend/services/analytics
mkdir -p backend/services/agents
mkdir -p backend/services/env

# Move analytics
mv backend/analytics/metrics_collector.py backend/services/metrics_service.py
mv backend/analytics/test_history.py backend/services/history_service.py
mv backend/analytics/coverage_tracker.py backend/services/analytics/coverage_tracker.py
mv backend/analytics/crash_detector.py backend/services/analytics/crash_detector.py

# Move agents
mv backend/agents/* backend/services/agents/

# Move env
mv backend/env/* backend/services/env/

# Move strategy selector
mv backend/core/strategy_selector.py backend/services/strategy_selector.py
mv backend/core/base_agent.py backend/services/agents/base_agent.py
```

#### Update Service Imports

**services/metrics_service.py** (was analytics/metrics_collector.py):
```python
# Old
from backend.core.config import settings
from backend.core.logging_config import get_logger
from backend.core.exceptions import MetricsError

# New
from config.settings import settings
from utils.logging import get_logger
from utils.exceptions import MetricsError
```

**services/history_service.py** (was analytics/test_history.py):
```python
# Old
from backend.core.config import settings
from backend.core.logging_config import get_logger
from backend.core.exceptions import MetricsError

# New
from config.settings import settings
from utils.logging import get_logger
from utils.exceptions import MetricsError
```

**services/env/*.py**:
```python
# Old
from backend.core.config import SCREEN_SETTINGS, IMG_WIDTH, IMG_HEIGHT, FRAME_STACK_SIZE

# New
from config.settings import settings
# Use: settings.SCREEN_SETTINGS, settings.IMG_WIDTH, etc.
```

**services/agents/*.py**:
```python
# Old
from backend.core.base_agent import BaseRLAgent
from backend.core.logging_config import get_logger

# New
from services.agents.base_agent import BaseRLAgent
from utils.logging import get_logger
```

### 3. Update Tests

Update `tests/conftest.py`:
```python
# Old
from backend.main import app
from backend.analytics.metrics_collector import metrics_collector
from backend.analytics.test_history import test_history_manager
from backend.rl_controller import rl_controller

# New
from app import app
from services.metrics_service import metrics_collector
from services.history_service import test_history_manager
from controllers.rl_controller import rl_controller
```

Update all test files similarly.

## 📝 Import Update Checklist

Search and replace across all files:

1. `from backend.core.config import` → `from config.settings import`
2. `from backend.core.logging_config import` → `from utils.logging import`
3. `from backend.core.exceptions import` → `from utils.exceptions import`
4. `from backend.core.middleware import` → `from middlewares.middleware import`
5. `from backend.api import` → `from routes.api import` or `from models.schemas import`
6. `from backend.api_history import` → `from routes.history import`
7. `from backend.rl_controller import` → `from controllers.rl_controller import`
8. `from backend.analytics.metrics_collector import` → `from services.metrics_service import`
9. `from backend.analytics.test_history import` → `from services.history_service import`
10. `from backend.env import` → `from services.env import`
11. `from backend.agents import` → `from services.agents import`
12. `from backend.core.strategy_selector import` → `from services.strategy_selector import`
13. `from backend.core.base_agent import` → `from services.agents.base_agent import`

## 🧪 Testing

After migration:

1. Run tests: `pytest`
2. Start server: `python app.py`
3. Verify endpoints work
4. Check logs for import errors

## ⚠️ Important Notes

- Keep old files until migration is verified
- Update `__init__.py` files in each directory
- Ensure all relative imports are correct
- Test each module after moving

## 🗑️ Cleanup

After verification, remove old directories:
- `backend/core/` (except keep for reference initially)
- `backend/analytics/` (moved to services/)
- Old `backend/api.py` and `backend/api_history.py`
- Old `backend/main.py` (replaced by app.py)

