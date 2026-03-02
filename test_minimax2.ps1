$ErrorActionPreference = 'SilentlyContinue'
Write-Host "Testing MiniMax API with redirect follow..."

try {
    $w = Invoke-WebRequest -Uri "https://api.minimax.chat" -Method GET -TimeoutSec 10 -MaximumRedirection 5
    Write-Host "Final Status: $($w.StatusCode)"
    Write-Host "Final URL: $($w.BaseResponse.ResponseUri)"
    Write-Host "Headers: $($w.Headers)"
} catch {
    Write-Host "Error: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        Write-Host "Status: $([int]$_.Exception.Response.StatusCode)"
        Write-Host "Headers: $($_.Exception.Response.Headers)"
    }
}
