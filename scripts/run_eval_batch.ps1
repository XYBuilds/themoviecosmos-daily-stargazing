#Requires -Version 7.0
<#
.SYNOPSIS
  Parallel N=10 Phase 3.6.5 run_eval batch with jitter and optional retry.

.DESCRIPTION
  Runs tests/eval_news batch (see batch-manifest.json) into output/Eval/phase3.6/{run_id}/.
  Does NOT write to phase3.5 or output/Eval root. Does NOT run summarize_eval.
  On full success only, runs score_eval_candidates with --review-out under phase3.6.

.PARAMETER WhatIf
  Print planned commands without invoking python.

.PARAMETER RetryFailed
  Re-run only failed run_ids from the last batch-summary.json (throttle K=4).

.PARAMETER SkipExisting
  Skip run_ids whose output marker already exists under PhaseDir (default: true).

.PARAMETER SkipMarkerFile
  Relative file under each run_id folder used by -SkipExisting (default: candidates.md).

.PARAMETER RunIds
  Explicit subset of run_ids (overrides manifest; with -RetryFailed, union with failed list).

.PARAMETER ThrottleLimit
  Parallel job cap (default 3; forced to 4 when -RetryFailed and not overridden).

.PARAMETER PhaseDir
  Eval phase root (default output/Eval/phase3.6).

.EXAMPLE
  pwsh -File scripts/run_eval_batch.ps1 -WhatIf

.EXAMPLE
  pwsh -File scripts/run_eval_batch.ps1

.EXAMPLE
  pwsh -File scripts/run_eval_batch.ps1 -RetryFailed

.EXAMPLE
  powershell -File scripts/run_eval_batch.ps1 -SkipExisting -ThrottleLimit 3
#>
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [switch]$RetryFailed,
    [bool]$SkipExisting = $true,
    [string]$SkipMarkerFile = "candidates.md",
    [string[]]$RunIds = @(),
    [int]$ThrottleLimit = 0,
    [string]$PhaseDir = "output/Eval/phase3.6",
    [string]$ManifestPath = "tests/eval_news/batch-manifest.json"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ($PSVersionTable.PSVersion.Major -lt 7) {
    throw "PowerShell 7+ required (ForEach-Object -Parallel). Current: $($PSVersionTable.PSVersion)"
}

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ManifestFile = Join-Path $RepoRoot $ManifestPath
if (-not (Test-Path -LiteralPath $ManifestFile)) {
    throw "Manifest not found: $ManifestFile"
}

$manifest = Get-Content -LiteralPath $ManifestFile -Raw -Encoding UTF8 | ConvertFrom-Json
$allRunIds = @($manifest.run_ids | ForEach-Object { [string]$_ })
if ($allRunIds.Count -ne 10) {
    throw "Manifest must list exactly 10 run_ids (found $($allRunIds.Count))"
}

$LogsDir = Join-Path $RepoRoot (Join-Path $PhaseDir "_logs")
$SummaryPath = Join-Path $LogsDir "batch-summary.json"

function Get-LastFailedRunIds {
    if (-not (Test-Path -LiteralPath $SummaryPath)) {
        throw "-RetryFailed requires prior summary at $SummaryPath"
    }
    $prev = Get-Content -LiteralPath $SummaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
    return @($prev.failed | ForEach-Object { [string]$_ })
}

$effectiveThrottle = $ThrottleLimit
if ($RetryFailed) {
    if ($effectiveThrottle -le 0) { $effectiveThrottle = 4 }
    $failedFromSummary = Get-LastFailedRunIds
    if ($RunIds.Count -gt 0) {
        $targetRunIds = @($RunIds | ForEach-Object { [string]$_ })
    } else {
        $targetRunIds = $failedFromSummary
    }
    if ($targetRunIds.Count -eq 0) {
        Write-Host "No failed run_ids in $SummaryPath — nothing to retry."
        exit 0
    }
} else {
    if ($effectiveThrottle -le 0) { $effectiveThrottle = 3 }
    if ($RunIds.Count -gt 0) {
        $targetRunIds = @($RunIds | ForEach-Object { [string]$_ })
    } else {
        $targetRunIds = $allRunIds
    }
}

foreach ($rid in $targetRunIds) {
    if ($rid -notin $allRunIds) {
        throw "Unknown run_id '$rid' (not in manifest)"
    }
}

$skippedExisting = @()
if ($SkipExisting -and -not $RetryFailed) {
    $toRun = [System.Collections.Generic.List[string]]::new()
    foreach ($rid in $targetRunIds) {
        $markerPath = Join-Path $RepoRoot (Join-Path $PhaseDir (Join-Path $rid $SkipMarkerFile))
        if (Test-Path -LiteralPath $markerPath) {
            $skippedExisting += $rid
        } else {
            [void]$toRun.Add($rid)
        }
    }
    if ($skippedExisting.Count -gt 0) {
        Write-Host "SkipExisting ($SkipMarkerFile): $($skippedExisting -join ', ')"
    }
    $targetRunIds = @($toRun)
}

if ($targetRunIds.Count -eq 0) {
    Write-Host "No run_ids to execute (all skipped or empty selection)."
    exit 0
}

$NewsDir = Join-Path $RepoRoot "tests/eval_news"
$python = "python"

Write-Host "Phase dir:     $PhaseDir"
Write-Host "Run count:     $($targetRunIds.Count)"
Write-Host "ThrottleLimit: $effectiveThrottle"
Write-Host "Logs:          $LogsDir"
Write-Host ""

