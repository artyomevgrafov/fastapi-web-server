@echo off
echo ========================================
echo FastAPI Server - Port 8080 Launcher
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Change to the script directory
cd /d "%~dp0"

REM Check if SSL certificates exist
if not exist "certs\cert.pem" (
    echo ⚠️  SSL certificates not found
    echo Running certificate synchronization...
    powershell -ExecutionPolicy Bypass -File "C:\server\httpd\win-acme\sync-certs.ps1"
    if errorlevel 1 (
        echo ❌ Failed to sync certificates
        pause
        exit /b 1
    )
)

if not exist "certs\key.pem" (
    echo ❌ SSL key file not found after synchronization
    pause
    exit /b 1
)

REM Set environment for development with SSL
set FASTAPI_ENV=development

echo ✅ Starting FastAPI server on port 8080...
echo 📍 Server will be available at:
echo    - Web Interface: https://localhost:8080
echo    - API Docs: https://localhost:8080/docs
echo    - Health Check: https://localhost:8080/api/health
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Start the FastAPI server
python start_8080.py

if errorlevel 1 (
    echo.
    echo ❌ Server failed to start
    echo Possible issues:
    echo   - Port 8080 is already in use
    echo   - SSL certificates are invalid
    echo   - Python dependencies missing
    echo.
    echo Run: pip install -r requirements.txt
    pause
    exit /b 1
)

pause
