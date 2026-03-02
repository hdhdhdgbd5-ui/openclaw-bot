# ANGEL ARMY - PowerShell Auto-Deploy
# Run this in PowerShell as Administrator

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "ANGEL ARMY - AUTO DEPLOYMENT" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Get credentials
$username = Read-Host "Enter your GitHub username"
$token = Read-Host "Enter your GitHub token" -AsSecureString
$tokenPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($token))

# Fix git config for all directories
Write-Host "Configuring git..." -ForegroundColor Yellow
$products = @("RentVault", "StreakVault", "FocusMaster", "BudgetVault")
foreach ($product in $products) {
    $path = "C:\Users\armoo\.openclaw\workspace\PRODUCTS\$product"
    git config --global --add safe.directory $path 2>$null
}
git config --global user.email "angel@angelarmy.ai"
git config --global user.name "Angel Army"

# Function to deploy a product
function Deploy-Product($productName) {
    Write-Host ""
    Write-Host "Deploying $productName..." -ForegroundColor Green
    
    $path = "C:\Users\armoo\.openclaw\workspace\PRODUCTS\$productName"
    Set-Location $path
    
    # Initialize git if needed
    if (-not (Test-Path ".git")) {
        git init
    }
    
    # Add and commit
    git add .
    $commit = git commit -m "$productName v1.0 ready for launch" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Nothing new to commit (already committed)" -ForegroundColor Yellow
    }
    
    # Set main branch
    git branch -M main 2>$null
    
    # Add remote
    git remote remove origin 2>$null
    git remote add origin "https://$username`:$tokenPlain@github.com/$username/$productName.git"
    
    # Push
    $push = git push -u origin main 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ $productName deployed successfully!" -ForegroundColor Green
        Write-Host "   URL: https://$username.github.io/$productName" -ForegroundColor Cyan
    } else {
        Write-Host "❌ ERROR deploying $productName" -ForegroundColor Red
        Write-Host "   $push" -ForegroundColor Gray
        Write-Host "   Make sure you created the repo on GitHub first!" -ForegroundColor Yellow
    }
}

# Deploy all products
foreach ($product in $products) {
    Deploy-Product $product
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your products:" -ForegroundColor Yellow
foreach ($product in $products) {
    Write-Host "  https://$username.github.io/$product" -ForegroundColor Cyan
}
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Go to each GitHub repo" -ForegroundColor White
Write-Host "2. Settings -> Pages" -ForegroundColor White
Write-Host "3. Select 'Deploy from branch: main'" -ForegroundColor White
Write-Host "4. Your sites will be LIVE!" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"
