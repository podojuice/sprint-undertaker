#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib import request

sys.path.insert(0, str(Path(__file__).parent))
from _su_lib import PLUGIN_VERSION

CONFIG_PATH = Path(
    os.environ.get("SPRINT_UNDERTAKER_CLAUDE_CONFIG", "~/.config/sprint-undertaker/claude-code-hook.env")
).expanduser()


def load_env_file() -> None:
    if not CONFIG_PATH.exists():
        return
    for raw_line in CONFIG_PATH.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key, value)


def progress_bar(value: int, target: int, width: int = 20) -> str:
    filled = int(width * min(value, target) / target) if target > 0 else 0
    return "█" * filled + "░" * (width - filled)


def main() -> int:
    load_env_file()
    server_url = os.environ.get("SPRINT_UNDERTAKER_SERVER_URL")
    api_key = os.environ.get("SPRINT_UNDERTAKER_API_KEY")

    if not server_url or not api_key:
        print(f"Error: config not found at {CONFIG_PATH}")
        return 1

    base_url = server_url.rstrip("/")
    headers = {"X-Api-Key": api_key, "X-Plugin-Version": PLUGIN_VERSION}

    req = request.Request(f"{base_url}/api/characters/weekly-project", headers=headers, method="GET")
    try:
        with request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
    except Exception as exc:
        print(f"Error: {exc}")
        return 1

    if data is None:
        print()
        print("  No active weekly project.")
        print()
        return 0

    title = data["project_title"]
    description = data["description"]
    value = data["progress_value"]
    target = data["target_progress"]
    is_completed = data["is_completed"]
    ends_at = data["ends_at"][:10]

    bar = progress_bar(value, target)
    status = "CLEARED" if is_completed else f"{value} / {target}"

    print()
    print(f"  {title}")
    print(f"  {description}")
    print()
    print(f"  [{bar}] {status}")
    print(f"  Ends: {ends_at}")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
