@echo off
echo ========================================
echo   FastAPI + Prometheus - Windows Launcher
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python not found or not in PATH
    echo    Please install Python or add it to PATH
    echo.
    pause
    exit /b 1
)

REM Check if Prometheus directory exists
if not exist "C:\Users\a.evgrahov\Downloads\prometheus-3.7.3.windows-amd64" (
    echo ⚠️  WARNING: Prometheus not found
    echo    Download from: https://prometheus.io/download/
    echo    Will start FastAPI only (without monitoring)
    echo.
    set PROMETHEUS_AVAILABLE=0
) else (
    set PROMETHEUS_AVAILABLE=1
    echo ✅ Prometheus found
)

REM Check if configuration file exists
if not exist "prometheus.yml" (
    echo ⚠️  WARNING: prometheus.yml not found
    echo    Will start FastAPI only (without monitoring)
    echo.
    set PROMETHEUS_AVAILABLE=0
)

echo.
echo 🚀 Starting Services...
echo.

REM Start Prometheus if available
if "%PROMETHEUS_AVAILABLE%"=="1" (
    echo 📊 Starting Prometheus monitoring...
    start "Prometheus Monitoring" cmd /k "cd /d C:\Users\a.evgrahov\Downloads\prometheus-3.7.3.windows-amd64 && prometheus.exe --config.file=C:\server\httpd\fastapi\prometheus.yml --web.enable-lifecycle"
    timeout /t 3 /nobreak >nul
    echo ✅ Prometheus started (PID: !)
)

REM Start FastAPI server
echo 🚀 Starting FastAPI Production Server...
echo.
echo 📋 Server Information:
echo    Host: 0.0.0.0
echo    Port: 8080
echo    Mode: Windows Production
echo.
echo 🌐 Access Points:
echo    Main:      http://localhost:8080
echo    Health:    http://localhost:8080/health
echo    Docs:      http://localhost:8080/docs
echo.

if "%PROMETHEUS_AVAILABLE%"=="1" (
    echo 📊 Monitoring:
    echo    Prometheus: http://localhost:9090
    echo    Metrics:    http://localhost:8080/metrics
    echo.
)

echo ⏳ Starting server... (Press Ctrl+C in this window to stop)
echo ========================================
echo.

REM Start FastAPI server
python start_production_windows.py

echo.
echo 🛑 FastAPI server stopped
echo.

if "%PROMETHEUS_AVAILABLE%"=="1" (
    echo ⚠️  Prometheus is still running in separate window
    echo    Close that window to stop Prometheus
    echo.
)

pause
