# sessionStart hook — inject latest SESSION-CONTEXT snippet into agent context
[Console]::Error.WriteLine("session-init.ps1 running - $(Get-Date -Format 'HH:mm:ss')")
$ErrorActionPreference = 'SilentlyContinue'

$searchRoots = @()

if (-not [string]::IsNullOrWhiteSpace($env:BA_INITIATIVES_ROOT)) {
    $searchRoots += $env:BA_INITIATIVES_ROOT
}

$searchRoots += @(
    (Join-Path $env:USERPROFILE '.cursor\Initiatives'),
    (Join-Path $env:USERPROFILE '.cursor\blueprints'),
    (Join-Path $env:USERPROFILE 'ba-initiatives'),
    (Join-Path $env:USERPROFILE 'Initiatives'),
    (Join-Path $env:USERPROFILE 'projects')
)

# Deduplicate roots (case-insensitive on Windows)
$searchRoots = $searchRoots | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Select-Object -Unique

$latest = $null
$latestTime = [datetime]::MinValue

foreach ($root in $searchRoots) {
    if (-not (Test-Path $root)) { continue }
    Get-ChildItem -Path $root -Recurse -Filter 'SESSION-CONTEXT.md' -ErrorAction SilentlyContinue | ForEach-Object {
        if ($_.LastWriteTime -gt $latestTime) {
            $latestTime = $_.LastWriteTime
            $latest = $_
        }
    }
}

$rootsLabel = if ($searchRoots.Count -gt 0) { ($searchRoots -join '; ') } else { '(none configured)' }
$contextBlock = "No SESSION-CONTEXT.md found under configured initiative roots: $rootsLabel. Set BA_INITIATIVES_ROOT to your project folder root."

if ($null -ne $latest) {
    $lines = Get-Content -Path $latest.FullName -ErrorAction SilentlyContinue
    $tail = if ($lines.Count -gt 45) { $lines[($lines.Count - 45)..($lines.Count - 1)] } else { $lines }
    $snippet = ($tail -join "`n")
    $contextBlock = @"
ACTIVE INITIATIVE CONTEXT (auto-injected from $($latest.FullName), modified $($latestTime.ToString('yyyy-MM-dd HH:mm')):
On BA-resume threads, READ the full file before acting. Do not rely on this snippet alone.

--- SESSION-CONTEXT tail ---
$snippet
--- end ---
"@
}

$output = @{
    additional_context = $contextBlock
    env                  = @{
        CURSOR_SESSION_CONTEXT_PATH = $(if ($latest) { $latest.FullName } else { '' })
    }
} | ConvertTo-Json -Depth 4 -Compress

Write-Output $output
exit 0
