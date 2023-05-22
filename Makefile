test:
	poetry run pytest

format:
	black .
	isort .

generate:
	poetry run python src/docker_composer/_utils/generate_class.py
