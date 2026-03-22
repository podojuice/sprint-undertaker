# Sprint Undertaker

Turn your Claude Code activity into RPG character growth.

Sprint Undertaker tracks your coding sessions through Claude Code hooks and converts them into experience points, stats, and titles — without ever collecting your actual code, prompts, or file paths.

## How it works

1. Install the Claude Code plugin
2. A character is created when you register
3. Every Claude Code turn (`UserPromptSubmit → Stop`) is summarized locally and sent as privacy-safe metadata
4. The server calculates EXP, stats, and titles based on your activity
5. Check your character status directly in Claude Code via the status line or `/undertaker:character-status`

## Claude Code Plugin

Install via the Claude Code marketplace:

```
/plugin marketplace add https://github.com/podojuice/sprint-undertaker-marketplace
/plugin install sprint-undertaker
```

Then register or log in:

```
/undertaker:register
/undertaker:login
```

Available skills:

| Skill | Description |
|---|---|
| `/undertaker:character-status` | Character level, stats, and active title |
| `/undertaker:titles` | All unlocked and locked titles |
| `/undertaker:project` | Current weekly project progress |
| `/undertaker:profile` | Look up another user's public profile |
| `/undertaker:help` | List all available skills |

## Privacy

Sprint Undertaker never collects:

- Code content
- Prompt or response text
- Command text
- File or directory paths

Only aggregated, non-identifying metadata is sent per turn: tool call counts, success/failure counts, prompt count, prompt length bucket, and model name.

## Stats

Characters grow across three stats:

- **impl** — implementation activity (successful edits)
- **stability** — reliability (successful validations)
- **focus** — engagement depth (prompt count and length)

Level formula: `required_exp = 100 × level^1.5`

## Self-hosting

Requirements: Python 3.12+, PostgreSQL, [uv](https://docs.astral.sh/uv/)

```bash
git clone https://github.com/podojuice/sprint-undertaker
cd sprint-undertaker
cp .env.example .env  # fill in your values
docker compose up --build
```

Run migrations:

```bash
uv run alembic upgrade head
```

The app runs at `http://localhost:8000`.

### Environment variables

See `.env.example` for all required variables. Key ones:

| Variable | Description |
|---|---|
| `RPG_DATABASE_URL` | PostgreSQL connection string |
| `RPG_SECRET_KEY` | JWT signing secret |
| `RPG_BASE_URL` | Public base URL of the server |

### Testing

```bash
docker compose up -d db_test
RPG_DATABASE_URL=postgresql+asyncpg://rpg:rpg@localhost:5433/rpg_test uv run pytest
```

## Tech stack

- **Server**: FastAPI, SQLAlchemy (async), Alembic, PostgreSQL
- **Client**: Claude Code plugin (Python scripts + SKILL.md)
- **Auth**: JWT + email verification

## License

MIT
