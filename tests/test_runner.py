"""
Simple test runner for data validation
Supports both standard tests and cleaner-specific custom tests
"""
import pandas as pd
from typing import Dict, List, Callable, Any, Optional
import logging
import importlib
import importlib.util
import inspect
from pathlib import Path
import sys


class TestRunner:
    """Lightweight test runner for cleaned data validation"""

    def __init__(self, cleaner_dir: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.cleaner_dir = cleaner_dir
        self.standard_tests = self._discover_standard_tests()
        self.custom_tests = self._discover_custom_tests() if cleaner_dir else {}

    def _discover_standard_tests(self) -> Dict[str, Callable]:
        """Discover all standard test functions in the tests/ directory"""
        tests = {}
        tests_dir = Path("tests")

        if not tests_dir.exists():
            self.logger.warning("No tests/ directory found")
            return tests

        # Import standard_tests.py
        standard_tests_file = tests_dir / "standard_tests.py"
        if standard_tests_file.exists():
            try:
                module = importlib.import_module("tests.standard_tests")

                # Find all functions that start with 'test_'
                for name, func in inspect.getmembers(module, inspect.isfunction):
                    if name.startswith('test_'):
                        tests[f"standard.{name}"] = func
                        self.logger.debug(f"Discovered standard test: {name}")

            except Exception as e:
                self.logger.error(f"Failed to load standard tests: {e}")

        return tests

    def _discover_custom_tests(self) -> Dict[str, Callable]:
        """Discover custom tests from the cleaner's directory"""
        tests = {}

        if not self.cleaner_dir:
            return tests

        # Look for custom_tests.py in the cleaner directory
        custom_tests_file = self.cleaner_dir / "custom_tests.py"

        if not custom_tests_file.exists():
            self.logger.info(f"No custom tests found for cleaner at {self.cleaner_dir}")
            return tests

        try:
            # Load the module from file
            spec = importlib.util.spec_from_file_location(
                f"cleaners.{self.cleaner_dir.name}.custom_tests",
                custom_tests_file
            )
            module = importlib.util.module_from_spec(spec)

            # Add cleaner directory to path temporarily
            old_path = sys.path.copy()
            sys.path.insert(0, str(self.cleaner_dir))

            try:
                spec.loader.exec_module(module)
            finally:
                sys.path = old_path

            # Find all functions that start with 'test_'
            for name, func in inspect.getmembers(module, inspect.isfunction):
                if name.startswith('test_'):
                    tests[f"custom.{name}"] = func
                    self.logger.debug(f"Discovered custom test: {name}")

        except Exception as e:
            self.logger.error(f"Failed to load custom tests from {custom_tests_file}: {e}")

        return tests

    def run_tests(self, df: pd.DataFrame, test_subset: List[str] = None,
                  skip_custom: bool = False, skip_standard: bool = False) -> Dict[str, Any]:
        """
        Run tests on cleaned data

        Args:
            df: Cleaned DataFrame to test
            test_subset: Optional list of specific tests to run
            skip_custom: Skip custom tests from the cleaner
            skip_standard: Skip standard tests

        Returns:
            Dictionary with test results
        """
        results = {
            'passed': True,
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': {}
        }

        # Combine standard and custom tests based on flags
        all_tests = {}

        if not skip_standard:
            all_tests.update(self.standard_tests)

        if not skip_custom:
            all_tests.update(self.custom_tests)

        # Determine which tests to run
        if test_subset:
            tests_to_run = {k: v for k, v in all_tests.items()
                           if any(k.endswith(f".{test}") for test in test_subset)}
        else:
            tests_to_run = all_tests

        # Run each test
        for test_name, test_func in tests_to_run.items():
            results['total_tests'] += 1

            try:
                # Call the test function with just the DataFrame
                test_result = test_func(df)

                # Process result
                if isinstance(test_result, bool):
                    # Simple pass/fail
                    passed = test_result
                    message = "Passed" if passed else "Failed"
                    details = {}
                elif isinstance(test_result, dict):
                    # Detailed result
                    passed = test_result.get('passed', False)
                    message = test_result.get('message', '')
                    details = test_result.get('details', {})
                else:
                    # Invalid return type
                    passed = False
                    message = f"Invalid test return type: {type(test_result)}"
                    details = {}

                # Record result
                results['test_details'][test_name] = {
                    'passed': passed,
                    'message': message,
                    'details': details
                }

                if passed:
                    results['passed_tests'] += 1
                    self.logger.info(f"✓ {test_name}: {message}")
                else:
                    results['failed_tests'] += 1
                    results['passed'] = False
                    self.logger.warning(f"✗ {test_name}: {message}")

            except Exception as e:
                # Test crashed
                results['failed_tests'] += 1
                results['passed'] = False
                results['test_details'][test_name] = {
                    'passed': False,
                    'message': f"Test crashed: {str(e)}",
                    'details': {'error': str(e)}
                }
                self.logger.error(f"✗ {test_name}: Test crashed - {e}")

        # Summary
        self.logger.info(
            f"Test summary: {results['passed_tests']}/{results['total_tests']} passed"
        )

        return results

    def list_tests(self) -> List[str]:
        """List all available tests"""
        all_tests = list(self.standard_tests.keys()) + list(self.custom_tests.keys())
        return sorted(all_tests)