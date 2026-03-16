# Claude Code Hook

`UserPromptSubmit -> Stop` turn 단위로 Claude Code 활동을 집계해서 Idle RPG 서버의 `/api/events`로 전송하는 hook collector입니다.

## What it does

- `SessionStart`에서 모델 정보를 기록
- `UserPromptSubmit`에서 새 turn을 시작
- `PostToolUse` / `PostToolUseFailure`에서 privacy-safe 카운터만 집계
- `Stop`에서 `turn_completed` summary를 전송

## Privacy

서버로 전송하지 않는 것:

- prompt 원문
- command 원문
- file path 원문
- 응답 원문

서버로 전송하는 것:

- prompt count
- prompt length bucket
- edit success count
- validation success/failure count
- tool failure count
- model name

## Installation

1. 앱에서 `claude_code` installation을 생성한다.
2. `/app` 또는 `/install/claude-code`의 installer command를 한 번 실행한다.
3. 표시된 Claude hook settings snippet을 `~/.claude/settings.json` 또는 `.claude/settings.local.json`에 추가한다.

## Notes

- `Stop`이 오면 turn summary를 전송하고 로컬 turn 상태를 비운다.
- `Stop`이 누락되면 다음 prompt 시작 시 이전 turn 상태를 폐기하고 새 turn을 시작한다.
- 검증성 `Bash` 판정은 로컬에서만 수행되며 원문 command는 저장하거나 전송하지 않는다.
