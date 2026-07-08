@echo off
REM Stop and remove the __SERVICE__ Windows service. Leaves files and logs untouched.

REM --- self-elevate ---
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrator rights ...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"

set "SERVICE=__SERVICE__"
set "NSSM=%~dp0nssm.exe"
if not exist "%NSSM%" set "NSSM=nssm"

REM not installed? clean any stray firewall rule and stop -- don't print "Removed".
sc query "%SERVICE%" >nul 2>&1
if errorlevel 1 (
    echo %SERVICE% is not installed -- nothing to remove.
    netsh advfirewall firewall delete rule name="%SERVICE%" >nul 2>&1
    pause
    exit /b 0
)

"%NSSM%" stop "%SERVICE%" >nul 2>&1
REM let stop settle so remove isn't deferred ("marked for deletion")
ping -n 4 127.0.0.1 >nul
"%NSSM%" remove "%SERVICE%" confirm

REM confirm it's actually gone before claiming success
for /l %%i in (1,1,8) do (
    sc query "%SERVICE%" >nul 2>&1
    if errorlevel 1 goto :gone
    ping -n 2 127.0.0.1 >nul
)
echo WARNING: %SERVICE% still registered ^(marked for deletion; close services.msc / reboot to finish^).
goto :fw
:gone
echo Removed %SERVICE% ^(files and logs kept^).
:fw
netsh advfirewall firewall delete rule name="%SERVICE%" >nul 2>&1
pause
