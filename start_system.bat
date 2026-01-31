@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Starting AI Game Testing System...
echo ========================================

REM Get the script directory
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%AI_Game_Testing_System"

if not exist "%PROJECT_DIR%" (
    echo ERROR: AI_Game_Testing_System directory not found!
    echo Expected at: %PROJECT_DIR%
    pause
    exit /b 1
)

echo.
echo [1/3] Cleaning Python cache files...
echo Removing __pycache__ directories and .pyc files...
cd /d "%PROJECT_DIR%\backend"
if exist __pycache__ (
    for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
)
for /r . %%f in (*.pyc) do @if exist "%%f" del /q "%%f" 2>nul
echo Cache cleared!

echo.
echo [2/3] Starting Backend Server...
start "Backend Server" cmd /k "cd /d "%PROJECT_DIR%\backend" && pip install -r requirements.txt --quiet && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo.
echo [3/3] Starting Frontend Dashboard...
start "Frontend Dashboard" cmd /k "cd /d "%PROJECT_DIR%\frontend" && npm install --silent && npm run dev"

echo.
echo ========================================
echo System started successfully!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo ========================================
echo.
echo NOTE: All Python cache files have been cleared.
echo The system will use the latest code changes.
echo.
echo Press any key to exit...
pause >nul
