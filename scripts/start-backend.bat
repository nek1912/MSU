@echo off
REM Start Backend Server
REM Run from project root: scripts\start-backend.bat

echo Starting FastAPI backend on http://localhost:8000 ...
cd backend
python -m uvicorn app.main:app --reload --port 8000
