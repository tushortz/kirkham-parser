"""Comprehensive test runner for the Kirkham Grammar Parser.

This module provides utilities for running all tests and generating
comprehensive coverage reports.

Author: Based on Samuel Kirkham's English Grammar (1829)
"""

import sys
import unittest
from pathlib import Path


def run_all_tests():
    """Run all tests in the test suite."""
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(start_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


def run_specific_tests(test_patterns):
    """Run specific test patterns."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for pattern in test_patterns:
        tests = loader.loadTestsFromName(pattern)
        suite.addTests(tests)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific tests
        test_patterns = sys.argv[1:]
        success = run_specific_tests(test_patterns)
    else:
        # Run all tests
        success = run_all_tests()

    sys.exit(0 if success else 1)
