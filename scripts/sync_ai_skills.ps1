# Sync .ai/skills/ to Cursor-discoverable locations.
# Run from repo root: powershell -File scripts/sync_ai_skills.ps1

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$source = Join-Path $repoRoot ".ai\skills"
$projectDest = Join-Path $repoRoot ".cursor\skills"
$globalDest = Join-Path $env:USERPROFILE ".claude\skills\skills"

if (-not (Test-Path $source)) {
    Write-Error "Missing skill source: $source"
}

New-Item -ItemType Directory -Force -Path $projectDest | Out-Null
New-Item -ItemType Directory -Force -Path $globalDest | Out-Null

Get-ChildItem -Path $source -Directory | ForEach-Object {
    $name = $_.Name
    $projectTarget = Join-Path $projectDest $name
    $globalTarget = Join-Path $globalDest $name
    if (Test-Path $projectTarget) { Remove-Item -Recurse -Force $projectTarget }
    if (Test-Path $globalTarget) { Remove-Item -Recurse -Force $globalTarget }
    Copy-Item -Path $_.FullName -Destination $projectTarget -Recurse -Force
    Copy-Item -Path $_.FullName -Destination $globalTarget -Recurse -Force
    Write-Host "Synced: $name"
}

Write-Host "Done. Project: $projectDest"
Write-Host "Done. Global:  $globalDest"
Write-Host "Reload Cursor window (Ctrl+Shift+P -> Developer: Reload Window) if /next does not appear."
