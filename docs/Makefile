# Makefile for Construction Project Tests

.PHONY: help install test test-backend test-frontend test-coverage test-all clean lint format

# Default target
help:
	@echo "Available commands:"
	@echo "  install          - Install all dependencies"
	@echo "  test             - Run all tests"
	@echo "  test-backend     - Run Django backend tests"
	@echo "  test-frontend    - Run JavaScript frontend tests"
	@echo "  test-coverage    - Run tests with coverage report"
	@echo "  test-all         - Run all tests with coverage"
	@echo "  clean            - Clean up test artifacts"
	@echo "  lint             - Run linting checks"
	@echo "  format           - Format code"

# Install dependencies
install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt
	pip install -r requirements-test.txt
	@echo "Installing JavaScript dependencies..."
	npm install

# Run all tests
test: test-backend test-frontend

# Run Django backend tests
test-backend:
	@echo "Running Django backend tests..."
	source env/bin/activate && python manage.py test tests/construction/ --verbosity=2

# Run JavaScript frontend tests
test-frontend:
	@echo "Running JavaScript frontend tests..."
	npm test

# Run tests with coverage
test-coverage:
	@echo "Running tests with coverage..."
	source env/bin/activate && coverage run --source='.' manage.py test tests/construction/
	source env/bin/activate && coverage report
	source env/bin/activate && coverage html

# Run all tests with coverage
test-all: test-coverage
	@echo "Running JavaScript tests with coverage..."
	npm test -- --coverage

# Clean up test artifacts
clean:
	@echo "Cleaning up test artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf node_modules/.cache/
	rm -rf coverage/

# Run linting checks
lint:
	@echo "Running Python linting..."
	source env/bin/activate && flake8 construction/ dashboard/ tests/
	@echo "Running JavaScript linting..."
	npm run lint

# Format code
format:
	@echo "Formatting Python code..."
	source env/bin/activate && black construction/ dashboard/ tests/
	@echo "Formatting JavaScript code..."
	npm run format

# Run specific test files
test-models:
	@echo "Running model tests..."
	source env/bin/activate && python manage.py test tests.construction.test_models --verbosity=2

test-serializers:
	@echo "Running serializer tests..."
	source env/bin/activate && python manage.py test tests.construction.test_serializers --verbosity=2

test-api:
	@echo "Running API tests..."
	source env/bin/activate && python manage.py test tests.construction.test_transaction_api --verbosity=2

# Run tests in parallel
test-parallel:
	@echo "Running tests in parallel..."
	source env/bin/activate && python -m pytest tests/ -n auto --verbosity=2

# Run tests with specific markers
test-slow:
	@echo "Running slow tests..."
	source env/bin/activate && python -m pytest tests/ -m slow --verbosity=2

test-fast:
	@echo "Running fast tests..."
	source env/bin/activate && python -m pytest tests/ -m "not slow" --verbosity=2

# Database tests
test-db:
	@echo "Running database tests..."
	source env/bin/activate && python manage.py test tests.construction.test_models tests.construction.test_transaction_api --verbosity=2

# API integration tests
test-api-integration:
	@echo "Running API integration tests..."
	source env/bin/activate && python manage.py test tests.construction.test_transaction_api.TransactionIntegrationTestCase --verbosity=2

# Performance tests
test-performance:
	@echo "Running performance tests..."
	source env/bin/activate && python -m pytest tests/ -m performance --verbosity=2

# Security tests
test-security:
	@echo "Running security tests..."
	source env/bin/activate && bandit -r construction/ dashboard/
	source env/bin/activate && safety check

# Generate test data
generate-test-data:
	@echo "Generating test data..."
	source env/bin/activate && python manage.py shell -c "from tests.test_data_generator import generate_test_data; generate_test_data()"

# Run tests with specific Django settings
test-debug:
	@echo "Running tests in debug mode..."
	source env/bin/activate && python manage.py test tests/construction/ --verbosity=2 --debug-mode

# Run tests and generate report
test-report:
	@echo "Running tests and generating report..."
	source env/bin/activate && python -m pytest tests/ --html=reports/test_report.html --self-contained-html --verbosity=2
