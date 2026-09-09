#!/usr/bin/env bash
set -euo pipefail
uv run pytest tests/ --cov=src --cov-report=term-missing
