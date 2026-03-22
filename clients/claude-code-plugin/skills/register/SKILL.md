---
name: register
description: Create a new Sprint Undertaker account — enter email, password, and character name to register and save credentials to config
---

Ask the user for:
1. **Email** — the email address for their new account
2. **Password** — their desired password (remind them it's only passed to a local script)
3. **Character name** — the in-game name for their character

**Step 1** — Send the verification code:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/register.py" --email "<EMAIL>" --password "<PASSWORD>" --character-name "<CHARACTER_NAME>"
```

Tell the user to check their email for a 6-digit verification code, then ask them to provide it.

**Step 2** — Verify and save credentials:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/register.py" --email "<EMAIL>" --password "<PASSWORD>" --character-name "<CHARACTER_NAME>" --code "<CODE>"
```

Display the script output exactly as returned.

If any command exits with an error:
- `409` / `Email already exists` → tell the user that email is already registered and suggest using `/undertaker:login` instead
- `400` / `Invalid or expired code` → ask the user to double-check the code
- `Error: ...` → show the error and suggest checking network connection
