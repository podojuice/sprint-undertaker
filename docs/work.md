# Sprint Undertaker Work Document

## TODO

- [x] FastAPI 앱, DB 초기화, Alembic 마이그레이션 구조 구성
- [x] 회원가입/로그인과 캐릭터 자동 생성
- [x] installation 생성, 조회, API key 회전
- [x] API key 기반 이벤트 적재
- [x] 조직 생성, 가입, 멤버 조회
- [x] 공개/숨김 칭호 지급
- [x] 칭호 메타데이터 확장
  - `visibility`
  - `theme_color`
  - `active_start_at`
  - `active_end_at`
- [x] `/api/titles/me`와 `/app` 타이틀 패널 추가
- [x] 날짜별 문서를 없애고 문서 체계를 `docs/product.md` + `docs/work.md`로 정리
- [x] provider 전략을 Codex-first에서 Claude Code hooks-first로 전환
- [x] 성장 단위를 세션이 아니라 `UserPromptSubmit -> Stop` turn으로 재설계
- [x] privacy-safe payload 원칙 확정
  - prompt 원문 금지
  - command 원문 금지
  - path 원문 금지
  - 집계치와 분류값만 전송
- [x] MVP 메트릭을 확실하게 수집 가능한 값만 남기도록 축소
- [x] MVP 스탯을 `impl`, `stability`, `focus` 3개로 축소
- [x] Claude turn summary 기준 서버 이벤트 스키마와 progression 로직 구현
- [x] Claude Code hook collector 초안 구현
- [x] `/app`, 랜딩, 설치 흐름을 Claude Code 기준으로 수정
- [x] Claude 설치 가이드에 `python3` 필요 조건과 settings merge 안내 추가
- [x] auth / organization / progression API 테스트 통과 확인
- [x] activity/history API 추가
  - 최근 turn summary 목록
  - 성장 이유를 보여줄 notification/history
- [x] `/app`에 최근 성장 로그 패널 추가
- [x] `/install/claude-code` 페이지에도 JSON hook snippet 직접 노출
- [x] hook notification을 Claude 콘솔에 출력하는 경로 연결
- [x] Claude-native 조회 표면 검토
  - status line을 항상 보이는 요약 표면으로 사용
  - project skill / command를 상세 조회 표면으로 사용
  - hook notification은 이벤트성 메시지로 제한
- [x] Claude Code plugin 구조로 전환
  - [x] plugin 디렉토리 구조 생성 (`clients/claude-code-plugin/`)
    - `.claude-plugin/plugin.json` — 메타데이터, 버전
    - `.claude-plugin/marketplace.json` — marketplace 카탈로그
    - `hooks/hooks.json` — 5개 이벤트 hook 등록
    - `scripts/sprint_undertaker_hook.py` — 기존 hook 스크립트 이동
    - `skills/rpg-status/SKILL.md` — status skill
  - [x] hook command 경로를 `${CLAUDE_PLUGIN_ROOT}/scripts/...`로 변경
  - [x] 기존 `~/.claude/settings.json` hook 등록 방식 제거 가능하도록 설치 가이드 수정
  - [x] 웹 설치 가이드를 plugin 설치 방식으로 업데이트
  - [x] `--plugin-dir`로 로컬 테스트
  - [x] register/login skill 추가 (`scripts/register.py`, `scripts/login.py`)
  - [x] register skill 이메일 인증 2단계 플로우 구현 (코드 발송 → `--code` 인자로 인증)
  - [x] register/login skill에서 서버 URL 입력 제거 (스크립트 기본값 사용)
  - [x] EmailCode enum `values_callable` 버그 수정 (대소문자 불일치)
  - [x] alembic `env.py`에 dotenv 연동 (`.env`의 `RPG_DATABASE_URL` 자동 로드)
  - [x] Supabase 원격 DB 연결 및 이메일 인증 end-to-end 검증
- [x] progression 재설계 검토
  - 현재 설계(impl×4 + stability×3 + focus×2, 레벨 공식 100×level^1.5) 그대로 유지 결정
- [x] 게임 이름 확정
  - 제품/브랜드 이름 후보 정리
  - 최종 이름 결정 후 문서와 UI 카피 반영
