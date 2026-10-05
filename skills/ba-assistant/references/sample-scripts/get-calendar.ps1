# Sample pointer only.
# The live calendar script ships as hooks/get-calendar.ps1 (supports -DaysAhead
# and -DaysBehind). The installer copies that file into ~/.cursor/hooks/.
# Prefer that path. This sample folder is kept so older docs that link here
# still resolve.
#
# Canonical: ../../../../hooks/get-calendar.ps1  (from this file)
# Installed: ~/.cursor/hooks/get-calendar.ps1
#
# Usage: powershell -File get-calendar.ps1 [-DaysAhead 2] [-DaysBehind 0]
# Writes: $env:USERPROFILE\.cursor\_workstream\calendar-feed.json

Write-Error "Use hooks/get-calendar.ps1 (copied by the installer into ~/.cursor/hooks/). This sample is a pointer only."
exit 1
