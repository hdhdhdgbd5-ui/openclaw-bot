# ContractGenius Deployment Script
$username = "hdhdhdgbd5-ui"
$token = "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"

Write-Host "Deploying ContractGenius..." -ForegroundColor Green

$headers = @{
    "Authorization" = "token $token"
    "Accept" = "application/vnd.github.v3+json"
}

# Create repo if not exists
$body = @{
    name = "ContractGenius"
    description = "AI-Powered Legal Contract Analyzer"
    private = $false
    auto_init = $true
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method Post -Headers $headers -Body $body
    Write-Host "Repository created" -ForegroundColor Green
} catch {
    Write-Host "Repository exists or error occurred" -ForegroundColor Yellow
}

# Upload index.html
$content = Get-Content -Path "frontend/dist/index.html" -Raw -Encoding UTF8
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
$base64 = [Convert]::ToBase64String($bytes)

$fileBody = @{
    message = "Deploy ContractGenius"
    content = $base64
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://api.github.com/repos/$username/ContractGenius/contents/index.html" -Method Put -Headers $headers -Body $fileBody

# Enable Pages
$pagesBody = @{
    source = @{
        branch = "main"
        path = "/"
    }
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri "https://api.github.com/repos/$username/ContractGenius/pages" -Method Post -Headers $headers -Body $pagesBody
    Write-Host "Pages enabled" -ForegroundColor Green
} catch {
    Write-Host "Pages already enabled" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "SUCCESS!" -ForegroundColor Green
Write-Host "Your site will be live at:" -ForegroundColor Yellow
Write-Host "https://$username.github.io/ContractGenius"
Write-Host ""
Write-Host "Wait 2-5 minutes for GitHub Pages to activate"
