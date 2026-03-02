# Quick wallet check
$body = @{
    jsonrpc = "2.0"
    method = "eth_getBalance"
    params = @("0xe23d9C5422A8bdB5281b15596111814808f98F1A", "latest")
    id = 1
} | ConvertTo-Json

$resp = Invoke-RestMethod -Uri 'https://eth.public-rpc.com' -Method Post -Body $body -ContentType 'application/json' -TimeoutSec 30
$balanceWei = [bigint]$resp.result
$balanceEth = [math]::Round($balanceWei / 1e18, 6)

Write-Host "=== WALLET BALANCE ==="
Write-Host "Address: 0xe23d9C5422A8bdB5281b15596111814808f98F1A"
Write-Host "Balance: $balanceEth ETH"