- [ ] 앱 UX 개선
  - [ ] API 서버 로그에 시간(timestamp) 찍히도록 수정
  - [ ] `/app` recent growth 패널을 시간·이벤트·스탯 3열로 간결하게 정리
  - [ ] `/app` titles 패널에서 중복 문구 제거, 획득/미획득만 직관적으로 표시
  - [ ] 화면 구조 분리
    - app 설치 가이드 페이지 분리
    - 로그인 페이지 분리
    - 캐릭터 상세 status 페이지 분리
  - [ ] 칭호 장착/해제 API 추가
  - [ ] 웹 앱에서 active title 변경 UI 추가
  - [ ] organization dashboard 추가
    - 멤버 레벨
    - 총 활동량
    - 최근 성장 요약
  - [ ] installation 관리 UX 보강
    - rotate key
    - 다중 installation 표시
  - [ ] UI/브랜딩 다듬기
    - 화면 분리 이후 정보 구조 재정리
    - 타이포/컬러/레이아웃 정리
    - 전체 제품 톤앤매너 정리
- [ ] Claude status line 추가
  - 현재 레벨
  - active title
  - active weekly project progress 요약
- [ ] Claude project skill / command 추가
  - [x] `/rpg-status` skill 구현
    - [x] API key 인증으로 캐릭터 정보를 내려주는 `/api/characters/status` 엔드포인트 추가
    - [x] 설정 파일은 기존 `~/.config/sprint-undertaker/claude-code-hook.env` 재사용
    - [x] `scripts/status.py` — API 호출 후 캐릭터 카드 콘솔 출력
    - [x] 스탯은 MVP 유효 스탯(impl, stability, focus)만 표시
    - [ ] 미확인 notification 요약도 함께 표시 (notification 시스템 구현 후)
  - [ ] `/rpg-project` skill 구현
    - 주간 프로젝트 진행률 조회
  - 웹 없이도 현재 상태와 진행률 조회 가능하게 구성
- [x] Notification 시스템 구현
  - [x] `notifications` 테이블 설계 및 마이그레이션
    - id, user_id, message, category (level_up, title_unlock, project_clear 등), created_at
  - [x] 이벤트 처리 시 notification 레코드 생성 (progression, title, project clear)
  - [x] `/api/notifications/me` 조회 API (unread만 반환)
  - [x] 확인 처리 (read mark) API
  - [ ] `/rpg-status` skill에서 미확인 notification 표시
  - [ ] hook에서 desktop notification 보내는 것은 MVP에서 제외
- [x] 칭호 작업 마무리
  - 마이그레이션 적용 검증
  - `/api/titles/me` 응답 형태 최종 점검
  - 타이틀 패널 UX 최종 점검
- [x] 칭호 조건 하드코딩 제거
  - title name 분기 제거
  - 정의 파일 + condition rule 파싱으로 전환
  - DB sync 스크립트 추가
- [ ] 실제 Claude Code 환경에서 hook 설치 end-to-end 검증
- [ ] 초기 프로덕션 배포 계획 수립
  - [ ] 로컬 개발 마무리 후 AWS Lightsail 4GB / 80GB SSD (`$24/mo`) 기준으로 배포
  - [ ] 단일 인스턴스에 `nginx` + `systemd` + FastAPI + PostgreSQL 구성
  - [ ] 이벤트 보관 기간과 주기 삭제 정책 정의
  - [ ] 도메인 구매 예산 반영 (`~$10/yr`)
  - [ ] 이후 필요 시 EC2 등으로 마이그레이션 가능한 운영 기준 정리
- [ ] GitHub repo push 후 marketplace git-subdir 방식으로 전환
  - `clients/claude-code-plugin/`을 `git-subdir` source로 마켓플레이스에 등록
  - 마켓플레이스 repo 별도 생성 필요
- [ ] Cursor provider 검토 및 연동 시작
- [ ] provider adapter 구조 분리
- [ ] 장비 모델/보상 루프 설계 구체화
- [ ] 레이드용 누적 전투력 계산 축 설계
- [x] 주간 프로젝트 / 개인 progress 기본 모델 초안 구현
  - `weekly_projects`
  - `project_progress`
  - clear notification + title reward

## Current Read

Claude Code plugin 구조로 전환이 완료됐고, Supabase 원격 DB 연결 및 이메일 인증 기반 회원가입 플로우까지 end-to-end 검증된 상태다. register/login skill이 추가됐고, 로컬 마켓플레이스(`directory` source)로 플러그인 설치 및 캐릭터 상태 조회까지 동작 확인됨.

