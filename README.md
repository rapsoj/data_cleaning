# Data Cleaning Pipeline

A simple, portable framework for standardizing data cleaning in machine learning projects.

## Overview

This pipeline helps you:
- Download data from various sources (APIs, files, web scraping)
- Clean and standardize the data for ML use
- Automatically validate data quality
- Save cleaned data in a consistent format

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Edit cleaner.py with your data source
# Then run:
python data_cleaning.py

# Test your cleaner
python data_cleaning.py --test

# See all options
python data_cleaning.py --help
```

## Structure

- `cleaner.py` - Your data cleaner (edit this!)
- `example_cleaner.py` - Working example for reference
- `tests/` - Automatic data validation
- `data/cleaned/` - Output location

## Documentation

📚 **[Student Guide](docs/student_guide.md)** - Step-by-step instructions for implementing a data cleaner

📖 **[User Guide](docs/user_guide.md)** - Complete reference for all features and options

## Basic Usage

1. Edit `cleaner.py` to implement three methods:
   - `get_metadata()` - Describe your data source
   - `download_to_df()` - Fetch the raw data
   - `clean_from_df()` - Clean and standardize

2. Run the pipeline:
   ```bash
   python data_cleaning.py
   ```

3. Find your cleaned data in `data/cleaned/cleaned_data.csv`

## Requirements

- Python 3.7+
- pandas
- See `requirements.txt` for full list

## Support

- Check the example: `python data_cleaning.py --cleaner-file example_cleaner`
- Run tests for debugging: `python data_cleaning.py --test`
- See documentation for detailed help
