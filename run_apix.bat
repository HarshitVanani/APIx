@echo off
title APIx Pipeline Launcher
echo ====================================================
echo Starting APIx High-Frequency Airfare Intelligence Engine
echo ====================================================

echo [1/2] Launching Backend FastAPI Server (Port 8000)...
start cmd /k "cd backend && call venv\Scripts\activate && python -m uvicorn api.main:app --reload --port 8000"

echo [2/2] Launching Frontend Dashboard (Port 5173)...
start cmd /k "cd frontend && npm run dev"

echo ====================================================
echo All services triggered successfully!
echo Backend Docs: http://localhost:8000/docs
echo Web Interface: http://localhost:5173
echo ====================================================
pause