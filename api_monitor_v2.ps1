# API HUNTER 24/7 - PowerShell Monitor (Updated)
# Monitors MiniMax and Groq APIs via HTTP requests

$LOG_DIR = "$PSScriptRoot\logs"
$LOG_FILE = "$LOG_DIR\api_monitor.log"
$STATUS_FILE = "$LOG_DIR\api_status.json"
$CHECK_INTERVAL = 30  # seconds
$GROQ_API_KEY = "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"

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
        "Authorization" = "Bearer $GROQ_API_KEY"
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
        
        if ($response.data) {
            $result.models = $response.data.Count
        }
    }
    catch [System.Net.WebException] {
        $result.code = [int]$_.Exception.Response.StatusCode
        if ($result.code -eq 401) {
            $result.status = "auth_error"
            $result.error = "Authentication failed"
        } else {
            $result.status = "degraded"
            $result.error = "HTTP $result.code"
        }
    }
    catch {
        $result.error = $_.Exception.Message
    }
    
    return $result
}

function Test-MiniMaxAPI {
    $result = @{
        status = "offline"
        code = 0
        error = $null
        note = $null
    }
    
    # Try multiple MiniMax endpoints
    $endpoints = @(
        @{ url = "https://api.minimax.chat/v1/models"; method = "GET" },
        @{ url = "https://api.minimax.chat/v1/text/chatcompletion_v2"; method = "POST" }
    )
    
    foreach ($ep in $endpoints) {
        try {
            if ($ep.method -eq "GET") {
                $response = Invoke-RestMethod -Uri $ep.url -TimeoutSec 10 -ErrorAction Stop
                $result.status = "online"
                return $result
            }
        } catch {
            $result.code = [int]$_.Exception.Response.StatusCode
            $result.error = $_.Exception.Message
            
            # Handle 308 redirect (API moved)
            if ($result.code -eq 308) {
                $result.status = "redirected"
                $result.note = "API redirected to minimaxi.com - may have moved"
            }
            # Handle 401/403 (API exists but needs auth)
            elseif ($result.code -eq 401 -or $result.code -eq 403) {
                $result.status = "online"
                $result.note = "Requires authentication (API is up)"
                return $result
            }
            # 404 or other errors
            elseif ($result.code -ge 400) {
                $result.status = "degraded"
            }
        }
    }
    
    # If we get here, all endpoints failed
    return $result
}

function Show-Dashboard($groq, $minimax) {
    Write-Host ""
    Write-Host "========================================"
    Write-Host "     API HUNTER 24/7 STATUS DASHBOARD   "
    Write-Host "========================================"
    
    # Groq Status
    $groqStatusStr = $groq.status.ToUpper()
    $groqColor = if ($groq.status -eq "online") { "Green" } elseif ($groq.status -eq "degraded") { "Yellow" } else { "Red" }
    Write-Host "  Groq API:    [$groqStatusStr]" -ForegroundColor $groqColor
    if ($groq.models) { Write-Host "    Models: $($groq.models) available" -ForegroundColor Gray }
    
    # MiniMax Status
    $mmStatusStr = $minimax.status.ToUpper()
    $mmColor = if ($minimax.status -eq "online") { "Green" } elseif ($minimax.status -eq "degraded" -or $minimax.status -eq "redirected") { "Yellow" } else { "Red" }
    Write-Host "  MiniMax API: [$mmStatusStr]" -ForegroundColor $mmColor
    if ($minimax.note) { Write-Host "    $($minimax.note)" -ForegroundColor Gray }
    
    Write-Host "----------------------------------------"
    Write-Host "  Last Check: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Write-Host "========================================"
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
        Write-Log "OK - Groq API: ONLINE ($($groqResult.models) models)" "SUCCESS"
    } elseif ($groqResult.status -eq "degraded") {
        Write-Log "WARNING - Groq API: DEGRADED ($($groqResult.error))" "WARNING"
    } else {
        Write-Log "ERROR - Groq API: OFFLINE ($($groqResult.error))" "ERROR"
    }
    
    # Check MiniMax API
    Write-Log "Checking MiniMax API..." "CHECK"
    $minimaxResult = Test-MiniMaxAPI
    
    if ($minimaxResult.status -eq "online") {
        Write-Log "OK - MiniMax API: ONLINE" "SUCCESS"
    } elseif ($minimaxResult.status -eq "redirected") {
        Write-Log "WARNING - MiniMax API: REDIRECTED ($($minimaxResult.note))" "WARNING"
    } elseif ($minimaxResult.status -eq "degraded") {
        Write-Log "WARNING - MiniMax API: DEGRADED ($($minimaxResult.error))" "WARNING"
    } else {
        Write-Log "ERROR - MiniMax API: OFFLINE ($($minimaxResult.error))" "ERROR"
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
    if ($currentStatus.groq -and $currentStatus.groq -ne $groqResult.status) {
        Write-Log "ALERT - Groq API changed: $($currentStatus.groq) -> $($groqResult.status)" "ALERT"
    }
    
    if ($currentStatus.minimax -and $currentStatus.minimax -ne $minimaxResult.status) {
        Write-Log "ALERT - MiniMax API changed: $($currentStatus.minimax) -> $($minimaxResult.status)" "ALERT"
    }
    
    # Display Dashboard
    Show-Dashboard $groqResult $minimaxResult
    
    return $newStatus
}

# MAIN - Single run
if ($args -contains "-once") {
    Start-MonitorCycle | Out-Null
    exit 0
}

# Continuous monitoring
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
