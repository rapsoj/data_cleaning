"""
Data cleaning pipeline runner
Runs the cleaner defined in cleaner.py (or another file specified via --cleaner-file)
"""
import importlib.util
import sys
from pathlib import Path
import pandas as pd
import logging
import traceback
from typing import Optional, Dict, Any

# Import the test runner
from tests.test_runner import TestRunner


class DataCleaningPipeline:
    """Simple data cleaning orchestrator - one cleaner per project"""

    def __init__(self, cleaner_file: str = "cleaner"):
        self.logger = logging.getLogger(__name__)
        # Strip .py extension if provided
        self.cleaner_file = cleaner_file.rstrip('.py') if cleaner_file.endswith('.py') else cleaner_file
        self.cleaner_class = self._load_cleaner()
        self.test_runner = TestRunner()

    def _load_cleaner(self):
        """Load the cleaner class from the specified file"""
        try:
            # Import the cleaner module
            module = importlib.import_module(self.cleaner_file)

            # Find the Cleaner class
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    attr_name.endswith('Cleaner') and
                    attr_name not in ['BaseCleaner', 'Cleaner']):
                    self.logger.info(f"Loaded cleaner: {attr_name} from {self.cleaner_file}.py")
                    return attr

            # If no custom cleaner found, look for the generic 'Cleaner' class
            if hasattr(module, 'Cleaner'):
                self.logger.info(f"Loaded cleaner: Cleaner from {self.cleaner_file}.py")
                return module.Cleaner

            raise ValueError(f"No Cleaner class found in {self.cleaner_file}.py")

        except ImportError as e:
            self.logger.error(f"Failed to import {self.cleaner_file}.py: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to load cleaner: {e}")
            raise

    def run(self, use_disk: bool = False,
            output_dir: Optional[Path] = None,
            skip_tests: bool = False) -> Optional[pd.DataFrame]:
        """
        Run the data cleaner

        Args:
            use_disk: If True, use disk-based processing if available
            output_dir: Output directory (defaults to data/cleaned/)
            skip_tests: If True, skip validation tests

        Returns:
            Cleaned DataFrame if successful, None if failed
        """
        try:
            # Instantiate the cleaner
            cleaner = self.cleaner_class()
            capabilities = cleaner.get_capabilities()

            self.logger.info(f"Running {self.cleaner_class.__name__}...")
            self.logger.info(f"Source: {cleaner.get_metadata().get('source', 'Unknown')}")

            # Download data
            self.logger.info("Downloading data...")

            # Determine which download method to use
            has_df_download = capabilities.get('download_to_df', False)
            has_path_download = capabilities.get('download_to_path', False)

            if not has_df_download and not has_path_download:
                raise NotImplementedError(
                    "Cleaner must implement download_to_df() or download_to_path()"
                )

            # Choose download method based on availability and preference
            use_path_method = False
            if has_path_download and has_df_download:
                # Both available - use disk flag to decide
                use_path_method = use_disk
                if use_disk:
                    self.logger.info("Both download methods available, using disk-based as requested")
                else:
                    self.logger.info("Both download methods available, using memory-based")
            elif has_path_download:
                # Only path available
                use_path_method = True
                self.logger.info("Using disk-based download (only method available)")
            else:
                # Only df available
                use_path_method = False
                self.logger.info("Using memory-based download (only method available)")

            # Execute download
            if use_path_method:
                raw_dir = Path("data/raw")
                raw_dir.mkdir(parents=True, exist_ok=True)
                data_path = cleaner.download_to_path(raw_dir)
                data_ref = data_path
                self.logger.info(f"Downloaded data to: {data_path}")
            else:
                data_ref = cleaner.download_to_df()
                self.logger.info(f"Downloaded data to memory")

            # Clean data - match the cleaning method to download method
            self.logger.info("Cleaning data...")

            if use_path_method:
                # We used download_to_path, so need clean_from_path
                if capabilities.get('clean_from_path'):
                    cleaned_df = cleaner.clean_from_path(data_ref)
                else:
                    raise NotImplementedError(
                        f"Cleaner implements download_to_path() but not clean_from_path(). "
                        f"Please implement clean_from_path() or use download_to_df() instead."
                    )
            else:
                # We used download_to_df, so need clean_from_df
                if capabilities.get('clean_from_df'):
                    cleaned_df = cleaner.clean_from_df(data_ref)
                else:
                    raise NotImplementedError(
                        f"Cleaner implements download_to_df() but not clean_from_df(). "
                        f"Please implement clean_from_df() or use download_to_path() instead."
                    )

            self.logger.info(f"Cleaned {len(cleaned_df)} records with {len(cleaned_df.columns)} columns")

            # Run custom validation if implemented
            if hasattr(cleaner, 'validate_output'):
                self.logger.info("Running custom validation...")
                if not cleaner.validate_output(cleaned_df):
                    self.logger.error("Custom validation failed")
                    return None

            # Run test suite unless skipped
            if not skip_tests:
                self.logger.info("Running validation tests...")
                test_results = self.test_runner.run_tests(cleaned_df)

                if not test_results['passed']:
                    self.logger.error(
                        f"\nValidation tests failed:\n"
                        f"  Passed: {test_results['passed_tests']}/{test_results['total_tests']}\n"
                        f"  Failed tests:"
                    )
                    # Show failed tests
                    for test_name, result in test_results['test_details'].items():
                        if not result['passed']:
                            self.logger.error(f"    ✗ {test_name}: {result['message']}")

                    self.logger.info("\nTo save data anyway, run with --skip-tests")
                    return None
                else:
                    self.logger.info(
                        f"All tests passed! ({test_results['passed_tests']}/{test_results['total_tests']})"
                    )

            # Save cleaned data
            if output_dir is None:
                output_dir = Path("data/cleaned")

            output_path = output_dir / "cleaned_data.csv"
            output_path.parent.mkdir(parents=True, exist_ok=True)

            cleaned_df.to_csv(output_path, index=False)
            self.logger.info(f"\nSaved cleaned data to: {output_path}")
            self.logger.info(f"Shape: {cleaned_df.shape}")

            return cleaned_df

        except Exception as e:
            self.logger.error(f"Error running cleaner: {e}")
            self.logger.error(traceback.format_exc())
            return None

    def test(self) -> Dict[str, Any]:
        """Run the cleaner and report test results"""
        try:
            # Run the cleaner with skip_tests=True to avoid double testing
            df = self.run(skip_tests=True)
            if df is None:
                return {"execution": False, "error": "Cleaner failed to run"}

            # Run full test suite
            test_results = self.test_runner.run_tests(df)

            return test_results

        except Exception as e:
            self.logger.error(f"Test failed: {e}")
            return {"execution": False, "error": str(e)}

    def info(self):
        """Display information about the cleaner"""
        try:
            cleaner = self.cleaner_class()
            metadata = cleaner.get_metadata()
            capabilities = cleaner.get_capabilities()

            print(f"\nCleaner: {self.cleaner_class.__name__}")
            print(f"File: {self.cleaner_file}.py")
            print("\nMetadata:")
            for key, value in metadata.items():
                print(f"  {key}: {value}")

            print("\nCapabilities:")
            print(f"  Download to memory: {'✓' if capabilities.get('download_to_df') else '✗'}")
            print(f"  Download to disk: {'✓' if capabilities.get('download_to_path') else '✗'}")
            print(f"  Clean from memory: {'✓' if capabilities.get('clean_from_df') else '✗'}")
            print(f"  Clean from disk: {'✓' if capabilities.get('clean_from_path') else '✗'}")

        except Exception as e:
            print(f"Error getting cleaner info: {e}")


