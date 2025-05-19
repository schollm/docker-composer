test:
	uv run pytest
	uv run flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

format:
	black .
	isort .

publish:
	uv build
	uv publish
generate:
	uv run python src/docker_composer/_utils/generate_class.py
