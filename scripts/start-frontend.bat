@echo off
REM Start Frontend Server
REM Run from project root: scripts\start-frontend.bat

echo Starting Next.js frontend on http://localhost:3000 ...
cd frontend
npm run dev
