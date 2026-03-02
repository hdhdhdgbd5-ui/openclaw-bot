@echo off
echo ===================================
echo Manual Deployment - ContractGenius
echo ===================================
echo.

cd /d "C:\Users\armoo\.openclaw\workspace\PRODUCTS\ContractGenius"

echo [1/4] Cloning repo...
git clone https://github.com/hdhdhdgbd5-ui/ContractGenius.git temp_repo 2>nul
if errorlevel 1 (
    echo Repo already exists, using existing...
)

echo [2/4] Copying build files...
if exist temp_repo (rmdir /s /q temp_repo)
git clone https://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@github.com/hdhdhdgbd5-ui/ContractGenius.git temp_repo
cd temp_repo
rmdir /s /q .git
copy /y "..\frontend\dist\index.html" .
xcopy /y /e "..\frontend\dist\assets" assets\

echo [3/4] Committing and pushing...
git init
git add .
git commit -m "Deploy ContractGenius v1.0"
git branch -M main
git remote add origin https://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@github.com/hdhdhdgbd5-ui/ContractGenius.git
git push -f origin main

echo [4/4] Cleaning up...
cd ..
rmdir /s /q temp_repo

echo.
echo ===================================
echo SUCCESS!
echo ===================================
echo.
echo LIVE URL: https://hdhdhdgbd5-ui.github.io/ContractGenius
echo.
echo Wait 2-5 minutes for GitHub Pages to activate
echo.
pause
