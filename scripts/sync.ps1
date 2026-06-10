# Dotfiles sync — sourced from PowerShell $PROFILE
# Checks every 3 hours; fetches first, only pulls when changes exist
$_DOTS  = "$env:USERPROFILE\dotfiles"
$_STAMP = "$_DOTS\.last-sync"
$_NOW   = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$_LAST  = if (Test-Path $_STAMP) { [long](Get-Content $_STAMP -Raw).Trim() } else { 0 }

if (($_NOW - $_LAST) -ge 10800) {
    git -C $_DOTS fetch --quiet origin main 2>$null
    $_CHANGES = git -C $_DOTS log HEAD..origin/main --oneline 2>$null
    if ($_CHANGES) {
        Write-Host "[dotfiles] update found, syncing..." -ForegroundColor Cyan
        $_FILES = git -C $_DOTS diff --name-only HEAD origin/main 2>$null
        $_DIRTY = git -C $_DOTS status --porcelain 2>$null
        if ($_DIRTY) {
            Write-Host "[dotfiles] WARNING: local uncommitted changes — pull may fail:" -ForegroundColor Yellow
            $_DIRTY | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
        }
        git -C $_DOTS pull --quiet origin main 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[dotfiles] PULL FAILED — resolve manually in $_DOTS" -ForegroundColor Red
        } else {
            if ($_FILES -match '^git/|bootstrap\.py') {
                Write-Host "[dotfiles] structural change — re-run: python $_DOTS\bootstrap.py" -ForegroundColor Yellow
            }
            if ($_FILES -match 'settings\.json') {
                Write-Host "[dotfiles] settings.json changed — restart Claude Code before using /model or /effort (stale sessions overwrite it)" -ForegroundColor Yellow
            }
            Write-Host "[dotfiles] synced" -ForegroundColor Green
        }
    }
    $_NOW | Set-Content $_STAMP
}

Remove-Variable _DOTS, _STAMP, _NOW, _LAST, _CHANGES, _FILES, _DIRTY -ErrorAction SilentlyContinue