if ($WhatIfPreference) {
    foreach ($rid in $targetRunIds) {
        $newsFile = Join-Path $NewsDir "$rid.json"
        $outDir = Join-Path $RepoRoot (Join-Path $PhaseDir $rid)
        $logFile = Join-Path $LogsDir "$rid.log"
        Write-Host "[WhatIf] jitter 5-15s then:"
        Write-Host "  $python scripts/run_eval.py --news-file $newsFile --run-id $rid --out $outDir"
        Write-Host "  log -> $logFile"
    }
    if (-not $RetryFailed -and $targetRunIds.Count -eq 10) {
        Write-Host "[WhatIf] if all 10 succeed:"
        Write-Host "  $python scripts/score_eval_candidates.py --dir $PhaseDir --review-out $PhaseDir/high-hit-score-review.md"
    }
    exit 0
}

New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null

$parallelResults = $targetRunIds | ForEach-Object -Parallel {
    $rid = $_
    $repoRoot = $using:RepoRoot
    $newsDir = $using:NewsDir
    $phaseDir = $using:PhaseDir
    $logsDir = $using:LogsDir
    $pythonCmd = $using:python

    $jitterSec = Get-Random -Minimum 5 -Maximum 16
    Start-Sleep -Seconds $jitterSec

    $newsFile = Join-Path $newsDir "$rid.json"
    $outRel = Join-Path $phaseDir $rid
    $outDir = Join-Path $repoRoot $outRel
    $logPath = Join-Path $logsDir "$rid.log"

    $header = @(
        "run_id=$rid"
        "started=$(Get-Date -Format o)"
        "jitter_sec=$jitterSec"
        "cwd=$repoRoot"
        "command=$pythonCmd scripts/run_eval.py --news-file $newsFile --run-id $rid --out $outRel"
        "---"
    ) -join "`n"

    Set-Location -LiteralPath $repoRoot
    $argList = @(
        "scripts/run_eval.py",
        "--news-file", $newsFile,
        "--run-id", $rid,
        "--out", $outRel
    )

    try {
        $output = & $pythonCmd @argList 2>&1
        $exitCode = $LASTEXITCODE
        if ($null -eq $exitCode) { $exitCode = 0 }
    } catch {
        $exitCode = 1
        $output = $_.Exception.Message
    }

    $body = if ($output) { ($output | Out-String) } else { "" }
    $footer = "`n---`nfinished=$(Get-Date -Format o)`nexit_code=$exitCode`n"
    ($header + "`n" + $body + $footer) | Set-Content -LiteralPath $logPath -Encoding UTF8

    [PSCustomObject]@{
        RunId    = $rid
        ExitCode = [int]$exitCode
        LogPath  = $logPath
    }
} -ThrottleLimit $effectiveThrottle

$succeeded = @($parallelResults | Where-Object { $_.ExitCode -eq 0 } | ForEach-Object { $_.RunId })
$failed = @($parallelResults | Where-Object { $_.ExitCode -ne 0 } | ForEach-Object { $_.RunId })
$exitCodes = @{}
foreach ($r in $parallelResults) {
    $exitCodes[$r.RunId] = $r.ExitCode
}

Write-Host ""
Write-Host "=== Batch summary ==="
Write-Host "Succeeded ($($succeeded.Count)): $($succeeded -join ', ')"
if ($failed.Count -gt 0) {
    Write-Host "Failed    ($($failed.Count)): $($failed -join ', ')"
    foreach ($rid in $failed) {
        $code = $exitCodes[$rid]
        Write-Host "  $rid exit=$code log=$LogsDir\$rid.log"
    }
} else {
    Write-Host "Failed    (0)"
}

$summaryObj = [ordered]@{
    timestamp       = (Get-Date -Format o)
    phase_dir       = $PhaseDir
    throttle        = $effectiveThrottle
    retry_mode      = [bool]$RetryFailed
    skip_existing   = [bool]$SkipExisting
    skip_marker     = $SkipMarkerFile
    skipped_existing = $skippedExisting
    succeeded       = $succeeded
    failed          = $failed
    exit_codes      = $exitCodes
}
$summaryObj | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $SummaryPath -Encoding UTF8
Write-Host "Wrote $SummaryPath"

$fullBatchOk = (-not $RetryFailed) -and ($targetRunIds.Count -eq 10) -and ($failed.Count -eq 0)
if ($fullBatchOk) {
    Write-Host ""
    Write-Host "All 10 runs succeeded — scoring candidates (phase-scoped review)..."
    $reviewOut = Join-Path $PhaseDir "high-hit-score-review.md"
    Set-Location -LiteralPath $RepoRoot
    & $python scripts/score_eval_candidates.py --dir $PhaseDir --review-out $reviewOut
    $scoreExit = $LASTEXITCODE
    if ($scoreExit -ne 0) {
        Write-Error "score_eval_candidates.py failed with exit $scoreExit"
        exit $scoreExit
    }
    Write-Host "Wrote review: $(Join-Path $RepoRoot $reviewOut)"
    exit 0
}

if ($failed.Count -gt 0) {
    Write-Host ""
    Write-Host "Retry failures only (K=4):"
    Write-Host "  pwsh -File scripts/run_eval_batch.ps1 -RetryFailed"
    exit 1
}

exit 0
