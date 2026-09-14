# Workboard overlay installer wrapper (Windows)
param(
    [string]$Package = (Split-Path -Parent $PSScriptRoot),
    [switch]$Apply,
    [switch]$ReplaceWrap,
    [switch]$ReplaceWorkboardCommand,
    [switch]$NoPreviewCanvas
)

$script = Join-Path $PSScriptRoot "upgrade-workboard.py"
$argsList = @("--package", $Package)
if ($Apply) { $argsList += "--apply" }
if ($ReplaceWrap) { $argsList += "--replace-wrap" }
if ($ReplaceWorkboardCommand) { $argsList += "--replace-workboard-command" }
if ($NoPreviewCanvas) { $argsList += "--no-preview-canvas" }
$runner = Get-Command py -ErrorAction SilentlyContinue
if ($runner) {
    & py $script @argsList
} else {
    & python $script @argsList
}
