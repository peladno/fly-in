PYTHON = python3
PIP = pip3
VENV = .venv

.PHONY: all install run debug clean lint test

all: run

install:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/$(PIP) install --upgrade pip
	$(VENV)/bin/$(PIP) install -r requirements.txt

run:
	$(PYTHON) src/main.py $(MAP)

debug:
	$(PYTHON) src/main.py --debug $(MAP)

lint:
	flake8 src tests
	mypy src tests

test:
	pytest tests/

clean:
	rm -rf __pycache__ src/**/__pycache__ tests/__pycache__
	rm -rf .pytest_cache .mypy_cache
	rm -rf $(VENV)
