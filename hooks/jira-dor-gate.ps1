# beforeMCPExecution hook — deny Jira STORY creation when no DoR pass is evident.
# Thin wrapper; logic lives in jira-dor-gate.py (shared with the .sh twin).
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) { $input | & py (Join-Path $scriptDir "jira-dor-gate.py") }
else     { $input | & python3 (Join-Path $scriptDir "jira-dor-gate.py") }
