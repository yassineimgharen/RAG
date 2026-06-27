install:
	uv sync

run:
	uv run python -m student

lint:
	uv run flake8 .
	uv run mypy . --warn-return-any ...

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .mypy_cache