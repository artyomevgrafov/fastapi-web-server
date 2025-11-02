@echo off
echo ========================================
echo FastAPI Migration Script
echo Replacing Apache with FastAPI Server
echo ========================================
echo.

REM Check if running as Administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo [1/4] Stopping Apache HTTP Server...
sc stop "Apache2.4" >nul 2>&1
if %errorLevel% equ 0 (
    echo ✓ Apache service stopped successfully
) else (
    echo ℹ Apache service not running or not found
)

echo [2/4] Installing Python dependencies...
cd /d "%~dp0"
pip install -r requirements.txt >nul 2>&1
if %errorLevel% equ 0 (
    echo ✓ Dependencies installed successfully
) else (
    echo ✗ Failed to install dependencies
    echo Please install manually: pip install -r requirements.txt
)

echo [3/4] Starting FastAPI Server...
echo Server will start on port 80...
echo Access points:
echo   - Web Interface: http://localhost
echo   - API Docs: http://localhost/docs
echo   - Health Check: http://localhost/health
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start FastAPI server
python start_server.py

echo.
echo [4/4] Migration complete!
echo FastAPI server is now running on port 80
echo.
pause
