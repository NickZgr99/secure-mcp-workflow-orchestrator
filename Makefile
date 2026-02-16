.PHONY: run-api run-worker test install

install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install poetry && poetry install --no-root

run-api:
	. .venv/bin/activate && export PYTHONPATH=. && uvicorn apps.api.app.main:app --reload --port 8000

run-worker:
	. .venv/bin/activate && export PYTHONPATH=. && python -m apps.worker.app.main

test:
	. .venv/bin/activate && export PYTHONPATH=. && pytest

lint:
	poetry run ruff check .
	poetry run black --check .
