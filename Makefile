test:
	poetry run pytest

format:
	black .
	isort .
