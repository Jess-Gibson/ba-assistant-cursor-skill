# preCompact hook — snapshot SESSION-CONTEXT before context compaction
$ErrorActionPreference = 'SilentlyContinue'

$scratch = Join-Path $env:LOCALAPPDATA 'Temp\cursor-agent-scratch'
if (-not (Test-Path $scratch)) { New-Item -ItemType Directory -Path $scratch -Force | Out-Null }

$ctxPath = $env:CURSOR_SESSION_CONTEXT_PATH
if ([string]::IsNullOrWhiteSpace($ctxPath) -or -not (Test-Path $ctxPath)) {
    Write-Output '{}'
    exit 0
}

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$dest = Join-Path $scratch "SESSION-CONTEXT-precompact-$stamp.md"
Copy-Item -Path $ctxPath -Destination $dest -Force

Write-Output '{}'
exit 0
