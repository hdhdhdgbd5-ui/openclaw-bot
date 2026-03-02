# MONEY ARMY 5 - Wallet Monitoring Script
# Checks Ethereum wallet balance every 30 minutes
# Reports all incoming funds

$WALLET_ADDRESS = "0xe23d9C5422A8bdB5281b15596111814808f98F1A"
$LOG_FILE = "$env:USERPROFILE\.openclaw\workspace\logs\wallet_check.log"
$LAST_BALANCE_FILE = "$env:USERPROFILE\.openclaw\workspace\data\last_balance.txt"

# Ensure directories exist
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.openclaw\workspace\logs" | Out-Null
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.openclaw\workspace\data" | Out-Null

function Check-WalletBalance {
    param([string]$Address)
    
    try {
        # Using Etherscan API publicly available endpoint
        $url = "https://api.etherscan.io/api?module=account&action=balance&address=$Address&tag=latest"
        $response = Invoke-RestMethod -Uri $url -Method GET -TimeoutSec 30
        
        if ($response.result) {
            $balanceWei = [bigint]$response.result
            $balanceEth = [math]::Round($balanceWei / 1e18, 6)
            return $balanceEth
        }
    } catch {
        Write-Host "Error checking balance: $_" -ForegroundColor Red
        return $null
    }
}

function Get-EthPrice {
    try {
        $url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
        $response = Invoke-RestMethod -Uri $url -Method GET -TimeoutSec 30
        return $response.ethereum.usd
    } catch {
        return $null
    }
}

# Main execution
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$balance = Check-WalletBalance -Address $WALLET_ADDRESS
$ethPrice = Get-EthPrice

if ($balance -ne $null) {
    $usdValue = if ($ethPrice) { [math]::Round($balance * $ethPrice, 2) } else { "N/A" }
    
    # Check last balance
    $lastBalance = 0
    if (Test-Path $LAST_BALANCE_FILE) {
        $lastBalance = [decimal](Get-Content $LAST_BALANCE_FILE)
    }
    
    $change = $balance - $lastBalance
    $changeStr = ""
    if ($change -gt 0) {
        $changeStr = " [+$$([math]::Round($change, 6)) ETH - NEW MONEY IN!]"
    } elseif ($change -lt 0) {
        $changeStr = " [$$([math]::Round($change, 6)) ETH]"
    }
    
    $logEntry = "[$timestamp] Wallet Balance: $balance ETH (~$$usdValue USD)$changeStr"
    Add-Content -Path $LOG_FILE -Value $logEntry
    Write-Host $logEntry -ForegroundColor Green
    
    # Save current balance
    $balance | Out-File $LAST_BALANCE_FILE
    
    # Report to main system
    if ($change -gt 0) {
        Write-Host "`n🎉🎉🎉 MONEY RECEIVED: +$$([math]::Round($change, 6)) ETH! 🎉🎉🎉" -ForegroundColor Yellow
    }
} else {
    $logEntry = "[$timestamp] Failed to check wallet balance"
    Add-Content -Path $LOG_FILE -Value $logEntry
    Write-Host $logEntry -ForegroundColor Red
}
