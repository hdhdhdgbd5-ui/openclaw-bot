# API HUNTER 24/7 - PowerShell Monitor
# Monitors MiniMax and Groq APIs via HTTP requests

$LOG_DIR = "$PSScriptRoot\logs"
$LOG_FILE = "$LOG_DIR\api_monitor.log"
$STATUS_FILE = "$LOG_DIR\api_status.json"
$CHECK_INTERVAL = 30  # seconds

# Create log directory
New-Item -ItemType Directory -Path $LOG_DIR -Force -ErrorAction SilentlyContinue | Out-Null

function Write-Log($message, $level = "INFO") {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$level] $message"
    
    # Color output
    switch ($level) {
        "ERROR"  { Write-Host $logEntry -ForegroundColor Red }
        "SUCCESS"{ Write-Host $logEntry -ForegroundColor Green }
        "WARNING"{ Write-Host $logEntry -ForegroundColor Yellow }
        "ALERT"  { Write-Host $logEntry -ForegroundColor Magenta }
        default  { Write-Host $logEntry }
    }
    
    # Write to file
    Add-Content -Path $LOG_FILE -Value $logEntry
}

function Load-Status {
    if (Test-Path $STATUS_FILE) {
        return Get-Content $STATUS_FILE | ConvertFrom-Json
    }
    return @{ 
        minimax = "unknown"
        groq = "unknown"
        last_check = $null
    }
}

function Save-Status($status) {
    $status | ConvertTo-Json -Depth 3 | Set-Content $STATUS_FILE
}

function Test-GroqAPI {
    $headers = @{
        "Authorization" = "Bearer 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"
    }
    
    $result = @{
        status = "offline"
        code = 0
        error = $null
        models = 0
    }
    
    try {
        $response = Invoke-RestMethod -Uri "https://api.groq.com/openai/v1/models" -Headers $headers -TimeoutSec 10 -ErrorAction Stop
        $result.status = "online"
        
        # Count available models
        if ($response.data) {
            $modelCount = $response.data.Count
            $result.models = $modelCount
            Write-Log "   Groq Response: $modelCount models available" "INFO"
        }
    }
    catch [System.Net.WebException] {
        $result.code = [int]$_.Exception.Response.StatusCode
        if ($result.code -eq 200) {
            $result.status = "online"
        } elseif ($result.code -eq 401) {
            $result.status = "auth_error"
            $result.error = "Authentication failed"
        } else {
            $result.status = "degraded"
            $result.error = "HTTP $($result.code)"
        }
    }
    catch {
        $result.error = $_.Exception.Message
    }
    
    return $result
}

function Test-MiniMaxAPI {
    $headers = @{
        "Content-Type" = "application/json"
    }
    
    $result = @{
        status = "offline"
        code = 0
        error = $null
        note = $null
    }
    
    try {
        # Try the models endpoint
        $response = Invoke-RestMethod -Uri "https://api.minimax.chat/v1/models" -Headers $headers -TimeoutSec 10 -ErrorAction Stop
        $result.status = "online"
    }
    catch [System.Net.WebException] {
        $result.code = [int]$_.Exception.Response.StatusCode
        if ($result.code -eq 401 -or $result.code -eq 403) {
            # API is responsive but needs auth - that's good
            $result.status = "online"
            $result.note = "Requires auth (expected)"
        } elseif ($result.code -eq 200) {
            $result.status = "online"
        } else {
            $result.status = "degraded"
            if ($result.code -eq 0) { $result.status = "offline" }
            $result.error = "HTTP $($result.code)"
        }
    }
    catch {
        $result.error = $_.Exception.Message
        # Check if we got any response at all
        if ($result.error -like "*401*" -or $result.error -like "*403*") {
            $result.status = "online"
            $result.note = "Requires auth (expected)"
        }
    }
    
    return $result
}

