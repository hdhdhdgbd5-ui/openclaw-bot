# API HUNTER 24/7 - PowerShell Launcher
# Runs the Python monitor as a persistent background job

$scriptPath = Join-Path $PSScriptRoot "api_monitor.py"
$logPath = Join-Path $PSScriptRoot "logs/monitor_service.log"

# Ensure logs directory exists
New-Item -ItemType Directory -Path (Join-Path $PSScriptRoot "logs") -Force | Out-Null

function Write-MonitorLog($message) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $message"
    Write-Host $logEntry
    Add-Content -Path $logPath -Value $logEntry
}

Write-MonitorLog "🚀 Starting API HUNTER 24/7 Monitor Service"
Write-MonitorLog "📁 Script: $scriptPath"
Write-MonitorLog "📝 Log: $logPath"

# Check Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command python3 -ErrorAction SilentlyContinue
}

if (-not $python) {
    Write-MonitorLog "❌ ERROR: Python not found! Install Python to run API monitor."
    exit 1
}

Write-MonitorLog "✅ Python found: $($python.Source)"
Write-MonitorLog "🔄 Starting continuous monitoring loop..."

# Run the monitor
& $python.Source $scriptPath

# If monitor exits, restart it
Write-MonitorLog "⚠️ Monitor exited - restarting in 5 seconds..."
Start-Sleep 5
& $PSCommandPath
