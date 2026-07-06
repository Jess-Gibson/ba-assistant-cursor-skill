# sessionStart hook v2 - inject latest SESSION-CONTEXT snippet + DETERMINISTIC downloads check (D5)
# Changes from v1 (personalised merge, 5 Jul 2026):
#   - Downloads/Recordings enumeration now uses `cmd /c dir /b` + Get-Item per file, because both
#     Get-ChildItem AND .NET GetFiles() silently return empty for Downloads in this agent
#     environment (verified 2 Jul 2026 - see references/workspace-operations.md).
#   - Honours BA_INITIATIVES_ROOT and BA_DOWNLOADS_PATH env vars (set by ba-setup wizard) with
#     the existing personal paths as fallbacks.
#   - Adds CURSOR_NEW_TRANSCRIPT_COUNT to the env output (execution-router re-entry card reads it).
#   - Injects workspace agent-file guidance (absorbs read-claude-first, D6).
# Kept from v1: last-session timestamp file, recordings-folder + .vtt support,
# workboard block, calendar refresh via get-calendar.ps1.
[Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSUseDeclaredVarsMoreThanAssignments', '')]
param()
[Console]::Error.WriteLine("session-init.ps1 v2 running - $(Get-Date -Format 'HH:mm:ss')")
$ErrorActionPreference = 'SilentlyContinue'

# --- State file for tracking last session timestamp ---
$scratchDir = "$env:LOCALAPPDATA\Temp\cursor-agent-scratch"
if (-not (Test-Path $scratchDir)) {
    New-Item -ItemType Directory -Force -Path $scratchDir | Out-Null
}
$timestampFile = "$scratchDir\last-session-timestamp.txt"
$lastSessionTime = [datetime]::MinValue
if (Test-Path $timestampFile) {
    try {
        $lastSessionTime = [datetime]::Parse((Get-Content $timestampFile -Raw).Trim())
    } catch { }
}
# Write current timestamp for next session's delta
Get-Date -Format 'o' | Set-Content $timestampFile -Force

# --- 1. Find latest SESSION-CONTEXT.md ---
$searchRoots = @()
if ($env:BA_INITIATIVES_ROOT) { $searchRoots += $env:BA_INITIATIVES_ROOT }
$searchRoots += @(
    "$env:USERPROFILE\.cursor\Initiatives",
    "$env:USERPROFILE\.cursor\blueprints"
)

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

$contextBlock = 'No SESSION-CONTEXT.md found under configured initiative roots. Set BA_INITIATIVES_ROOT (ba-setup wizard) if initiatives live elsewhere.'

if ($null -ne $latest) {
    $lines = Get-Content -Path $latest.FullName -ErrorAction SilentlyContinue
    $tail = if ($lines.Count -gt 45) { $lines[($lines.Count - 45)..($lines.Count - 1)] } else { $lines }
    $snippet = ($tail -join "`n")
    $contextBlock = @"
ACTIVE INITIATIVE CONTEXT (auto-injected from $($latest.FullName), modified $($latestTime.ToString('yyyy-MM-dd HH:mm')):
On BA-resume threads, READ the full file before acting. Do not rely on this snippet alone.
If the open workspace has AGENTS.md or !CLAUDE.md at its root, read it as primary project context (else README.md).

--- SESSION-CONTEXT tail ---
$snippet
--- end ---
"@
}

# --- 2. Deterministic downloads check (D5) - cmd /c dir enumeration ---
# Get-ChildItem / .NET GetFiles silently fail on Downloads in this environment (verified 2 Jul 2026).
# Enumerate names with cmd /c dir /b (reliable), then stat each via Get-Item (single-file access works).
function Get-FolderFilesReliable {
    param([string]$Folder)
    $names = @(cmd /c "dir /b /a-d `"$Folder`"" 2>$null)
    $files = @()
    foreach ($n in $names) {
        if ([string]::IsNullOrWhiteSpace($n)) { continue }
        $item = Get-Item -LiteralPath (Join-Path $Folder $n) -ErrorAction SilentlyContinue
        if ($item) { $files += $item }
    }
    return $files
}

$transcriptFolders = @()
if ($env:BA_DOWNLOADS_PATH) { $transcriptFolders += $env:BA_DOWNLOADS_PATH }
$transcriptFolders += @(
    "$env:USERPROFILE\Downloads",
    # (add your recordings folder here or set BA_DOWNLOADS_PATH)
)
$transcriptFolders = $transcriptFolders | Select-Object -Unique
$transcriptExtensions = @('.docx', '.vtt')
$newTranscripts = @()
$otherNewFiles = @()

foreach ($folder in $transcriptFolders) {
    if (-not (Test-Path $folder)) { continue }
    foreach ($f in (Get-FolderFilesReliable -Folder $folder)) {
        if ($f.LastWriteTime -le $lastSessionTime) { continue }
        $entry = @{
            name = $f.Name
            path = $f.FullName
            modified = $f.LastWriteTime.ToString('yyyy-MM-dd HH:mm')
            folder = $folder
        }
        if ($transcriptExtensions -contains $f.Extension.ToLower()) {
            $newTranscripts += $entry
        } elseif ($f.Extension.ToLower() -in @('.pdf', '.png', '.jpg', '.jpeg', '.xlsx', '.csv', '.txt', '.md', '.pptx')) {
            # Not only .docx matters - see workspace-operations reference (3 Jul 2026 PDF miss)
            $otherNewFiles += $entry
        }
    }
}

$transcriptBlock = ''
if ($newTranscripts.Count -gt 0) {
    $fileList = ($newTranscripts | ForEach-Object { "  - $($_.name) ($($_.modified)) in $($_.folder)" }) -join "`n"
    $transcriptBlock = @"

NEW TRANSCRIPTS DETECTED ($($newTranscripts.Count) file(s) since last session):
$fileList
Process these as meeting debriefs (ba-meeting-debrief) before or alongside the user's first ask.
"@
}
if ($otherNewFiles.Count -gt 0) {
    $otherList = ($otherNewFiles | Select-Object -First 10 | ForEach-Object { "  - $($_.name) ($($_.modified))" }) -join "`n"
    $transcriptBlock += @"

OTHER NEW DOWNLOADS ($($otherNewFiles.Count) file(s) - PDFs/images/sheets can carry decisions and proposals too):
$otherList
Triage per the workspace-operations reference before asking the user what they need.
"@
}

# --- 3. Check for workboard ---
$workboardBlock = ''
$workboardPath = "$env:USERPROFILE\.cursor\_workstream\workboard.json"
if (Test-Path $workboardPath) {
    try {
        $wb = Get-Content $workboardPath -Raw | ConvertFrom-Json
        $taskCount = 0
        if ($wb.personal_tasks) {
            $taskCount = ($wb.personal_tasks | Where-Object { $_.status -eq 'open' }).Count
        }
        if ($taskCount -gt 0) {
            $workboardBlock = "`nWORKBOARD: $taskCount open personal tasks. Say /workboard for full view."
        }
    } catch { }
}

# --- 4. Refresh calendar feed then check it ---
$calendarBlock = ''
$calendarScript = "$env:USERPROFILE\.cursor\hooks\get-calendar.ps1"
$calendarPath = "$env:USERPROFILE\.cursor\_workstream\calendar-feed.json"

if (Test-Path $calendarScript) {
    try {
        & $calendarScript -DaysAhead 2 2>$null
    } catch {
        [Console]::Error.WriteLine("Calendar refresh failed: $($_.Exception.Message)")
    }
}

if (Test-Path $calendarPath) {
    try {
        $cal = Get-Content $calendarPath -Raw | ConvertFrom-Json
        if ($cal.meetings -and $cal.meetings.Count -gt 0) {
            $todayMeetings = ($cal.meetings | Where-Object {
                [datetime]::Parse($_.start) -gt (Get-Date).Date -and [datetime]::Parse($_.start) -lt (Get-Date).Date.AddDays(1)
            }).Count
            if ($todayMeetings -gt 0) {
                $calendarBlock = "`nCALENDAR: $todayMeetings meeting(s) today. Check /workboard for details."
            }
        }
    } catch { }
}

# --- Assemble output ---
$fullContext = $contextBlock + $transcriptBlock + $workboardBlock + $calendarBlock

$output = @{
    additional_context = $fullContext
    env = @{
        CURSOR_SESSION_CONTEXT_PATH = $(if ($latest) { $latest.FullName } else { '' })
        CURSOR_LAST_SESSION = $(if ($lastSessionTime -ne [datetime]::MinValue) { $lastSessionTime.ToString('o') } else { '' })
        CURSOR_NEW_TRANSCRIPTS = $(if ($newTranscripts.Count -gt 0) { ($newTranscripts | ForEach-Object { $_.path }) -join ';' } else { '' })
        CURSOR_NEW_TRANSCRIPT_COUNT = "$($newTranscripts.Count)"
    }
} | ConvertTo-Json -Depth 4 -Compress

Write-Output $output
exit 0
