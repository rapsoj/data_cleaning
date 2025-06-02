import pandas as pd
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from tests.test_registry import TestRegistry


class TestRunner:
    """Main test orchestrator that runs standard and custom tests"""

    def __init__(self, test_specs_dir: str = "tests/test_specs"):
        self.test_specs_dir = Path(test_specs_dir)
        self.logger = logging.getLogger(__name__)
        self.test_registry = TestRegistry()

        # Auto-discover and register all available test functions
        self.test_registry.auto_discover()

    def run_tests(self, cleaner_name: str, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Run tests for a cleaner. First runs standard tests, then any custom tests.

        Args:
            cleaner_name: Name of the cleaner
            df: Cleaned DataFrame to test

        Returns:
            Dict with keys: passed (bool), errors (list), warnings (list), details (dict)
        """
        results = {
            'passed': True,
            'errors': [],
            'warnings': [],
            'details': {}
        }

        # Run standard tests (these are just tests without a YAML spec)
        self.logger.info(f"Running standard tests for {cleaner_name}")
        standard_results = self._run_standard_tests(df)
        results['details']['standard'] = standard_results

        # Aggregate standard test results
        self._aggregate_results(standard_results, results)

        # Check for custom test specification
        custom_spec = self._load_custom_spec(cleaner_name)
        if custom_spec:
            self.logger.info(f"Running custom tests for {cleaner_name}")
            custom_results = self._run_custom_tests(df, custom_spec)
            results['details']['custom'] = custom_results

            # Aggregate custom test results
            self._aggregate_results(custom_results, results)

        # Log summary
        if results['passed']:
            self.logger.info(f"All tests passed for {cleaner_name}")
        else:
            self.logger.error(
                f"Tests failed for {cleaner_name}: {len(results['errors'])} errors, {len(results['warnings'])} warnings")

        return results

    def _run_standard_tests(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Run built-in standard tests that apply to all cleaners"""
        results = {}

        # Standard test configuration - these always run
        standard_tests = {
            'not_empty': {
                'type': 'not_empty',
                'params': {},
                'severity': 'error'
            },
            'no_null_columns': {
                'type': 'no_null_columns',
                'params': {},
                'severity': 'error'
            },
            'duplicate_rows': {
                'type': 'duplicate_rows',
                'params': {'threshold': 1},
                'severity': 'warning'
            },
            'data_types': {
                'type': 'data_types',
                'params': {},
                'severity': 'warning'
            },
        }

        # Run each standard test
        for test_name, test_config in standard_tests.items():
            test_type = test_config['type']
            params = test_config.get('params', {})
            severity = test_config.get('severity', 'error')

            try:
                test_func = self.test_registry.get_test(test_type)
                if test_func:
                    result = test_func(df, params)
                    result['severity'] = severity
                    results[test_name] = result
                else:
                    self.logger.warning(f"Standard test '{test_type}' not found in registry")
            except Exception as e:
                results[test_name] = {
                    'passed': False,
                    'message': f"Standard test failed with error: {str(e)}",
                    'severity': 'error',
                    'details': {'error': str(e)}
                }

        return results

    def _run_custom_tests(self, df: pd.DataFrame, spec: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Run custom tests defined in YAML spec"""
        results = {}

        for test_name, test_config in spec.get('tests', {}).items():
            test_type = test_config.get('type')
            params = test_config.get('params', {})
            severity = test_config.get('severity', 'error')

            try:
                # Get test function from registry
                test_func = self.test_registry.get_test(test_type)
                if test_func:
                    result = test_func(df, params)
                    result['severity'] = severity
                    results[test_name] = result
                else:
                    results[test_name] = {
                        'passed': False,
                        'message': f"Unknown test type: {test_type}",
                        'severity': 'error',
                        'details': {}
                    }
            except Exception as e:
                results[test_name] = {
                    'passed': False,
                    'message': f"Test failed with error: {str(e)}",
                    'severity': 'error',
                    'details': {'error': str(e), 'test_type': test_type}
                }

        return results

    def _aggregate_results(self, test_results: Dict[str, Dict[str, Any]],
                           aggregate: Dict[str, Any]) -> None:
        """Aggregate test results into the main results dictionary"""
        for test_name, test_result in test_results.items():
            if not test_result['passed']:
                message = f"[{test_name}] {test_result['message']}"
                if test_result['severity'] == 'error':
                    aggregate['errors'].append(message)
                    aggregate['passed'] = False
                else:
                    aggregate['warnings'].append(message)

    def _load_custom_spec(self, cleaner_name: str) -> Optional[Dict[str, Any]]:
        """Load custom test specification if it exists"""
        spec_path = self.test_specs_dir / f"{cleaner_name}.yaml"
        if spec_path.exists():
            try:
                with open(spec_path, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                self.logger.error(f"Failed to load test spec for {cleaner_name}: {e}")
        return None

    def list_available_tests(self) -> Dict[str, str]:
        """Get all available test types and their descriptions"""
        return self.test_registry.list_tests()