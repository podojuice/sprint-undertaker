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


def exp_bar(exp: int, exp_to_next: int, width: int = 20) -> str:
    total = exp + exp_to_next
    filled = int(width * exp / total) if total > 0 else 0
    return "█" * filled + "░" * (width - filled)


def main() -> int:
    load_env_file()
    server_url = os.environ.get("SPRINT_UNDERTAKER_SERVER_URL")
    api_key = os.environ.get("SPRINT_UNDERTAKER_API_KEY")

    if not server_url or not api_key:
        print(f"Error: SPRINT_UNDERTAKER_SERVER_URL and SPRINT_UNDERTAKER_API_KEY must be set in {CONFIG_PATH}")
        return 1

    base_url = server_url.rstrip("/")
    headers = {"X-Api-Key": api_key, "X-Plugin-Version": PLUGIN_VERSION}

    req = request.Request(f"{base_url}/api/characters/status", headers=headers, method="GET")
    try:
        with request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
    except Exception as exc:
        print(f"Error: {exc}")
        return 1

    name = data["name"]
    char_class = data["character_class"]
    level = data["level"]
    exp = data["exp"]
    exp_to_next = data["exp_to_next_level"]
    title = data.get("title") or "(no title)"
    upgrade_notice = data.get("upgrade_notice")
    impl = data["impl"]
    stability = data["stability"]
    focus = data["focus"]

    bar = exp_bar(exp, exp_to_next)

    print()
    print(f"  {name}  [{title}]")
    print(f"  {char_class}  Lv.{level}")
    print(f"  EXP [{bar}] {exp} / {exp + exp_to_next}")
    print()
    print(f"  impl      {impl:>5}")
    print(f"  stability {stability:>5}")
    print(f"  focus     {focus:>5}")

    try:
        notif_req = request.Request(
            f"{base_url}/api/notifications/me", headers=headers, method="GET"
        )
        with request.urlopen(notif_req, timeout=5) as response:
            notif_data = json.loads(response.read().decode())

        items = notif_data.get("items", [])
        if items:
            print()
            print(f"  -- {len(items)} unread --")
            for item in items:
                print(f"  {item['message']}")

            read_req = request.Request(
                f"{base_url}/api/notifications/me/read", headers=headers, method="POST"
            )
            request.urlopen(read_req, timeout=5).close()
    except Exception:
        pass

    if upgrade_notice:
        print(f"  !! {upgrade_notice}")

    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
