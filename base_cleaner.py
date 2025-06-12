"""
Base class for data cleaners
All cleaners should inherit from this class and implement the required methods
"""
from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd
from typing import Dict, Any
import logging


class BaseCleaner(ABC):
    """Base class for all data cleaners"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Return metadata about this cleaner.

        Required fields:
            - source: Where the data comes from
            - description: What the data contains

        Optional fields:
            - update_frequency: How often the data updates
            - url: Source URL
            - documentation: Link to data documentation

        Example:
            return {
                'source': 'US Census API',
                'description': 'Population demographics by county',
                'update_frequency': 'annual',
                'url': 'https://api.census.gov/data'
            }
        """
        pass

    @abstractmethod
    def download_to_df(self) -> pd.DataFrame:
        """
        Download data and return as DataFrame.
        Use this for datasets that fit comfortably in memory.

        Returns:
            pd.DataFrame: The raw data

        Example:
            response = requests.get('https://api.example.com/data')
            return pd.DataFrame(response.json())
        """
        pass

    @abstractmethod
    def clean_from_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the raw DataFrame.
        This is where your main data cleaning logic goes.

        Args:
            df: Raw DataFrame from download_to_df()

        Returns:
            pd.DataFrame: Cleaned data

        Common cleaning steps:
            - Rename columns to consistent format
            - Handle missing values
            - Convert data types
            - Remove duplicates
            - Filter bad data
            - Add derived columns
        """
        pass

    # Optional methods - override these for more functionality

    def download_to_path(self, output_dir: Path) -> Path:
        """
        Download data to disk (for large files).
        Override this if you need to handle files too large for memory.

        Args:
            output_dir: Directory to save the raw data

        Returns:
            Path: Path to the downloaded file
        """
        raise NotImplementedError("This cleaner only supports in-memory processing")

    def clean_from_path(self, data_path: Path) -> pd.DataFrame:
        """
        Clean data from a file path (for large files).
        Override this if you need to process files in chunks.

        Args:
            data_path: Path to the raw data file

        Returns:
            pd.DataFrame: Cleaned data
        """
        # Default implementation: just load and clean in memory
        df = pd.read_csv(data_path)
        return self.clean_from_df(df)

    def validate_output(self, df: pd.DataFrame) -> bool:
        """
        Custom validation for cleaned data.
        Override this to add specific validation rules.

        Args:
            df: Cleaned DataFrame

        Returns:
            bool: True if data passes validation, False otherwise
        """
        # Basic validation
        if df.empty:
            self.logger.error("Cleaned dataframe is empty")
            return False

        if len(df.columns) == 0:
            self.logger.error("Cleaned dataframe has no columns")
            return False

        return True

    def get_capabilities(self) -> Dict[str, bool]:
        """
        Return which methods this cleaner implements.
        Used by the pipeline to determine how to run the cleaner.
        """
        return {
            'download_to_df': hasattr(self, 'download_to_df') and callable(self.download_to_df),
            'download_to_path': hasattr(self, 'download_to_path') and callable(self.download_to_path),
            'clean_from_df': hasattr(self, 'clean_from_df') and callable(self.clean_from_df),
            'clean_from_path': hasattr(self, 'clean_from_path') and callable(self.clean_from_path),
        }