남은 플러그인 작업은 GitHub repo에 push한 뒤 마켓플레이스를 `git-subdir` 방식으로 전환하는 것이다. 서버와 클라이언트가 한 repo에 있어도 마켓플레이스에서 서브디렉토리만 참조할 수 있으므로 별도 분리 없이 배포 가능하다.

그 다음 묶음은 progression 구조 의미 확정, 앱 UX 개선, Claude status line 추가, notification 시스템 구현이다.

배포 쪽은 로컬 개발을 마무리한 뒤 AWS Lightsail 4GB / 80GB SSD 플랜을 초기 프로덕션 후보로 잡는다. 운영 형태는 `nginx` + `systemd` + FastAPI + PostgreSQL 단일 인스턴스를 기본안으로 두고, 도메인 비용은 연간 약 `$10` 수준으로 별도 반영한다.

## Claude-native Review

웹 없이 Claude Code 안에서 상태를 보여주는 표면은 두 개로 나누는 게 가장 현실적이다.

1. `status line`
   - 항상 보이는 짧은 상태 요약
   - 레벨, active title, 주간 프로젝트 진행률처럼 짧고 자주 확인할 값에 적합
2. project skill / command
   - 유저가 직접 호출하는 상세 조회
   - `/rpg-status`, `/rpg-project` 같은 형태가 적합
   - 스탯, 최근 성장, 최근 칭호 해금, 프로젝트 상세를 보여주기 좋다

추천안:

- 기본 조회는 Claude `status line`
- 상세 조회는 Claude project skill / command
- 기존 hook notification은 짧은 이벤트 메시지에만 사용

피해야 할 것:

- hook stderr/stdout에 매 turn 전체 상태를 길게 출력하는 것
- UserPromptSubmit 훅을 상태 조회용 컨텍스트 주입으로 쓰는 것 (hook stdout은 Claude 컨텍스트에만 들어가고 유저에게 표시되지 않음)
- 웹과 Claude 콘솔에서 서로 다른 계산 로직을 가지는 것

구현 순서 추천:

1. status line용 최소 읽기 전용 엔드포인트 또는 로컬 snapshot 형식 확정
2. Claude status line 스크립트 추가
3. `/rpg-status`, `/rpg-project` skill / command 추가
4. 이후 웹 UI와 Claude UI가 같은 데이터를 보도록 공용 응답 스키마 정리

## MVP Metrics

MVP 1차에서 사용하는 메트릭:

- `prompt_count`
- `prompt_length_bucket`
- `edit_success_count`
- `validation_success_count`
- `validation_failure_count`
- `tool_failure_count`
- `model_name`

제외:

- `turn_duration_bucket`
- `write_success_count`
- `task_success_count`
- 모든 `best-effort` 메트릭

## MVP Stats

MVP 1차 스탯은 3개만 사용한다.

- `impl`
  - `edit_success_count`
- `stability`
  - `validation_success_count`
  - 실패 후 같은 turn 내 성공 여부
- `focus`
  - `prompt_count`
  - `prompt_length_bucket`

주의:

- `focus`는 쉽게 왜곡될 수 있으므로 보상 강도를 가장 약하게 둔다
- `versatility`, `efficiency`, `endurance`는 MVP 1차에서 제외한다

## Progression Redesign Brief

이 검토는 "재미용 게임 루프"를 더 멀리 보는 설계 태스크다. 메트릭이 제한적이라는 전제는 받아들이고, 완벽한 현실 반영보다 일관된 게임 해석을 우선한다.

우선순위를 낮추는 걱정:

- 실제 산출과 완전히 정밀하게 대응하지 못하는 문제
- 활동량 점수화의 일부 왜곡

대신 우선순위를 높게 보는 것:

- EXP, 스탯, 레벨이 각각 무엇을 뜻하는지 일관되게 정의하는 것
- 현재 hook 메트릭만으로도 돌아가는 장기 루프를 설계하는 것
- 주간 보스 / 프로젝트 진행 / 업적이 서로 충돌하지 않게 연결하는 것

어디서부터 고민할지:

1. 레벨의 의미부터 정한다
   - 레벨이 단순 누적 성장인지
   - 기능 해금 축인지
   - 전투력의 핵심 축인지
