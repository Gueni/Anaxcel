# Full build of Anaxcel: venv -> deps -> sample data -> tests -> PyInstaller -> Inno Setup installer.
# Usage:  powershell -ExecutionPolicy Bypass -File build.ps1 [-SkipTests]
param([switch]$SkipTests)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$py = ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    Write-Host "==> Creating virtual environment"
    py -m venv .venv
    if ($LASTEXITCODE) { throw "venv creation failed" }
}
Write-Host "==> Installing dependencies"
& $py -m pip install --quiet --upgrade pip
& $py -m pip install --quiet -r requirements-dev.txt
if ($LASTEXITCODE) { throw "pip install failed" }

$version = (& $py -c "from lib.core import __version__; print(__version__)").Trim()
Write-Host "==> Anaxcel $version"

Write-Host "==> Generating sample data"
& $py tools\make_sample_data.py
if (-not $SkipTests) {
    Write-Host "==> Running tests"
    & $py -m pytest -q
    if ($LASTEXITCODE) { throw "tests failed" }
}

Write-Host "==> Building executable"
& $py -m PyInstaller anaxcel.spec --noconfirm --clean
if ($LASTEXITCODE) { throw "PyInstaller failed" }

$iscc = @("$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe",
          "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
          "$env:ProgramFiles\Inno Setup 6\ISCC.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $iscc) {
    Write-Warning "Inno Setup 6 not found (winget install JRSoftware.InnoSetup). Portable build is in dist\Anaxcel."
    exit 0
}
Write-Host "==> Building installer"
& $iscc /Q "/DAppVersion=$version" installer\anaxcel.iss
if ($LASTEXITCODE) { throw "Inno Setup failed" }
Write-Host "==> Done: dist\Anaxcel-$version-Setup.exe"
