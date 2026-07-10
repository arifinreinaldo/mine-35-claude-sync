@echo off
REM restart-service.bat -- build the current source, then redeploy the service
REM in ONE step (replaces the two-step "build.bat then reinstall").
REM
REM Build runs FIRST, in your normal (non-elevated) context -- Go lives on the
REM user PATH, which an elevated Administrator shell often does NOT have, so we
REM must compile before elevating. install-service.bat then self-elevates and
REM does the admin part: remove old service -> install current build -> start.

cd /d "%~dp0"

REM --- build (mirror build.bat; if your build command differs, change it here too) ---
echo Building __EXE__ ...
go build -o __EXE__ .
if errorlevel 1 (
    echo.
    echo BUILD FAILED -- service left untouched.
    pause
    exit /b 1
)
echo Build OK.

REM --- reinstall: install-service.bat is self-cleaning (remove old + install
REM     current build + firewall + start) and self-elevates for the admin steps ---
echo Reinstalling __SERVICE__ with the new build ...
call "%~dp0install-service.bat"
