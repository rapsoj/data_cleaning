"""
Data cleaner implementation
Fill in the methods below to create your data cleaner

REQUIRED METHODS:
- get_metadata(): Provide information about your data source
- download_to_df() OR download_to_path(): Choose one based on your data size
- clean_from_df() OR clean_from_path(): Choose one based on your data size

OPTIONAL METHODS:
- validate_output(): Add custom validation rules
- download_to_path(): Only needed for very large files
- clean_from_path(): Only needed for very large files
"""
import pandas as pd
from pathlib import Path
from typing import Dict, Any

from base_cleaner import BaseCleaner


class Cleaner(BaseCleaner):
    """Your data cleaner - rename this class if you want"""

    def get_metadata(self) -> Dict[str, Any]:
        """
        REQUIRED: Provide information about your data source
        """
        return {
            'source': 'TODO: Your data source name',
            'description': 'TODO: What this data contains',
            'update_frequency': 'TODO: How often it updates (daily/weekly/monthly/annual)',
            'url': 'TODO: Source URL (optional)'
        }

    def download_to_df(self) -> pd.DataFrame:
        """
        REQUIRED (unless using download_to_path): Download data to DataFrame
        Use this for datasets that fit comfortably in memory (< 1-2 GB)

        Examples:
            # From API:
            response = requests.get('https://api.example.com/data')
            return pd.DataFrame(response.json())

            # From CSV URL:
            return pd.read_csv('https://example.com/data.csv')

            # From local file:
            return pd.read_csv('raw_data/myfile.csv')
        """
        # TODO: Implement your download logic here
        raise NotImplementedError("Please implement download_to_df or download_to_path")

    def clean_from_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        REQUIRED (unless using clean_from_path): Clean your DataFrame

        Common cleaning operations:
            # Make a copy to avoid modifying original
            cleaned_df = df.copy()

            # Standardize column names
            cleaned_df.columns = cleaned_df.columns.str.lower().str.replace(' ', '_')

            # Handle missing values
            cleaned_df['column_name'] = cleaned_df['column_name'].fillna(0)

            # Convert data types
            cleaned_df['date'] = pd.to_datetime(cleaned_df['date'])

            # Remove duplicates
            cleaned_df = cleaned_df.drop_duplicates()

            # Filter data
            cleaned_df = cleaned_df[cleaned_df['value'] > 0]

            # Add derived columns
            cleaned_df['year'] = cleaned_df['date'].dt.year

            return cleaned_df
        """
        # TODO: Implement your cleaning logic here
        cleaned_df = df.copy()

        # Your cleaning steps go here...

        return cleaned_df

    # ===== OPTIONAL METHODS BELOW =====
    # Only implement these if you need them

    def validate_output(self, df: pd.DataFrame) -> bool:
        """
        OPTIONAL: Add custom validation for your cleaned data
        Return False if the data doesn't meet your requirements

        The pipeline will run standard tests automatically, but you can
        add specific checks here.
        """
        # Call parent validation first
        if not super().validate_output(df):
            return False

        # Add your custom validation here
        # Example:
        # required_columns = ['id', 'date', 'value']
        # if not all(col in df.columns for col in required_columns):
        #     self.logger.error(f"Missing required columns")
        #     return False

        return True

    def download_to_path(self, output_dir: Path) -> Path:
        """
        OPTIONAL: Download data to disk for very large files
        Only implement this if your data doesn't fit in memory

        Args:
            output_dir: Directory to save the raw data

        Returns:
            Path: Path to the downloaded file

        Example:
            import requests

            output_path = output_dir / "large_dataset.csv"

            # Stream download for large files
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(output_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            return output_path
        """
        # If not implemented, the pipeline will use download_to_df instead
        raise NotImplementedError("This cleaner only supports in-memory processing")

    def clean_from_path(self, data_path: Path) -> pd.DataFrame:
        """
        OPTIONAL: Clean data from a file path for very large files
        Only implement this if you need to process files in chunks

        Args:
            data_path: Path to the raw data file

        Returns:
            pd.DataFrame: Cleaned data

        Example for chunk processing:
            chunks = []
            for chunk in pd.read_csv(data_path, chunksize=10000):
                # Clean each chunk
                cleaned_chunk = self._clean_chunk(chunk)
                chunks.append(cleaned_chunk)

            return pd.concat(chunks, ignore_index=True)
        """
        # Default: just load the whole file and clean normally
        # Override this if you need chunk processing
        df = pd.read_csv(data_path)
        return self.clean_from_df(df)