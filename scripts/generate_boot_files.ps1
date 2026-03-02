$ErrorActionPreference = 'Stop'
$ws = Join-Path $env:USERPROFILE '.openclaw\workspace'
Set-Location $ws

# Collect all markdown files that represent operational memory/state.
# (We skip node_modules-like folders; keep it inside workspace.)
$excludeDirs = @('node_modules', '.git', '.openclaw', '.clawhub', 'dist', 'build', 'out', '.cache')

$mdFiles = Get-ChildItem -Recurse -File -Filter '*.md' |
  Where-Object {
    $p = $_.FullName
    foreach($d in $excludeDirs){ if($p -match ([regex]::Escape("\\$d\\"))) { return $false } }
    return $true
  } |
  Sort-Object FullName

$out = @()
$out += "# BOOT_FILES.md (Auto-generated)"
$out += ""
$out += "This file lists ALL markdown state files in the workspace that the agent must read on startup/session restore."
$out += "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss K')"
$out += ""
$out += "## Files"
$out += ""
foreach($f in $mdFiles){
  $rel = $f.FullName.Substring($ws.Length).TrimStart('\\') -replace '\\','/'
  $out += "- $rel"
}
$out += ""
$out += "## Rule"
$out += "- On gateway startup (BOOT.md) and after any context reset, read EVERY file listed above before responding."

$outPath = Join-Path $ws 'BOOT_FILES.md'
[IO.File]::WriteAllLines($outPath, $out, (New-Object System.Text.UTF8Encoding($false)))
Write-Host "Wrote $outPath with $($mdFiles.Count) files."
