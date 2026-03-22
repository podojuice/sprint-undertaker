---
name: titles
description: Show your Sprint Undertaker title collection — unlocked and locked titles
---

Run the following command:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/titles.py"
```

Then output the result as a code block in your response so the user can see it directly. Do not summarize or reformat the content.

If the command exits with an error about missing config, tell the user:

> Config not found. `/undertaker:login` 으로 로그인하거나 `/undertaker:register` 로 회원가입하세요.

If the command exits with a `401` or `Unauthorized` error, tell the user:

> 인증이 필요합니다. `/undertaker:login` 으로 로그인해주세요.
