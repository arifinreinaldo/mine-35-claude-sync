# Builds a single pasteable file containing this machine's whole Claude Code
# configuration, prefixed with an adversarial review prompt. Paste the result
# into a DIFFERENT model (ChatGPT / Gemini) — different architecture, different
# blind spots. Monthly cadence.
#
# ponytail: plain concat, overwrites in place. No dated copies, no templating.

$claude = Join-Path $HOME '.claude'
$out    = Join-Path $claude 'audit\config-bundle.md'
New-Item -ItemType Directory -Force (Split-Path $out) | Out-Null

function Get-Text($path) { if (Test-Path $path) { (Get-Content $path -Raw) } else { '' } }

$prompt = @'
# Critical review request

Below is the complete configuration of a personal AI coding agent (Claude Code):
global standing instructions, settings and hooks, safety rules, skill inventory,
and the persistent memory index.

You are a different model reviewing another model's setup. Say what is wrong,
not what is good. Assume the author is an experienced developer who wants the
holes found, not encouragement.

Answer in order, with specifics and references to the section/line:

1. What would this agent get wrong under time pressure, or when two instructions conflict?
2. Where does the decision authority matrix have gaps? Which actions have no stated gate or owner?
3. What behaviors are underspecified — where would two reasonable readings produce different actions?
4. Which rules contradict each other, and which are unfollowable as written?
5. What is dead weight — rules that never fire, or that only restate default model behavior?

No praise section. No closing summary. Ranked findings only, worst first.
'@

$skills = (Get-ChildItem (Join-Path $claude 'skills\*\SKILL.md') | ForEach-Object {
    # frontmatter only — full skill bodies would bloat the bundle past pasteable size
    $fm = (Get-Content $_ -Raw) -split '(?m)^---\s*$' | Select-Object -Index 1
    "### $($_.Directory.Name)`n$($fm.Trim())"
  }) -join "`n`n"

$hookify = (Get-ChildItem (Join-Path $claude 'hookify.*.md') | ForEach-Object {
    "### $($_.Name)`n$(Get-Content $_ -Raw)"
  }) -join "`n"

$memory = (Get-ChildItem (Join-Path $claude 'projects\*\memory\MEMORY.md') | ForEach-Object {
    Get-Content $_ -Raw
  }) -join "`n"

$sections = [ordered]@{
  'Global CLAUDE.md (standing instructions)' = Get-Text (Join-Path $claude 'CLAUDE.md')
  'settings.json (hooks, plugins, defaults)' = Get-Text (Join-Path $claude 'settings.json')
  'settings.local.json'                      = Get-Text (Join-Path $claude 'settings.local.json')
  'Safety rules (hookify)'                   = $hookify
  'API standard directive'                   = Get-Text (Join-Path $claude 'directives\api-standard.md')
  'Personal skill inventory (frontmatter)'   = $skills
  'Persistent memory index'                  = $memory
}

$fence = '```'
$sb = [System.Text.StringBuilder]::new()
[void]$sb.AppendLine($prompt)
foreach ($k in $sections.Keys) {
  $v = $sections[$k]
  if ([string]::IsNullOrWhiteSpace($v)) { Write-Warning "EMPTY section: $k"; $v = '(missing)' }
  [void]$sb.AppendLine("`n## $k`n")
  [void]$sb.AppendLine($fence)
  [void]$sb.AppendLine($v.Trim())
  [void]$sb.AppendLine($fence)
}
Set-Content -Path $out -Value $sb.ToString() -Encoding UTF8

# self-check: an empty or shrunken section is visible here, not discovered in the other model
"Wrote $out  ($((Get-Item $out).Length) bytes)"
$sections.Keys | ForEach-Object { "  {0,-42} {1,6} chars" -f $_, $sections[$_].Length }
