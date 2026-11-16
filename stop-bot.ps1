# Stop running freqtrade trade processes.
$ErrorActionPreference = "Stop"

$procs = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -match 'freqtrade(\.exe)?\s+trade' }

if (-not $procs) {
    Write-Host "No freqtrade trade process found."
    exit 0
}

foreach ($p in $procs) {
    Write-Host "Stopping PID $($p.ProcessId)..."
    Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
}

Start-Sleep -Seconds 1
$still = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -match 'freqtrade(\.exe)?\s+trade' }
if ($still) {
    Write-Host "Warning: some processes may still be running."
    exit 1
}

Write-Host "Bot stopped."
