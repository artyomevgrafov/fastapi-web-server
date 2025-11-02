@echo off
echo ========================================
echo FastAPI Server - Port 443 Launcher
echo ========================================
echo.

REM Check if running as Administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ This script must be run as Administrator
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

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

REM Check if Apache is running
netstat -an | find ":443" >nul
if not errorlevel 1 (
    echo ⚠️  Port 443 is in use (Apache is probably running)
    echo Stopping Apache service...
    sc stop "Apache2.4" >nul 2>&1
    timeout /t 3 >nul

    REM Check again
    netstat -an | find ":443" >nul
    if not errorlevel 1 (
        echo ❌ Failed to free port 443
        echo Please stop Apache manually and try again
        pause
        exit /b 1
    )
    echo ✅ Apache stopped successfully
)

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

REM Set environment for production
set FASTAPI_ENV=production

echo ✅ Starting FastAPI server on port 443...
echo 📍 Server will be available at:
echo    - Web Interface: https://localhost
echo    - API Docs: https://localhost/docs
echo    - Health Check: https://localhost/api/health
echo.
echo 🚨 IMPORTANT: This is production server on standard HTTPS port
echo    Make sure Apache is stopped before continuing
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Start the FastAPI server
python start_443.py

if errorlevel 1 (
    echo.
    echo ❌ Server failed to start
    echo Possible issues:
    echo   - Port 443 is still in use
    echo   - SSL certificates are invalid
    echo   - Administrator privileges missing
    echo   - Python dependencies missing
    echo.
    echo Run: pip install -r requirements.txt
    echo.

    REM Restart Apache if FastAPI failed
    echo Restarting Apache for fallback...
    sc start "Apache2.4" >nul 2>&1
    pause
    exit /b 1
)

REM If server stopped normally, restart Apache
echo.
echo 🛑 FastAPI server stopped
echo Restarting Apache...
sc start "Apache2.4" >nul 2>&1
echo ✅ Apache restarted

pause
