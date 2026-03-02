# Quick API Status Viewer
$statusFile = "$PSScriptRoot\logs\api_status.json"

if (-not (Test-Path $statusFile)) {
    Write-Host "No status file found. Run api_monitor_v2.ps1 first!" -ForegroundColor Red
    exit 1
}

$status = Get-Content $statusFile | ConvertFrom-Json

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "       API HUNTER 24/7 QUICK STATUS    " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Groq
$groqColor = if ($status.groq -eq "online") { "Green" } elseif ($status.groq -eq "degraded") { "Yellow" } else { "Red" }
Write-Host "Groq API:   " -NoNewline
Write-Host $status.groq.ToUpper() -ForegroundColor $groqColor
if ($status.groq_details.models) {
    Write-Host "  Models: $($status.groq_details.models) available" -ForegroundColor Gray
}

# MiniMax
$mmColor = if ($status.minimax -eq "online") { "Green" } elseif ($status.minimax -eq "degraded" -or $status.minimax -eq "redirected") { "Yellow" } else { "Red" }
Write-Host "MiniMax:    " -NoNewline
Write-Host $status.minimax.ToUpper() -ForegroundColor $mmColor
if ($status.minimax_details.note) {
    Write-Host "  $($status.minimax_details.note)" -ForegroundColor Gray
}

Write-Host "----------------------------------------" -ForegroundColor Cyan
Write-Host "Last Check: $($status.timestamp)"
Write-Host "========================================" -ForegroundColor Cyan
