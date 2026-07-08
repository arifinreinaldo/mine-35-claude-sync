@echo off
REM Rebuild the service binary. Only needed when .go source changes
REM (NOT for .env edits -- those load at runtime). If the app uses go:embed
REM for templates/static, the .exe is fully self-contained.
cd /d "%~dp0"
echo Building __EXE__ ...
go build -o __EXE__ .
if errorlevel 1 (
    echo.
    echo BUILD FAILED
    pause
    exit /b 1
)
echo.
echo Build OK -^> __EXE__
pause
