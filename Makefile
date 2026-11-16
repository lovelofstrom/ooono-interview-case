.PHONY: setup all

setup:
	uv sync
	test -f .env || cp .env.example .env

all:
	uv run python -m ingestion
	cd dbt && uv run dbt build
