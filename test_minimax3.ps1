$ErrorActionPreference = 'SilentlyContinue'
Write-Host "Testing MiniMax API with auto-redirect..."

try {
    # Use Session to handle redirects automatically
    $session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
    $w = Invoke-WebRequest -Uri "https://api.minimax.chat" -Method GET -TimeoutSec 10 -WebSession $session
    Write-Host "Status: $($w.StatusCode)"
    Write-Host "Final URL: $($w.BaseResponse.ResponseUri)"
} catch {
    Write-Host "Error: $($_.Exception.Message)"
}

# Try with explicit redirect
Write-Host ""
Write-Host "Trying with explicit Location header..."
try {
    $r = [System.Net.WebRequest]::Create("https://api.minimax.chat")
    $r.AllowAutoRedirect = $true
    $resp = $r.GetResponse()
    Write-Host "Status: $($resp.StatusCode)"
    Write-Host "Location: $($resp.ResponseUri)"
    $resp.Close()
} catch {
    Write-Host "Error: $($_.Exception.Message)"
}
