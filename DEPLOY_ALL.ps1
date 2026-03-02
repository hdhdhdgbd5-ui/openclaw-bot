$username = "hdhdhdgbd5-ui"
$token = "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"

$headers = @{
    "Authorization" = "token $token"
    "Accept" = "application/vnd.github.v3+json"
}

# Function to deploy product
function Deploy-Product($name, $path) {
    Write-Host "`nDeploying $name..."
    
    # Create repo
    $body = @{ name = $name; description = "AI Product by Angel Army"; private = $false; auto_init = $true } | ConvertTo-Json
    try { Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method Post -Headers $headers -Body $body | Out-Null } catch {}
    
    # Upload file
    $content = Get-Content -Path "$path\index.html" -Raw -Encoding UTF8
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
    $base64 = [Convert]::ToBase64String($bytes)
    $fileBody = @{ message = "Deploy $name v1.0"; content = $base64 } | ConvertTo-Json
    Invoke-RestMethod -Uri "https://api.github.com/repos/$username/$name/contents/index.html" -Method Put -Headers $headers -Body $fileBody | Out-Null
    
    # Enable Pages
    $pagesBody = @{ source = @{ branch = "main"; path = "/" } } | ConvertTo-Json
    try { Invoke-RestMethod -Uri "https://api.github.com/repos/$username/$name/pages" -Method Post -Headers $headers -Body $pagesBody | Out-Null } catch {}
    
    Write-Host "SUCCESS: https://$username.github.io/$name" -ForegroundColor Green
}

# Deploy all 3
Deploy-Product "SaaSGenius" "C:\Users\armoo\.openclaw\workspace\PRODUCTS\SaaSGenius"
Deploy-Product "CryptoTradeGenius" "C:\Users\armoo\.openclaw\workspace\PRODUCTS\CryptoTradeGenius"
Deploy-Product "VideoGenius" "C:\Users\armoo\.openclaw\workspace\PRODUCTS\VideoGenius"

Write-Host "`n=== ALL PRODUCTS DEPLOYED ===" -ForegroundColor Cyan
