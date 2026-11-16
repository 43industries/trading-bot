# Start 43_industries dry-run bot and open FreqUI.
$ErrorActionPreference = "Stop"
$RepoRoot = $PSScriptRoot
$FreqtradeDir = Join-Path $RepoRoot "freqtrade"
$VenvActivate = Join-Path $FreqtradeDir ".venv\Scripts\Activate.ps1"
$LogDir = Join-Path $FreqtradeDir "user_data\logs"
$LogFile = Join-Path $LogDir "freqai_dryrun.log"
$UiUrl = "http://127.0.0.1:8080/"

if (-not (Test-Path $VenvActivate)) {
    Write-Error "Missing venv at $VenvActivate. Run Setup steps in README first."
}

$existing = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -match 'freqtrade(\.exe)?\s+trade' }
if ($existing) {
    $pids = ($existing | ForEach-Object { $_.ProcessId }) -join ", "
    Write-Host "Bot already running (PID: $pids). Use .\status.ps1 or .\stop-bot.ps1."
    Start-Process $UiUrl
    exit 0
}

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

Write-Host "Starting dry-run: FreqaiSpotStrategy + LightGBMRegressor"
Write-Host "Log: $LogFile"
Write-Host "UI:  $UiUrl"

$inner = @"
Set-Location '$FreqtradeDir'
. '$VenvActivate'
freqtrade trade --config user_data/config.json --strategy FreqaiSpotStrategy --freqaimodel LightGBMRegressor --userdir user_data 2>&1 | Out-File -FilePath '$LogFile' -Append -Encoding utf8
"@

Start-Process -FilePath "powershell.exe" -WorkingDirectory $FreqtradeDir -WindowStyle Minimized -ArgumentList @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-Command", $inner
)

Start-Sleep -Seconds 3
Start-Process $UiUrl
Write-Host "Bot start requested. Run .\status.ps1 to confirm RUNNING."
