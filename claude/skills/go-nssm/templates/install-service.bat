@echo off
REM Install __EXE__ as an auto-start, auto-restart Windows service via NSSM.
REM Run from the app folder (this .bat, __EXE__, nssm.exe, .env live together).
REM Re-running is safe: it removes the old service, waits for it to clear, then reinstalls.

REM --- self-elevate (NSSM needs admin) ---
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrator rights ...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"

REM app dir WITHOUT trailing backslash -- a trailing \ before a closing quote
REM escapes the quote, so nssm stores a bad path and the service won't start.
set "APPDIR=%~dp0"
if "%APPDIR:~-1%"=="\" set "APPDIR=%APPDIR:~0,-1%"

set "SERVICE=__SERVICE__"
set "EXE=%APPDIR%\__EXE__"

REM === PORT (firewall rule only) =========================================
REM This fallback ALWAYS stays -- every variant below only overrides it when
REM it successfully reads a port, so a missing/empty .env safely keeps 8080.
set "PORT=8080"
REM
REM Pick ONE variant. Default (kept below) reads LISTEN_ADDR=":8080" or
REM "host:8080" from .env. To switch, delete the marked default block and
REM paste the alternative in its place (the "set PORT=8080" line stays).
REM   ALT A -- app uses a PORT= key in .env (e.g. PORT=9100):
REM     REM  /c: is REQUIRED: without it findstr treats the space as an OR
REM     REM  separator and splits the pattern, matching any PORT*-prefixed key.
REM     if exist "%APPDIR%\.env" for /f "tokens=2 delims==:" %%a in ('findstr /b /i /r /c:"^PORT *[=:]" "%APPDIR%\.env"') do set "PORT=%%a"
REM     set "PORT=%PORT: =%"
REM   ALT B -- fixed port: nothing to add, the set "PORT=8080" above is it.
REM   ALT C -- app is not a listener: delete this whole block AND the two
REM            netsh firewall lines further down.
REM
REM >>> default variant (LISTEN_ADDR) -- delete these 3 lines to switch variant
set "LISTEN="
if exist "%APPDIR%\.env" for /f "tokens=2 delims==" %%a in ('findstr /b /i /c:"LISTEN_ADDR" "%APPDIR%\.env"') do set "LISTEN=%%a"
set "LISTEN=%LISTEN: =%"
if defined LISTEN for /f "tokens=2 delims=:" %%b in ("x%LISTEN%") do set "PORT=%%b"
REM <<< end default variant. The "x" prefix keeps a leading-colon value
REM     (":8080") from collapsing to token 1.
REM =======================================================================

REM --- locate nssm: vendored next to this .bat, else on PATH ---
REM (don't probe with `nssm version` -- it exits 1 even when working)
set "NSSM=%APPDIR%\nssm.exe"
if not exist "%NSSM%" (
    where nssm >nul 2>&1
    if errorlevel 1 (
        echo nssm.exe not found next to this .bat or on PATH.
        pause
        exit /b 1
    )
    set "NSSM=nssm"
)
if not exist "%EXE%" (
    echo __EXE__ not found -- run build.bat first.
    pause
    exit /b 1
)
if not exist "%APPDIR%\.env" (
    echo.
    echo WARNING: no .env in this folder -- the service may crash-loop at startup.
    echo Create it before the service can run. Continuing with install anyway ...
    echo.
)

if not exist "%APPDIR%\logs" mkdir "%APPDIR%\logs"

REM --- remove any prior install, then WAIT until it's fully gone ---
REM (an immediate reinstall can hit ERROR_SERVICE_MARKED_FOR_DELETE 1072)
"%NSSM%" stop "%SERVICE%" >nul 2>&1
"%NSSM%" remove "%SERVICE%" confirm >nul 2>&1
for /l %%i in (1,1,15) do (
    sc query "%SERVICE%" >nul 2>&1
    if errorlevel 1 goto :removed
    ping -n 2 127.0.0.1 >nul
)
:removed

REM --- install ---
"%NSSM%" install "%SERVICE%" "%EXE%" || (
    echo install failed -- service may be marked for deletion; close services.msc and retry.
    pause
    exit /b 1
)
"%NSSM%" set "%SERVICE%" AppDirectory "%APPDIR%"
"%NSSM%" set "%SERVICE%" Start SERVICE_AUTO_START
"%NSSM%" set "%SERVICE%" AppExit Default Restart
"%NSSM%" set "%SERVICE%" AppThrottle 5000
"%NSSM%" set "%SERVICE%" AppStdout "%APPDIR%\logs\out.log"
"%NSSM%" set "%SERVICE%" AppStderr "%APPDIR%\logs\err.log"
"%NSSM%" set "%SERVICE%" AppRotateFiles 1
"%NSSM%" set "%SERVICE%" AppRotateOnline 1
"%NSSM%" set "%SERVICE%" AppRotateBytes 10485760

REM --- firewall: rule named by SERVICE (not port) so re-runs / port changes
REM don't leave orphaned rules, and uninstall can always find it to delete ---
netsh advfirewall firewall delete rule name="%SERVICE%" >nul 2>&1
netsh advfirewall firewall add rule name="%SERVICE%" dir=in action=allow protocol=TCP localport=%PORT% >nul 2>&1

REM --- start: sc start is non-blocking and quiet. `nssm start` prints a scary
REM "Unexpected status SERVICE_START_PENDING" while the app is merely still
REM coming up (throttle window + any startup checks before it listens) ---
sc start "%SERVICE%" >nul 2>&1

echo.
echo Waiting for %SERVICE% to reach RUNNING ...
REM ponytail: assumes English Windows (sc prints "RUNNING"); a localized SKU
REM would need the numeric state code (4). Upgrade there if you localize.
for /l %%i in (1,1,20) do (
    sc query "%SERVICE%" | findstr /c:"RUNNING" >nul
    if not errorlevel 1 goto :running
    ping -n 3 127.0.0.1 >nul
)
echo WARNING: %SERVICE% has not reached RUNNING -- check %APPDIR%\logs\err.log
echo (most common cause: missing/incorrect .env, or a dependency unreachable.)
goto :report
:running
echo %SERVICE% is RUNNING.
:report
echo Logs: %APPDIR%\logs  ^|  Port: %PORT%
pause
