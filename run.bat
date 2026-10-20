@echo off
setlocal
set "SCRIPT=%~dp0run.ps1"
if not exist "%SCRIPT%" (
  >&2 echo Could not find the ShieldBlur launcher: "%SCRIPT%"
  exit /b 1
)
set "POWERSHELL=powershell.exe"
where "%POWERSHELL%" >nul 2>&1
if errorlevel 1 set "POWERSHELL=pwsh.exe"
where "%POWERSHELL%" >nul 2>&1
if errorlevel 1 (
  >&2 echo PowerShell was not found. Install Windows PowerShell or PowerShell 7.
  exit /b 1
)
"%POWERSHELL%" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT%" %*
set "EXIT_CODE=%ERRORLEVEL%"
endlocal & exit /b %EXIT_CODE%
