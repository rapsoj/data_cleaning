# Data Cleaning Pipeline

A simple, portable framework for standardizing data cleaning in machine learning projects.

## Overview

This pipeline helps you:
- Download data from various sources (APIs, files, web scraping)
- Clean and standardize the data for ML use
- Automatically validate data quality with both standard and custom tests
- Save cleaned data in a consistent format
- Organize multiple data cleaners in a structured way

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# List available cleaners
python data_cleaning.py --list

# Run a specific cleaner
python data_cleaning.py --cleaner-name EXAMPLE

# Test your cleaner
python data_cleaning.py --cleaner-name EXAMPLE --test

# See all options
python data_cleaning.py --help
````

## Project Structure

```
.
├── data_cleaning.py      # Main pipeline runner
├── base_cleaner.py       # Base class for all cleaners
├── cleaners/             # All data cleaners live here
│   ├── example/          # Example cleaner with synthetic data
│   │   ├── cleaner.py    
│   │   └── custom_tests.py  # Example-specific tests
│   └── YOUR_CLEANER_HERE/     # Your custom cleaners
│       ├── cleaner.py    
│       └── custom_tests.py  
├── tests/                # Standard validation tests
│   ├── test_runner.py    # Test orchestration
│   └── standard_tests.py # Tests that run on ALL cleaners
├── data/                 # Data storage
│   ├── raw/              # Downloaded raw data
│   │   └── {cleaner}/    # Raw data per cleaner
│   └── cleaned/          # Cleaned output data
│       └── {cleaner}/    # Cleaned data per cleaner
└── docs/                 # Documentation
    ├── student_guide.md  # Step-by-step tutorial
    └── user_guide.md     # Complete reference
```

## Documentation

📚 **[Student Guide](docs/student_guide.md)** - Step-by-step instructions for implementing a data cleaner
📖 **[User Guide](docs/user_guide.md)** - Complete reference for all features and options

## Creating a New Cleaner

### 1. Copy the template

```bash
# First, create a template from the example cleaner
cp -r cleaners/example cleaners/my_new_cleaner
```

### 2. Edit the cleaner

Open `cleaners/YOUR_CLEANER_HERE/cleaner.py` and implement the following **required methods**:

* `get_metadata()` — Describe your data source
* `download_data(format='dataframe')` — Fetch the raw data in memory
* `clean_data(raw_data)` — Clean and standardize the data

> For large files, you can optionally override:
>
> * `download_to_path()` — For file-based downloading
> * `clean_from_path()` — For cleaning from disk

### 3. Add custom tests (optional but recommended)

Edit `cleaners/my_new_cleaner/custom_tests.py` to add validation specific to your data.

### 4. Run your cleaner

```bash
python data_cleaning.py --cleaner-name my_new_cleaner
```

## Basic Usage Examples

```bash
# List all available cleaners
python data_cleaning.py --list

# Run a specific cleaner
python data_cleaning.py --cleaner-name weather

# Get info about a cleaner
python data_cleaning.py --cleaner-name weather --info

# Test a cleaner (shows detailed test results)
python data_cleaning.py --cleaner-name weather --test

# Run without validation tests
python data_cleaning.py --cleaner-name weather --skip-tests

# Use disk-based processing for large files
python data_cleaning.py --cleaner-name large_dataset --disk

# Specify custom output directory
python data_cleaning.py --cleaner-name weather --output-dir /path/to/output
```

## Testing System

Each cleaner is validated with two types of tests:

### Standard Tests (run on all cleaners)

Located in `tests/standard_tests.py`, these validate common data quality issues:

* Not empty
* Has columns
* No all-null columns
* No duplicate rows
* Reasonable memory usage
* Valid column names
* Valid numeric/date columns
* Reasonable null percentages
* Trimmed string columns

### Custom Tests (cleaner-specific)

Located in `cleaners/{cleaner_name}/custom_tests.py`, these validate data specific to each cleaner:

* Required columns for that dataset
* Domain-specific value ranges
* Business rule validation
* Data relationship checks

## Output Structure

Cleaned data is organized by cleaner:

```
data/
├── raw/
│   # Raw data for cleaner
└── cleaned/
    # Cleaned data from cleaner
```

## Required Methods

Each cleaner must implement:

1. **`get_metadata()`**: Return information about your data source
2. **`download_data(format='dataframe' | 'array')`**: Download the raw data in memory
3. **`clean_data(raw_data)`**: Clean the raw data (can accept DataFrame or NumPy array)

## Optional Methods

* **`validate_output(df)`**: Add custom validation rules beyond the standard tests
* **`download_to_path()`**: Use this if you need disk-based downloading
* **`clean_from_path()`**: Use this if you want to process files in chunks

## Tips

* Each cleaner runs in isolation — no shared state between cleaners
* Use the logger (`self.logger`) for status messages
* The base cleaner provides common functionality — call `super()` methods when overriding
* Add any required packages to your project's `requirements.txt`
* Write comprehensive custom tests to catch data quality issues early
* Standard tests catch common issues, but custom tests catch domain-specific problems
* Check the example cleaner for reference: `python data_cleaning.py --cleaner-name example`

## Requirements

* Python 3.7+
* pandas
* See `requirements.txt` for full list

## Support

* Run the example cleaner to see it in action: `python data_cleaning.py --cleaner-name example`
* Run tests for debugging: `python data_cleaning.py --cleaner-name your_cleaner --test`
* Check the [Student Guide](docs/student_guide.md) for step-by-step instructions
* See the [User Guide](docs/user_guide.md) for detailed reference
