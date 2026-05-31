.PHONY: install lint format type-check test security pre-commit-check

install:
	pip install -r requirements.txt

lint:
	ruff check .
	black --check .

format:
	ruff check . --fix
	black .

type-check:
	mypy --follow-imports=skip app.py ingest.py

test:
	pytest

security:
	bandit -r app.py ingest.py -ll

pre-commit-check:
	pre-commit run --all-files
