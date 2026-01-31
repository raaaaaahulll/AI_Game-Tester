# Screenshot Storage System

## Overview

The system automatically saves screenshots for:
- **Game Screenshots**: Regular gameplay screenshots during testing
- **Bug Screenshots**: Screenshots captured when bugs, crashes, or issues are detected

## Storage Locations

### Directory Structure

```
backend/logs/
├── screenshots/
│   ├── game/              # Game screenshots
│   │   └── {test_id}/     # Organized by test ID
│   │       └── *.png      # Screenshot files
│   │
│   └── bugs/              # Bug/issue screenshots
│       └── {test_id}/     # Organized by test ID
│           ├── *.png      # Screenshot files
│           └── *.json     # Metadata files
```

### Paths

- **Base Directory**: `backend/logs/screenshots/`
- **Game Screenshots**: `backend/logs/screenshots/game/`
- **Bug Screenshots**: `backend/logs/screenshots/bugs/`

## Usage

### Saving Game Screenshots

```python
from services.screenshot_service import screenshot_service
from services.env.screen_capture import ScreenCapture

# Capture a frame
screen_capture = ScreenCapture()
frame = screen_capture.capture()

# Save game screenshot
screenshot_path = screenshot_service.save_game_screenshot(
    frame=frame,
    test_id="test-123",
    step=1000,
    prefix="checkpoint"
)
```

### Saving Bug Screenshots

```python
# When a bug/crash is detected
bug_path = screenshot_service.save_bug_screenshot(
    frame=frame,
    test_id="test-123",
    bug_type="crash",  # or "freeze", "error", etc.
    description="Game crashed at step 5000",
    step=5000
)
```

### Retrieving Screenshots

```python
# Get all screenshots for a test
screenshots = screenshot_service.get_screenshots_for_test("test-123")
# Returns: {"game": [...], "bugs": [...]}
```

## Database Integration

Screenshot paths are stored in the SQLite database:

- `screenshot_paths`: JSON array of game screenshot paths
- `bug_screenshot_paths`: JSON array of bug screenshot paths

## File Naming Convention

### Game Screenshots
- Format: `{prefix}_step_{step}_{timestamp}_{uuid}.png`
- Example: `checkpoint_step_1000_20260127_143022_a1b2c3d4.png`

### Bug Screenshots
- Format: `{bug_type}_step_{step}_{timestamp}_{uuid}.png`
- Example: `crash_step_5000_20260127_143022_e5f6g7h8.png`
- Metadata: `crash_step_5000_20260127_143022_e5f6g7h8.json`

## Bug Types

Supported bug types:
- `crash`: Game crashed
- `freeze`: Game froze/hung
- `error`: Error occurred
- `glitch`: Visual glitch detected
- `performance`: Performance issue

## Metadata Files

Each bug screenshot has a corresponding JSON metadata file:

```json
{
  "test_id": "test-123",
  "bug_type": "crash",
  "timestamp": "20260127_143022",
  "step": 5000,
  "description": "Game crashed at step 5000",
  "screenshot_path": "/path/to/screenshot.png"
}
```

## Cleanup

Automatically clean up old screenshots:

```python
# Delete screenshots older than 30 days
deleted_count = screenshot_service.cleanup_old_screenshots(days=30)
```

## Integration with Crash Detector

The crash detector can automatically save screenshots:

```python
from services.analytics.crash_detector import CrashDetector
from services.screenshot_service import screenshot_service

crash_detector = CrashDetector()
result = crash_detector.check(frame_hash, is_running)

if result["is_crash"] or result["is_freeze"]:
    # Save bug screenshot
    screenshot_service.save_bug_screenshot(
        frame=current_frame,
        test_id=test_id,
        bug_type="crash" if result["is_crash"] else "freeze",
        step=current_step
    )
```

## Best Practices

1. **Organize by Test ID**: Always provide test_id for better organization
2. **Include Step Numbers**: Helps identify when issues occurred
3. **Use Descriptive Prefixes**: Makes it easier to find specific screenshots
4. **Regular Cleanup**: Set up periodic cleanup of old screenshots
5. **Metadata**: Always include descriptions for bug screenshots

## Storage Size Considerations

- Screenshots can take significant disk space
- Average screenshot size: ~500KB - 2MB (depending on resolution)
- Recommended: Implement cleanup after 30-90 days
- Consider compression for long-term storage

## Accessing Screenshots via API

Screenshots are accessible via file paths stored in the database. You can create API endpoints to serve screenshots if needed.
