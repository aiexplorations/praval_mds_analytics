.PHONY: help test test-unit test-integration test-e2e coverage clean deploy start stop restart logs

help:
	@echo "Praval Manufacturing Analytics - Testing & Deployment"
	@echo ""
	@echo "Testing commands:"
	@echo "  make test              - Run unit and integration tests"
	@echo "  make test-unit         - Run unit tests only"
	@echo "  make test-integration  - Run integration tests only"
	@echo "  make test-e2e          - Run end-to-end tests"
	@echo "  make coverage          - Generate coverage report"
	@echo ""
	@echo "Development commands:"
	@echo "  make deploy            - Run tests and start containers (test-first deployment)"
	@echo "  make start             - Start containers (without tests)"
	@echo "  make stop              - Stop all containers"
	@echo "  make restart           - Restart all containers"
	@echo "  make logs              - View container logs"
	@echo ""
	@echo "Maintenance commands:"
	@echo "  make clean             - Remove cache files and coverage reports"
	@echo ""

test: test-unit test-integration
	@echo ""
	@echo "✓ All tests passed!"

test-unit:
	@echo "Running unit tests..."
	@./venv/bin/pytest tests/unit -v --tb=short --no-cov

test-integration:
	@echo "Running integration tests..."
	@./venv/bin/pytest tests/integration -v --tb=short --no-cov

test-e2e:
	@echo "Running end-to-end tests..."
	@./venv/bin/pytest tests/e2e -v --tb=short --no-cov

coverage:
	@echo "Generating coverage report..."
	@./venv/bin/pytest tests/ --cov --cov-report=html --cov-report=term-missing
	@echo ""
	@echo "✓ Coverage report generated: htmlcov/index.html"
	@echo "  Open with: open htmlcov/index.html"

clean:
	@echo "Cleaning cache files..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@rm -rf htmlcov .coverage .pytest_cache
	@echo "✓ Cache cleaned"

deploy:
	@echo "Starting test-first deployment..."
	@./scripts/run_tests.sh
	@./scripts/dev_start.sh

start:
	@echo "Starting containers (without tests)..."
	@docker-compose up -d
	@echo "✓ Containers started"

stop:
	@echo "Stopping containers..."
	@docker-compose down
	@echo "✓ Containers stopped"

restart:
	@echo "Restarting containers..."
	@docker-compose restart
	@echo "✓ Containers restarted"

logs:
	@docker-compose logs -f
