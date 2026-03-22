# Weekly Project 설계서

## 개요

매주 하나의 주간 프로젝트가 열린다. 유저는 Claude Code 작업을 통해 진행률을 쌓고, 목표치를 달성하면 클리어 칭호를 받는다. UI에서는 보스 레이드처럼 표현하지만 내부 계산은 프로젝트 진행률 기반이다.

---

## 데이터 모델

**`weekly_projects`**

| 컬럼 | 타입 | 설명 |
|---|---|---|
| `id` | int | PK |
| `week_number` | int | 주차 번호 (1부터 시작, unique) |
| `slug` | str | 고유 식별자 |
| `title` | str | 프로젝트 이름 |
| `theme` | str | 테마 (space, cyber 등) — 세트 칭호 기준 |
| `description` | str | 설명 |
| `target_progress` | int | 클리어 목표 (EXP 단위) |
| `starts_at` | datetime | 시작 시각 (UTC) |
| `ends_at` | datetime | 종료 시각 (UTC) |
| `active` | bool | 활성 여부 |

**`project_rewards`**

프로젝트 하나에 여러 보상 칭호를 연결. 칭호는 프로젝트 생성 시 미리 Title 테이블에 insert됨.

| 컬럼 | 타입 | 설명 |
|---|---|---|
| `id` | int | PK |
| `project_id` | int | FK → weekly_projects |
| `title_id` | int | FK → titles |
| `condition_type` | str | `clear` / `fast_clear` |
| `condition_params` | JSON | `{}` / `{"days": 3}` |

프로젝트 생성 시 만들어지는 Title은 기본적으로 HIDDEN. 획득 전까지 칭호 이름이 보이지 않음.

MVP condition 타입:
- `clear` — 클리어하면 지급
- `fast_clear` — `starts_at`으로부터 `days`일 이내 클리어 시 지급

**`project_progress`**

| 컬럼 | 타입 | 설명 |
|---|---|---|
| `id` | int | PK |
| `project_id` | int | FK → weekly_projects |
| `user_id` | int | FK → users |
| `progress_value` | int | 현재 누적 진행량 (EXP 단위) |
| `is_completed` | bool | 클리어 여부 |
| `completed_at` | datetime? | 클리어 시각 |
| `updated_at` | datetime | 마지막 갱신 |

---

## 진행량 계산

**EXP = 주간 프로젝트 진행량**

turn 1회에서 얻은 EXP가 그대로 프로젝트 진행량에 더해진다. 별도 공식 없음.

```
turn_exp = impl×4 + stability×3 + focus×2
→ character.exp += turn_exp
→ project.progress_value += turn_exp   ← 동일값 사용
```

---

## 클리어 보상 구조

### 1. 일반 클리어
`progress_value >= target_progress` 도달 시 즉시 클리어.
→ `clear_title_name` 칭호 지급

### 2. 속도 클리어 (Speed Clear)
`project_rewards`에 `fast_clear` 조건이 있는 경우, `completed_at - starts_at <= days`이면 속도 클리어.
→ 해당 칭호 **추가** 지급 (일반 클리어 칭호와 별개)

예시:
- 3일 이내 클리어 → `Orbital Breaker` (일반) + `Orbital Blitz` (속도)
- 7일 이내 클리어 → `Orbital Breaker` (일반)만

### 3. 연속 클리어 스트릭 (Streak)
연속 N주 클리어 시 별도 칭호 시리즈 지급.
칭호는 `title_definitions.py`에 streak rule로 정의.

| 스트릭 | 칭호 |
|---|---|
| 3주 | `Iron Streak` |
| 5주 | `Obsidian Streak` |
| 8주 | `Phantom Streak` |
| 13주 | `Eternal Vanguard` |

스트릭 tracking: `characters` 테이블에 `weekly_streak` 컬럼 추가. 클리어 시 +1, 주간 프로젝트 만료 시 미완료면 0 리셋.

> **구현 주의**: 스트릭은 프로젝트 클리어 시점에만 계산. `week_number = N` 클리어 시 `N-1` 클리어 여부 확인 → 연속이면 `+1`, 아니면 `1`로 리셋. 별도 cron 없이.

### 4. 테마 세트 칭호 (Theme Set)
같은 테마의 프로젝트를 N개 클리어하면 세트 칭호 지급.
칭호는 `title_definitions.py`에 theme_set rule로 정의.

예시:
- `space` 테마 3개 클리어 → `Star Architect`
- `cyber` 테마 3개 클리어 → `Grid Phantom`

체크 방법: `project_progress` + `weekly_projects` 조인으로 테마별 클리어 수 집계.

---

## 운영

### 스크립트
`scripts/weekly_project.py`로 직접 등록/조회.

```bash
# 목록
uv run scripts/weekly_project.py list

# 등록
uv run scripts/weekly_project.py create \
  --week-number 2 \
  --slug "stabilize-the-core-reactor" \
  --title "Stabilize the Core Reactor" \
  --theme cyber \
  --description "..." \
  --target 500 \
  --reward "clear:Reactor Stabilizer" \
  --reward "fast_clear:3:Instant Stabilizer" \
  --starts "2026-03-31 00:00" \
  --ends "2026-04-06 23:59"
```

### 롤오버
별도 로직 없음. `starts_at <= now <= ends_at` 조건으로 자동 전환.

### 미완료 처리
만료 시 progress 소멸, 보상 없음. 스트릭은 0 리셋.

### 공백 주
허용. 활성 프로젝트 없으면 progress 계산 스킵.

---

## 미결 사항

없음.

---

## 구현 순서

- [ ] EXP를 project progress로 통합 (공식 단순화)
- [ ] 마이그레이션
  - `weekly_projects`에 `week_number` 추가
  - `weekly_projects`에서 `clear_title_name`, `fast_clear_days`, `fast_clear_title_name` 제거
  - `project_rewards` 테이블 신규 생성
  - `project_progress`에서 `is_fast_clear` 제거
  - `characters`에 `weekly_streak` 추가
- [ ] `project_rewards` 모델 구현
- [ ] 클리어 보상 로직 리팩터 (`project_rewards` 기반)
- [ ] 속도 클리어 로직 구현
- [ ] 스트릭 칭호 정의 + rule 엔진에 `streak_threshold` 추가
- [ ] 스트릭 업데이트 로직 구현 (클리어 시점에 N-1 체크)
- [ ] 테마 세트 칭호 정의 + rule 엔진에 `theme_set` 추가
- [ ] `scripts/weekly_project.py` 전면 업데이트 (`--reward` 인자, `week_number`)
