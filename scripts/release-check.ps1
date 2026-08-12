param(
    [string]$Python = "",
    [string]$Version = "v0.1.0"
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path

if ([string]::IsNullOrWhiteSpace($Python)) {
    $venvPython = Join-Path $repoRoot ".venv/Scripts/python.exe"
    $Python = if (Test-Path -LiteralPath $venvPython) { $venvPython } else { "python" }
}

function Invoke-Checked {
    param([string[]]$Arguments)
    & $Python @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: $Python $($Arguments -join ' ')"
    }
}

Push-Location $repoRoot
try {
    $testTempRoot = Join-Path $repoRoot ".test-tmp"
    $testBaseTemp = Join-Path $testTempRoot "release-check"
    New-Item -ItemType Directory -Path $testTempRoot -Force | Out-Null

    Invoke-Checked @("-m", "ruff", "check", ".")
    Invoke-Checked @(
        "-m", "pytest",
        "--basetemp", $testBaseTemp,
        "--cov=pepper_pet",
        "--cov-report=term-missing",
        "--cov-fail-under=90"
    )
    Invoke-Checked @("-m", "pepper_pet.cli", "validate", "pet", "--json")
    Invoke-Checked @("tools/write_provenance.py", "--check")
    Invoke-Checked @("tools/update_checksums.py", "--check")
    Invoke-Checked @("tools/sync_site_asset.py", "--check")
    Invoke-Checked @("tools/preflight.py", "--version", $Version)
    Invoke-Checked @("tools/release_audit.py", "--version", $Version)
    Invoke-Checked @("-m", "build")
    Invoke-Checked @(
        "-m", "pepper_pet.cli",
        "package",
        "--repo-root", ".",
        "--out-dir", "dist",
        "--version", $Version,
        "--json"
    )
    Write-Host "Release gate passed for $Version"
} finally {
    Pop-Location
}
