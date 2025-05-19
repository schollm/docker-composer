test:
	uv run ruff check
	uv run ruff format --check
	uv run pytest

format:
	uv run ruff format

publish:
	uv build
	uv publish
generate:
	uv run python src/docker_composer/_utils/generate_class.py