2. 스탯의 역할을 정한다
   - 전투 계산용인지
   - 캐릭터 성향 표현용인지
   - 둘 다라면 어느 비중이 큰지
3. 주간 루프의 정체를 정한다
   - "보스 레이드"가 본체인지
   - "프로젝트 진행률"이 본체인지
   - 둘을 같은 시스템의 다른 스킨으로 볼지
4. 업적의 역할을 정한다
   - 단순 수집 보상인지
   - 특정 플레이스타일을 유도하는 가이드인지
5. 현재 메트릭과 연결 가능한 최소 규칙을 정한다
   - `edit_success_count`
   - `validation_success_count`
   - `tool_failure_count`
   - `prompt_count`
   - `prompt_length_bucket`
   - `model_name`

먼저 결정하고 넘어가야 할 것:

- EXP는 무엇을 올리는가
  - 레벨만 올리는지
  - 보스/프로젝트 진척에도 직접 쓰이는지
- 스탯은 어디에 쓰이는가
  - 개인 성장 표현
  - 레이드 전투력
  - 프로젝트 진행 보정치
- 주간 보스와 프로젝트는 어떤 관계인가
  - 별개 시스템인지
  - 같은 시스템을 테마만 바꾼 것인지
- 업적은 언제 주는가
  - 단순 누적 기준
  - 특정 행동 조합 기준
  - 시즌/주간 이벤트 기준
- 실패는 어떻게 해석하는가
  - 단순 감점 요소인지
  - 복구 성공 시 오히려 스토리텔링 자원인지

설계 구멍을 줄이기 위한 decision checklist:

- 레벨 1 증가가 유저 경험상 무엇을 바꾸는지 한 문장으로 설명 가능한가
- 각 스탯이 왜 존재하는지, 다른 스탯과 겹치지 않게 설명 가능한가
- 현재 메트릭만으로 계산 가능한 규칙인지
- turn 단위 데이터만으로도 서버가 일관되게 집계 가능한가
- 보스 / 프로젝트 / 업적 중 하나를 빼도 나머지가 성립하는가
- "지금 구현 가능한 MVP 규칙"과 "나중 확장 규칙"이 분리되어 있는가

추천 진행 순서:

1. 레벨의 의미 정의
2. 스탯의 역할 정의
3. 주간 루프를 보스 중심으로 갈지 프로젝트 중심으로 갈지 결정
4. 업적을 그 루프의 보조 보상으로 배치
5. 그 다음에야 EXP 공식을 다시 손본다

## Progression Redesign Proposal

현재 메트릭 제약 안에서 가장 일관적인 추천 방향은 아래와 같다.

### 1. 레벨의 의미

추천:

- 레벨은 "누적 성장 + 해금 축"이다
- 직접 전투 계산의 핵심 수치로 쓰기보다, 기능 해금과 장기 성장 체감에 우선 연결한다

이유:

- 현재 메트릭으로 정교한 전투력 계산을 만들기엔 입력이 얕다
- 반면 레벨은 누적 활동을 표현하고, 칭호/업적/주간 콘텐츠 해금 축으로 쓰기 좋다

레벨이 해금하는 것의 추천안:

- 레벨 달성 칭호
- 주간 프로젝트 참여 자격
- 이후 확장 시 희귀 칭호 풀
- 이후 확장 시 장비/보상 슬롯

초기 해금 예시:

- Lv.3: 주간 프로젝트 참여
- Lv.5: 레벨 달성 칭호 추가
- Lv.7: 희귀 칭호 등장
- Lv.10: 향후 장비 슬롯 또는 시즌 보상 해금

### 2. 스탯의 의미

추천:

- `impl`: 주간 콘텐츠에 들어가는 기본 공격력 또는 진행력
- `stability`: 성공 보정, 보상 배수, 실패 복구 보너스
- `focus`: 지속 참여 보너스, streak 보너스, 주간 프로젝트 효율 보정

이유:

- 현재 수집 가능한 메트릭과 직접 연결된다
- 각 스탯 역할이 덜 겹친다
- 전투든 프로젝트든 같은 해석으로 재사용 가능하다

### 3. 주간 루프의 정체

추천:

- 본체는 "주간 프로젝트"
- 보스는 그 프로젝트를 RPG적으로 표현하는 스킨

예:

