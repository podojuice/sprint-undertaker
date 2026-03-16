# Idle RPG Product Document

## One-line Summary

개발자의 AI 코딩 활동을 자동 수집해 캐릭터 성장으로 바꾸는 RPG 서비스. 현재 MVP는 Claude Code hooks-first로 진행한다.

## Product Goal

- AI 도구 사용 로그를 "대시보드 데이터"가 아니라 "RPG 성장 재료"로 해석한다.
- 유저는 메타데이터보다 캐릭터 레벨, 스탯, 칭호를 먼저 체감한다.
- MVP 이후 Cursor 같은 다른 provider로 확장 가능한 구조를 남긴다.

## Core Principles

- Game-first: 내부는 메타데이터 파이프라인이지만, 전면 경험은 RPG여야 한다.
- Privacy-first: 코드 본문, 프롬프트 원문, 응답 원문, command 원문, file path는 저장하거나 전송하지 않는다.
- Turn-first: 성장 단위는 세션이 아니라 `UserPromptSubmit -> Stop` 사이의 turn이다.
- Server-scored: 클라이언트는 원문을 전송하지 않고, 서버가 최종 해석과 보상을 담당한다.
- Expandable: 이후 칭호, 조직, 장비, 레이드로 확장 가능한 성장 축을 유지한다.

## MVP Scope

포함:

- FastAPI monolith
- PostgreSQL
- JWT 기반 웹 인증
- installation 단위 API key 발급
- Claude Code hook 기반 canonical event ingestion
- 캐릭터 경험치/스탯 성장
- 칭호 지급 및 노출
- 주간 프로젝트 progress 프로토타입
- 조직 생성/가입/멤버 조회
- 간단한 웹 앱

제외:

- 장비 시스템 실구현
- 레이드 실구현
- OAuth
- Cursor 연동
- 고급 분석 대시보드
- Codex wrapper 고도화

## Core User Flow

1. 유저가 회원가입하면 캐릭터가 생성된다.
2. 웹에서 installation을 만들고 API key를 발급받는다.
3. Claude Code hook를 설치한다.
4. 유저가 프롬프트를 제출하면 하나의 turn이 시작된다.
5. turn 안의 tool 활동이 로컬에서 privacy-safe하게 집계된다.
6. `Stop` 시점에 turn summary가 서버로 전송된다.
7. 서버가 경험치, 스탯, 칭호를 계산한다.
8. active 주간 프로젝트가 있으면 turn progress가 누적된다.
9. 유저는 `/app`에서 캐릭터와 성장 로그를 확인한다.

## Domain Model

### User / Character

- 유저 1명당 캐릭터 1개
- 캐릭터는 `level`, `exp`, `title`과 핵심 스탯을 가진다
- MVP 핵심 스탯: `impl`, `stability`, `focus`

### Provider Installation

- installation 단위로 provider, 이름, API key를 가진다
- 한 유저가 여러 installation을 가질 수 있다
- 운영상 사용자 단위 key보다 installation 단위 key가 추적과 회전에 유리하다

### Activity Event

- provider별 원본 활동을 canonical event로 저장한다
- 현재 MVP의 의미 있는 작업 단위는 turn이다
- turn은 `UserPromptSubmit -> Stop`
- 현재 Claude MVP에서 다루는 canonical event subset:
  - `turn_started`
  - `tool_result`
  - `validation_result`
  - `turn_completed`

### Titles

- 초기 성장 체감을 만드는 주요 보상 축
- 공개 칭호와 숨김 칭호를 모두 지원한다
- 필요 시 기간 한정 칭호도 지원한다
- 레벨 달성 칭호와 주간 프로젝트 클리어 칭호를 모두 보상 축으로 사용한다

### Weekly Projects

- MVP에서는 개인 progress 기반 주간 프로젝트를 지원한다
- turn 종료 시 project progress가 누적된다
- 목표 progress를 달성하면 프로젝트 클리어와 고유 칭호 지급이 발생한다
- UI 표현은 나중에 보스/레이드 느낌으로 강화할 수 있다

### Organization

- 길드 시스템의 시작점
- MVP에서는 생성, 가입, 멤버 조회까지만 지원한다
- 이후 레이드와 시즌 경쟁의 기본 단위가 된다

## Privacy Rules

절대 수집/전송하지 않는 것:

- 코드 본문
- 프롬프트 원문
- 응답 원문
- command 원문
- 파일/디렉토리 path 원문
- 검색어/URL 원문

