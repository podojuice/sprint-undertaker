"""Shared helpers for Sprint Undertaker CLI scripts."""

from __future__ import annotations

import json
import os
from pathlib import Path
from urllib import request
from urllib.error import HTTPError


CONFIG_PATH = Path(
    os.environ.get("SPRINT_UNDERTAKER_CLAUDE_CONFIG", "~/.config/sprint-undertaker/claude-code-hook.env")
).expanduser()

INSTALLATION_NAME = "claude-code"


def _read_plugin_version() -> str:
    plugin_json = Path(__file__).parent.parent / ".claude-plugin" / "plugin.json"
    try:
        return json.loads(plugin_json.read_text())["version"]
    except Exception:
        return "unknown"


PLUGIN_VERSION = _read_plugin_version()


def api_post(base_url: str, path: str, body: dict, *, auth_token: str | None = None) -> dict:
    data = json.dumps(body).encode()
    headers = {"Content-Type": "application/json", "X-Plugin-Version": PLUGIN_VERSION}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    req = request.Request(f"{base_url}{path}", data=data, headers=headers, method="POST")
    try:
        with request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as exc:
        body_text = exc.read().decode()
        try:
            detail = json.loads(body_text).get("detail", body_text)
        except Exception:
            detail = body_text
        raise SystemExit(f"Error {exc.code}: {detail}") from exc


def api_get(base_url: str, path: str, *, auth_token: str) -> dict | list:
    headers = {"Authorization": f"Bearer {auth_token}", "X-Plugin-Version": PLUGIN_VERSION}
    req = request.Request(f"{base_url}{path}", headers=headers, method="GET")
    try:
        with request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as exc:
        body_text = exc.read().decode()
        try:
            detail = json.loads(body_text).get("detail", body_text)
        except Exception:
            detail = body_text
        raise SystemExit(f"Error {exc.code}: {detail}") from exc


def write_config(server_url: str, api_key: str) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    managed_keys = {"SPRINT_UNDERTAKER_SERVER_URL", "SPRINT_UNDERTAKER_API_KEY"}
    existing_lines: list[str] = []
    if CONFIG_PATH.exists():
        for line in CONFIG_PATH.read_text().splitlines():
            key = line.split("=", 1)[0].strip()
            if key not in managed_keys:
                existing_lines.append(line)

    lines = [
        f"SPRINT_UNDERTAKER_SERVER_URL={server_url}",
        f"SPRINT_UNDERTAKER_API_KEY={api_key}",
        *existing_lines,
        "",
    ]
    CONFIG_PATH.write_text("\n".join(lines))


def ensure_installation(base_url: str, token: str) -> dict:
    """Return an active claude_code installation, creating one if needed."""
    installations = api_get(base_url, "/api/installations", auth_token=token)
    assert isinstance(installations, list)

    active = [i for i in installations if i["provider"] == "claude_code" and i["status"] == "active"]
    if active:
        print(f"Using existing installation: {active[0]['installation_name']}")
        return active[0]

    print(f"Creating new installation '{INSTALLATION_NAME}' ...")
    return api_post(
        base_url,
        "/api/installations",
        {"provider": "claude_code", "installation_name": INSTALLATION_NAME},
        auth_token=token,
    )


def save_and_print(base_url: str, token: str) -> None:
    installation = ensure_installation(base_url, token)
    api_key = installation["api_key"]
    write_config(base_url, api_key)
    print(f"Config saved to {CONFIG_PATH}")
    print(f"  Server : {base_url}")
    print(f"  API key: {api_key[:12]}...")
