.PHONY: setup test format lint run-api train

setup:
\tpython -m pip install -r requirements.txt
\tpre-commit install

format:
\tblack src tests
\tisort src tests

lint:
\tflake8 src tests

test:
\tpytest -q --cov=src --cov-report=term-missing

train:
\tpython -m src.training.train

run-api:
\tuvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload
