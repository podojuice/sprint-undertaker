---
name: profile
description: Look up another user's public Sprint Undertaker character profile
---

Ask the user for the nickname they want to look up:

> 조회할 닉네임을 입력해주세요.

Then run the following command with the nickname as argument:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/profile.py" "<nickname>"
```

Then output the result as a code block in your response so the user can see it directly. Do not summarize or reformat the content.

If the result says "Profile not found", tell the user:

> `<nickname>` 의 프로필을 찾을 수 없습니다. 닉네임을 확인하거나, 해당 유저가 프로필을 공개로 설정했는지 확인해주세요.
