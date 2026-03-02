param(
  [Parameter(Mandatory=$true)]
  [string]$Zip
)
$ErrorActionPreference = 'Stop'

$home = $env:USERPROFILE
$root = Join-Path $home '.openclaw'
$backupDir = Join-Path $root 'backups'

if(!(Test-Path $Zip)) { throw "Zip not found: $Zip" }

$extract = Join-Path $backupDir ("restore_" + (Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'))
New-Item -ItemType Directory -Force -Path $extract | Out-Null

Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::ExtractToDirectory($Zip, $extract)

# Restore config + workspace
$cfgSrc = Join-Path $extract 'openclaw.json'
$wsSrc  = Join-Path $extract 'workspace'
if(!(Test-Path $cfgSrc)) { throw "Missing openclaw.json in backup" }
if(!(Test-Path $wsSrc))  { throw "Missing workspace/ in backup" }

Copy-Item -Force $cfgSrc (Join-Path $root 'openclaw.json')
Copy-Item -Recurse -Force $wsSrc (Join-Path $root 'workspace')

Write-Host "Restore completed. You can now start/restart the gateway."
Write-Host "Restored from: $Zip"
