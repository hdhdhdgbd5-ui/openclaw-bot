@echo off
REM Angel Army - One-Click Deploy Launcher

echo ==========================================
echo ANGEL ARMY - FULL AUTO DEPLOYMENT
echo ==========================================
echo.
echo This will deploy all 4 products AUTOMATICALLY.
echo.
echo Requirements:
echo - GitHub account (free)
echo - GitHub token (from github.com/settings/tokens)
echo.

set /p username="Enter GitHub username: "
set /p token="Enter GitHub token (ghp_...): "

echo.
echo Launching full deployment...
echo.

powershell -ExecutionPolicy Bypass -File "FULL_AUTO_DEPLOY.ps1" -GitHubUsername "%username%" -GitHubToken "%token%"

pause
