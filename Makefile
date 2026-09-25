.PHONY: help install generate-data test run docker-up docker-down clean

VENV_PYTHON = ./venv/bin/python
VENV_PYTEST = ./venv/bin/pytest
VENV_PIP = ./venv/bin/pip

help:
	@echo "Luxury VIP Travel CRM Data Engine - Commands:"
	@echo "  make install        Install Python dependencies"
	@echo "  make generate-data  Generate 10k+ synthetic raw records"
	@echo "  make run            Run full ETL pipeline"
	@echo "  make test           Run pytest unit tests"
	@echo "  make docker-up      Spin up PostgreSQL & LocalStack"
	@echo "  make docker-down    Stop Docker containers"
	@echo "  make clean          Clean local output data files & cache"

install:
	$(VENV_PIP) install -r requirements.txt

generate-data:
	$(VENV_PYTHON) scripts/generate_dataset.py --count 10500

run:
	PYTHONPATH=. $(VENV_PYTHON) run_pipeline.py

test:
	PYTHONPATH=. $(VENV_PYTEST) tests/ -v

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

clean:
	rm -f data/raw/*.csv data/cleaned/*.csv data/rejected/*.csv
	rm -rf .pytest_cache __pycache__ src/__pycache__ tests/__pycache__