- "Tesla Launch Week"라는 주간 프로젝트가 열림
- UI에서는 보스처럼 보이지만, 내부적으로는 프로젝트 진행률을 쌓는다
- 일정 진행률을 넘기면 프로젝트 완료, 업적/칭호/보상 지급

이유:

- 현재 메트릭은 실제로 "전투 행동"보다 "작업 진행"에 더 가깝다
- 프로젝트 프레임이 데이터와 더 잘 맞고, 보스 표현은 나중에 얹기 쉽다
- 재미용 테마는 보스로 유지하면서도 내부 계산은 단순하게 갈 수 있다

### 4. 업적의 역할

추천:

- 업적은 장기 누적 보상과 특정 플레이스타일 유도 둘 다 담당한다
- 단, 주간 프로젝트의 핵심 보상과는 분리한다

예:

- 누적 `edit_success_count` 달성
- validation 성공 누적
- 실패 후 복구 성공 횟수
- 특정 주간 프로젝트 완료

이유:

- 업적이 메인 루프를 대신하면 안 된다
- 메인 루프는 프로젝트/보스, 업적은 보조 레이어가 더 안정적이다

### 5. EXP의 역할

추천:

- EXP는 레벨 전용 재화로 둔다
- 주간 프로젝트 진척은 EXP와 분리된 별도 게이지로 계산한다

이유:

- EXP와 프로젝트 진척을 한 값으로 섞으면 밸런스가 바로 꼬인다
- "많이 활동해서 레벨업"과 "이번 주 프로젝트를 얼마나 밀었나"는 분리된 축이 더 이해하기 쉽다

### 6. 주간 프로젝트 계산 초안

추천:

- 기본 진행력:
  - `impl` 중심
- 보정:
  - `stability`로 성공 배수 또는 실패 패널티 완화
  - `focus`로 연속 참여 보너스

예시 해석:

- `edit_success_count` -> 기본 진행력
- `validation_success_count` -> 안정적 진행 보너스
- `tool_failure_count` -> 직접 감점보다 보정 감소
- `prompt_count`, `prompt_length_bucket` -> 참여도 보너스

### 7. 지금 단계에서 먼저 확정할 추천 결정

1. 레벨은 해금 축으로 본다
2. 주간 콘텐츠의 본체는 프로젝트 진행률로 본다
3. 보스는 프로젝트의 표현 레이어로 둔다
4. EXP와 프로젝트 진척은 분리한다
5. 스탯 3개는 각각 `진행력`, `안정 보정`, `참여 보정` 역할로 둔다

이 다섯 가지를 먼저 확정하면:

- EXP 공식 재설계
- 주간 프로젝트 모델 추가
- 업적/칭호/조직 보상 연결

이 세 가지를 비교적 헛점 없이 다음 단계로 넘길 수 있다

현재 합의안:

- 레벨은 AI 활동 누적에 따라 자연스럽게 오른다
- 특정 레벨 달성 시 칭호를 추가로 지급한다
- 주간 보스/프로젝트 진척은 EXP 축과 분리한다
- 주간 보스/프로젝트 클리어 시에도 칭호를 지급한다
- MVP에서는 보상 다양화는 하지 않고 칭호 중심으로 단순화한다

## Formula Draft

현재 추천 초안은 "EXP는 누적 성장", "프로젝트 진척은 별도 게이지"로 분리하는 것이다.

### EXP 공식 초안

turn 1회당:

- `impl_exp = edit_success_count * 4`
- `stability_exp = validation_success_count * 3`
- `focus_exp = focus_delta * 2`
- `failure_penalty = 0`

여기서:

- `focus_delta = 1`
- `prompt_length_bucket == long`이면 `focus_delta += 1`

최종:

- `turn_exp = impl_exp + stability_exp + focus_exp`

레벨업 요구 EXP:

- 현재 유지안: `required_exp = 100 * level^1.5`

의도:

- EXP는 꾸준히 쌓인다
- validation과 edit 모두 가치가 있다
- focus는 보조 가중치만 가진다

### 주간 프로젝트 진행 공식 초안

turn 1회당 기본 진행력:

- `base_progress = edit_success_count * 5`

안정 보정:

- `stability_bonus = validation_success_count * 2`

참여 보정:

- `focus_bonus = focus_delta`

실패 보정:

- `failure_drag = min(tool_failure_count, 2)`

최종:

