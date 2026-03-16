---
name: rpg-status
description: Show your Idle RPG character status — level, stats, and active title
---

Run the following command and display the output exactly as returned. Do not summarize or reformat.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/rpg_status.py"
```

If the command exits with an error about missing config, tell the user:

> Config not found. Set `IDLE_RPG_SERVER_URL` and `IDLE_RPG_API_KEY` in `~/.config/idle-rpg/claude-code-hook.env`.
> Run the installer from your Idle RPG app to create this file automatically.
