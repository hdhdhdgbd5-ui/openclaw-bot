# SaaSGenius Deployment
$username = "hdhdhdgbd5-ui"
$token = "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"

$headers = @{
    "Authorization" = "token $token"
    "Accept" = "application/vnd.github.v3+json"
}

$body = @{
    name = "SaaSGenius"
    description = "SaaS Boilerplate Generator"
    private = $false
    auto_init = $true
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method Post -Headers $headers -Body $body
    Write-Host "Repo created"
} catch { }

$content = Get-Content -Path "index.html" -Raw -Encoding UTF8
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
$base64 = [Convert]::ToBase64String($bytes)

$fileBody = @{
    message = "Deploy SaaSGenius v1.0"
    content = $base64
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://api.github.com/repos/$username/SaaSGenius/contents/index.html" -Method Put -Headers $headers -Body $fileBody

$pagesBody = @{
    source = @{
        branch = "main"
        path = "/"
    }
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri "https://api.github.com/repos/$username/SaaSGenius/pages" -Method Post -Headers $headers -Body $pagesBody
} catch {}

Write-Host "SUCCESS! https://$username.github.io/SaaSGenius"
