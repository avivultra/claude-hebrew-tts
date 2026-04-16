# setup.ps1 — One-time setup for claude-hebrew-tts (Windows)
# Creates a local Python venv inside the skill folder and installs edge-tts.
# Idempotent: re-running does no harm; it re-checks and reports status.

$ErrorActionPreference = 'Stop'

$SkillRoot = Split-Path -Parent $PSScriptRoot     # .../skills/hebrew-tts
$VenvDir   = Join-Path $SkillRoot 'venv'
$VenvPy    = Join-Path $VenvDir 'Scripts\python.exe'

Write-Host "[claude-hebrew-tts setup]"
Write-Host "Skill root : $SkillRoot"
Write-Host "Venv dir   : $VenvDir"

# 1) Locate a Python interpreter to bootstrap from.
$Python = $null
foreach ($cmd in @('py -3', 'python', 'python3')) {
    try {
        $parts = $cmd -split ' '
        $out = & $parts[0] $parts[1..($parts.Length - 1)] --version 2>$null
        if ($LASTEXITCODE -eq 0) { $Python = $cmd; break }
    } catch { }
}
if (-not $Python) {
    Write-Error "Python 3 not found on PATH. Install Python 3.10+ first: https://www.python.org/downloads/"
    exit 1
}
Write-Host "Using Python: $Python"

# 2) Create venv if missing.
if (-not (Test-Path $VenvPy)) {
    Write-Host "Creating venv..."
    $parts = $Python -split ' '
    & $parts[0] $parts[1..($parts.Length - 1)] -m venv "$VenvDir"
    if ($LASTEXITCODE -ne 0) { Write-Error "venv creation failed"; exit 1 }
} else {
    Write-Host "Venv already exists."
}

# 3) Upgrade pip quietly, install edge-tts.
Write-Host "Installing edge-tts..."
& "$VenvPy" -m pip install --quiet --upgrade pip
& "$VenvPy" -m pip install --quiet edge-tts
if ($LASTEXITCODE -ne 0) { Write-Error "pip install failed"; exit 1 }

# 4) Smoke-test import.
& "$VenvPy" -c "import edge_tts; print('edge-tts OK')"
if ($LASTEXITCODE -ne 0) { Write-Error "Import check failed"; exit 1 }

Write-Host ""
Write-Host "Setup complete. You can now ask Claude to read Hebrew aloud."
