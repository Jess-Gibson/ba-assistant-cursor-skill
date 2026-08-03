# Upgrade BA Assistant to Version 10 (Windows)
# Dry-run:
#   .\tools\upgrade-ba-assistant.ps1 -PackageRoot "C:\path\to\ba-assistant-cursor-skill"
# Apply:
#   .\tools\upgrade-ba-assistant.ps1 -PackageRoot "C:\path\to\ba-assistant-cursor-skill" -Apply
param(
    [Parameter(Mandatory = $true)][string]$PackageRoot,
    [switch]$Apply,
    [switch]$ForcePersonal
)
$script = Join-Path $PSScriptRoot "upgrade-ba-assistant.py"
$argsList = @($script, "--package", $PackageRoot)
if ($Apply) { $argsList += "--apply" }
if ($ForcePersonal) { $argsList += "--force-personal" }
$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) { & py @argsList } else { & python @argsList }