- `turn_project_progress = max(0, base_progress + stability_bonus + focus_bonus - failure_drag)`

의도:

- 프로젝트 진척은 `impl` 중심이다
- `stability`는 같은 작업이라도 더 믿을 수 있게 만든다
- `focus`는 작은 참여 보너스만 준다
- 실패는 직접 큰 감점보다 진행 보정 감소 정도로만 반영한다

### 스탯과 프로젝트의 관계

- `impl`
  - 프로젝트 기본 진행력의 원천
- `stability`
  - 프로젝트 진행 품질 보정치
- `focus`
  - 꾸준한 참여 보정치

### 왜 EXP와 프로젝트 진척을 분리하는가

- 레벨은 장기 누적 성장이다
- 프로젝트는 이번 주 목표 진척이다
- 둘을 섞으면 밸런스 조정이 어려워진다
- 분리하면 "캐릭터는 꾸준히 성장하지만, 이번 주 프로젝트는 별도로 밀어야 한다"는 구조가 자연스럽다

### 레벨 보상 초안

MVP에서는 레벨업 보상을 칭호로 단순화한다.

예시:

- Lv.3 달성 칭호
- Lv.5 달성 칭호
- Lv.10 달성 칭호

의도:

- 레벨업의 의미를 분명하게 만든다
- 장비/재화/드랍 같은 추가 보상 축 없이도 성취감을 준다
- 현재 메트릭과 구현 범위에 맞는다

### 주간 보스/프로젝트 보상 초안

MVP에서는 주간 보스 또는 주간 프로젝트 완료 보상도 칭호로 단순화한다.

현재 합의안:

- 주간 프로젝트마다 고유 칭호를 직접 세팅한다
- 서버에서 매주 프로젝트 제목, 테마, 클리어 값, 보상 칭호를 직접 운영한다
- 그 시점에 화제가 되는 프로젝트/테마를 curated 방식으로 세팅한다

예시:

- 특정 주간 프로젝트 첫 클리어 칭호
- 특정 보스 테마 클리어 칭호
- 주간 프로젝트별 고유 named title

의도:

- 레벨 축과 주간 콘텐츠 축을 분리한다
- 보상 종류를 늘리지 않고도 "이번 주 목표"의 의미를 만든다
- 구현 범위를 과도하게 늘리지 않는다

## Weekly Project / Boss Draft

현재 추천 구조는 "주간 프로젝트가 본체, 보스는 표현 레이어"다.

### 핵심 개념

- 매주 하나의 주간 프로젝트가 열린다
- 프로젝트는 내부적으로 진행률 게이지를 가진다
- UI에서는 프로젝트를 보스/레이드처럼 보여줄 수 있다
- 프로젝트 완료 시 이번 주 콘텐츠 클리어로 처리한다

예:

- "Launch the Orbital Stack"
- "Ship the Mars Console"
- "Stabilize the Core Reactor"

이런 프로젝트를 내부적으로는 진행률로 계산하고, 외부 표현은 보스 체력이나 레이드 목표처럼 보여준다.

### 최소 데이터 모델 초안

- `weekly_projects`
  - `id`
  - `slug`
  - `title`
  - `theme`
  - `description`
  - `target_progress`
  - `starts_at`
  - `ends_at`
  - `active`
- `project_progress`
  - `project_id`
  - `user_id` 또는 `organization_id`
  - `progress_value`
  - `is_completed`
  - `completed_at`
- `project_rewards`
  - `project_id`
  - `reward_type`
  - `reward_ref`

MVP에서는 실제 보상 테이블을 넓히지 않고, `reward_type = title` 하나만 써도 된다.

MVP 1차 추천 스키마:

- `weekly_projects`
  - `id`
  - `slug`
  - `title`
  - `theme`
  - `description`
  - `target_progress`
  - `starts_at`
  - `ends_at`
  - `active`
  - `clear_title_name`
- `project_progress`
  - `id`
  - `project_id`
  - `user_id`
  - `progress_value`
  - `is_completed`
  - `completed_at`
  - `updated_at`

MVP 1차에서는:

- organization progress는 아직 넣지 않는다
- clear reward는 title 1개만 둔다
- 한 유저가 한 주간 프로젝트를 1회 클리어하는 구조로 단순화한다

이유:

- 지금 메트릭과 구현 범위에 맞다
- 개인 루프로 먼저 닫은 뒤 organization 합산으로 확장하기 쉽다

