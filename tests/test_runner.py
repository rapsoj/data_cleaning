"""
Simple test runner for data validation
"""
import pandas as pd
from typing import Dict, List, Callable, Any
import logging
import importlib
import inspect
from pathlib import Path


class TestRunner:
    """Lightweight test runner for cleaned data validation"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tests = self._discover_tests()

    def _discover_tests(self) -> Dict[str, Callable]:
        """Discover all test functions in the tests/ directory"""
        tests = {}
        tests_dir = Path("tests")

        if not tests_dir.exists():
            self.logger.warning("No tests/ directory found")
            return tests

        # Import all test modules
        for py_file in tests_dir.glob("*.py"):
            if py_file.name.startswith('_') or py_file.name == '__init__.py' or py_file.name == 'test_runner.py':
                continue

            module_name = py_file.stem
            try:
                module = importlib.import_module(f"tests.{module_name}")

                # Find all functions that start with 'test_'
                for name, func in inspect.getmembers(module, inspect.isfunction):
                    if name.startswith('test_'):
                        tests[f"{module_name}.{name}"] = func
                        self.logger.debug(f"Discovered test: {module_name}.{name}")

            except Exception as e:
                self.logger.error(f"Failed to load test module {module_name}: {e}")

        return tests

    def run_tests(self, df: pd.DataFrame, test_subset: List[str] = None) -> Dict[str, Any]:
        """
        Run tests on cleaned data

        Args:
            df: Cleaned DataFrame to test
            test_subset: Optional list of specific tests to run

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

        # Determine which tests to run
        if test_subset:
            tests_to_run = {k: v for k, v in self.tests.items() if k in test_subset}
        else:
            tests_to_run = self.tests

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
        return list(self.tests.keys())