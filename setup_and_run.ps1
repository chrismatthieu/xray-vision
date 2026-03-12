# X-Ray Vision demo: setup venv, install deps, run (Windows PowerShell)
# Run from project root: .\setup_and_run.ps1

$ErrorActionPreference = "Stop"
$projectRoot = $PSScriptRoot
Set-Location $projectRoot

# Find Python
$python = $null
foreach ($cmd in @("python", "py", "python3")) {
    try {
        $null = Get-Command $cmd -ErrorAction Stop
        $python = $cmd
        break
    } catch {}
}

if (-not $python) {
    Write-Host "Python not found. Install Python 3.10+ and add it to PATH." -ForegroundColor Red
    Write-Host "See SETUP_WINDOWS.md for steps (python.org or Microsoft Store)." -ForegroundColor Yellow
    exit 1
}

Write-Host "Using: $python" -ForegroundColor Green

# Create venv if missing
$venvPath = Join-Path $projectRoot ".venv"
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

if (-not (Test-Path $activateScript)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    & $python -m venv $venvPath
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

# Activate and run pip + demo in one process
Write-Host "Installing dependencies..." -ForegroundColor Cyan
& $venvPath\Scripts\python.exe -m pip install --quiet -r (Join-Path $projectRoot "requirements.txt")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Starting X-Ray Vision demo (press Q to quit)." -ForegroundColor Green
& $venvPath\Scripts\python.exe (Join-Path $projectRoot "run_demo.py") @args
exit $LASTEXITCODE
