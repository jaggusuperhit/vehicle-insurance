#!/usr/bin/env python
"""
Script to run tests for the Vehicle Insurance Prediction application.
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

def setup_test_environment():
    """Set up the test environment."""
    print("Setting up test environment...")

    # Create reports directory if it doesn't exist
    reports_dir = Path("tests/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Set environment variables for testing
    os.environ["ENVIRONMENT"] = "testing"

    # Return success
    return True

def run_tests(args):
    """Run the tests."""
    print(f"Running tests with {'coverage' if args.coverage else 'no coverage'}...")

    # Build the command
    cmd = ["pytest"]

    # Add verbosity
    if args.verbose:
        cmd.append("-v")

    # Add coverage
    if args.coverage:
        cmd.extend(["--cov=src", "--cov-report=term", "--cov-report=xml:tests/reports/coverage.xml"])

    # Add test path
    if args.test_path:
        cmd.append(args.test_path)

    # Run the command
    result = subprocess.run(cmd)

    # Return success or failure
    return result.returncode == 0

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run tests for the Vehicle Insurance Prediction application.")
    parser.add_argument("-c", "--coverage", action="store_true", help="Run tests with coverage")
    parser.add_argument("-v", "--verbose", action="store_true", help="Run tests with verbose output")
    parser.add_argument("test_path", nargs="?", help="Path to test file or directory")

    args = parser.parse_args()

    # Set up the test environment
    if not setup_test_environment():
        print("Failed to set up test environment.")
        return 1

    # Run the tests
    if not run_tests(args):
        print("Tests failed.")
        return 1

    print("Tests passed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