수집 가능한 것:

- tool 종류
- 성공/실패 여부
- prompt count
- prompt length bucket
- edit 성공 횟수
- validation 성공/실패 횟수
- tool failure 횟수
- 모델 이름

## Growth Rules

- turn 안의 `Edit` / `Write` / `MultiEdit` / `Task` 성공 -> `impl` + EXP
- turn 안의 검증성 `Bash` 성공 -> `stability` + EXP
- turn 안의 prompt 수, prompt 길이 bucket -> `focus` 보조 지표
- 실패 후 같은 turn 안에서 작업이 정상 완료되면 `stability` 보조 보상 가능
- active 주간 프로젝트가 있으면 turn마다 별도 project progress를 누적한다

레벨업 기준:

- `required_exp = 100 * level^1.5`

## MVP Metrics Draft

turn summary에서 서버로 보내는 초안 메트릭:

- `prompt_count`
- `prompt_length_bucket`
- `edit_success_count`
- `validation_success_count`
- `validation_failure_count`
- `tool_failure_count`
- `model_name`

MVP 1차 원칙:

- `best-effort` 메트릭은 사용하지 않는다
- `turn_duration_bucket`, `write_success_count`, `task_success_count`는 검증 전까지 제외한다

## Current Provider Strategy

현재 MVP provider:

- Claude Code

후속 provider 후보:

- Cursor
- Codex

## Current UX Surface

- `/` 랜딩 페이지
- `/app` 계정, 캐릭터, 칭호, installation 흐름
- Claude 콘솔 내 notification 피드백
- Claude status line / project command 기반의 Claude-native 조회 표면 검토 진행

## Claude-native Surface

웹에 들어오지 않아도 Claude Code 안에서 상태를 볼 수 있는 표면을 별도로 둔다.

- `status line`
  - 항상 보이는 요약 표면
  - 추천 내용:
    - 현재 레벨
    - 현재 칭호
    - active 주간 프로젝트 진행률
  - 너무 자주 바뀌는 상세 로그 대신 짧은 snapshot만 보여준다
- project command / skill
  - 필요할 때 직접 호출하는 상세 표면
  - 예시:
    - `/rpg-status`
    - `/rpg-project`
  - 추천 내용:
    - 스탯
    - 최근 성장 요약
    - active 주간 프로젝트 상세
    - 최근 unlock / clear 이력

현재 추천안:

- 항상 보이는 정보는 Claude `status line`으로 제공한다
- 자세한 정보는 Claude project skill 또는 command로 제공한다
- hook stdout/stderr를 매 turn마다 길게 뿌려서 상태 조회를 대체하지는 않는다

이유:

- status line은 Claude Code가 공식적으로 지원하는 지속 UI 표면이다
- project command / skill은 상세 정보를 필요할 때만 꺼내 보게 만들어 콘솔 노이즈를 줄인다
- hook notification은 `Level up`, `Title unlocked`, `Project clear` 같은 짧은 이벤트 피드백에만 쓰는 편이 맞다

## Near-term UX Restructure

다음 UX 정리 작업을 예정한다.

- 게임 이름과 브랜드 톤 확정
- 로그인 페이지 분리
- 설치 가이드 페이지 분리
- 캐릭터 상세 status 페이지 분리
- 분리 이후 전체 정보 구조와 UI 톤 정리

## Current Product Risks

- progression 장기 설계가 아직 문서 단계이며, EXP / 레벨 / 주간 프로젝트의 최종 밸런스는 미확정이다.
- 칭호 시스템이 현재는 소수의 정적 칭호에 맞춘 구현이다.
- 멀티 provider 메시지에 비해 실제 완성도는 Claude Code 중심 MVP다.

## Near-term Product Priorities

- Claude hooks에서 실제로 안전하게 수집 가능한 이벤트 집합을 확정한다
- turn summary 기반으로 수집 이벤트와 성장 규칙을 일치시킨다
- 주간 프로젝트와 레벨 축의 장기 progression 의미를 확정한다
- 칭호를 "획득"에서 끝내지 말고 "장착/표현"까지 닫는다
- 게임 이름과 화면 구조를 정리해 제품 표현을 더 선명하게 만든다

## Not Doing Yet

- 코드 내용 저장
- 프롬프트 원문 저장
- 응답 원문 저장
- command 원문 저장
- path 저장
- 장비/드랍 테이블의 실제 게임 루프
- 레이드 전투 로직
- 복수 provider의 동등한 완성도 지원
