#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${IDLE_RPG_BIN_DIR:-$HOME/.local/bin}"
CONFIG_DIR="${IDLE_RPG_CONFIG_DIR:-$HOME/.config/idle-rpg}"
CONFIG_PATH="$CONFIG_DIR/codex-wrapper.env"
TARGET_BIN="$INSTALL_DIR/codex-rpg"

read_config_value() {
  local key="$1"
  python3 - "$CONFIG_PATH" "$key" <<'PY'
from pathlib import Path
import sys

config_path = Path(sys.argv[1])
key = sys.argv[2]
if not config_path.exists():
    raise SystemExit(0)
for line in config_path.read_text().splitlines():
    if line.startswith(f"{key}="):
        print(line.split("=", 1)[1])
        break
PY
}

mkdir -p "$INSTALL_DIR"
mkdir -p "$CONFIG_DIR"

EXISTING_REAL_BIN="$(read_config_value CODEX_REAL_BIN || true)"
CURRENT_CODEX_PATH="$(command -v codex || true)"

if [[ -n "$CURRENT_CODEX_PATH" && "$CURRENT_CODEX_PATH" != "$TARGET_BIN" ]]; then
  REAL_CODEX_PATH="$CURRENT_CODEX_PATH"
elif [[ -n "$EXISTING_REAL_BIN" && -x "$EXISTING_REAL_BIN" ]]; then
  REAL_CODEX_PATH="$EXISTING_REAL_BIN"
else
  echo "codex binary not found in PATH. Install Codex first, then rerun this installer." >&2
  echo "If codex-rpg is already installed, set CODEX_REAL_BIN manually in $CONFIG_PATH and rerun." >&2
  exit 1
fi

if [[ ! -f "$CONFIG_PATH" ]]; then
  cp "$SCRIPT_DIR/config.example" "$CONFIG_PATH"
fi

python3 - "$CONFIG_PATH" "$REAL_CODEX_PATH" <<'PY'
from pathlib import Path
import sys

config_path = Path(sys.argv[1])
real_bin = sys.argv[2]
lines = config_path.read_text().splitlines()
updated = []
found = False
for line in lines:
    if line.startswith("CODEX_REAL_BIN="):
        updated.append(f"CODEX_REAL_BIN={real_bin}")
        found = True
    else:
        updated.append(line)
if not found:
    updated.append(f"CODEX_REAL_BIN={real_bin}")
config_path.write_text("\n".join(updated) + "\n")
PY

ln -sf "$SCRIPT_DIR/dev-rpg-codex" "$TARGET_BIN"
chmod +x "$SCRIPT_DIR/dev-rpg-codex" "$SCRIPT_DIR/install.sh"

cat <<EOF
Codex wrapper installed.

Next steps:
1. Edit $CONFIG_PATH
2. Set IDLE_RPG_SERVER_URL and IDLE_RPG_API_KEY
3. Run the wrapper with: codex-rpg

Installed wrapper command:
  $TARGET_BIN

Recorded real codex binary:
  $REAL_CODEX_PATH
EOF
