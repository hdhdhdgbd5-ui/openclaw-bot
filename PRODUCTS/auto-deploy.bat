@echo off
REM ANGEL ARMY AUTO-DEPLOY SCRIPT
REM Deploys all 4 products to GitHub Pages automatically

echo ==========================================
echo ANGEL ARMY - AUTO DEPLOYMENT
echo ==========================================
echo.

REM Check if git is installed
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Git not installed
    echo Install from: https://git-scm.com/download/win
    pause
    exit /b 1
)

REM Get GitHub username from user
set /p GITHUB_USER="Enter your GitHub username: "
set /p GITHUB_TOKEN="Enter your GitHub token (hidden): "

echo.
echo Deploying RentVault...
cd RentVault
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://%GITHUB_USER%:%GITHUB_TOKEN%@github.com/%GITHUB_USER%/RentVault.git
git push -u origin main
if %errorlevel% neq 0 echo ERROR deploying RentVault
cd ..

echo.
echo Deploying StreakVault...
cd StreakVault
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://%GITHUB_USER%:%GITHUB_TOKEN%@github.com/%GITHUB_USER%/StreakVault.git
git push -u origin main
if %errorlevel% neq 0 echo ERROR deploying StreakVault
cd ..

echo.
echo Deploying FocusMaster...
cd FocusMaster
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://%GITHUB_USER%:%GITHUB_TOKEN%@github.com/%GITHUB_USER%/FocusMaster.git
git push -u origin main
if %errorlevel% neq 0 echo ERROR deploying FocusMaster
cd ..

echo.
echo Deploying BudgetVault...
cd BudgetVault
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://%GITHUB_USER%:%GITHUB_TOKEN%@github.com/%GITHUB_USER%/BudgetVault.git
git push -u origin main
if %errorlevel% neq 0 echo ERROR deploying BudgetVault
cd ..

echo.
echo ==========================================
echo DEPLOYMENT COMPLETE
echo ==========================================
echo.
echo Your products are now at:
echo https://%GITHUB_USER%.github.io/RentVault
echo https://%GITHUB_USER%.github.io/StreakVault
echo https://%GITHUB_USER%.github.io/FocusMaster
echo https://%GITHUB_USER%.github.io/BudgetVault
echo.
echo Next steps:
echo 1. Go to each GitHub repo
echo 2. Settings -> Pages
echo 3. Select "Deploy from branch: main"
echo 4. Your sites will be LIVE!
echo.
pause
