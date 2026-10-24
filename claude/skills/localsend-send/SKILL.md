---
name: localsend-send
description: Send files from this Mac to a device running LocalSend (phone, laptop) on the same Wi-Fi. Use when the user says "send file to my device/phone", "localsend", or "send this apk to wise banana".
---

# localsend-send

Script: `~/.claude/skills/localsend-send/send.py` (stdlib Python 3, LocalSend protocol v2).

1. `python3 ~/.claude/skills/localsend-send/send.py list` — prints `alias<TAB>ip` per device found.
2. `python3 ~/.claude/skills/localsend-send/send.py send "<alias>" <file>...` — alias is a case-insensitive substring.

Rules:
- The receiver must tap Accept; the script waits up to 120 s.
- Several devices or no alias given: run `list`, ask which one.
- File path unclear: ask. Do not search the disk.
- Empty `list`: LocalSend closed on the target, different Wi-Fi, or client isolation. Say so.
- Scans the Mac's /24 subnet only.
