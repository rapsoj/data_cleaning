import pandas as pd
import numpy as np
from typing import Dict, Any
from datetime import datetime
import logging

from core.base_cleaner import DataCleaner


class Cleaner(DataCleaner):
    """Example cleaner that works entirely in memory"""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)

    def download_to_df(self) -> pd.DataFrame:
        """Download data directly to a DataFrame"""
        self.logger.info("Downloading data to memory...")

        # Or generate sample data for demonstration
        df = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=365, freq='D'),
            'value': np.random.randn(365) * 10 + 50,
            'category': np.random.choice(['A', 'B', 'C'], 365)
        })

        self.logger.info(f"Downloaded {len(df)} records")
        return df

    def clean_from_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean the DataFrame"""
        self.logger.info("Cleaning data...")

        # Make a copy to avoid modifying the original
        cleaned = df.copy()

        # Example cleaning operations
        cleaned['date'] = pd.to_datetime(cleaned['date'])
        cleaned['value'] = cleaned['value'].fillna(cleaned['value'].mean())
        cleaned['category'] = cleaned['category'].str.upper()

        # Remove outliers
        cleaned = cleaned[cleaned['value'].between(-100, 200)]

        self.logger.info(f"Cleaned data has {len(cleaned)} records")
        return cleaned
