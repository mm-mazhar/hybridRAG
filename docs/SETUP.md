# Setup

## Backend (uv)

```bash
uv sync
uv run lefthook install
cp .env.example .env
```

Set `LLM_API_KEY`. An existing `OPENAI_API_KEY` still works as a fallback.

Model URL and slugs live in `config/model_config.yaml`.

```bash
uv run uvicorn api.main:app --reload --reload-dir src --reload-dir config --app-dir src --port 8000
```

## Frontend (pnpm)

```bash
cd web
pnpm install
cp .env.example .env.local
```

Put the same `LLM_API_KEY` in `web/.env.local` and keep `FASTAPI_URL=http://127.0.0.1:8000`.

```bash
pnpm dev
```

UI: http://localhost:3000  
API docs: http://127.0.0.1:8000/docs

## Docker

```bash
docker compose up --build
```
