# AI Game Testing System - Setup and Run Guide

Complete instructions for setting up and running the AI Game Testing System.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [Running the Application](#running-the-application)
6. [Configuration](#configuration)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)
9. [API Endpoints](#api-endpoints)

---

## 🔧 Prerequisites

### Required Software

1. **Python 3.9+**
   - Check version: `python --version` or `python3 --version`
   - Download: https://www.python.org/downloads/

2. **Node.js 18+ and npm**
   - Check version: `node --version` and `npm --version`
   - Download: https://nodejs.org/

3. **Git** (optional, for version control)
   - Download: https://git-scm.com/

### Optional (for Windows)

4. **pywin32** (for enhanced window detection)
   - Install after Python setup: `pip install pywin32`

---

## 📁 Project Structure

```
AI_Game_Testing_System/
├── backend/                 # Python FastAPI backend
│   ├── app.py              # Main application entry point
│   ├── config/             # Configuration settings
│   ├── controllers/       # Business logic controllers
│   ├── services/           # Business services
│   ├── routes/             # API route definitions
│   ├── models/             # Pydantic schemas
│   ├── middlewares/        # Custom middleware
│   ├── utils/              # Utility functions
│   ├── tests/              # Automated tests
│   └── requirements.txt    # Python dependencies
│
└── frontend/               # React + Vite frontend
    ├── src/
    │   ├── components/     # React components
    │   ├── services/       # API service functions
    │   └── main.jsx        # Entry point
    ├── package.json        # Node.js dependencies
    └── vite.config.js       # Vite configuration
```

---

## 🐍 Backend Setup

### Step 1: Navigate to Backend Directory

```bash
cd AI_Game_Testing_System/backend
```

### Step 2: Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** This will install:
- FastAPI and Uvicorn (web framework)
- Stable-Baselines3 (RL algorithms)
- PyTorch (ML framework)
- OpenCV, MSS, PyAutoGUI (screen capture & input)
- Pydantic (data validation)
- And other dependencies...

**Installation may take 10-15 minutes** due to PyTorch and ML libraries.

### Step 4: Optional - Install pywin32 (Windows only)

For enhanced game window detection on Windows:

```bash
pip install pywin32
```

### Step 5: Verify Installation

```bash
python -c "import fastapi; import stable_baselines3; print('✓ Dependencies installed')"
```

---

## ⚛️ Frontend Setup

### Step 1: Navigate to Frontend Directory

```bash
cd AI_Game_Testing_System/frontend
```

### Step 2: Install Dependencies

```bash
npm install
```

**Note:** This will install:
- React 19
- Vite (build tool)
- Tailwind CSS (styling)
- Axios (HTTP client)
- Recharts (charts)
- Framer Motion (animations)
- Lucide React (icons)

### Step 3: Verify Installation

```bash
npm list --depth=0
```

---

## 🚀 Running the Application

### ⚠️ Important: Use Separate Terminal Windows

**You MUST use TWO separate terminal windows** - one for the backend and one for the frontend. They need to run simultaneously.

### Option 1: Run Backend and Frontend Separately (Recommended for Development)

#### Step 1: Open First Terminal Window (for Backend)

**Windows (PowerShell):**
1. Open a new PowerShell window
2. Navigate to the backend directory:
   ```powershell
   cd "C:\Users\DELL\Desktop\antigravity copy\AI_Game Tester\AI_Game_Testing_System\backend"
   ```
   *(Adjust the path to match your project location)*

3. Activate virtual environment:
   ```powershell
   venv\Scripts\activate
   ```

4. Run the backend:
   ```powershell
   python app.py
   ```

**Linux/Mac:**
1. Open a new terminal window
2. Navigate to the backend directory:
   ```bash
   cd AI_Game_Testing_System/backend
   ```

3. Activate virtual environment:
   ```bash
   source venv/bin/activate
   ```

4. Run the backend:
   ```bash
   python app.py
   ```

**Expected Output:**
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Keep this terminal window open!** The backend must keep running.

Backend will be available at: **http://localhost:8000**

#### Step 2: Open Second Terminal Window (for Frontend)

**Windows (PowerShell):**
1. Open a **NEW** PowerShell window (don't close the first one!)
2. Navigate to the frontend directory:
   ```powershell
   cd "C:\Users\DELL\Desktop\antigravity copy\AI_Game Tester\AI_Game_Testing_System\frontend"
   ```

3. Run the frontend:
   ```powershell
   npm run dev
   ```

**Linux/Mac:**
1. Open a **NEW** terminal window (don't close the first one!)
2. Navigate to the frontend directory:
   ```bash
   cd AI_Game_Testing_System/frontend
   ```

3. Run the frontend:
   ```bash
   npm run dev
   ```

**Expected Output:**
```
  VITE v7.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**Keep this terminal window open too!** The frontend must keep running.

Frontend will be available at: **http://localhost:5173**

### 📌 Quick Reference

**You should have TWO terminal windows open:**

1. **Terminal 1 (Backend):**
   - Shows: `INFO: Uvicorn running on http://0.0.0.0:8000`
   - **DO NOT CLOSE** - backend must keep running

2. **Terminal 2 (Frontend):**
   - Shows: `Local: http://localhost:5173/`
   - **DO NOT CLOSE** - frontend must keep running

**To stop:**
- Press `CTRL+C` in each terminal window to stop that service
- Stop backend first, then frontend (or vice versa)

### Option 2: Using Alternative Backend Entry Point

**Note:** Still use a separate terminal window for this!

If `app.py` doesn't work, in your **backend terminal window**, try:

```bash
cd AI_Game_Testing_System/backend
python main.py
```

Or using uvicorn directly:

```bash
cd AI_Game_Testing_System/backend
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

**Remember:** You still need the frontend running in a separate terminal window!

---

## ⚙️ Configuration

### Environment Variables (Optional)

Create a `.env` file in `backend/` directory:

```env
# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Environment
ENVIRONMENT=development

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=text

# Screen Capture (optional)
SCREEN_TOP=0
SCREEN_LEFT=0
SCREEN_WIDTH=1920
SCREEN_HEIGHT=1080
SCREEN_MONITOR=1

# RL Hyperparameters (optional)
TIMESTEPS=100000
SAVE_INTERVAL=10000
```

**Note:** The application will work with defaults if no `.env` file is present.

### Frontend API Configuration

The frontend is configured to connect to `http://localhost:8000` by default.

To change this, edit `frontend/src/services/api.js`:

```javascript
const API_URL = 'http://localhost:8000/api';  // Change this if needed
```

---

## 🧪 Testing

### Backend Tests

```bash
cd AI_Game_Testing_System/backend

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest --cov=backend tests/
```

### Frontend Tests

Currently, no frontend tests are configured. To add testing:

```bash
cd AI_Game_Testing_System/frontend
npm install --save-dev vitest @testing-library/react
```

---

## 🔍 Troubleshooting

### Backend Issues

#### Issue: `ModuleNotFoundError` or import errors

**Solution:**
```bash
# Ensure virtual environment is activated
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### Issue: Port 8000 already in use

**Solution:**
- Change port in `.env` file: `API_PORT=8001`
- Or kill the process using port 8000:
  - Windows: `netstat -ano | findstr :8000` then `taskkill /PID <pid> /F`
  - Linux/Mac: `lsof -ti:8000 | xargs kill -9`

#### Issue: PyTorch installation fails

**Solution:**
```bash
# Install PyTorch separately first
pip install torch torchvision torchaudio

# Then install other requirements
pip install -r requirements.txt
```

#### Issue: `win32gui` not found (Windows)

**Solution:**
```bash
pip install pywin32
```

This is optional - the app will work without it using basic process detection.

### Frontend Issues

#### Issue: `npm install` fails

**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### Issue: Port 5173 already in use

**Solution:**
- Vite will automatically use the next available port
- Or specify a port: `npm run dev -- --port 3000`

#### Issue: CORS errors in browser console

**Solution:**
- Ensure backend is running on port 8000
- Check that `CORS_ORIGINS` in backend `.env` includes `http://localhost:5173`
- Restart backend after changing `.env`

### General Issues

#### Issue: Can't connect frontend to backend

**Checklist:**
1. ✅ Backend is running on `http://localhost:8000`
2. ✅ Frontend is running on `http://localhost:5173`
3. ✅ Backend logs show no errors
4. ✅ Browser console shows no CORS errors
5. ✅ Test backend directly: `curl http://localhost:8000/api/status`

#### Issue: Game window detection not working

**Solution:**
- On Windows: Install `pywin32` for better detection
- Ensure games are actually running
- Check backend logs for errors
- The system uses heuristics - not all processes may be detected

---

## 📡 API Endpoints

### Main API

- `GET /` - Health check
- `GET /health` - Health endpoint
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

### Testing Endpoints

- `POST /api/start-test` - Start a test session
  ```json
  { "genre": "platformer" }
  ```

- `POST /api/stop-test` - Stop current test session

- `GET /api/metrics` - Get real-time metrics

- `GET /api/status` - Get current status

### History Endpoints

- `GET /api/history` - List test history
- `GET /api/history/{test_id}` - Get specific test
- `GET /api/history/statistics` - Get aggregated statistics
- `DELETE /api/history/{test_id}` - Delete test
- `DELETE /api/history` - Clear all history

### Game Selector Endpoints

- `GET /api/game-selector/windows` - Get active game windows
- `GET /api/game-selector/sessions` - Get previous sessions
- `POST /api/game-selector/sessions` - Save game session
- `DELETE /api/game-selector/sessions/{session_id}` - Delete session

**Full API Documentation:** Visit `http://localhost:8000/docs` when backend is running.

---

## 🎮 Usage Workflow

### Step-by-Step Instructions

1. **Open First Terminal Window (Backend)**
   - Open PowerShell (Windows) or Terminal (Linux/Mac)
   - Navigate to backend directory
   - Activate virtual environment
   - Run: `python app.py`
   - **Leave this window open!**

2. **Open Second Terminal Window (Frontend)**
   - Open a **NEW** PowerShell/Terminal window
   - Navigate to frontend directory
   - Run: `npm run dev`
   - **Leave this window open!**

3. **Open Browser**
   - Navigate to `http://localhost:5173`
   - You should see the AI Game Testing System interface

4. **Start Testing**
   - Select a genre (Platformer, FPS, Racing, RPG)
   - Click "GAME: Auto-detect" to select a game window (optional)
   - Click "Start Testing"
   - Monitor metrics in real-time
   - Click "Stop" to end testing

5. **View History**
   - Test results are automatically saved
   - Access via History API endpoints

### ⚠️ Important Notes

- **Both terminal windows must stay open** while using the application
- If you close either window, that service will stop
- To stop the application: Press `CTRL+C` in each terminal window
- You can minimize the terminal windows, but don't close them

---

## 📝 Additional Notes

### Development Mode

- **Backend:** Auto-reloads on code changes (when using `--reload`)
- **Frontend:** Hot Module Replacement (HMR) enabled by default

### Production Build

**Frontend:**
```bash
cd frontend
npm run build
# Output in frontend/dist/
```

**Backend:**
```bash
cd backend
# Use production WSGI server like gunicorn
pip install gunicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Database

- Test history is stored in SQLite: `backend/logs/game_sessions.db`
- Metrics are stored in JSON: `backend/logs/metrics.json`
- Logs are stored in: `backend/logs/app.log`

---

## 🆘 Getting Help

1. Check the logs:
   - Backend: `backend/logs/app.log`
   - Browser console (F12)

2. Verify all prerequisites are installed

3. Check that ports 8000 and 5173 are available

4. Review the API documentation at `http://localhost:8000/docs`

5. Check existing documentation files:
   - `PRODUCTION_REFACTORING.md`
   - `RESTRUCTURING_COMPLETE.md`
   - `GAME_SELECTOR_FEATURE.md`
   - `TEST_HISTORY_FEATURE.md`

---

## ✅ Quick Start Checklist

- [ ] Python 3.9+ installed
- [ ] Node.js 18+ installed
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Browser opened to `http://localhost:5173`
- [ ] No errors in terminal or browser console

---

**Happy Testing! 🎮🤖**

