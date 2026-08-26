# Sahayak Foundation - Local Verification Script
# Run from project root: .\scripts\verify.ps1

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Sahayak Foundation Verification" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Backend tests
Write-Host "[1/6] Backend tests..." -ForegroundColor Yellow
Set-Location backend
python -m pytest -v --tb=short
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED: Backend tests" -ForegroundColor Red; exit 1 }
Set-Location ..

# 2. Backend lint
Write-Host "`n[2/6] Backend lint..." -ForegroundColor Yellow
Set-Location backend
ruff check .
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED: Backend lint" -ForegroundColor Red; exit 1 }
Set-Location ..

# 3. Frontend test
Write-Host "`n[3/6] Frontend test..." -ForegroundColor Yellow
Set-Location frontend
npx vitest run
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED: Frontend test" -ForegroundColor Red; exit 1 }
Set-Location ..

# 4. Frontend build
Write-Host "`n[4/6] Frontend build..." -ForegroundColor Yellow
Set-Location frontend
npm run build
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED: Frontend build" -ForegroundColor Red; exit 1 }
Set-Location ..

# 5. Corpus quality check
Write-Host "`n[5/6] Corpus quality check..." -ForegroundColor Yellow
python eval/corpus_check.py
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED: Corpus check" -ForegroundColor Red; exit 1 }

# 6. Security scan
Write-Host "`n[6/6] Security scan..." -ForegroundColor Yellow
python eval/security_check.py
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED: Security check" -ForegroundColor Red; exit 1 }

Write-Host "`n============================================" -ForegroundColor Green
Write-Host "  ALL CHECKS PASSED" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
