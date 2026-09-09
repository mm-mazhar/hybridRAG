.PHONY: setup lint typecheck test api web

setup:
	uv sync
	uv run lefthook install

lint:
	uv run ruff check .
	uv run ruff format --check .

typecheck:
	uv run mypy

test:
	uv run pytest -q

api:
	uv run uvicorn api.main:app --reload --reload-dir src --reload-dir config --app-dir src --port 8000

web:
	pnpm --dir web dev
