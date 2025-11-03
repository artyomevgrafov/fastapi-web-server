@echo off
echo ========================================
echo   Prometheus Monitoring for FastAPI
echo ========================================
echo.

REM Check if Prometheus directory exists
if not exist "C:\Users\a.evgrahov\Downloads\prometheus-3.7.3.windows-amd64" (
    echo ❌ ERROR: Prometheus not found at:
    echo    C:\Users\a.evgrahov\Downloads\prometheus-3.7.3.windows-amd64
    echo.
    echo 📥 Download Prometheus from:
    echo    https://prometheus.io/download/
    echo.
    pause
    exit /b 1
)

REM Check if configuration file exists
if not exist "prometheus.yml" (
    echo ❌ ERROR: prometheus.yml configuration file not found
    echo.
    pause
    exit /b 1
)

echo ✅ Prometheus found
echo ✅ Configuration file found
echo.
echo 📊 Starting Prometheus monitoring...
echo 🌐 Prometheus Web UI: http://localhost:9090
echo 📈 FastAPI Metrics: http://localhost:8080/metrics
echo.

REM Change to Prometheus directory and start
cd /d "C:\Users\a.evgrahov\Downloads\prometheus-3.7.3.windows-amd64"
.\prometheus.exe --config.file="C:\server\httpd\fastapi\prometheus.yml" --web.enable-lifecycle

echo.
echo 🛑 Prometheus stopped
pause
