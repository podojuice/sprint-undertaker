from pathlib import Path

from fastapi import APIRouter, Query, Request
from fastapi.responses import PlainTextResponse

CLIENTS_DIR = Path(__file__).resolve().parent.parent / "clients" / "claude-code-hook"

router = APIRouter(include_in_schema=False)


def _read_client_file(name: str) -> str:
    return (CLIENTS_DIR / name).read_text()


@router.get("/install/claude-code.sh", response_class=PlainTextResponse)
async def claude_code_installer_script(
    request: Request,
    api_key: str | None = Query(default=None),
    installation_name: str = Query(default="local-claude"),
) -> PlainTextResponse:
    server_url = str(request.base_url).rstrip("/")
    hook_script = _read_client_file("idle_rpg_claude_hook.py")
    api_key_value = api_key or "rpg_sk_replace_me"

    script = f"""#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="${{IDLE_RPG_CONFIG_DIR:-$HOME/.config/idle-rpg}}"
HOOK_PATH="$CONFIG_DIR/claude-code-hook.py"
CONFIG_PATH="$CONFIG_DIR/claude-code-hook.env"
SERVER_URL="{server_url}"
API_KEY_VALUE="{api_key_value}"
INSTALLATION_NAME_VALUE="{installation_name}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required to run the Claude Code hook collector." >&2
  echo "Install Python 3 first, then rerun this installer." >&2
  exit 1
fi

mkdir -p "$CONFIG_DIR"

cat > "$HOOK_PATH" <<'EOF_HOOK'
{hook_script}
EOF_HOOK
chmod +x "$HOOK_PATH"

cat > "$CONFIG_PATH" <<EOF_CONFIG
IDLE_RPG_SERVER_URL=$SERVER_URL
IDLE_RPG_API_KEY=$API_KEY_VALUE
IDLE_RPG_INSTALLATION_NAME=$INSTALLATION_NAME_VALUE
EOF_CONFIG

cat <<EOF_DONE
Idle RPG Claude Code hook installed.

Hook script:
  $HOOK_PATH

Config file:
  $CONFIG_PATH

Next step:
  Add the Claude hook settings snippet from /app or /install/claude-code to your Claude settings file.
EOF_DONE
"""
    return PlainTextResponse(script)
