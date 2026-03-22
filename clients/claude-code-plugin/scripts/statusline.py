#!/usr/bin/env python3
"""Sprint Undertaker Claude Code status line script.

Reads stdin (Claude Code session JSON) and outputs a status line.
Character data is read from a local cache updated by the hook.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

STATE_DIR = Path(
    os.environ.get("SPRINT_UNDERTAKER_CLAUDE_STATE_DIR", "~/.config/sprint-undertaker/claude-code-hook-state")
).expanduser()


def progress_bar(value: int, target: int, width: int = 10) -> str:
    filled = int(width * min(value, target) / target) if target > 0 else 0
    return "█" * filled + "░" * (width - filled)


def main() -> None:
    # consume stdin (required by Claude Code, contains session JSON)
    try:
        json.load(sys.stdin)
    except Exception:
        pass

    cache_path = STATE_DIR / "status-cache.json"
    if not cache_path.exists():
        return

    try:
        cache = json.loads(cache_path.read_text())
    except Exception:
        return

    level = cache.get("level")
    title = cache.get("title")
    project = cache.get("project")

    if level is None:
        return

    parts: list[str] = []

    char_part = f"Lv.{level}"
    if title:
        char_part += f"  {title}"
    parts.append(char_part)

    if project:
        if project.get("is_completed"):
            parts.append(f"{project['title']}  CLEARED")
        else:
            val = project["progress_value"]
            tgt = project["target_progress"]
            bar = progress_bar(val, tgt)
            parts.append(f"{project['title']}  {bar}  {val}/{tgt}")

    print("  ⚔  " + "   ·   ".join(parts))


if __name__ == "__main__":
    main()
