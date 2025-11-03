@echo off
echo ========================================
echo   FastAPI Server Auto-Start
echo ========================================
echo.

REM Change to FastAPI directory
cd /d "C:\server\httpd\fastapi"

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python not found
    echo    Please install Python or add to PATH
    pause
    exit /b 1
)

REM Check if port 443 is available
netstat -ano | findstr ":443" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo ⚠️  WARNING: Port 443 is in use
    echo    Another server might be running
    echo.
)

echo 🚀 Starting FastAPI Server on port 443...
echo 🌐 Server will be available at:
echo    https://localhost
echo    https://localhost/docs
echo    https://localhost/health
echo.
echo ⏳ Starting server... (Press Ctrl+C to stop)
echo ========================================
echo.

REM Start the FastAPI server
python start_443.py

echo.
echo 🛑 Server stopped
echo.
pause
