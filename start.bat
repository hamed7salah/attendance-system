@echo off
REM Quick start script for Windows

echo ========================================
echo Face Recognition Attendance System
echo Docker Quick Start
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop and try again.
    echo.
    pause
    exit /b 1
)

echo [OK] Docker is running
echo.

echo Starting containers...
echo This may take a few minutes on first run...
echo.

docker-compose up -d

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start containers!
    echo Check the error messages above.
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo [SUCCESS] Containers started!
echo ========================================
echo.
echo Waiting for application to be ready...
timeout /t 10 /nobreak >nul

echo.
echo Application is starting up...
echo.
echo Access the application at:
echo   http://localhost:8501
echo.
echo To view logs:
echo   docker-compose logs -f app
echo.
echo To stop:
echo   docker-compose down
echo.
echo ========================================
pause
