# Show dry-run bot process status and recent log heartbeats.
$ErrorActionPreference = "Continue"
$RepoRoot = $PSScriptRoot
$LogFile = Join-Path $RepoRoot "freqtrade\user_data\logs\freqai_dryrun.log"

$procs = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -match 'freqtrade(\.exe)?\s+trade' }

if (-not $procs) {
    Write-Host "Status: NOT RUNNING"
} else {
    Write-Host "Status: RUNNING"
    foreach ($p in $procs) {
        $strategy = "unknown"
        if ($p.CommandLine -match '--strategy\s+(\S+)') { $strategy = $Matches[1] }
        $model = "unknown"
        if ($p.CommandLine -match '--freqaimodel\s+(\S+)') { $model = $Matches[1] }
        Write-Host ("  PID={0}  strategy={1}  model={2}" -f $p.ProcessId, $strategy, $model)
    }
}

Write-Host ""
Write-Host "UI: http://127.0.0.1:8080/"
Write-Host "Log: $LogFile"
Write-Host ""

if (Test-Path $LogFile) {
    Write-Host "Recent log (heartbeat / dry_run / error):"
    Select-String -Path $LogFile -Pattern "Bot heartbeat|dry_run|ERROR|Traceback|state=" |
        Select-Object -Last 8 |
        ForEach-Object { $_.Line.Trim() }
} else {
    Write-Host "No log file yet."
}
