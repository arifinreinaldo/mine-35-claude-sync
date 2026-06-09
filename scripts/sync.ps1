# Dotfiles daily sync — sourced from PowerShell $PROFILE
$_DOTFILES = "$env:USERPROFILE\dotfiles"
$_STAMP    = "$_DOTFILES\.last-sync"
$_TODAY    = (Get-Date).ToString("yyyy-MM-dd")

if (-not (Test-Path $_STAMP) -or (Get-Content $_STAMP -Raw).Trim() -ne $_TODAY) {
    Write-Host "[dotfiles] syncing..." -ForegroundColor Cyan
    $result = git -C $_DOTFILES pull --quiet origin main 2>&1
    if ($LASTEXITCODE -eq 0) {
        $_TODAY | Set-Content $_STAMP
        Write-Host "[dotfiles] synced" -ForegroundColor Green
    } else {
        Write-Host "[dotfiles] sync failed (offline?)" -ForegroundColor Yellow
    }
}

Remove-Variable _DOTFILES, _STAMP, _TODAY -ErrorAction SilentlyContinue
