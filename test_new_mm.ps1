# Test new minimaxi endpoints
Write-Host "Testing new minimaxi endpoints..."

$endpoints = @(
    "https://www.minimaxi.com/api/v1/models",
    "https://api.minimaxi.com/v1/models", 
    "https://api.minimaxi.com/v1"
)

foreach ($ep in $endpoints) {
    try {
        $w = Invoke-WebRequest -Uri $ep -Method GET -TimeoutSec 8
        Write-Host "$ep : $($w.StatusCode)"
    } catch {
        Write-Host "$ep : FAIL"
    }
}
