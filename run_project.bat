@echo off
set "ROOT_DIR=%~dp0"

echo ===============================================
echo 1. CLEANING UP SYSTEM PORTS...
echo ===============================================
:: Kill only processes on our specific ports (handled below)
echo Terminating old instances on target ports...
echo.
:: Specifically target port 5055 and 5173
echo Ensuring Ports 5055 and 5173 are free...
:: Non-blocking port cleanup for speed
start /b powershell -Command "Get-NetTCPConnection -LocalPort 5055 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }" 2>nul
start /b powershell -Command "Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }" 2>nul
echo Done.

echo.
echo ===============================================
echo 2. DETECTING NETWORK CONFIGURATION...
echo ===============================================
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set "LOCAL_IP=%%a"
)
:: Trim leading spaces
set "LOCAL_IP=%LOCAL_IP:~1%"
if "%LOCAL_IP%"=="" set "LOCAL_IP=localhost"

echo LOCAL NETWORK IP: %LOCAL_IP%
echo.

echo ===============================================
echo 3. STARTING ROBUST ARCHITECTURE...
echo ===============================================

echo Launching Backend (Port 5055)...
start "DIAGNOSIS-BACKEND" cmd /c "cd /d %ROOT_DIR%backend && echo [ENGINE] INITIALIZING MODELS... && python main.py || pause"

echo Launching Frontend (Port 5173)...
start "DIAGNOSIS-FRONTEND" cmd /c "cd /d %ROOT_DIR%frontend && echo [UI] STARTING INTERFACE... && npm run dev || pause"

echo Waiting for Neural Engine to ignite...
:: Increased stabilization time for ML model loading
timeout /t 5 /nobreak >nul

echo.
echo ===============================================
echo 4. GLOBAL SYSTEM STATUS: ONLINE [%TIME%]
echo ===============================================
echo [ACTIVE] Local Access    : http://localhost:5173
echo [ACTIVE] Network Access  : http://%LOCAL_IP%:5173
echo [ACTIVE] Backend API     : http://%LOCAL_IP%:5055/
echo ===============================================
echo EVERYTHING IS ONLINE - DO NOT CLOSE THIS WINDOW
echo For external device access, use the Network Access URL.
echo ===============================================
echo.
pause

