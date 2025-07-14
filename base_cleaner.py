"""
Base class for data cleaners
All cleaners should inherit from this class and implement the required methods
"""
from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, Any, Union, Literal
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
    def download_data(self, format: Literal['dataframe', 'array'] = 'dataframe') -> Union[pd.DataFrame, np.ndarray]:
        """
        Download raw data in the desired format.

        Args:
            format: 'dataframe' or 'array' — determines return type.

        Returns:
            Union[pd.DataFrame, np.ndarray]: The raw data
        """
        pass

    @abstractmethod
    def clean_data(self, raw_data: Union[pd.DataFrame, np.ndarray]) -> Union[pd.DataFrame, np.ndarray]:
        """
        Clean raw data, which may be either a DataFrame or a NumPy array.

        Args:
            raw_data: The raw input data.

        Returns:
            Cleaned data of the same type.

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

        Args:
            data_path: Path to the raw data file

        Returns:
            Cleaned data (assumed to be a DataFrame here)
        """
        df = pd.read_csv(data_path)
        cleaned = self.clean_data(df)
        if isinstance(cleaned, pd.DataFrame):
            return cleaned
        else:
            raise TypeError("clean_data must return a DataFrame when cleaning from path.")

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

    def get_capabilities(self) -> Dict[str, Any]:
        supported_formats = []
        try:
            self.download_data(format='dataframe')
            supported_formats.append('dataframe')
        except Exception:
            pass
        try:
            self.download_data(format='array')
            supported_formats.append('array')
        except Exception:
            pass

        return {
            'download_data': True,
            'supported_formats': supported_formats,
            'clean_data': hasattr(self, 'clean_data') and callable(self.clean_data),
            'clean_from_path': hasattr(self, 'clean_from_path') and callable(self.clean_from_path),
        }