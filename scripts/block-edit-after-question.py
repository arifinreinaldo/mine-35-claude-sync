#!/usr/bin/env python3
"""PreToolUse hook (Edit|Write|MultiEdit): block an edit when the assistant's
latest text asked a question and the user has not replied since.
Fails open: any error or unknown transcript shape allows the edit.
macOS only for now: on any other platform (Windows) it allows every edit."""
import json
import sys

if sys.platform != "darwin":
    sys.exit(0)


def text_of(content):
    if isinstance(content, str):
        return content
    return "".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")


def is_user_prompt(content):
    if isinstance(content, str):
        return bool(content.strip())
    return any(isinstance(b, dict) and b.get("type") == "text" and b.get("text", "").strip() for b in content)


def main():
    path = json.load(sys.stdin).get("transcript_path")
    if not path:
        return 0
    last_text = None  # latest assistant text with no real user prompt after it
    with open(path) as f:
        for line in f:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            msg = e.get("message") or {}
            content = msg.get("content")
            if content is None or e.get("isSidechain"):
                continue
            if e.get("type") == "user" and is_user_prompt(content):
                last_text = None
            elif e.get("type") == "assistant":
                t = text_of(content).strip()
                if t:
                    last_text = t
    if last_text and last_text.endswith("?"):
        sys.stderr.write("Blocked: you asked a question and have no answer yet. Stop and wait for the reply before editing.\n")
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
