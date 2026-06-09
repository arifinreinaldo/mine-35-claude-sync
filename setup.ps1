# Bootstrap script for Windows
# Requires: Developer Mode enabled (Settings > System > For Developers)
# Run from: anywhere

$DOTFILES = "$env:USERPROFILE\dotfiles"
$REPO = "https://github.com/arifinreinaldo/mine-35-claude-sync.git"

# Clone if not already present
if (-not (Test-Path $DOTFILES)) {
    git clone $REPO $DOTFILES
}

function New-Link {
    param($Path, $Target)
    if (Test-Path $Path) {
        $item = Get-Item $Path -ErrorAction SilentlyContinue
        if ($item.LinkType -eq "SymbolicLink") {
            Write-Host "SKIP (already linked): $Path"
            return
        }
        Write-Host "BACKUP: $Path -> $Path.bak"
        Move-Item $Path "$Path.bak" -Force
    }
    New-Item -ItemType SymbolicLink -Path $Path -Target $Target | Out-Null
    Write-Host "LINKED: $Path -> $Target"
}

# Claude Code
New-Link "$env:USERPROFILE\.claude\CLAUDE.md"     "$DOTFILES\claude\CLAUDE.md"
New-Link "$env:USERPROFILE\.claude\settings.json" "$DOTFILES\claude\settings.json"
New-Link "$env:USERPROFILE\.claude\skills"        "$DOTFILES\claude\skills"

# Git
New-Link "$env:USERPROFILE\.gitconfig"            "$DOTFILES\git\.gitconfig"

Write-Host "`nDone. All dotfiles linked."