### 계산 구조 초안

- turn이 끝날 때
  - EXP는 캐릭터 레벨 축으로 들어간다
  - 동시에 `turn_project_progress`를 계산한다
- 그 값이 이번 주 프로젝트 progress에 누적된다
- 누적 progress가 `target_progress`를 넘으면 클리어
- 클리어 시 주간 프로젝트 칭호 지급

MVP 1차 turn progress 공식 초안:

- `base_progress = edit_success_count * 5`
- `stability_bonus = validation_success_count * 2`
- `focus_bonus = focus_delta`
- `failure_drag = min(tool_failure_count, 2)`
- `turn_project_progress = max(0, base_progress + stability_bonus + focus_bonus - failure_drag)`

여기서:

- `focus_delta = 1`
- `prompt_length_bucket == long`이면 `focus_delta += 1`

의도:

- edit 성공이 프로젝트 진척의 핵심이다
- validation은 안정적 진행 보너스다
- focus는 약한 참여 보너스다
- 실패는 진행을 완전히 막기보다 속도를 늦춘다

MVP 1차 목표 진행량 초안:

- 쉬운 주간 프로젝트: `target_progress = 80`
- 기본 주간 프로젝트: `target_progress = 100`
- 긴 주간 프로젝트: `target_progress = 180`

추천:

- MVP 시작은 `target_progress = 100`

이유:

- 보통의 꾸준한 turn 몇 번으로 클리어 가능해야 한다
- 너무 길면 주간 루프 체감이 사라진다
- 너무 짧으면 "이번 주 목표"의 의미가 약해진다

### 개인 / 조직 확장 경로

MVP 1차 추천:

- 개인 progress만 먼저 계산

이후 확장:

- organization 합산 progress
- organization 단위 주간 클리어
- 멤버 contribution ranking

### 왜 프로젝트 본체 + 보스 표현이 좋은가

- 현재 메트릭은 "작업 진행" 해석에 더 자연스럽다
- 하지만 유저에게는 보스/레이드 표현이 더 재미있다
- 내부 계산과 외부 표현을 분리하면 둘 다 가져갈 수 있다

### 주간 프로젝트 클리어 규칙 초안

- 한 주에 active project는 1개
- 각 turn 종료 시 개인 progress 누적
- progress가 `target_progress`를 넘는 순간 즉시 clear
- clear 후 추가 progress는 무시하거나 archive로만 남김
- clear 시:
  - notification 발생
  - clear title 지급
  - activity/history에 clear event 남김

추천:

- MVP에서는 "같은 프로젝트 중복 보상 없음"
- 같은 clear title을 같은 유저에게 여러 번 주지 않는다

이유:

- 보상 로직이 단순해진다
- title reward가 희소성을 가진다

## Hook Feedback Draft

hook 응답으로 유저 콘솔에 진행 메시지를 보여주는 것은 가능하다.

현재 구조:

- 서버가 notification을 DB에 저장한다
- 유저가 `/rpg-status` skill로 조회하면 미확인 notification을 함께 표시한다
- hook stdout은 Claude 컨텍스트에만 주입되고 유저 콘솔에 직접 표시되지 않는다
- hook에서 desktop notification을 보내는 것은 MVP에서 제외한다

예시 메시지:

- `Level up! Lv.4 -> Lv.5`
- `Title unlocked: Deep Focus`
- `Project clear! Launch the Orbital Stack`
- `Congratulations! Weekly boss defeated`

추천 원칙:

- turn 완료 시점에만 짧게 출력
- 너무 자주 출력하지 않는다
- MVP에서는 `level up`, `title unlocked`, `project clear` 정도만 쓴다
- 카피 톤은 과하게 장난스럽지 않은 중간톤으로 간다

이 구조의 장점:

- 추가 UI 없이도 유저가 즉시 피드백을 받는다
- Claude Code 콘솔 안에서 게임 반응을 바로 보여줄 수 있다
- 서버가 메시지를 결정하므로 밸런싱과 카피를 중앙에서 관리할 수 있다

MVP 1차 notification 규칙 초안:

- 항상 보여주지 않는 것:
  - 매 turn stat 변화
  - 매 turn EXP 획득
- 보여주는 것:
  - `Level up!`
  - `Title unlocked!`
