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


def main() -> int:
    load_env_file()
    server_url = os.environ.get("SPRINT_UNDERTAKER_SERVER_URL")
    api_key = os.environ.get("SPRINT_UNDERTAKER_API_KEY")

    if not server_url or not api_key:
        print(f"Error: config not found at {CONFIG_PATH}")
        return 1

    base_url = server_url.rstrip("/")
    headers = {"X-Api-Key": api_key, "X-Plugin-Version": PLUGIN_VERSION}

    req = request.Request(f"{base_url}/api/characters/titles", headers=headers, method="GET")
    try:
        with request.urlopen(req, timeout=5) as response:
            titles = json.loads(response.read().decode())
    except Exception as exc:
        print(f"Error: {exc}")
        return 1

    unlocked = [t for t in titles if t["unlocked"]]
    locked = [t for t in titles if not t["unlocked"]]

    print()
    print(f"  Titles  {len(unlocked)} / {len(titles)}")
    print()

    if unlocked:
        print("  [Unlocked]")
        for t in unlocked:
            active_mark = " *" if t["status_label"] == "Active" else ""
            print(f"  {t['name']}{active_mark}")
            if t["description"]:
                print(f"    {t['description']}")
        print()

    if locked:
        print("  [Locked]")
        for t in locked:
            print(f"  ???  ({t['status_note']})")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
