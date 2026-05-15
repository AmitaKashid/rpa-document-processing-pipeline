install:
	python -m pip install -e ".[dev]"

run-api:
	uvicorn app.main:app --reload

run-sample:
	python scripts/run_sample_pipeline.py

test:
	pytest -q

lint:
	ruff check app tests scripts
