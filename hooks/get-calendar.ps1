# Pull calendar events from Outlook COM and write to calendar-feed.json
# Run on demand or from session-init
# Usage: powershell -File get-calendar.ps1 [-DaysAhead 2] [-DaysBehind 0]
param(
    [int]$DaysAhead = 2,
    [int]$DaysBehind = 0
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

    # Outlook COM Restrict uses the system's short date format
    # NZ/AU locale: d/MM/yyyy; US: M/d/yyyy -- use system culture
    $rangeStart = (Get-Date).Date.AddDays(-$DaysBehind)
    $rangeEnd = (Get-Date).Date.AddDays($DaysAhead)
    $startDate = $rangeStart.ToString('d/MM/yyyy h:mm tt')
    $endDate = $rangeEnd.ToString('d/MM/yyyy h:mm tt')
    $filter = "[Start] >= '$startDate' AND [Start] < '$endDate'"

    $restricted = $items.Restrict($filter)

    # IncludeRecurrences makes .Count return Int32.MaxValue
    # Use Find/iteration with a cap instead
    $meetings = @()
    $maxItems = 200
    $item = $restricted.GetFirst()
    while ($null -ne $item -and $meetings.Count -lt $maxItems) {
        # Only include appointments and meetings (skip all-day events optionally)
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
        range_start   = $rangeStart.ToString('o')
        range_end     = $rangeEnd.ToString('o')
        meeting_count = $meetings.Count
        meetings      = $meetings
    }

    $output | ConvertTo-Json -Depth 4 | Set-Content $outputPath -Encoding UTF8
    Write-Host "Calendar feed written: $($meetings.Count) meetings to $outputPath"

} catch {
    Write-Host "Calendar access failed: $($_.Exception.Message)"
    Write-Host "Fallback: Use Power Automate to export calendar, or run this script when Outlook is open."

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
