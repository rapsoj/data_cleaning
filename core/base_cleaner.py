from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd
from pathlib import Path


class DataCleaner(ABC):
    """
    Base class for all data cleaners.

    Students must implement EITHER:
    - download_to_df() and clean_from_df() for in-memory processing
    OR
    - download_to_path() and clean_from_path() for file-based processing
    OR
    - Both sets for maximum flexibility
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = self.__class__.__module__.split('.')[-2]  # Extract from module path

    # Download methods - implement at least one
    def download_to_df(self) -> pd.DataFrame:
        """
        Download data and return as a pandas DataFrame.
        Override this method if your data fits in memory.

        Returns:
            pd.DataFrame: The downloaded raw data
        """
        raise NotImplementedError(
            f"{self.name} must implement either download_to_df() or download_to_path()"
        )

    def download_to_path(self, output_path: Path) -> Path:
        """
        Download data and save to a file path.
        Override this method for large datasets or files that shouldn't be loaded into memory.

        Args:
            output_path: Directory where data should be saved

        Returns:
            Path: Path to the saved file
        """
        raise NotImplementedError(
            f"{self.name} must implement either download_to_df() or download_to_path()"
        )

    # Clean methods - implement at least one
    def clean_from_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean a pandas DataFrame.
        Override this method if you implemented download_to_df().

        Args:
            df: Raw data as a DataFrame

        Returns:
            pd.DataFrame: Cleaned data
        """
        raise NotImplementedError(
            f"{self.name} must implement either clean_from_df() or clean_from_path()"
        )

    def clean_from_path(self, input_path: Path) -> pd.DataFrame:
        """
        Clean data from a file path.
        Override this method if you implemented download_to_path() or need to handle large files.

        Args:
            input_path: Path to the raw data file

        Returns:
            pd.DataFrame: Cleaned data
        """
        raise NotImplementedError(
            f"{self.name} must implement either clean_from_df() or clean_from_path()"
        )

    def get_capabilities(self) -> Dict[str, bool]:
        """Determine which methods this cleaner implements"""
        return {
            'download_to_df': self.__class__.download_to_df != DataCleaner.download_to_df,
            'download_to_path': self.__class__.download_to_path != DataCleaner.download_to_path,
            'clean_from_df': self.__class__.clean_from_df != DataCleaner.clean_from_df,
            'clean_from_path': self.__class__.clean_from_path != DataCleaner.clean_from_path,
        }

    def validate_output(self, df: pd.DataFrame) -> bool:
        """
        Optional: Add custom validation logic for your cleaned data.

        Args:
            df: Cleaned DataFrame to validate

        Returns:
            bool: True if validation passes, False otherwise
        """
        return True
