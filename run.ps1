[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet('run', 'test', 'demo')]
    [string]$Mode = 'run'
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$PinFile = Join-Path $Root '.python-version'
$RequiredVersion = '3.11.2'
if (-not (Test-Path -LiteralPath $PinFile -PathType Leaf)) {
    throw "Missing pinned Python version file: $PinFile"
}
$PinnedVersion = (Get-Content -LiteralPath $PinFile -Raw).Trim()
if ($PinnedVersion -ne $RequiredVersion) {
    throw "This project requires the pinned Python $RequiredVersion runtime; found pin in $PinFile`: $PinnedVersion"
}
if ($PinnedVersion -notmatch '^(?<Major>\d+)\.(?<Minor>\d+)\.(?<Patch>\d+)$') {
    throw "Invalid Python version pin in $PinFile`: $PinnedVersion"
}
$PythonMajor = [int]$Matches.Major
$PythonMinor = [int]$Matches.Minor
$PythonPatch = [int]$Matches.Patch
$VersionCheck = 'import sys; expected=tuple(int(value) for value in sys.argv[1:4]); actual=sys.version_info[:3]; sys.exit("expected Python %s.%s.%s, found %s.%s.%s" % (*expected, *actual)) if actual != expected else None'

$Python = Join-Path $Root '.venv\Scripts\python.exe'
$Venv = Join-Path $Root '.venv'
$LockFile = Join-Path $Root 'requirements.lock'
$StampFile = Join-Path $Root '.venv\.requirements.lock.sha256'

function Assert-PythonVersion {
    param(
        [Parameter(Mandatory = $true)][string]$Interpreter,
        [string[]]$PrefixArguments = @()
    )

    & $Interpreter @PrefixArguments -c $VersionCheck $PythonMajor $PythonMinor $PythonPatch
    if ($LASTEXITCODE -ne 0) {
        throw "Python $PinnedVersion is required; refusing to use an arbitrary interpreter."
    }
}

if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    if (Test-Path -LiteralPath $Venv) {
        throw "The project virtual environment is incomplete: $Python. Remove .venv and rerun this launcher to recreate it with Python $PinnedVersion."
    }
    $PythonLauncher = Get-Command py -ErrorAction SilentlyContinue
    if (-not $PythonLauncher) {
        throw "Python $PinnedVersion is required, but the Python Launcher (py) was not found. Install that runtime and try again."
    }
    $PythonSelector = "-$PythonMajor.$PythonMinor"
    Assert-PythonVersion -Interpreter $PythonLauncher.Source -PrefixArguments @($PythonSelector)
    & $PythonLauncher.Source $PythonSelector -m venv $Venv
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
Assert-PythonVersion -Interpreter $Python

if (-not (Test-Path -LiteralPath $LockFile -PathType Leaf)) {
    throw "Missing dependency lockfile: $LockFile"
}
$LockHash = (Get-FileHash -LiteralPath $LockFile -Algorithm SHA256).Hash.ToLowerInvariant()
$InstallDependencies = (-not (Test-Path -LiteralPath $StampFile)) -or ((Get-Content -LiteralPath $StampFile -Raw).Trim() -ne $LockHash)
if ($InstallDependencies) {
    Write-Host 'Installing the pinned local dependencies...'
    & $Python -m pip install --disable-pip-version-check --requirement $LockFile
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Set-Content -LiteralPath $StampFile -Value $LockHash -NoNewline -Encoding ascii
}

$ExitCode = 0
if ($Mode -eq 'test' -and [string]::IsNullOrEmpty($env:QT_QPA_PLATFORM)) {
    $env:QT_QPA_PLATFORM = 'offscreen'
}
switch ($Mode) {
    'run'   { & $Python -m app; $ExitCode = $LASTEXITCODE }
    'test'  { & $Python -m unittest discover -s tests -v; $ExitCode = $LASTEXITCODE }
    'demo'  { & $Python -m demo.redaction_demo; $ExitCode = $LASTEXITCODE }
}
exit $ExitCode
