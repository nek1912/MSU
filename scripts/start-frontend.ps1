# Start Frontend Server
# Run from project root: .\scripts\start-frontend.ps1

Write-Host "Starting Next.js frontend on http://localhost:3000 ..." -ForegroundColor Yellow
Set-Location frontend
npm run dev
