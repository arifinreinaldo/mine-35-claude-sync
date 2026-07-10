@echo off
REM restart-service.bat -- redeploy __SERVICE__ in ONE step (uninstall+install).
REM install-service.bat is self-cleaning: it stops and removes any existing
REM service, waits for it to clear, then installs the CURRENT build fresh,
REM re-adds the firewall rule, and starts it. So "restart" = run install once.
REM Typical flow after changing code:  build.bat  ->  restart-service.bat

REM --- self-elevate once, so install-service.bat runs inline (single UAC prompt) ---
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrator rights ...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo Restarting __SERVICE__ (remove old + install current build) ...
call "%~dp0install-service.bat"
