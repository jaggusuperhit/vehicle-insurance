#!/bin/bash
# Script to run tests for the Vehicle Insurance Prediction application

# Set up environment
export ENVIRONMENT="testing"

# Create reports directory
mkdir -p tests/reports

# Run tests with coverage
echo "Running tests with coverage..."
python -m pytest --cov=src --cov-report=xml:tests/reports/coverage.xml --cov-report=term

# Check if tests passed
if [ $? -eq 0 ]; then
    echo "Tests passed!"
    exit 0
else
    echo "Tests failed!"
    exit 1
fi
