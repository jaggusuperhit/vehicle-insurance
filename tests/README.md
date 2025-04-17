# Vehicle Insurance Prediction Tests

This directory contains tests for the Vehicle Insurance Prediction application.

## Test Structure

The tests are organized as follows:

- **Unit Tests**: Tests for individual components of the application
  - `tests/unit/entity`: Tests for entity classes
  - `tests/unit/utils`: Tests for utility functions
  - `tests/unit/pipeline`: Tests for pipeline components
- **Integration Tests**: Tests for the interaction between components
  - `tests/integration`: Tests for the FastAPI application
- **Basic Tests**: Simple tests to ensure the environment is set up correctly
  - `tests/test_basic.py`: Basic tests for the environment

## Running Tests

You can run the tests using the `run_tests.py` script:

```bash
# Run all tests
python run_tests.py

# Run tests with coverage
python run_tests.py -c

# Run tests with verbose output
python run_tests.py -v

# Run a specific test file
python run_tests.py tests/unit/utils/test_main_utils.py
```

## Test Coverage

The tests are configured to generate coverage reports in both XML and terminal formats. The XML report is saved to `tests/reports/coverage.xml` and can be used by tools like Codecov to track coverage over time.

## CI/CD Integration

The tests are integrated into the CI/CD pipeline and run automatically on every pull request and push to the main branch. The pipeline is configured to fail if any tests fail.

## Adding New Tests

When adding new tests, follow these guidelines:

1. Place unit tests in the appropriate subdirectory under `tests/unit/`
2. Place integration tests in `tests/integration/`
3. Use pytest fixtures for common setup and teardown
4. Use descriptive test names that clearly indicate what is being tested
5. Use assertions to verify expected behavior
6. Add docstrings to test functions to describe what they test

## Test Dependencies

The test dependencies are listed in `requirements-test.txt` and include:

- pytest: For running tests
- pytest-cov: For generating coverage reports
- httpx: For testing FastAPI applications
