$ErrorActionPreference = 'Stop'

$home = $env:USERPROFILE
$root = Join-Path $home '.openclaw'
$ws   = Join-Path $root 'workspace'
$cfg  = Join-Path $root 'openclaw.json'
$secrets = Join-Path $ws 'secrets'

$backupDir = Join-Path $root 'backups'
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

$stamp = Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'
$zipPath = Join-Path $backupDir ("openclaw_backup_$stamp.zip")

# Build a temp staging folder so we always backup a consistent snapshot.
$stage = Join-Path $backupDir ("stage_$stamp")
New-Item -ItemType Directory -Force -Path $stage | Out-Null

Copy-Item -Force $cfg (Join-Path $stage 'openclaw.json')
Copy-Item -Recurse -Force $ws (Join-Path $stage 'workspace')

# Create zip
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($stage, $zipPath)

# Cleanup stage
Remove-Item -Recurse -Force $stage

Write-Host "Backup written: $zipPath"
