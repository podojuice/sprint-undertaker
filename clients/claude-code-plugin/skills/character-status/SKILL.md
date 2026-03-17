---
name: character-status
description: Show your Sprint Undertaker character status — level, stats, and active title
---

Run the following command and display the output exactly as returned. Do not summarize or reformat.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/status.py"
```

If the command exits with an error about missing config, tell the user:

> Config not found. Set `SPRINT_UNDERTAKER_SERVER_URL` and `SPRINT_UNDERTAKER_API_KEY` in `~/.config/sprint-undertaker/claude-code-hook.env`.
> Run the installer from your Sprint Undertaker app to create this file automatically.
