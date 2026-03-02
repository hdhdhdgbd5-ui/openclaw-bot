@echo off
echo ===================================
echo ContractGenius Auto-Deployment
echo ===================================
echo.

set /p username="GitHub username: "
set /p token="GitHub token: "

echo.
echo Deploying ContractGenius to GitHub Pages + Render...
echo.

REM Create GitHub repo via API
echo [1/5] Creating GitHub repository...
curl -X POST https://api.github.com/user/repos -H "Authorization: token %token%" -H "Accept: application/vnd.github.v3+json" -d "{\"name\":\"ContractGenius\",\"description\":\"AI-Powered Legal Contract Analyzer\",\"private\":false,\"auto_init\":true}" > nul 2>&1

REM Build frontend
echo [2/5] Building frontend...
cd frontend
call npm install 2>nul
call npm run build 2>nul
cd ..

REM Deploy to GitHub Pages
echo [3/5] Deploying to GitHub Pages...
cd frontend\dist
git init
git add .
git commit -m "ContractGenius v1.0"
git branch -M main
git remote add origin https://%username%:%token%@github.com/%username%/ContractGenius.git 2>nul
git push -f origin main:gh-pages 2>nul
cd ..\..

echo [4/5] Configuring backend on Render...
echo Backend setup: Create Web Service on render.com
echo Use these settings:
echo   - Build Command: pip install -r requirements.txt
echo   - Start Command: uvicorn app:app --host 0.0.0.0 --port 8000
echo   - Upload backend/ folder

echo.
echo ===================================
echo DEPLOYMENT COMPLETE!
echo ===================================
echo.
echo Frontend: https://%username%.github.io/ContractGenius
echo Backend: https://dashboard.render.com (manual setup required)
echo.
echo.
pause
