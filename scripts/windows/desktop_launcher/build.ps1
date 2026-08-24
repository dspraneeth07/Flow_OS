#!/usr/bin/env pwsh
# Builds FlowOS.exe: a small Windows launcher that downloads an embeddable
# Python runtime and installs the `flowos` package on first run, then starts
# the server and opens the browser. See README.md in this directory.

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$projectRoot = Resolve-Path (Join-Path $scriptDir "..\..\..")
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    throw "Could not find $venvPython. Run this from a repo with an initialized .venv (make init)."
}

Write-Host "Ensuring PyInstaller is available..." -ForegroundColor Yellow
& $venvPython -m pip install --quiet --upgrade pyinstaller

Write-Host "Building FlowOS.exe..." -ForegroundColor Yellow
Set-Location $scriptDir
& $venvPython -m PyInstaller `
    --name FlowOS `
    --onefile `
    --windowed `
    --icon "$scriptDir\assets\icon.ico" `
    --add-data "$scriptDir\assets;assets" `
    --distpath "$scriptDir\dist" `
    --workpath "$scriptDir\build" `
    --specpath "$scriptDir\build" `
    "$scriptDir\launcher.py"

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller build failed."
}

Write-Host "`nBuilt: $scriptDir\dist\FlowOS.exe" -ForegroundColor Green
Write-Host "This exe is unsigned - Windows SmartScreen will warn first-time users (click 'More info' > 'Run anyway')." -ForegroundColor Cyan
