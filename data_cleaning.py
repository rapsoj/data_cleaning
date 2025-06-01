import importlib
import sys
from pathlib import Path
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback

from core.base_cleaner import DataCleaner
# from tests.test_framework import TestRunner


class DataCleaningPipeline:
    """Main orchestrator for data cleaning pipeline"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # self.test_runner = TestRunner()
        self._discovered_cleaners = {}
        self._discover_cleaners()

    def _discover_cleaners(self):
        """Automatically discover all available cleaners"""
        # Discover built-in cleaners
        cleaners_dir = Path("cleaners")
        if cleaners_dir.exists():
            for cleaner_path in cleaners_dir.iterdir():
                if cleaner_path.is_dir() and not cleaner_path.name.startswith('_'):
                    self._try_load_cleaner(cleaner_path.name, "cleaners")

        # Discover external cleaners
        external_dir = Path("external_cleaners")
        if external_dir.exists():
            for cleaner_path in external_dir.iterdir():
                if cleaner_path.is_dir() and not cleaner_path.name.startswith('.'):
                    self._try_load_cleaner(cleaner_path.name, "external_cleaners")

    def _try_load_cleaner(self, cleaner_name: str, base_path: str):
        """Try to load a cleaner from a directory"""
        try:
            if base_path == "external_cleaners":
                # For external cleaners, we need to handle imports properly
                cleaner_path = Path(base_path) / cleaner_name

                # Check if __init__.py exists in the cleaner directory
                init_file = cleaner_path / "__init__.py"
                if not init_file.exists():
                    # Create an empty __init__.py to make it a proper package
                    init_file.write_text("")

                # Add the parent directory to sys.path so relative imports work
                parent_path = str(Path(base_path).absolute())
                if parent_path not in sys.path:
                    sys.path.insert(0, parent_path)

                # Import as a package
                module = importlib.import_module(f"{cleaner_name}.data_cleaner")
            else:
                # For built-in cleaners
                module = importlib.import_module(f"{base_path}.{cleaner_name}.data_cleaner")

            # Look for a class named 'Cleaner'
            if hasattr(module, 'Cleaner'):
                cleaner_class = getattr(module, 'Cleaner')

                # Verify it inherits from DataCleaner
                if issubclass(cleaner_class, DataCleaner):
                    self._discovered_cleaners[cleaner_name] = cleaner_class
                    self.logger.info(f"Discovered cleaner: {cleaner_name}")
                else:
                    raise ValueError(
                        f"Cleaner class in {cleaner_name}/data_cleaner.py "
                        f"does not inherit from DataCleaner"
                    )
            else:
                raise ValueError(
                    f"No 'Cleaner' class found in {cleaner_name}/data_cleaner.py"
                )

        except Exception as e:
            self.logger.error(f"Failed to load cleaner {cleaner_name}: {e}")

    def list_cleaners(self) -> List[str]:
        """List all available cleaners"""
        return list(self._discovered_cleaners.keys())

    def get_cleaner_info(self, cleaner_name: str) -> Dict[str, Any]:
        """Get information about a specific cleaner"""
        if cleaner_name not in self._discovered_cleaners:
            raise ValueError(f"Cleaner '{cleaner_name}' not found")

        cleaner = self._discovered_cleaners[cleaner_name]()
        info = {
            'name': cleaner_name,
            'metadata': cleaner.get_metadata()
        }
        return info

    def run_cleaner(self, cleaner_name: str,
                    use_disk: bool = False,
                    test_only: bool = False,
                    output_dir: Optional[Path] = None) -> Optional[pd.DataFrame]:
        """
        Run a single cleaner.

        Args:
            cleaner_name: Name of the cleaner to run
            use_disk: If True, use disk-based processing if available
            test_only: If True, only run tests without saving output
            output_dir: Optional output directory for cleaned data

        Returns:
            Cleaned DataFrame if successful, None if failed
        """
        if cleaner_name not in self._discovered_cleaners:
            raise ValueError(
                f"Cleaner '{cleaner_name}' not found. "
                f"Available cleaners: {', '.join(self.list_cleaners())}"
            )

        try:
            # Instantiate the cleaner
            cleaner = self._discovered_cleaners[cleaner_name]()
            capabilities = cleaner.get_capabilities()

            self.logger.info(f"Running cleaner: {cleaner_name}")

            # Download data
            if use_disk and capabilities['download_to_path']:
                # Use disk-based download
                raw_dir = Path("data/raw") / cleaner_name
                raw_dir.mkdir(parents=True, exist_ok=True)
                data_path = cleaner.download_to_path(raw_dir)
                data_ref = data_path
                self.logger.info(f"Downloaded data to: {data_path}")
            elif capabilities['download_to_df']:
                # Use in-memory download
                data_ref = cleaner.download_to_df()
                self.logger.info(f"Downloaded data to memory")
            else:
                raise NotImplementedError(
                    f"Cleaner {cleaner_name} must implement download_to_df() or download_to_path()"
                )

            # Clean data
            if isinstance(data_ref, Path) and capabilities['clean_from_path']:
                cleaned_df = cleaner.clean_from_path(data_ref)
            elif isinstance(data_ref, pd.DataFrame) and capabilities['clean_from_df']:
                cleaned_df = cleaner.clean_from_df(data_ref)
            elif isinstance(data_ref, Path) and capabilities['clean_from_df']:
                # Load from path and clean in memory
                df = pd.read_csv(data_ref)
                cleaned_df = cleaner.clean_from_df(df)
            else:
                raise NotImplementedError(
                    f"Cleaner {cleaner_name} does not support the required cleaning method"
                )

            self.logger.info(f"Cleaned {len(cleaned_df)} records")

            # Run custom validation
            if not cleaner.validate_output(cleaned_df):
                self.logger.error(f"Custom validation failed for {cleaner_name}")
                return None

            # Run standard tests
            # test_results = self.test_runner.run_tests(cleaner_name, cleaned_df)

            # if test_only:
            #     self.logger.info(f"Test results: {test_results}")
            #     return cleaned_df if test_results['passed'] else None
            #
            # if not test_results['passed']:
            #     self.logger.error(
            #         f"Tests failed for {cleaner_name}: {test_results['errors']}"
            #     )
            #     return None

            # Save cleaned data
            if output_dir:
                output_path = output_dir / f"{cleaner_name}_cleaned.csv"
            else:
                output_path = Path("data/cleaned") / f"{cleaner_name}_cleaned.csv"

            output_path.parent.mkdir(parents=True, exist_ok=True)
            cleaned_df.to_csv(output_path, index=False)
            self.logger.info(f"Saved cleaned data to: {output_path}")

            return cleaned_df

        except Exception as e:
            self.logger.error(f"Error running cleaner {cleaner_name}: {e}")
            self.logger.error(traceback.format_exc())
            return None

    def run_multiple(self, cleaner_names: List[str],
                     parallel: bool = True,
                     use_disk: bool = False) -> Dict[str, pd.DataFrame]:
        """Run multiple cleaners"""
        results = {}

        if parallel:
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {
                    executor.submit(self.run_cleaner, name, use_disk): name
                    for name in cleaner_names
                }
                for future in as_completed(futures):
                    cleaner_name = futures[future]
                    try:
                        result = future.result()
                        if result is not None:
                            results[cleaner_name] = result
                    except Exception as e:
                        self.logger.error(f"Error in {cleaner_name}: {e}")
        else:
            for cleaner_name in cleaner_names:
                try:
                    result = self.run_cleaner(cleaner_name, use_disk)
                    if result is not None:
                        results[cleaner_name] = result
                except Exception as e:
                    self.logger.error(f"Error in {cleaner_name}: {e}")

        return results

    def run_all(self, parallel: bool = True, use_disk: bool = False) -> Dict[str, pd.DataFrame]:
        """Run all discovered cleaners"""
        return self.run_multiple(self.list_cleaners(), parallel, use_disk)


# CLI interface
if __name__ == "__main__":
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    parser = argparse.ArgumentParser(description='Run data cleaning pipeline')
    parser.add_argument('--cleaner', type=str, help='Run specific cleaner')
    parser.add_argument('--list', action='store_true', help='List available cleaners')
    parser.add_argument('--info', type=str, help='Get info about a cleaner')
    parser.add_argument('--test', action='store_true', help='Test mode only')
    parser.add_argument('--disk', action='store_true', help='Use disk-based processing')
    parser.add_argument('--parallel', action='store_true', default=True,
                        help='Run cleaners in parallel')
    parser.add_argument('--output-dir', type=str, help='Output directory for cleaned data')

    args = parser.parse_args()

    pipeline = DataCleaningPipeline()

    if args.list:
        print("Available cleaners:")
        for cleaner in pipeline.list_cleaners():
            print(f"  - {cleaner}")

    elif args.info:
        info = pipeline.get_cleaner_info(args.info)
        print(f"\nCleaner: {info['name']}")
        print(f"Capabilities: {info['capabilities']}")
        print(f"Metadata: {info['metadata']}")

    elif args.cleaner:
        output_dir = Path(args.output_dir) if args.output_dir else None
        result = pipeline.run_cleaner(
            args.cleaner,
            use_disk=args.disk,
            test_only=args.test,
            output_dir=output_dir
        )
        if result is not None:
            print(f"Successfully cleaned {len(result)} records")
        else:
            print("Cleaning failed")
            sys.exit(1)

    else:
        results = pipeline.run_all(parallel=args.parallel, use_disk=args.disk)
        print(f"Successfully cleaned {len(results)} datasets")