- `Project clear!`
- `Weekly boss defeated!`

현재 합의안:

- hook notification 카피 톤은 중간톤으로 간다
- 콘솔에서 바로 이해 가능해야 하고, 너무 과장되지는 않게 한다

예시:

- `Level up! Lv.4 -> Lv.5`
- `Title unlocked: Deep Focus`
- `Project clear! Launch the Orbital Stack`
- `Congratulations! Weekly boss defeated: Launch the Orbital Stack`

### 다음에 결정할 것

1. `weekly_projects` 운영 입력 필드 확정
2. `target_progress` 기본값을 100으로 확정할지 여부
3. 레벨별 칭호 지급 구간
4. 주간 클리어 고유 칭호 운영 규칙
5. hook notification 카피 톤

## Level Title Draft

MVP 1차에서는 레벨 보상을 칭호로만 준다.

현재 합의안:

- 만렙은 `50`
- 레벨링은 초반에 쉽게, 후반에 크게 스케일링한다
- 레벨 칭호 지급 구간은 아래처럼 둔다

확정 구간:

- Lv.2
- Lv.5
- Lv.10
- Lv.15
- Lv.20
- Lv.30
- Lv.40
- Lv.50

의도:

- 초반엔 시원하게 레벨업 체감을 준다
- 중반 이후엔 큰 이정표를 준다
- 만렙 50까지 장기 목표를 유지한다

예시 이름 방향:

- Lv.2: First Commit Flame
- Lv.5: Reliable Climber
- Lv.10: Deep Cycle Operator
- Lv.15: Quiet Maintainer
- Lv.20: Project Vanguard
- Lv.30: Weekly Hunter
- Lv.40: System Ascendant
- Lv.50: Weekly Vanguard

지금 단계에서 필요한 결정:

- 레벨 칭호가 고정 이름인지
- 시즌/주간과 무관한 영구 칭호인지
- 현재 active title과 자동 장착 관계를 어떻게 둘지

## Weekly Clear Title Rule

현재 합의안:

- 주간 클리어 칭호는 프로젝트별 고유 칭호로 간다
- 공통 템플릿 자동 생성보다 curated 운영을 우선한다
- 운영자는 매주 프로젝트 제목, `target_progress`, `clear_title_name`을 같이 세팅한다

이유:

- 매주 콘텐츠 개성을 강하게 줄 수 있다
- "그 주에 어떤 프로젝트를 깼는가"가 더 선명하게 남는다
- 재미용 운영에 더 잘 맞는다

MVP 운영 입력 예시:

- `title`: `Launch the Orbital Stack`
- `theme`: `space`
- `target_progress`: `100`
- `clear_title_name`: `Orbital Breaker`

주의:

- 운영자 입력 실수 방지를 위한 서버 검증이 필요하다
- clear title 이름 충돌을 피하기 위한 naming rule이 필요하다

## Technical Debt

- 칭호 조건 판정이 title name 기반 하드코딩이다
- progression 규칙이 단일 함수에 모여 있다
- README가 개발 가이드 중심이고 제품 상태 설명은 약하다
- 테스트가 API happy path 중심이다
- `Character` 모델에 MVP에서 쓰지 않는 스탯 컬럼(`efficiency`, `versatility`, `endurance`)이 그대로 남아 있다
  - `CharacterResponse` 스키마에도 함께 노출 중
  - 삭제하려면 알embic 마이그레이션 + 스키마 정리 필요
- `clients/claude-code-hook/`의 기존 hook 스크립트가 plugin으로 이동 후에도 그대로 남아 있다
  - plugin 방식이 안정화되면 `clients/claude-code-hook/` 디렉토리 정리 필요

## Working Rules

- 날짜별 문서는 더 만들지 않는다
- 기획 변경은 `docs/product.md`에 반영한다
- 구현 상태와 남은 일은 `docs/work.md` 체크리스트를 먼저 갱신한다
- 새 작업을 시작할 때는 해당 TODO를 먼저 확인하고, 필요하면 더 잘게 쪼개서 체크리스트에 추가한다
- 작업이 끝나면 같은 턴 안에서 반드시 `docs/work.md`의 `[ ]`를 `[x]`로 바꾸거나, 다음 액션을 새 TODO로 남긴다
- 큰 기능을 끝낼 때마다 `[x]` 처리와 다음 TODO를 같이 갱신한다
