test:
	poetry run pytest
	poetry run flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

format:
	black .
	isort .

generate:
	poetry run python src/docker_composer/_utils/generate_class.py
