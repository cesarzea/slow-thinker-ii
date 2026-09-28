.PHONY: setup verify format backend frontend components

export UV_CACHE_DIR ?= $(CURDIR)/.cache/uv
export UV_PYTHON_INSTALL_DIR ?= $(CURDIR)/.cache/python
export PLAYWRIGHT_BROWSERS_PATH ?= $(CURDIR)/.cache/playwright

setup:
	npm ci --ignore-scripts
	uv sync --locked
	npx --no-install playwright install --with-deps chromium

verify:
	uv run --locked python -m tooling.quality.verify

format:
	uv run --locked ruff format backend components examples tooling
	npm run format

backend:
	uv run --locked uvicorn slow_thinker_ii.bootstrap:configured_app --factory --host 127.0.0.1 --port 8000

frontend:
	npm run dev --workspace frontend -- --host 127.0.0.1 --port 5173 --strictPort

components:
	uv run --locked python -m tooling.components --component all
