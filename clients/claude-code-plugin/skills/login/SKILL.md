---
name: login
description: Login to Sprint Undertaker — enter email and password to get an API key saved to local config
---

Ask the user for:
1. **Email** — their Sprint Undertaker account email
2. **Password** — their password (remind them it's only passed to a local script)
3. **Server URL** — default `http://localhost:8000`, only ask if they want to use a different server

Then run the following command with the provided values:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/login.py" --email "<EMAIL>" --password "<PASSWORD>" --server-url "<SERVER_URL>"
```

Display the script output exactly as returned.

If the command exits with an error:
- `401` / `Invalid credentials` → tell the user their email or password is incorrect
- `Error: ...` → show the error and suggest checking the server URL or network connection
