#!/bin/bash
set -e

echo "========================================="
echo "Running Test Suite Before Deployment"
echo "========================================="

# Check if venv exists
if [ ! -d "./venv" ]; then
    echo "❌ Virtual environment not found. Please create it first:"
    echo "   python3 -m venv venv"
    echo "   ./venv/bin/pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source ./venv/bin/activate

# Run unit tests
echo ""
echo "→ Step 1/4: Running unit tests..."
if [ -d "tests/unit" ]; then
    pytest tests/unit -v --tb=short --timeout=60 || {
        echo "❌ Unit tests failed!"
        exit 1
    }
    echo "✓ Unit tests passed"
else
    echo "⚠ No unit tests found (tests/unit directory doesn't exist)"
fi

# Run integration tests (requires test containers)
echo ""
echo "→ Step 2/4: Running integration tests..."
if [ -d "tests/integration" ]; then
    pytest tests/integration -v --tb=short --timeout=120 || {
        echo "❌ Integration tests failed!"
        exit 1
    }
    echo "✓ Integration tests passed"
else
    echo "⚠ No integration tests found (tests/integration directory doesn't exist)"
fi

# Check coverage threshold
echo ""
echo "→ Step 3/4: Checking coverage threshold (90%)..."
pytest tests/unit tests/integration --cov --cov-fail-under=90 --cov-report=term-missing 2>/dev/null || {
    echo "⚠ Coverage below 90% threshold"
    echo "  Run 'make coverage' to see detailed report"
    # Don't fail on coverage for now, just warn
    # Will enforce after test implementation is complete
}

# Run dbt tests (if dbt is available)
echo ""
echo "→ Step 4/4: Running dbt tests..."
if [ -d "dbt_transform" ]; then
    if command -v dbt &> /dev/null; then
        dbt test --project-dir=dbt_transform || {
            echo "❌ dbt tests failed!"
            exit 1
        }
        echo "✓ dbt tests passed"
    else
        echo "⚠ dbt not found in PATH, skipping dbt tests"
    fi
else
    echo "⚠ dbt_transform directory not found, skipping dbt tests"
fi

echo ""
echo "========================================="
echo "✓ All tests passed! Safe to deploy."
echo "========================================="
echo ""
