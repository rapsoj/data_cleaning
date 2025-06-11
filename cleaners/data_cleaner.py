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
        """Download data from source if it is dynamic or from the repo if it is static"""
        self.logger.info("Downloading data to memory...")

        #### Your code here
        #### df = ...

        self.logger.info(f"Downloaded {len(df)} records")
        return df

    def clean_from_df(self, data) -> object:
        """Clean the input tabular data (e.g., DataFrame, GeoDataFrame, etc.)."""
        self.logger.info("Cleaning data...")

        # Make a copy to avoid modifying the original
        df = data.copy()

        #### Your code here
        #### df = ...

        self.logger.info(f"Cleaned data has {len(cleaned)} records")
        return cleaned

   def get_metadata(self) -> Dict[str, Any]:  
       return {  
           'source_name': '', # Copy from project-tracking file
           'variables': {} # Write all variables 
           'temporal_resolution': '',
           'spatial_resolution': '',
           'update_frequency': ''
       }