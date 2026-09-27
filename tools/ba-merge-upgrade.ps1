# Personalised-install upgrade helper (Windows). Passes every argument through.
# Example:
#   .\tools\ba-merge-upgrade.ps1 backup
#   .\tools\ba-merge-upgrade.ps1 classify --session "$HOME\ba-assistant-upgrade-20260927-101500" --base ..\v14 --new . --rules rules.json
# See docs\V15-WORK-LAPTOP.md for the full walkthrough.
$script = Join-Path $PSScriptRoot "ba-merge-upgrade.py"
$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) { & py $script @args } else { & python $script @args }
exit $LASTEXITCODE
