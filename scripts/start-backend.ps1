# Start Backend Server
# Run from project root: .\scripts\start-backend.ps1

Write-Host "Starting FastAPI backend on http://localhost:8000 ..." -ForegroundColor Yellow
Set-Location backend
python -m uvicorn app.main:app --reload --port 8000
