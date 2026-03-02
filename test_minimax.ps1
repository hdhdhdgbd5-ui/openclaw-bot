$ErrorActionPreference = 'SilentlyContinue'
Write-Host "Testing MiniMax API endpoints..."

$endpoints = @(
    "https://api.minimax.chat",
    "https://api.minimax.chat/v1",
    "https://api.minimax.chat/v1/models",
    "https://minimax.chat/api"
)

foreach ($ep in $endpoints) {
    try {
        $w = Invoke-WebRequest -Uri $ep -Method GET -TimeoutSec 8
        Write-Host "$ep : $($w.StatusCode)"
    } catch {
        $status = if ($_.Exception.Response) { [int]$_.Exception.Response.StatusCode } else { "FAIL" }
        Write-Host "$ep : $status"
    }
}

Write-Host "Done."
