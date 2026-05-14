@echo off
REM Stop script for Windows

echo ========================================
echo Face Recognition Attendance System
echo Stopping Docker Containers
echo ========================================
echo.

docker-compose down

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to stop containers!
    echo.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Containers stopped!
echo.
echo To start again, run: start.bat
echo.
echo To remove all data (including database):
echo   docker-compose down -v
echo.
pause
