$body = @{
    name = "llama2:7b"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/pull' -Method Post -Body $body -ContentType 'application/json' -TimeoutSec 60
    Write-Host "Pull started: $($response | ConvertTo-Json)"
} catch {
    Write-Host "Error: $_"
}
