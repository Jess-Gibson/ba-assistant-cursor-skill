# Upgrade BA Assistant to the current package version (Windows)
# Dry-run:
#   .\tools\upgrade-ba-assistant.ps1 -PackageRoot "C:\path\to\ba-assistant-cursor-skill"
# Apply:
#   .\tools\upgrade-ba-assistant.ps1 -PackageRoot "C:\path\to\ba-assistant-cursor-skill" -Apply
param(
    [Parameter(Mandatory = $true)][string]$PackageRoot,
    [switch]$Apply,
    [switch]$ForcePersonal,
    [switch]$MigrateLegacy,
    [switch]$PatchProfile,
    [string]$CursorHome
)
$script = Join-Path $PSScriptRoot "upgrade-ba-assistant.py"
$argsList = @($script, "--package", $PackageRoot)
if ($Apply) { $argsList += "--apply" }
if ($ForcePersonal) { $argsList += "--force-personal" }
if ($MigrateLegacy) { $argsList += "--migrate-legacy" }
if ($PatchProfile) { $argsList += "--patch-profile" }
if ($CursorHome) { $argsList += @("--cursor-home", $CursorHome) }
$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) { & py @argsList } else { & python @argsList }
