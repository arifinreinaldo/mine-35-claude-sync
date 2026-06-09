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
        git -C $_DOTS pull --quiet origin main 2>$null
        Write-Host "[dotfiles] synced" -ForegroundColor Green
    }
    $_NOW | Set-Content $_STAMP
}

Remove-Variable _DOTS, _STAMP, _NOW, _LAST, _CHANGES -ErrorAction SilentlyContinue