function Show-Dashboard($groq, $minimax) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "     API HUNTER 24/7 STATUS DASHBOARD   " -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    
    # Groq Status
    $groqStatusStr = $groq.status.ToUpper()
    $groqColor = if ($groq.status -eq "online") { "Green" } elseif ($groq.status -eq "degraded") { "Yellow" } else { "Red" }
    Write-Host "  Groq API:    [$groqStatusStr]" -ForegroundColor $groqColor
    
    # MiniMax Status
    $mmStatusStr = $minimax.status.ToUpper()
    $mmColor = if ($minimax.status -eq "online") { "Green" } elseif ($minimax.status -eq "degraded") { "Yellow" } else { "Red" }
    Write-Host "  MiniMax API: [$mmStatusStr]" -ForegroundColor $mmColor
    
    Write-Host "----------------------------------------" -ForegroundColor Cyan
    Write-Host "  Last Check: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Start-MonitorCycle {
    $currentStatus = Load-Status
    
    Write-Log "============================================================"
    Write-Log "API HUNTER - Starting Health Check Cycle"
    
    # Check Groq API
    Write-Log "Checking Groq API..." "CHECK"
    $groqResult = Test-GroqAPI
    
    if ($groqResult.status -eq "online") {
        $modelInfo = if ($groqResult.models) { " - $($groqResult.models) models" } else { "" }
        Write-Log "OK - Groq API: ONLINE$modelInfo" "SUCCESS"
    } elseif ($groqResult.status -eq "degraded") {
        Write-Log "WARNING - Groq API: DEGRADED (HTTP $($groqResult.code))" "WARNING"
    } else {
        Write-Log "ERROR - Groq API: OFFLINE - $($groqResult.error)" "ERROR"
    }
    
    # Check MiniMax API
    Write-Log "Checking MiniMax API..." "CHECK"
    $minimaxResult = Test-MiniMaxAPI
    
    if ($minimaxResult.status -eq "online") {
        if ($minimaxResult.note) {
            Write-Log "OK - MiniMax API: ONLINE ($($minimaxResult.note))" "SUCCESS"
        } else {
            Write-Log "OK - MiniMax API: ONLINE" "SUCCESS"
        }
    } elseif ($minimaxResult.status -eq "degraded") {
        Write-Log "WARNING - MiniMax API: DEGRADED (HTTP $($minimaxResult.code))" "WARNING"
    } else {
        Write-Log "ERROR - MiniMax API: OFFLINE - $($minimaxResult.error)" "ERROR"
    }
    
    # Save status
    $newStatus = @{
        groq = $groqResult.status
        minimax = $minimaxResult.status
        last_check = (Get-Date).ToString("o")
        groq_details = $groqResult
        minimax_details = $minimaxResult
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    }
    Save-Status $newStatus
    
    # Check for status changes
    if ($currentStatus.groq -ne $groqResult.status) {
        Write-Log "ALERT - Groq API status changed: $($currentStatus.groq) -> $($groqResult.status)" "ALERT"
    }
    
    if ($currentStatus.minimax -ne $minimaxResult.status) {
        Write-Log "ALERT - MiniMax API status changed: $($currentStatus.minimax) -> $($minimaxResult.status)" "ALERT"
    }
    
    # Display Dashboard
    Show-Dashboard $groqResult $minimaxResult
    
    return $newStatus
}

# MAIN
Write-Log "API HUNTER 24/7 MONITOR STARTING..."
Write-Log "Logs: $LOG_FILE"
Write-Log "Status: $STATUS_FILE"
Write-Log "Interval: $CHECK_INTERVAL seconds"
Write-Log "============================================================"

$cycleCount = 0

try {
    while ($true) {
        $cycleCount++
        Write-Log ""
        Write-Log "CYCLE #$cycleCount"
        
        try {
            Start-MonitorCycle | Out-Null
        } catch {
            Write-Log "Error in monitor cycle: $_" "ERROR"
        }
        
        Write-Log "Sleeping for $CHECK_INTERVAL seconds..."
        Start-Sleep -Seconds $CHECK_INTERVAL
    }
} catch {
    Write-Log "FATAL ERROR: $_" "FATAL"
    throw
} finally {
    Write-Log "Monitor stopped" "STOP"
}
