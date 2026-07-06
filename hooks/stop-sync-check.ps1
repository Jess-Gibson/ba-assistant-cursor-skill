# stop hook - sync-gate breakpoint check at end of an agent response (D3). PowerShell twin
# of stop-sync-check.sh. Reuses inject-state-reminder.py: same computation, different event.
# Emits additional context only when there is real drift.
param()
$ErrorActionPreference = 'SilentlyContinue'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command py -ErrorAction SilentlyContinue }
if ($py) {
    & $py.Source "$scriptDir\inject-state-reminder.py" --stop
} else {
    Write-Output '{}'
}
exit 0
