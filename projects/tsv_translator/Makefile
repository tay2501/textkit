# Makefile for TSV Translator project

.PHONY: help install install-dev test test-cov lint format clean build docs

# Default target
help:
	@echo "Available targets:"
	@echo "  install     - Install project dependencies"
	@echo "  install-dev - Install development dependencies"
	@echo "  test        - Run tests"
	@echo "  test-cov    - Run tests with coverage report"
	@echo "  lint        - Run linting (ruff)"
	@echo "  format      - Format code (black)"
	@echo "  clean       - Clean build artifacts"
	@echo "  build       - Build the package"
	@echo "  docs        - Generate documentation"

# Install dependencies
install:
	uv sync

# Install development dependencies
install-dev:
	uv sync --extra dev

# Run tests
test:
	uv run pytest

# Run tests with coverage
test-cov:
	uv run pytest --cov=tsv_translator --cov-report=term-missing --cov-report=html

# Run quick tests (unit tests only)
test-quick:
	uv run pytest -m "unit" --tb=short

# Run integration tests
test-integration:
	uv run pytest -m "integration"

# Run linting
lint:
	uv run ruff check .
	uv run ruff format --check .

# Format code
format:
	uv run black .
	uv run ruff format .
	uv run ruff check --fix .

# Type checking (if mypy is added later)
typecheck:
	@echo "Type checking not configured yet"

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build package
build: clean
	uv build

# Install in editable mode
install-editable:
	uv pip install -e .

# Run all quality checks
check: lint test-cov

# Development setup
dev-setup: install-dev
	@echo "Development environment set up!"
	@echo "Run 'make test' to run tests"
	@echo "Run 'make check' to run all quality checks"

# Run performance tests
test-perf:
	uv run pytest -m "slow" -v

# Generate documentation (placeholder)
docs:
	@echo "Documentation generation not configured yet"
	@echo "Consider adding Sphinx configuration"

# Watch mode for tests (requires pytest-watch)
test-watch:
	@echo "Test watch mode not available"
	@echo "Install pytest-watch for continuous testing"

# Security scan (placeholder)
security:
	@echo "Security scanning not configured"
	@echo "Consider adding bandit or safety"

# Benchmark tests
benchmark:
	@echo "Benchmark tests not configured"
	@echo "Consider adding pytest-benchmark"