@echo off
REM Run in the foreground for local dev. Press this after editing .env to
REM reload it (close with Ctrl+C and run again). Reads config from this folder.
cd /d "%~dp0"
if not exist __EXE__ (
    echo __EXE__ not found -- running build.bat first ...
    call "%~dp0build.bat"
)
if not exist "%~dp0.env" (
    echo.
    echo WARNING: no .env in this folder -- the app may exit at startup.
    echo Copy .env.example to .env and fill it in.
    echo.
)
REM kill any prior instance so we don't collide on the port
taskkill /IM __EXE__ /F >nul 2>&1
echo Starting __EXE__ (Ctrl+C to stop) ...
__EXE__
pause
