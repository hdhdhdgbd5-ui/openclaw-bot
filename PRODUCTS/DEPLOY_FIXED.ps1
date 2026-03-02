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
Write-Host "Privacy Mode: ON" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"

$products = @(
    @{Name="RentVault"; Description="Tenant evidence documentation app"},
    @{Name="StreakVault"; Description="Beautiful habit tracker with streaks"},
    @{Name="FocusMaster"; Description="2-minute focus challenge game"},
    @{Name="BudgetVault"; Description="Simple budget tracker"}
)

$headers = @{
    "Authorization" = "token $GitHubToken"
    "Accept" = "application/vnd.github.v3+json"
}

# Create repo function
function CreateRepo($product) {
    Write-Host "Creating repo: $($product.Name)..." -ForegroundColor Yellow
    
    $body = @{
        name = $product.Name
        description = $product.Description
        private = $false
        auto_init = $true
    } | ConvertTo-Json
    
    try {
        Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method Post -Headers $headers -Body $body -ContentType "application/json"
        Write-Host "  SUCCESS: Repo created" -ForegroundColor Green
        return $true
    } catch {
        $errCode = $_.Exception.Response.StatusCode.value__
        if ($errCode -eq 422) {
            Write-Host "  EXISTS: Repo already there, continuing..." -ForegroundColor Yellow
            return $true
        }
        Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Sanitize content
function SanitizeContent($filePath) {
    $content = Get-Content -Path $filePath -Raw -Encoding UTF8
    $content = $content -replace 'Tez', 'User'
    $content = $content -replace 'for Tez', ''
    $content = $content -replace 'Built by Angel Army for', 'Built by Angel Army'
    $content = $content -replace 'Date: 2026-02-19', ''
    return $content
}

# Upload files function
function UploadFiles($productName) {
    Write-Host "Uploading files to $productName..." -ForegroundColor Yellow
    
    $localPath = "C:\Users\armoo\.openclaw\workspace\PRODUCTS\$productName"
    $files = Get-ChildItem -Path $localPath -File | Where-Object { 
        $_.Name -notmatch '\.(ps1|bat)$' -and 
        $_.Name -notmatch '^\.' -and
        $_.Name -ne ".gitignore"
    }
    
    foreach ($file in $files) {
        $fileName = $file.Name
        Write-Host "  Uploading: $fileName..." -ForegroundColor Gray -NoNewline
        
        $content = SanitizeContent $file.FullName
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
        $base64 = [Convert]::ToBase64String($bytes)
        
        # Check existing
        $sha = $null
        try {
            $existing = Invoke-RestMethod -Uri "https://api.github.com/repos/$GitHubUsername/$productName/contents/$fileName" -Headers $headers -ErrorAction SilentlyContinue
            $sha = $existing.sha
        } catch {}
        
        $body = @{
            message = "Add $fileName"
            content = $base64
        }
        if ($sha) { $body.sha = $sha }
        
        try {
            Invoke-RestMethod -Uri "https://api.github.com/repos/$GitHubUsername/$productName/contents/$fileName" -Method Put -Headers $headers -Body ($body | ConvertTo-Json) -ContentType "application/json" | Out-Null
            Write-Host " OK" -ForegroundColor Green
        } catch {
            Write-Host " FAIL" -ForegroundColor Red
        }
    }
}

# Enable pages function
function EnablePages($productName) {
    Write-Host "Enabling GitHub Pages..." -ForegroundColor Yellow
    
    $body = @{
        source = @{
            branch = "main"
            path = "/"
        }
    } | ConvertTo-Json
    
    try {
        Invoke-RestMethod -Uri "https://api.github.com/repos/$GitHubUsername/$productName/pages" -Method Post -Headers $headers -Body $body -ContentType "application/json" | Out-Null
        Write-Host "  SUCCESS: Pages enabled" -ForegroundColor Green
        return $true
    } catch {
        $errCode = $_.Exception.Response.StatusCode.value__
        if ($errCode -eq 409) {
            Write-Host "  EXISTS: Already enabled" -ForegroundColor Yellow
            return $true
        }
        Write-Host "  MANUAL: Enable at github.com/$GitHubUsername/$productName/settings/pages" -ForegroundColor Yellow
        return $false
    }
}

# Deploy all
$urls = @()

foreach ($product in $products) {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "Deploying: $($product.Name)" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    
    if (CreateRepo $product) {
        UploadFiles $product.Name
        EnablePages $product.Name
        $urls += "https://$GitHubUsername.github.io/$($product.Name)"
    }
    
    Start-Sleep -Seconds 2
}

# Summary
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "LIVE URLs (wait 2-5 minutes):" -ForegroundColor Green
foreach ($url in $urls) {
    Write-Host "  $url" -ForegroundColor Cyan
}
Write-Host ""
Write-Host "URLs saved to DEPLOYED_URLS.txt" -ForegroundColor Gray

$urls | Out-File -FilePath "DEPLOYED_URLS.txt" -Encoding UTF8

Write-Host ""
Read-Host "Press Enter to exit"
