.PHONY: help install install-dev test test-verbose lint clean run-example

help:
	@echo "MDMI CLI Development Commands"
	@echo "============================"
	@echo "install      Install package in development mode"
	@echo "install-dev  Install with development dependencies"
	@echo "test         Run all tests"
	@echo "test-verbose Run tests with verbose output"
	@echo "lint         Run linting checks"
	@echo "clean        Clean build artifacts"
	@echo "run-example  Run example with fake interface"

install:
	pip3 install -e .
.PHONY: install

install-dev:
	pip3 install -e ".[dev]"
.PHONY: install-dev

test:
	python3 -m pytest tests/ -v
.PHONY: test

test-verbose:
	python3 -m pytest tests/ -v -s
.PHONY: test-verbose

lint:
	ruff check --fix .
.PHONY: lint

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
.PHONY: clean

run-example:
	@echo "Creating example TFI file..."
	@python3 -c "import pathlib; pathlib.Path('example.tfi').write_bytes(b'\\x23' + b'\\x00' * 41)"
	@echo "Loading preset with fake interface..."
	mdmi load-preset example.tfi --channel 0 --fake
	@echo "Cleaning up..."
	@rm -f example.tfi
.PHONY: run-example