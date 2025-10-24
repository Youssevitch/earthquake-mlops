.PHONY: setup test format lint run-api train

setup:
	python -m pip install -r requirements.txt
	pre-commit install

format:
	black src tests
	isort src tests

lint:
	flake8 src tests

test:
	pytest -q --cov=src --cov-report=term-missing

train:
	python -m src.training.train

run-api:
	uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload
