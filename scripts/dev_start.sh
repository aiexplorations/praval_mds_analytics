#!/bin/bash
set -e

echo "========================================="
echo "Starting Development Environment"
echo "========================================="
echo ""

# Run tests first
echo "→ Step 1: Running pre-deployment tests..."
./scripts/run_tests.sh || {
    echo ""
    echo "❌ Tests failed! Cannot start containers."
    echo "   Fix the failing tests before deployment."
    exit 1
}

# If tests pass, start containers
echo ""
echo "→ Step 2: Starting Docker containers..."
docker-compose up -d || {
    echo "❌ Failed to start containers"
    exit 1
}

# Wait for services to be healthy
echo ""
echo "→ Step 3: Waiting for services to be ready..."
echo "   (This may take 30-60 seconds for all services to initialize)"

max_wait=120
elapsed=0
all_healthy=false

while [ $elapsed -lt $max_wait ]; do
    sleep 5
    elapsed=$((elapsed + 5))

    # Check if analytics-agents service is healthy
    if docker-compose ps | grep -q "analytics-agents.*healthy\|analytics-agents.*Up"; then
        all_healthy=true
        break
    fi

    echo "   Waiting... (${elapsed}s / ${max_wait}s)"
done

if [ "$all_healthy" = false ]; then
    echo "⚠ Services did not become healthy within ${max_wait}s"
    echo "   Continuing anyway, but services may not be ready..."
fi

# Run E2E smoke tests
echo ""
echo "→ Step 4: Running E2E smoke tests..."
if [ -f "tests/e2e/test_basic_smoke.py" ]; then
    source ./venv/bin/activate
    pytest tests/e2e/test_basic_smoke.py -v --tb=short || {
        echo ""
        echo "⚠ E2E smoke tests failed!"
        echo "   Services are running but may not be functioning correctly."
        echo "   Check logs with:"
        echo "     docker logs analytics-agents --tail=50"
        echo "     docker-compose logs"
        exit 1
    }
    echo "✓ E2E smoke tests passed"
else
    echo "⚠ E2E smoke tests not found, skipping..."
fi

echo ""
echo "========================================="
echo "✓ Development environment is ready!"
echo "========================================="
echo ""
echo "Access points:"
echo "  • Frontend:    http://localhost:3000"
echo "  • Agents API:  http://localhost:8000/docs"
echo "  • Cube.js:     http://localhost:4000"
echo "  • Airflow:     http://localhost:8080 (admin/admin)"
echo ""
echo "Useful commands:"
echo "  • View logs:         docker-compose logs -f"
echo "  • Restart services:  docker-compose restart"
echo "  • Stop services:     docker-compose down"
echo "  • Run tests:         make test"
echo ""
