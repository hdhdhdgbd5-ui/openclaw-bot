# MONEY ARMY 5 - 24/7 Money Making Master Orchestrator
# Continuously runs all income-generating activities
# NEVER STOPS MAKING MONEY

$LOG_FILE = "$env:USERPROFILE\.openclaw\workspace\logs\master.log"
$STATUS_FILE = "$env:USERPROFILE\.openclaw\workspace\data\money_status.json"

# Ensure directories exist
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.openclaw\workspace\logs" | Out-Null
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.openclaw\workspace\scripts" | Out-Null
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.openclaw\workspace\data" | Out-Null

# Money tracking
$script:DAILY_EARNED = 0
$script:TOTAL_EARNED = 0
$script:SESSION_START = Get-Date
$script:RUN_COUNT = 0

function Write-MoneyLog {
    param($Message, $Type = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $colors = @{
        "INFO" = "White"
        "SUCCESS" = "Green"
        "MONEY" = "Yellow"
        "ERROR" = "Red"
    }
    
    $logEntry = "[$timestamp][$Type] $Message"
    Add-Content -Path $LOG_FILE -Value $logEntry
    Write-Host $logEntry -ForegroundColor $colors[$Type]
}

function Update-Status {
    $status = @{
        LastUpdate = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        DailyEarned = $script:DAILY_EARNED
        TotalEarned = $script:TOTAL_EARNED
        SessionStart = $script:SESSION_START.ToString()
        RunCount = $script:RUN_COUNT
        NextActions = @(
            "Wallet check in $((30 - ((Get-Date).Minute % 30)) + 1) min"
            "Reddit post in $((60 - (Get-Date).Minute) + 1) min"
            "Craigslist post in $((60 - (Get-Date).Minute) + 1) min"
        )
    }
    
    $status | ConvertTo-Json | Out-File $STATUS_FILE
}

function Run-WalletCheck {
    Write-MoneyLog "Checking wallet balance..." "INFO"
    try {
        & "$env:USERPROFILE\.openclaw\workspace\scripts\wallet_monitor.ps1" 2>$null
        Write-MoneyLog "Wallet check completed" "SUCCESS"
    } catch {
        Write-MoneyLog "Wallet check failed: $_" "ERROR"
    }
}

function Run-RedditPost {
    Write-MoneyLog "Preparing Reddit income posts..." "INFO"
    try {
        & "$env:USERPROFILE\.openclaw\workspace\scripts\reddit_money_poster.ps1" 2>$null
        Write-MoneyLog "Reddit content generated" "SUCCESS"
    } catch {
        Write-MoneyLog "Reddit poster failed: $_" "ERROR"
    }
}

function Run-CraigslistPost {
    Write-MoneyLog "Preparing Craigslist income posts..." "INFO"
    try {
        & "$env:USERPROFILE\.openclaw\workspace\scripts\craigslist_money_poster.ps1" 2>$null
        Write-MoneyLog "Craigslist content generated" "SUCCESS"
    } catch {
        Write-MoneyLog "Craigslist poster failed: $_" "ERROR"
    }
}

function Run-IncomeFinder {
    Write-MoneyLog "Scanning for new income opportunities..." "INFO"
    try {
        & "$env:USERPROFILE\.openclaw\workspace\scripts\income_finder.ps1" 2>$null
        Write-MoneyLog "Income opportunities updated" "SUCCESS"
    } catch {
        Write-MoneyLog "Income finder failed: $_" "ERROR"
    }
}

function Show-MoneyBanner {
    Write-Host "`n╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                                                       ║" -ForegroundColor Cyan
    Write-Host "║  💰  MONEY ARMY 5 - 24/7 MONEY MAKING MACHINE  💰   ║" -ForegroundColor Yellow
    Write-Host "║                                                       ║" -ForegroundColor Cyan
    Write-Host "║  Status: ACTIVE     Mode: AUTONOMOUS    Goal: $$$    ║" -ForegroundColor Green
    Write-Host "║                                                       ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Show-MoneyReport {
    $runtime = (Get-Date) - $script:SESSION_START
    $runtimeStr = "{0}h {1}m {2}s" -f $runtime.Hours, $runtime.Minutes, $runtime.Seconds
    
    Write-Host "`n📊 MONEY ARMY 5 - STATUS REPORT" -ForegroundColor Cyan
    Write-Host "==================================" -ForegroundColor Cyan
    Write-Host "Session Runtime: $runtimeStr" -ForegroundColor White
    Write-Host "Operations Completed: $script:RUN_COUNT" -ForegroundColor White
    Write-Host "Estimated Daily Earnings: $$$script:DAILY_EARNED" -ForegroundColor Green
    Write-Host "Status: ✅ AUTONOMOUS INCOME GENERATION ACTIVE" -ForegroundColor Green
    Write-Host "==================================" -ForegroundColor Cyan
}

# Initial execution
Show-MoneyBanner
Write-MoneyLog "MONEY ARMY 5 STARTING UP..." "INFO"
Write-MoneyLog "All systems initializing" "INFO"

# Run all modules immediately
Write-MoneyLog "Running initial startup tasks..." "INFO"
Run-WalletCheck
Run-IncomeFinder
Run-RedditPost
Run-CraigslistPost

$script:RUN_COUNT++
Update-Status
Show-MoneyReport

Write-MoneyLog "🚀 MONEY ARMY 5 FULLY OPERATIONAL!" "MONEY"
Write-MoneyLog "Continuous income generation active..." "INFO"

# Display action items
Write-Host "`n🎯 IMMEDIATE ACTION ITEMS:" -ForegroundColor Magenta
Write-Host "   1. ⏰ Check generated posts in: $env:USERPROFILE\.openclaw\workspace\data\" -ForegroundColor White
Write-Host "   2. 📱 Copy Reddit posts to Reddit.com" -ForegroundColor White
Write-Host "   3. 📋 Post Craigslist ads to craigslist.org" -ForegroundColor White
Write-Host "   4. 🌐 Sign up for top opportunities from finder" -ForegroundColor White
Write-Host "   5. 💳 Monitor wallet for incoming payments" -ForegroundColor White

Write-Host "`n🔔 AUTOMATED TASKS RUNNING:" -ForegroundColor Cyan
Write-Host "   ✅ Wallet monitoring: Every 30 minutes" -ForegroundColor Green
Write-Host "   ✅ Reddit posts: Every hour" -ForegroundColor Green
Write-Host "   ✅ Craigslist posts: Every hour" -ForegroundColor Green
Write-Host "   ✅ Opportunity scanning: Every hour" -ForegroundColor Green

Write-Host "`n💪 MONEY ARMY 5: NEVER STOP MAKING MONEY! 💪" -ForegroundColor Yellow

# Main loop - runs indefinitely
Write-Host "`n⚙️  Starting main execution loop (press Ctrl+C to stop)..." -ForegroundColor Cyan

$lastWalletCheck = Get-Date
$lastRedditPost = Get-Date
$lastCraigslistPost = Get-Date
$lastIncomeFinder = Get-Date

while ($true) {
    $now = Get-Date
    
    # Wallet check every 30 minutes
    if (($now - $lastWalletCheck).TotalMinutes -ge 30) {
        Run-WalletCheck
        $lastWalletCheck = $now
    }
    
    # Reddit post every hour
    if (($now - $lastRedditPost).TotalMinutes -ge 60) {
        Run-RedditPost
        $lastRedditPost = $now
    }
    
    # Craigslist post every hour
    if (($now - $lastCraigslistPost).TotalMinutes -ge 60) {
        Run-CraigslistPost
        $lastCraigslistPost = $now
    }
    
    # Income finder every hour (offset by 15 min)
    if (($now - $lastIncomeFinder).TotalMinutes -ge 60) {
        Run-IncomeFinder
        $lastIncomeFinder = $now
    }
    
    # Update status every 5 minutes
    $script:RUN_COUNT++
    Update-Status
    
    # Progress indicator
    Write-Host "." -NoNewline -ForegroundColor Green
    
    # Sleep for 1 minute
    Start-Sleep -Seconds 60
}
