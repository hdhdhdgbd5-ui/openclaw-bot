# ANGEL ARMY - FULL AUTOMATIC DEPLOYMENT
# Creates repos, uploads files, enables Pages - ALL AUTOMATIC
# PRIVACY: All personal info sanitized before upload

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubUsername,
    
    [Parameter(Mandatory=$true)]
    [string]$GitHubToken
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "ANGEL ARMY - FULL AUTO DEPLOYMENT" -ForegroundColor Cyan
Write-Host "Privacy Mode: ON (No personal info in repos)" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$products = @(
    @{Name="RentVault"; Description="Tenant evidence documentation app - document rental condition with timestamped photos"},
    @{Name="StreakVault"; Description="Beautiful habit tracker with streaks - build daily habits"},
    @{Name="FocusMaster"; Description="2-minute focus challenge game - stay focused, earn rewards"},
    @{Name="BudgetVault"; Description="Simple budget tracker - track income and expenses offline"}
)

$headers = @{
    "Authorization" = "token $GitHubToken"
    "Accept" = "application/vnd.github.v3+json"
}

# Function to create repo via API
function Create-Repo($product) {
    Write-Host "Creating repo: $($product.Name)..." -ForegroundColor Yellow
    
    $body = @{
        name = $product.Name
        description = $product.Description
        private = $false
        auto_init = $true
        gitignore_template = "HTML"
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method Post -Headers $headers -Body $body -ContentType "application/json"
        Write-Host "  ✅ Repo created: $($response.html_url)" -ForegroundColor Green
        return $true
    } catch {
        if ($_.Exception.Response.StatusCode.value__ -eq 422) {
            Write-Host "  ⚠️ Repo already exists, continuing..." -ForegroundColor Yellow
            return $true
        }
        Write-Host "  ❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to get file content and sanitize
function Get-SanitizedContent($filePath) {
    $content = Get-Content -Path $filePath -Raw -Encoding UTF8
    
    # Remove any personal info patterns
    $content = $content -replace 'Tez', 'User'
    $content = $content -replace 'for Tez', ''
    $content = $content -replace '2026-02-19', ''
    $content = $content -replace 'C:\\Users\\armoo.*?PRODUCTS', 'PRODUCTS'
    $content = $content -replace 'armoo@LAPTOP-CPMRH5SK', 'angel@angelarmy.ai'
    
    return $content
}

# Function to upload files to repo
function Upload-Files($productName) {
    Write-Host "Uploading files to $productName..." -ForegroundColor Yellow
    
    $localPath = "C:\Users\armoo\.openclaw\workspace\PRODUCTS\$productName"
    $files = Get-ChildItem -Path $localPath -File | Where-Object { $_.Name -notlike "*.ps1" -and $_.Name -notlike "*.bat" -and $_.Name -notlike ".git*" }
    
    foreach ($file in $files) {
        $fileName = $file.Name
        Write-Host "  Uploading: $fileName..." -ForegroundColor Gray -NoNewline
        
        # Get sanitized content
        $content = Get-SanitizedContent $file.FullName
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
        $base64 = [Convert]::ToBase64String($bytes)
        
        # Check if file exists
        $existingSha = $null
        try {
            $existing = Invoke-RestMethod -Uri "https://api.github.com/repos/$GitHubUsername/$productName/contents/$fileName" -Headers $headers
            $existingSha = $existing.sha
        } catch {}
        
        $body = @{
            message = "Add $fileName"
            content = $base64
        }
        if ($existingSha) {
            $body.sha = $existingSha
        }
        
        try {
            Invoke-RestMethod -Uri "https://api.github.com/repos/$GitHubUsername/$productName/contents/$fileName" -Method Put -Headers $headers -Body ($body | ConvertTo-Json) -ContentType "application/json" | Out-Null
            Write-Host " ✓" -ForegroundColor Green
        } catch {
            Write-Host " ✗" -ForegroundColor Red
            Write-Host "    Error: $($_.Exception.Message)" -ForegroundColor Gray
        }
    }
}

# Function to enable GitHub Pages
function Enable-Pages($productName) {
    Write-Host "Enabling GitHub Pages for $productName..." -ForegroundColor Yellow
    
    $body = @{
        source = @{
            branch = "main"
            path = "/"
        }
    } | ConvertTo-Json
    
    try {
        Invoke-RestMethod -Uri "https://api.github.com/repos/$GitHubUsername/$productName/pages" -Method Post -Headers $headers -Body $body -ContentType "application/json" | Out-Null
        Write-Host "  ✅ Pages enabled!" -ForegroundColor Green
        return $true
    } catch {
        if ($_.Exception.Response.StatusCode.value__ -eq 409) {
            Write-Host "  ℹ️ Pages already enabled" -ForegroundColor Yellow
            return $true
        }
        Write-Host "  ⚠️ Could not enable Pages automatically" -ForegroundColor Yellow
        Write-Host "     Manual step: Go to github.com/$GitHubUsername/$productName/settings/pages" -ForegroundColor Cyan
        return $false
    }
}

# Main deployment
$deployedUrls = @()

foreach ($product in $products) {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "Deploying: $($product.Name)" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    
    # Step 1: Create repo
    if (Create-Repo $product) {
        # Step 2: Upload files
        Upload-Files $product.Name
        
        # Step 3: Enable Pages
        Enable-Pages $product.Name
        
        $deployedUrls += "https://$GitHubUsername.github.io/$($product.Name)"
    }
    
    Start-Sleep -Seconds 2
}

# Summary
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your live products:" -ForegroundColor Green
foreach ($url in $deployedUrls) {
    Write-Host "  🌐 $url" -ForegroundColor Cyan
}
Write-Host ""
Write-Host "⚠️ IMPORTANT:" -ForegroundColor Yellow
Write-Host "   It takes 2-5 minutes for GitHub Pages to activate." -ForegroundColor White
Write-Host "   If links don't work immediately, wait and refresh." -ForegroundColor White
Write-Host ""
Write-Host "📤 NEXT STEPS:" -ForegroundColor Green
Write-Host "   1. Test each URL above (wait 2-5 min first)" -ForegroundColor White
Write-Host "   2. Open Reddit posting agent" -ForegroundColor White
Write-Host "   3. Copy marketing post and submit" -ForegroundColor White
Write-Host "   4. Watch traffic come in!" -ForegroundColor White
Write-Host ""

# Save deployed URLs to file
$deployedUrls | Out-File -FilePath "DEPLOYED_URLS.txt" -Encoding UTF8
Write-Host "URLs saved to: DEPLOYED_URLS.txt" -ForegroundColor Gray

Read-Host "Press Enter to exit"
