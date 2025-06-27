"""
Example data cleaner that works entirely in memory
Located in: cleaners/example/cleaner.py
To use: python data_cleaning.py --cleaner-name example
"""
import pandas as pd
import numpy as np
from typing import Dict, Any

from base_cleaner import BaseCleaner


class Cleaner(BaseCleaner):
    """Example cleaner that works entirely in memory"""

    def get_metadata(self) -> Dict[str, Any]:
        """Provide information about this data source"""
        return {
            'source': 'Sample Data Generator',
            'description': 'Randomly generated time series data for demonstration',
            'update_frequency': 'on-demand',
            'type': 'synthetic'
        }

    def download_to_df(self) -> pd.DataFrame:
        """Download data directly to a DataFrame"""
        self.logger.info("Downloading data to memory...")

        # Generate sample data for demonstration
        df = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=365, freq='D'),
            'value': np.random.randn(365) * 10 + 50,
            'category': np.random.choice(['A', 'B', 'C'], 365)
        })

        self.logger.info(f"Downloaded {len(df)} records")
        return df

    def clean_from_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean the DataFrame"""
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

    def validate_output(self, df: pd.DataFrame) -> bool:
        """Custom validation for the example data"""
        if not super().validate_output(df):
            return False

        # Check that we have the expected columns
        expected_columns = ['date', 'value', 'category']
        if not all(col in df.columns for col in expected_columns):
            self.logger.error("Missing expected columns")
            return False

        # Check that categories are uppercase
        if not df['category'].str.isupper().all():
            self.logger.error("Categories are not all uppercase")
            return False

        return True