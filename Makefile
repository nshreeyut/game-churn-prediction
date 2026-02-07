.PHONY: install lint format test train dashboard clean

install:
	uv sync --all-extras

lint:
	uv run ruff check src/ tests/ dashboard/
	uv run ruff format --check src/ tests/ dashboard/

format:
	uv run ruff check --fix src/ tests/ dashboard/
	uv run ruff format src/ tests/ dashboard/

typecheck:
	uv run mypy src/

test:
	uv run pytest

train:
	uv run python -m game_churn.models.train

dashboard:
	uv run streamlit run dashboard/app.py

collect:
	uv run python -m game_churn.collectors.run_all

features:
	uv run python -m game_churn.features.build

clean:
	rm -rf .ruff_cache .mypy_cache .pytest_cache htmlcov dist
	find . -type d -name __pycache__ -exec rm -rf {} +
