# Start All Servers (Backend + Frontend)
# Run from project root: .\scripts\start-all.ps1

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Starting Sahayak Dev Servers" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Green
Write-Host "API docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop both servers." -ForegroundColor Yellow
Write-Host ""

# Start backend in background
$backend = Start-Process powershell -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "$PSScriptRoot\start-backend.ps1" -PassThru -WindowStyle Minimized

# Start frontend in background
$frontend = Start-Process powershell -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "$PSScriptRoot\start-frontend.ps1" -PassThru -WindowStyle Minimized

Write-Host "Servers started. Backend PID: $($backend.Id), Frontend PID: $($frontend.Id)" -ForegroundColor Green
Write-Host ""

# Wait for user to press Ctrl+C
try {
    while ($true) { Start-Sleep -Seconds 5 }
} finally {
    Write-Host "`nStopping servers..." -ForegroundColor Yellow
    Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $frontend.Id -Force -ErrorAction SilentlyContinue
    Write-Host "Done." -ForegroundColor Green
}
