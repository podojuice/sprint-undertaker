# Public Profile 설계서

## 개요

유저가 자신의 캐릭터 프로필을 공개로 설정하면, 다른 사람이 닉네임으로 검색해서 조회할 수 있다. 본인의 스탯과 칭호를 자랑하는 표면.

---

## 기능 범위

- 유저가 프로필 공개/비공개 토글
- 공개 프로필 웹 페이지 (`/u/{nickname}`)
- Claude skill (`/undertaker:profile <nickname>`)

노출 정보:
- 캐릭터 이름, 레벨, 클래스
- 스탯 (impl, stability, focus)
- 장착 중인 칭호 (active title)
- 획득한 칭호 목록 (PUBLIC 칭호만)

비노출:
- 이메일
- HIDDEN 칭호 (획득 여부 포함)
- installation, API key 정보

---

## API

### `PATCH /api/characters/me/visibility`
본인 프로필 공개 여부 설정.

```json
{ "is_public": true }
```

### `GET /api/characters/profile/{nickname}`
닉네임으로 공개 프로필 조회. 인증 불필요.

비공개이거나 존재하지 않으면 404.

---

## 데이터 모델 변경

`characters` 테이블에 `is_public` 컬럼 추가 (bool, default false).

---

## 웹 페이지

`/u/{nickname}` — 서버사이드 렌더링, 기존 템플릿 구조 재사용.

---

## Claude Skill

`/undertaker:profile` — nickname을 입력받아 API 호출 후 캐릭터 카드 출력.

```
  ice  [Orbital Breaker]
  Novice  Lv.3
  EXP [████░░░░░░░░░░░░░░░░] 47 / 171

  impl          12
  stability      8
  focus          5

  Titles (4)
  ✦ Orbital Breaker       ✦ First Commit Flame
  ✦ Phantom Maintainer    ✦ Reliable Climber
```

---

## 구현 순서

- [ ] `characters`에 `is_public` 컬럼 추가 (마이그레이션)
- [ ] `PATCH /api/characters/me/visibility` 엔드포인트
- [ ] `GET /api/characters/profile/{nickname}` 엔드포인트
- [ ] `/u/{nickname}` 웹 페이지
- [ ] `/undertaker:profile` skill (`scripts/profile.py`)
