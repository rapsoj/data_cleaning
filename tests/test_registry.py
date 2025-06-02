import importlib
import inspect
from pathlib import Path
from typing import Dict, Any, Callable, Optional
import logging
import os


class TestRegistry:
    """Registry for all available test functions"""

    def __init__(self):
        self.tests: Dict[str, Callable] = {}
        self.logger = logging.getLogger(__name__)

    def register(self, name: str, func: Callable):
        """Register a test function"""
        self.tests[name] = func
        self.logger.debug(f"Registered test: {name}")

    def get_test(self, name: str) -> Optional[Callable]:
        """Get a test function by name"""
        return self.tests.get(name)

    def list_tests(self) -> Dict[str, str]:
        """List all available tests with their docstrings"""
        return {
            name: (func.__doc__ or "No description").strip()
            for name, func in self.tests.items()
        }

    def auto_discover(self):
        """Auto-discover all test functions from test_definitions directory"""
        # Get the path to test_definitions directory
        current_dir = Path(__file__).parent
        test_definitions_dir = current_dir / "test_definitions"

        if not test_definitions_dir.exists():
            self.logger.error(f"test_definitions directory not found at {test_definitions_dir}")
            return

        # Find all Python files in test_definitions directory
        for file_path in test_definitions_dir.glob("*.py"):
            if file_path.name.startswith("__"):
                continue  # Skip __init__.py and other special files

            # Convert file path to module name
            module_name = f"tests.test_definitions.{file_path.stem}"

            try:
                module = importlib.import_module(module_name)
                self._register_module_tests(module)
                self.logger.info(f"Loaded tests from {module_name}")
            except ImportError as e:
                self.logger.error(f"Failed to import {module_name}: {e}")
            except Exception as e:
                self.logger.error(f"Error processing {module_name}: {e}")

    def _register_module_tests(self, module):
        """Register all test functions from a module"""
        registered_count = 0

        for name, obj in inspect.getmembers(module):
            if (inspect.isfunction(obj) and
                    name.startswith('test_') and
                    not name.startswith('_')):
                # Extract test name from function name (test_no_nulls -> no_nulls)
                test_name = name[5:]  # Remove 'test_' prefix
                self.register(test_name, obj)
                registered_count += 1
                self.logger.debug(f"Registered {test_name} from {module.__name__}")

        if registered_count > 0:
            self.logger.info(f"Registered {registered_count} tests from {module.__name__}")


# Global registry instance
test_registry = TestRegistry()


def register_test(name: str):
    """Decorator to register a test function"""

    def decorator(func):
        test_registry.register(name, func)
        return func

    return decorator