# Sample calendar feed script for BA Assistant /workboard (Windows).
# Not installed automatically - copy to ~/.cursor/hooks/ and wire into hooks.json
# (sessionStart) yourself if you want an automated calendar feed. Requires Outlook
# desktop with COM automation (Windows only). For macOS see get-calendar.mac.sh.
# Calendar is optional; /workboard degrades gracefully without calendar-feed.json.
#
# Usage: powershell -File get-calendar.ps1 [-DaysAhead 2]
# Writes: $env:USERPROFILE\.cursor\_workstream\calendar-feed.json
param(
    [int]$DaysAhead = 2
)

$ErrorActionPreference = 'Stop'
$outputPath = "$env:USERPROFILE\.cursor\_workstream\calendar-feed.json"

try {
    $outlook = New-Object -ComObject Outlook.Application
    $ns = $outlook.GetNamespace('MAPI')
    $cal = $ns.GetDefaultFolder(9)  # olFolderCalendar
    $items = $cal.Items
    $items.Sort('[Start]')
    $items.IncludeRecurrences = $true

    # Outlook COM Restrict uses the system's short date format.
    # Adjust the format string below if your locale isn't d/MM/yyyy (NZ/AU) — e.g. US is M/d/yyyy.
    $startDate = (Get-Date).Date.ToString('d/MM/yyyy h:mm tt')
    $endDate = (Get-Date).Date.AddDays($DaysAhead).ToString('d/MM/yyyy h:mm tt')
    $filter = "[Start] >= '$startDate' AND [Start] < '$endDate'"

    $restricted = $items.Restrict($filter)

    # IncludeRecurrences makes .Count return Int32.MaxValue — iterate with a cap instead.
    $meetings = @()
    $maxItems = 50
    $item = $restricted.GetFirst()
    while ($null -ne $item -and $meetings.Count -lt $maxItems) {
        $bodyText = ''
        try { $bodyText = $item.Body } catch { }
        $bodyPreview = if ($bodyText.Length -gt 200) { $bodyText.Substring(0, 200) + '...' } else { $bodyText }

        $meetings += @{
            subject      = $item.Subject
            start        = $item.Start.ToString('o')
            end          = $item.End.ToString('o')
            location     = $item.Location
            organizer    = $item.Organizer
            required     = $item.RequiredAttendees
            is_all_day   = $item.AllDayEvent
            is_online    = ($item.Location -match 'Teams')
            duration_min = $item.Duration
            body_preview = $bodyPreview
        }
        $item = $restricted.GetNext()
    }

    $output = @{
        last_updated  = (Get-Date).ToString('o')
        range_start   = (Get-Date).Date.ToString('o')
        range_end     = (Get-Date).Date.AddDays($DaysAhead).ToString('o')
        meeting_count = $meetings.Count
        meetings      = $meetings
    }

    $output | ConvertTo-Json -Depth 4 | Set-Content $outputPath -Encoding UTF8
    Write-Host "Calendar feed written: $($meetings.Count) meetings to $outputPath"

} catch {
    Write-Host "Calendar access failed: $($_.Exception.Message)"
    Write-Host "Fallback: export your calendar another way, or run this script when Outlook is open."

    if (-not (Test-Path $outputPath)) {
        @{
            last_updated  = (Get-Date).ToString('o')
            range_start   = (Get-Date).Date.ToString('o')
            range_end     = (Get-Date).Date.AddDays($DaysAhead).ToString('o')
            meeting_count = 0
            meetings      = @()
            error         = $_.Exception.Message
        } | ConvertTo-Json -Depth 4 | Set-Content $outputPath -Encoding UTF8
    }
}