# CLI interface
if __name__ == "__main__":
    import argparse

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    parser = argparse.ArgumentParser(
        description='Run data cleaning pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python data_cleaning.py                    # Run the cleaner
  python data_cleaning.py --test             # Test the cleaner
  python data_cleaning.py --info             # Show cleaner info
  python data_cleaning.py --skip-tests       # Run without validation
  python data_cleaning.py --cleaner-file example_cleaner      # Use example_cleaner.py
  python data_cleaning.py --cleaner-file example_cleaner.py   # Also works!
        """
    )

    parser.add_argument('--test', action='store_true',
                       help='Test mode - run cleaner and show detailed test results')
    parser.add_argument('--disk', action='store_true',
                       help='Use disk-based processing for large files')
    parser.add_argument('--skip-tests', action='store_true',
                       help='Skip validation tests and save output anyway')
    parser.add_argument('--list-tests', action='store_true',
                       help='List all available validation tests')
    parser.add_argument('--info', action='store_true',
                       help='Show information about the cleaner')
    parser.add_argument('--output-dir', type=str,
                       help='Output directory for cleaned data (default: data/cleaned/)')
    parser.add_argument('--cleaner-file', type=str, default='cleaner',
                       help='Python file containing the Cleaner class (with or without .py extension, default: cleaner.py)')

    args = parser.parse_args()

    # Handle list-tests separately (doesn't need a cleaner)
    if args.list_tests:
        test_runner = TestRunner()
        print("Available validation tests:")
        for test in test_runner.list_tests():
            module, name = test.rsplit('.', 1)
            print(f"  - {name} (from {module})")
        sys.exit(0)

    # Initialize pipeline with specified cleaner file
    try:
        pipeline = DataCleaningPipeline(cleaner_file=args.cleaner_file)
    except Exception as e:
        logging.error(f"Failed to initialize pipeline: {e}")
        sys.exit(1)

    # Handle different modes
    if args.info:
        pipeline.info()

    elif args.test:
        print(f"\nTesting {args.cleaner_file}.py...")
        results = pipeline.test()

        if results.get('passed') is not None:
            print(f"\nTest Results:")
            print(f"  Total tests: {results['total_tests']}")
            print(f"  Passed: {results['passed_tests']}")
            print(f"  Failed: {results['failed_tests']}")

            if results['test_details']:
                print("\nDetailed Results:")
                for test_name, result in results['test_details'].items():
                    status = '✓' if result['passed'] else '✗'
                    print(f"  {status} {test_name}: {result['message']}")

            if not results['passed']:
                print("\nTests FAILED - data may not meet quality standards")
                sys.exit(1)
            else:
                print("\nAll tests PASSED! ✨")
        else:
            print(f"Failed to run tests: {results.get('error', 'Unknown error')}")
            sys.exit(1)

    else:
        # Run the cleaner
        output_dir = Path(args.output_dir) if args.output_dir else None
        result = pipeline.run(
            use_disk=args.disk,
            output_dir=output_dir,
            skip_tests=args.skip_tests
        )

        if result is not None:
            print(f"\n✅ Successfully cleaned {len(result)} records!")
        else:
            print("\n❌ Cleaning failed")
            sys.exit(1)