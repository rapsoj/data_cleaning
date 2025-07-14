"""
Example data cleaner that works entirely in memory.
Located in: cleaners/example/cleaner.py
To use: python data_cleaning.py --cleaner-name example
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Union

from base_cleaner import BaseCleaner


class Cleaner(BaseCleaner):
    """Example cleaner that generates and processes synthetic in-memory data"""

    def get_metadata(self) -> Dict[str, Any]:
        """Provide information about this data source"""
        return {
            'source': 'Sample Data Generator',
            'description': 'Randomly generated time series data for demonstration',
            'update_frequency': 'on-demand',
            'type': 'synthetic'
        }

    def download_data(self, format: str = 'dataframe') -> Union[pd.DataFrame, np.ndarray]:
        """Generate synthetic data and return it in the requested format"""
        self.logger.info("Generating synthetic data...")

        df = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=365, freq='D'),
            'value': np.random.randn(365) * 10 + 50,
            'category': np.random.choice(['A', 'B', 'C'], 365)
        })

        self.logger.info(f"Generated {len(df)} records")

        if format == 'dataframe':
            return df
        elif format == 'array':
            # For demonstration, only return the 'value' column as a numeric array
            return df[['value']].to_numpy()
        else:
            raise ValueError(f"Unsupported format: {format}. Expected 'dataframe' or 'array'.")

    def clean_data(self, raw_data: Union[pd.DataFrame, np.ndarray]) -> Union[pd.DataFrame, np.ndarray]:
        """Clean either a pandas DataFrame or a NumPy array"""
        if isinstance(raw_data, pd.DataFrame):
            cleaned = raw_data.copy()

            # Standardize date column
            cleaned['date'] = pd.to_datetime(cleaned['date'], errors='coerce')

            # Fill missing numeric values
            cleaned['value'] = cleaned['value'].fillna(cleaned['value'].mean())

            # Normalize categorical column
            cleaned['category'] = cleaned['category'].str.upper()

            # Remove outliers in the value column
            cleaned = cleaned[cleaned['value'].between(-100, 200)]

            self.logger.info(f"Cleaned DataFrame with {len(cleaned)} rows")
            return cleaned

        elif isinstance(raw_data, np.ndarray):
            # Remove rows with NaNs
            cleaned = raw_data[~np.isnan(raw_data).any(axis=1)]

            # Remove numeric outliers
            cleaned = cleaned[(cleaned >= -100).all(axis=1) & (cleaned <= 200).all(axis=1)]

            self.logger.info(f"Cleaned array with {len(cleaned)} rows")
            return cleaned

        else:
            raise TypeError("clean_data supports only pandas DataFrame or numpy ndarray")

    def validate_output(self, df: pd.DataFrame) -> bool:
        """Custom validation for the example DataFrame output"""
        if not super().validate_output(df):
            return False

        expected_columns = ['date', 'value', 'category']
        if not all(col in df.columns for col in expected_columns):
            self.logger.error("Missing expected columns")
            return False

        if not df['category'].str.isupper().all():
            self.logger.error("Not all categories are uppercase")
            return False

        return True