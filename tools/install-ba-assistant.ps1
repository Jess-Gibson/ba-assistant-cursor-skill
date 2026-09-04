# Install BA Assistant into your Cursor home (Windows)
# Usage:
#   .\tools\install-ba-assistant.ps1
#   .\tools\install-ba-assistant.ps1 -Apply
#   .\tools\install-ba-assistant.ps1 -Apply -CursorHome "$env:USERPROFILE\.cursor"

param(
    [switch]$Apply,
    [string]$PackageRoot = "",
    [string]$CursorHome = ""
)

$ErrorActionPreference = "Stop"

if (-not $PackageRoot) {
    $PackageRoot = Split-Path -Parent $PSScriptRoot
}
if (-not $CursorHome) {
    $CursorHome = Join-Path $env:USERPROFILE ".cursor"
}

$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) {
    $python = "py"
    $prefix = @("-3")
} else {
    $python = "python"
    $prefix = @()
}

$script = Join-Path $PSScriptRoot "install-ba-assistant.py"
$argsList = $prefix + @(
    $script,
    "--package", $PackageRoot,
    "--cursor-home", $CursorHome
)
if ($Apply) {
    $argsList += "--apply"
} else {
    $argsList += "--dry-run"
}

Write-Host "Running: $python $($argsList -join ' ')"
& $python @argsList
exit $LASTEXITCODE
