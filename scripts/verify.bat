@echo off
REM Sahayak Foundation - Local Verification Script
REM Run from project root: scripts\verify.bat

echo ============================================
echo   Sahayak Foundation Verification
echo ============================================
echo.

echo [1/6] Backend tests...
cd backend
python -m pytest -v --tb=short
if %errorlevel% neq 0 (
    echo FAILED: Backend tests
    exit /b 1
)
cd ..

echo.
echo [2/6] Backend lint...
cd backend
ruff check .
if %errorlevel% neq 0 (
    echo FAILED: Backend lint
    exit /b 1
)
cd ..

echo.
echo [3/6] Frontend test...
cd frontend
npx vitest run
if %errorlevel% neq 0 (
    echo FAILED: Frontend test
    exit /b 1
)
cd ..

echo.
echo [4/6] Frontend build...
cd frontend
npm run build
if %errorlevel% neq 0 (
    echo FAILED: Frontend build
    exit /b 1
)
cd ..

echo.
echo [5/6] Corpus quality check...
python eval/corpus_check.py
if %errorlevel% neq 0 (
    echo FAILED: Corpus check
    exit /b 1
)

echo.
echo [6/6] Security scan...
python eval/security_check.py
if %errorlevel% neq 0 (
    echo FAILED: Security check
    exit /b 1
)

echo.
echo ============================================
echo   ALL CHECKS PASSED
echo ============================================
