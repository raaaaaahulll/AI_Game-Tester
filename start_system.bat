@echo off
echo Starting AI Game Testing System...

cd AI_Game_Testing_System

echo Starting Backend...
start "Backend Server" cmd /k "pip install -r backend/requirements.txt && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

echo Starting Frontend...
cd frontend
start "Frontend Dashboard" cmd /k "npm install && npm run dev"

echo Done! Access dashboard at http://localhost:5173
