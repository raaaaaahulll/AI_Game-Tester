# Game Selector Feature

## Overview

A compact "Game Selector" dropdown has been added next to the Genre selector in the Dashboard. This feature allows users to:

1. **View Active Game Windows**: Automatically detects and lists currently running game processes
2. **Access Previous Sessions**: Retrieves and displays previously used games from SQLite database
3. **Manual Browse**: Option to manually enter a game executable path

## Backend Implementation

### New Files

1. **`backend/services/game_selector_service.py`**
   - `GameSelectorService` class for managing game selection
   - SQLite database for storing game sessions
   - Windows API integration for active window detection (with fallback to psutil)
   - Methods:
     - `get_active_windows()`: Detects active game windows
     - `get_previous_sessions()`: Retrieves previous game sessions
     - `save_session()`: Saves/updates game sessions
     - `delete_session()`: Deletes game sessions

2. **`backend/routes/game_selector.py`**
   - REST API endpoints for game selection:
     - `GET /api/game-selector/windows`: Get active game windows
     - `GET /api/game-selector/sessions`: Get previous sessions
     - `POST /api/game-selector/sessions`: Save a game session
     - `DELETE /api/game-selector/sessions/{session_id}`: Delete a session

### Database Schema

The SQLite database (`game_sessions.db`) stores:
- `id`: Primary key
- `game_name`: Name of the game
- `game_path`: Path to game executable
- `genre`: Game genre (optional)
- `last_used`: Timestamp of last use
- `usage_count`: Number of times used
- `created_at`: Creation timestamp

### Dependencies

- `psutil`: For process detection (already in requirements)
- `pywin32`: Optional, for Windows window enumeration (install manually on Windows)

## Frontend Implementation

### Updated Files

1. **`frontend/src/services/api.js`**
   - Added functions:
     - `getActiveWindows()`: Fetch active game windows
     - `getPreviousSessions()`: Fetch previous sessions
     - `saveGameSession()`: Save a game session

2. **`frontend/src/components/Dashboard.jsx`**
   - Added Game Selector dropdown next to Genre selector
   - State management for game selection
   - Auto-refresh of game options every 30 seconds
   - Manual path input with inline form
   - Preserves existing UI styling and layout

### UI Features

- **Dropdown Structure**:
  - Active Windows section (🖥️ icon)
  - Previous Sessions section (📁 icon)
  - Manual Browse option (📂 icon)
  
- **Manual Input**:
  - Appears as a popup when "Browse..." is selected
  - Text input for game executable path
  - Add/Cancel buttons
  - Automatically saves to database on Add

- **Styling**:
  - Matches existing Genre selector styling
  - Dark theme with red accents
  - Responsive design
  - Disabled during training

## Usage

1. **Select Active Window**:
   - Open the Game Selector dropdown
   - Choose from "Active Windows" section
   - Game is automatically saved to sessions

2. **Select Previous Session**:
   - Open the Game Selector dropdown
   - Choose from "Previous Sessions" section
   - Shows usage count for each session

3. **Manual Browse**:
   - Select "Browse..." option
   - Enter game executable path (e.g., `C:\Games\MyGame\game.exe`)
   - Click "Add" to save
   - Game appears in Previous Sessions

## API Endpoints

### Get Active Windows
```http
GET /api/game-selector/windows
```

**Response:**
```json
[
  {
    "title": "My Game",
    "process_name": "game.exe",
    "exe_path": "C:\\Games\\MyGame\\game.exe",
    "pid": 12345,
    "hwnd": 67890
  }
]
```

### Get Previous Sessions
```http
GET /api/game-selector/sessions?limit=20
```

**Response:**
```json
[
  {
    "id": 1,
    "game_name": "My Game",
    "game_path": "C:\\Games\\MyGame\\game.exe",
    "genre": "platformer",
    "last_used": "2024-01-01T12:00:00",
    "usage_count": 5,
    "created_at": "2024-01-01T10:00:00"
  }
]
```

### Save Session
```http
POST /api/game-selector/sessions
Content-Type: application/json

{
  "game_name": "My Game",
  "game_path": "C:\\Games\\MyGame\\game.exe",
  "genre": "platformer"
}
```

### Delete Session
```http
DELETE /api/game-selector/sessions/{session_id}
```

## Notes

- Windows window detection requires `pywin32` package (optional)
- Falls back to psutil-based detection if pywin32 is not available
- Database is stored in `logs/game_sessions.db`
- Game options refresh every 30 seconds automatically
- Manual input form appears inline below the dropdown

## Future Enhancements

- File browser dialog for manual selection
- Game icon extraction and display
- Filter/search functionality
- Game validation before saving
- Integration with test execution (use selected game path)

