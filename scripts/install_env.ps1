# install_env.ps1 - Install deps with progress / rough ETA
#
# Usage:
#   install_env.cmd
#   powershell -ExecutionPolicy Bypass -File .\scripts\install_env.ps1
#   powershell -ExecutionPolicy Bypass -File .\scripts\install_env.ps1 -MonitorOnly

param(
    [switch]$MonitorOnly,
    [string]$Requirements = "requirements.txt"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $ProjectRoot

$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Host "[ERROR] .venv not found. Run: py -3.11 -m venv .venv" -ForegroundColor Red
    exit 1
}

$KeyPackages = [ordered]@{
    "numpy"                 = "numpy"
    "pandas"                = "pandas"
    "torch"                 = "torch"
    "scikit-learn"          = "sklearn"
    "transformers"          = "transformers"
    "sentence-transformers" = "sentence_transformers"
    "openai"                = "openai"
    "httpx"                 = "httpx"
    "feedparser"            = "feedparser"
    "python-dotenv"         = "dotenv"
}

$SitePackages = Join-Path $ProjectRoot ".venv\Lib\site-packages"

function Test-PackageInstalled([string]$DirName) {
    Test-Path (Join-Path $SitePackages $DirName)
}

function Show-ProgressPanel([datetime]$StartTime, [string]$Phase) {
    $done = 0
    $total = $KeyPackages.Count
    foreach ($kv in $KeyPackages.GetEnumerator()) {
        if (Test-PackageInstalled $kv.Value) { $done++ }
    }
    $elapsed = (Get-Date) - $StartTime
    $pct = if ($total -gt 0) { [math]::Round(100.0 * $done / $total, 0) } else { 0 }
    if ($done -eq 0) {
        $etaStr = "waiting..."
    }
    elseif ($done -lt $total) {
        $secPerPkg = $elapsed.TotalSeconds / $done
        $remaining = ($total - $done) * $secPerPkg
        $etaStr = ([TimeSpan]::FromSeconds([math]::Max(0, $remaining))).ToString("mm\:ss")
    }
    else {
        $etaStr = "00:00"
    }

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host " Install progress | $Phase" -ForegroundColor Cyan
    Write-Host " Elapsed $($elapsed.ToString('mm\:ss')) | $done / $total ($pct%) | ETA ~ $etaStr" -ForegroundColor Cyan
    Write-Host " (ETA = avg time per ready pkg x remaining; slow on NAS)" -ForegroundColor DarkGray
    Write-Host "----------------------------------------"
    foreach ($kv in $KeyPackages.GetEnumerator()) {
        $mark = if (Test-PackageInstalled $kv.Value) { "[x]" } else { "[ ]" }
        Write-Host "  $mark $($kv.Key)"
    }
    Write-Host "----------------------------------------"
}

if ($MonitorOnly) {
    Write-Host "Monitor mode: refresh every 2s. Run pip in another terminal. Ctrl+C to stop." -ForegroundColor Yellow
    $StartTime = Get-Date
    while ($true) {
        Clear-Host
        Show-ProgressPanel $StartTime "monitoring"
        $all = $true
        foreach ($kv in $KeyPackages.GetEnumerator()) {
            if (-not (Test-PackageInstalled $kv.Value)) { $all = $false; break }
        }
        if ($all) {
            Write-Host ""
            Write-Host "[OK] All key packages ready." -ForegroundColor Green
            break
        }
        Start-Sleep -Seconds 2
    }
    exit 0
}

$StartTime = Get-Date
Show-ProgressPanel $StartTime "before install"

$ReqPath = Join-Path $ProjectRoot $Requirements
$LogPath = Join-Path $ProjectRoot ("state\install_{0:yyyyMMdd_HHmmss}.log" -f (Get-Date))

Write-Host ""
Write-Host ">>> pip install (download progress bars below)" -ForegroundColor Yellow
Write-Host ">>> For checklist + ETA in parallel: install_env.cmd -MonitorOnly" -ForegroundColor Yellow
Write-Host ">>> Log: $LogPath" -ForegroundColor DarkGray
Write-Host ""

& $VenvPython -m pip install -r $ReqPath --progress-bar on 2>&1 | Tee-Object -FilePath $LogPath

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[FAIL] pip exit code $LASTEXITCODE. See $LogPath" -ForegroundColor Red
    exit $LASTEXITCODE
}

Show-ProgressPanel $StartTime "verifying imports"

& $VenvPython -c "import numpy, pandas, torch, sklearn, transformers, sentence_transformers, openai, httpx, feedparser; from dotenv import load_dotenv; print('ALL IMPORTS OK')"

if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] import failed. Retry: install_env.cmd" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "[OK] Environment ready. Total $(((Get-Date) - $StartTime).ToString('mm\:ss'))" -ForegroundColor Green
