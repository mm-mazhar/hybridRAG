.PHONY: setup lint typecheck test

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
