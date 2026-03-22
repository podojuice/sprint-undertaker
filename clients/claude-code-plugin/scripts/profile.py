#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib import request
from urllib.error import HTTPError

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

    if not server_url:
        print("Error: config not found")
        return 1

    if len(sys.argv) < 2 or not sys.argv[1].strip():
        print("Usage: profile.py <nickname>")
        return 1

    nickname = sys.argv[1].strip()
    base_url = server_url.rstrip("/")
    url = f"{base_url}/api/characters/profile/{nickname}"
    headers = {"X-Plugin-Version": PLUGIN_VERSION}

    req = request.Request(url, headers=headers, method="GET")
    try:
        with request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
    except HTTPError as exc:
        if exc.code == 404:
            print()
            print(f"  Profile not found: {nickname}")
            print()
            return 0
        print(f"Error: HTTP {exc.code}")
        return 1
    except Exception as exc:
        print(f"Error: {exc}")
        return 1

    title_str = f"  [{data['title']}]" if data.get("title") else ""
    exp = data["exp"]
    exp_to_next = data["exp_to_next_level"]
    exp_total = exp + exp_to_next
    bar = progress_bar(exp, exp_total)

    print()
    print(f"  {data['name']}{title_str}")
    print(f"  {data['character_class']}  Lv.{data['level']}")
    print(f"  EXP [{bar}] {exp} / {exp_total}")
    print()
    print(f"  impl       {data['impl']}")
    print(f"  stability  {data['stability']}")
    print(f"  focus      {data['focus']}")

    titles = data.get("titles", [])
    if titles:
        print()
        print(f"  Titles ({len(titles)})")
        pairs = [titles[i:i+2] for i in range(0, len(titles), 2)]
        for pair in pairs:
            line = "  " + "  ·  ".join(f"✦ {t}" for t in pair)
            print(line)

    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
