@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   FastAPI Server Auto-Start Installer
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  This script requires Administrator privileges
    echo    Please run as Administrator
    echo.
    pause
    exit /b 1
)

echo ✅ Running as Administrator
echo.

REM Delete existing task if exists
echo 📋 Removing existing FastAPI task...
schtasks /delete /tn "FastAPI Server" /f >nul 2>&1

REM Create new scheduled task
echo 📋 Creating new scheduled task...
schtasks /create /tn "FastAPI Server" /xml "fastapi_task.xml" /f

if %errorlevel% equ 0 (
    echo ✅ Scheduled task created successfully!
    echo.
    echo 📋 Task Details:
    echo    Name: FastAPI Server
    echo    Trigger: System startup and user logon
    echo    Action: Start FastAPI on port 443
    echo    Run as: SYSTEM (highest privileges)
    echo.
    echo 🌐 Server will start automatically on:
    echo    - System startup
    echo    - User logon
    echo.
    echo 🚀 To start manually: schtasks /run /tn "FastAPI Server"
    echo 🛑 To stop manually: schtasks /end /tn "FastAPI Server"
    echo 📊 To check status: schtasks /query /tn "FastAPI Server"
) else (
    echo ❌ Failed to create scheduled task
    echo 💡 Try running: schtasks /create /tn "FastAPI Server" /xml "fastapi_task.xml"
)

echo.
echo 📋 Testing server startup...
echo 🚀 Starting FastAPI server manually...
start "" "start_fastapi.bat"

echo.
echo ⏳ Waiting for server to start...
timeout /t 5 /nobreak >nul

echo 📊 Checking if server is running...
curl -k -s -o nul -w "%%{http_code}" https://localhost/health
if !errorlevel! equ 0 (
    echo ✅ Server is running and responding!
    echo 🌐 Access points:
    echo    Main: https://localhost
    echo    Docs: https://localhost/docs
    echo    Health: https://localhost/health
) else (
    echo ⚠️  Server might not be running yet
    echo 💡 Check the opened window for errors
)

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo ✅ FastAPI server will now start automatically
echo ✅ Manual start: Double-click start_fastapi.bat
echo ✅ Auto-start: Enabled via Windows Task Scheduler
echo.
pause
