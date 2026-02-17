.PHONY: install install-dev test test-cov lint format clean build run-example help

# Default target
help:
	@echo "PDF Document Generator - Development Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  install       Install package dependencies"
	@echo "  install-dev   Install with development dependencies"
	@echo "  test          Run tests"
	@echo "  test-cov      Run tests with coverage report"
	@echo "  lint          Run linting checks"
	@echo "  format        Format code with black"
	@echo "  clean         Remove build artifacts"
	@echo "  build         Build distribution packages"
	@echo "  run-example   Generate example PDF"
	@echo "  help          Show this help message"

# Install dependencies
install:
	pip install -r requirements.txt
	pip install -e .

# Install with dev dependencies
install-dev:
	pip install -r requirements.txt
	pip install -e ".[dev]"

# Run tests
test:
	pytest tests/ -v

# Run tests with coverage
test-cov:
	pytest tests/ -v --cov=docgen --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/"

# Run linting
lint:
	flake8 src/docgen tests --max-line-length=100
	mypy src/docgen --ignore-missing-imports

# Format code
format:
	black src/docgen tests --line-length=100

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf src/*.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build distribution
build: clean
	python -m build

# Generate example PDFs
run-example:
	@echo "Generating example PDFs..."
	python -m docgen examples/sample_release_notes.md \
		-o examples/output/sample_release_notes.pdf \
		--template ford_release_notes
	python -m docgen examples/sample_document.adoc \
		-o examples/output/sample_document.pdf \
		--template ford_release_notes
	@echo "Example PDFs generated in examples/output/"

# List available templates
list-templates:
	python -m docgen --list-templates

# Quick test run
quick-test:
	pytest tests/test_parsers.py tests/test_models.py -v
