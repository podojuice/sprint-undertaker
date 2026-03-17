# sprint-undertaker

FastAPI 기반의 멀티 provider 개발 RPG 서버입니다.

## Docs

앞으로 문서는 아래 두 파일만 계속 갱신합니다.

- [docs/product.md](/Users/users/workspace/sprint-undertaker/docs/product.md): 제품 정의, 범위, 원칙, 방향
- [docs/work.md](/Users/users/workspace/sprint-undertaker/docs/work.md): 현재 상태, 진행 중 작업, TODO, 기술 부채

## Development

로컬 Python 개발은 `uv` 기준으로 관리합니다.

먼저 `uv`가 설치되어 있어야 합니다.

```bash
brew install uv
```

그 다음 가상환경과 의존성을 준비합니다.

```bash
uv venv
uv sync
```

앱을 로컬 프로세스로 실행할 때는 아래 명령을 사용합니다.

```bash
uv run uvicorn server.main:app --reload
```

Docker 개발 환경은 `.env.example`를 `.env`로 복사한 뒤 아래 명령으로 실행합니다.

```bash
cp .env.example .env
docker compose up --build
```

DB 마이그레이션은 아래처럼 실행합니다.

```bash
UV_CACHE_DIR=.uv-cache uv run alembic upgrade head
```

앱은 `http://localhost:8000`, Postgres는 `localhost:5432`로 열립니다.

헬스체크:

```bash
curl http://localhost:8000/health
```

기본 웹 페이지:

- `/` : 랜딩 페이지
- `/app` : 로그인, 캐릭터 상태, installation 생성
- `/install/claude-code` : Claude Code hook 설치 안내

## Environment

개발 환경에서는 `docker-compose.yml`로 app + postgres를 같이 띄웁니다.

운영 환경에서는 Postgres를 별도 운영하고 `RPG_DATABASE_URL`만 해당 값으로 바꾸면 됩니다.

## Testing

테스트용 Postgres를 띄운 뒤 pytest를 실행합니다.

```bash
docker compose up -d db_test
RPG_DATABASE_URL=postgresql+asyncpg://rpg:rpg@localhost:5433/rpg_test UV_CACHE_DIR=.uv-cache uv run pytest
```

## Claude Code Hook

Claude Code용 자동 수집 hook는 아래 경로에 있습니다.

- [clients/claude-code-hook/README.md](/Users/users/workspace/sprint-undertaker/clients/claude-code-hook/README.md)
- [clients/claude-code-hook/sprint_undertaker_hook.py](/Users/users/workspace/sprint-undertaker/clients/claude-code-hook/sprint_undertaker_hook.py)

로컬 파일 설치 대신 서버 installer도 사용할 수 있습니다.

```bash
curl -fsSL "http://localhost:8000/install/claude-code.sh?api_key=su_sk_...&installation_name=local-claude" | bash
```

설치 후에는 Claude settings에 hook snippet을 추가하면 되고, 이후 사용자는 Claude Code를 평소처럼 사용하면 됩니다.
