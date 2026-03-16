# Codex Wrapper

`codex-rpg` 실행 전후 메타데이터를 수집해서 Idle RPG 서버의 `/api/events`로 전송하는 wrapper입니다.

## What it does

- `session_started` 전송
- 실제 `codex` 실행
- 가능한 경우 git worktree delta 기반 `code_applied` 전송
- 종료 코드와 실행 시간 기반 `command_finished` 전송
- 세션 종료 시 `session_ended` 전송

코드 본문이나 프롬프트 내용은 보내지 않습니다.

## Install

먼저 서버에서 installation을 하나 생성해서 API key를 발급받습니다.

```bash
curl -X POST http://localhost:8000/api/installations \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{"provider":"codex","installation_name":"local-codex"}'
```

그 다음 설치합니다.

```bash
./clients/codex-wrapper/install.sh
```

이 스크립트는 멱등하게 동작하도록 작성되어 있어서, 같은 명령을 여러 번 실행해도 `codex-rpg`와 config를 다시 맞춰줍니다.

설치 후 아래 파일을 수정합니다.

`~/.config/idle-rpg/codex-wrapper.env`

```bash
IDLE_RPG_SERVER_URL=http://localhost:8000
IDLE_RPG_API_KEY=rpg_sk_...
IDLE_RPG_INSTALLATION_NAME=local-codex
CODEX_REAL_BIN=/absolute/path/to/real/codex
```

## PATH

설치 후에는 아래 명령으로 wrapper를 사용합니다.

```bash
codex-rpg
```

기존 `codex` 명령은 건드리지 않습니다.

## Collected metadata

- session start time
- session end time
- duration
- command success or failure
- exit code
- best-effort code change volume from git worktree delta
- provider name
- project hash derived from the current working directory

## Notes

- `code_applied`는 git 저장소 안에서만 best-effort로 계산됩니다. 기존 dirty worktree가 있으면 완전히 정확하지 않을 수 있습니다.
- codex 내부 토큰 사용량이나 세부 tool trace는 아직 수집하지 않습니다.
- `tool_used`, `token_reported`, `test_result`는 현재 Codex wrapper에서 자동 수집하지 않습니다.
- 코드 본문, 프롬프트 원문, 응답 원문, 파일 경로 원문은 저장하지 않습니다.
