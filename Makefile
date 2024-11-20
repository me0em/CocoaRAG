.PHONY: test test-coverage format lint mypy pyright ruff

install:
	poetry config virtualenvs.in-project true
	poetry install

test:
	poetry run pytest -s ./cocoarag/**

test-coverage:
	poetry run pytest \
		--cov-config=.coveragerc \
		--cov-report=term \
		--cov-report=html \
		--cov-report=xml \
		--no-cov-on-fail \
		--cov=. \
		-s ./cocoarag/**

format:
	poetry run black .

lint: ruff  #  mypy pyright

mypy:
	poetry run mypy --ignore-missing-imports .

pyright:
	poetry run pyright

ruff:
	poetry run ruff check