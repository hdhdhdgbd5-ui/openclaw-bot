@echo off
echo ==========================================
echo  MONEY ARMY 5 - 24/7 Money Machine
echo  Starting Continuous Income Generation
echo ==========================================
echo.

rem Change to workspace directory
cd /d %USERPROFILE%\.openclaw\workspace

rem Create necessary directories
if not exist logs mkdir logs
if not exist scripts mkdir scripts
if not exist data mkdir data

echo [INFO] Checking system...
echo [INFO] Initializing Money Army 5...
echo.

rem Run the master orchestrator
powershell.exe -ExecutionPolicy Bypass -File scripts\money_army_master.ps1

echo.
echo ==========================================
echo Money Army 5 session complete
echo ==========================================
pause
