[CmdletBinding()]
param(
    [ValidateSet('run', 'test', 'demo')]
    [string]$Mode = 'run'
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$Python = Join-Path $Root '.venv\Scripts\python.exe'
$LockFile = Join-Path $Root 'requirements.lock'
$StampFile = Join-Path $Root '.venv\.requirements.lock.sha256'

if (-not (Test-Path $Python)) {
    if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
        throw 'Python Launcher (py) was not found. Install Python 3.11+ and try again.'
    }
    & py -3.11 -m venv (Join-Path $Root '.venv')
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$LockHash = (Get-FileHash -Path $LockFile -Algorithm SHA256).Hash
$InstallDependencies = (-not (Test-Path $StampFile)) -or ((Get-Content $StampFile -Raw).Trim() -ne $LockHash)
if ($InstallDependencies) {
    Write-Host 'Installing the pinned local dependencies...'
    & $Python -m pip install --disable-pip-version-check --requirement $LockFile
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Set-Content -Path $StampFile -Value $LockHash -NoNewline
}

switch ($Mode) {
    'run'   { & $Python -m app }
    'test'  { & $Python -m unittest discover -s tests -v }
    'demo'  { & $Python -m demo.redaction_demo }
}
exit $LASTEXITCODE
