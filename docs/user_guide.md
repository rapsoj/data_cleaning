# User Guide: Data Cleaning Pipeline

## Introduction

The Data Cleaning Pipeline is a lightweight framework for standardizing data preparation in machine learning projects. It provides a consistent interface for data cleaning tasks with automatic validation, designed to be simple enough for students while powerful enough for production use.

## Getting Started

### Installation

```bash
# Clone your project repository
git clone https://github.com/your-org/your-project.git
cd your-project

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

The pipeline runs a single data cleaner defined in `cleaner.py`:

```bash
# Run the cleaner
python data_cleaning.py

# Run with validation tests
python data_cleaning.py --test

# Show cleaner information
python data_cleaning.py --info
```

## Command Line Interface

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| (no args) | Run the cleaner | `python data_cleaning.py` |
| `--test` | Run cleaner and show detailed test results | `python data_cleaning.py --test` |
| `--info` | Display cleaner metadata and capabilities | `python data_cleaning.py --info` |
| `--skip-tests` | Run cleaner without validation tests | `python data_cleaning.py --skip-tests` |
| `--disk` | Use disk-based processing for large files | `python data_cleaning.py --disk` |
| `--list-tests` | Show all available validation tests | `python data_cleaning.py --list-tests` |
| `--output-dir PATH` | Specify custom output directory | `python data_cleaning.py --output-dir ./output` |
| `--cleaner-file NAME` | Use a different cleaner file | `python data_cleaning.py --cleaner-file example_cleaner` |

### Examples

```bash
# Run the default cleaner
python data_cleaning.py

# Test your cleaner without saving output
python data_cleaning.py --test

# Use the example cleaner instead
python data_cleaning.py --cleaner-file example_cleaner

# Process large files using disk storage
python data_cleaning.py --disk

# Save output to custom location
python data_cleaning.py --output-dir /path/to/output

# Run without validation (useful during development)
python data_cleaning.py --skip-tests
```

## Data Flow

### Directory Structure

```
project/
├── cleaner.py              # Your data cleaner (edit this!)
├── example_cleaner.py      # Working example for reference
├── base_cleaner.py         # Base class (don't edit)
├── data_cleaning.py        # Main runner (don't edit)
├── requirements.txt        # Python dependencies
│
├── tests/                  # Validation tests
│   ├── test_runner.py      # Test orchestrator
│   ├── standard_tests.py   # Built-in tests
│   └── custom_tests.py     # Project-specific tests
│
└── data/
    ├── raw/                # Raw downloaded data (optional)
    └── cleaned/            # Output directory
        └── cleaned_data.csv # Your cleaned dataset
```

### Output

- **Default location**: `data/cleaned/cleaned_data.csv`
- **Custom location**: Use `--output-dir` to specify
- **Format**: Always CSV with UTF-8 encoding

## Testing Framework

### How Testing Works

The pipeline automatically validates your cleaned data using a suite of tests:

1. **Standard tests** run on all data (e.g., checking for empty dataframes)
2. **Custom tests** specific to your project requirements

### Standard Tests

These tests run automatically on every dataset:

| Test | What it checks | Fails when |
|------|----------------|------------|
| `test_not_empty` | Dataset has rows | No data returned |
| `test_has_columns` | Dataset has columns | No columns present |
| `test_no_all_null_columns` | No completely empty columns | Any column is 100% null |
| `test_no_duplicate_rows` | Duplicate row count | Exact duplicates exist |
| `test_column_names_valid` | Clean column names | Spaces or special chars in names |
| `test_numeric_columns_valid` | Numeric data quality | Infinity values or all identical |
| `test_date_columns_valid` | Date formatting | Dates before 1900 or after 2100 |

### Adding Custom Tests

Add project-specific validations to `tests/custom_tests.py`:

```python
def test_required_columns(df):
    """Check that essential columns exist"""
    required = ['date', 'value', 'location']
    missing = [col for col in required if col not in df.columns]
    
    return {
        'passed': len(missing) == 0,
        'message': f'Missing columns: {missing}' if missing else 'All required columns present',
        'details': {'missing': missing}
    }

def test_positive_values(df):
    """Ensure values are positive where expected"""
    if 'price' not in df.columns:
        return {'passed': True, 'message': 'No price column to check', 'details': {}}
    
    negative_count = (df['price'] < 0).sum()
    return {
        'passed': negative_count == 0,
        'message': f'Found {negative_count} negative prices',
        'details': {'count': int(negative_count)}
    }
```

### Test Results

When you run `python data_cleaning.py --test`, you'll see:

```
Test Results:
  Total tests: 15
  Passed: 14
  Failed: 1

Detailed Results:
  ✓ standard_tests.test_not_empty: DataFrame has 1000 rows
  ✓ standard_tests.test_has_columns: DataFrame has 10 columns
  ✗ custom_tests.test_required_columns: Missing columns: ['location']
  ...
```

## Writing a Data Cleaner

### Basic Structure

Your `cleaner.py` must contain a class that inherits from `BaseCleaner`:

```python
from base_cleaner import BaseCleaner
import pandas as pd

class Cleaner(BaseCleaner):
    def get_metadata(self):
        return {
            'source': 'Your data source',
            'description': 'What this data contains',
            'update_frequency': 'daily/weekly/monthly/static'
        }
    
    def download_data(self):
        # Download and return raw data
        return pd.read_csv('https://example.com/data.csv')
    
    def clean_data(self, df):
        # Clean and return the data
        cleaned = df.copy()
        # ... cleaning steps ...
        return cleaned
```

### Processing Large Files

For datasets that don't fit in memory, implement the disk-based methods:

```python
def download_to_path(self, output_dir):
    """Download large file to disk"""
    import requests
    
    output_path = output_dir / 'large_file.csv'
    with requests.get(url, stream=True) as r:
        with open(output_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    
    return output_path

def clean_from_path(self, data_path):
    """Process file in chunks"""
    chunks = []
    for chunk in pd.read_csv(data_path, chunksize=10000):
        # Clean each chunk
        cleaned_chunk = self._process_chunk(chunk)
        chunks.append(cleaned_chunk)
    
    return pd.concat(chunks, ignore_index=True)
```

## Common Patterns

### API Authentication

```python
import os

class Cleaner(BaseCleaner):
    def __init__(self):
        super().__init__()
        self.api_key = os.environ.get('API_KEY')
        if not self.api_key:
            raise ValueError("API_KEY environment variable not set")
```

### Error Handling

```python
def download_data(self):
    try:
        response = requests.get(self.url)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except requests.RequestException as e:
        self.logger.error(f"Download failed: {e}")
        raise
```

### Progress Logging

```python
def clean_from_df(self, df):
    self.logger.info(f"Starting with {len(df)} rows")
    
    # Cleaning steps...
    df = df.dropna()
    self.logger.info(f"After removing nulls: {len(df)} rows")
    
    return df
```

## Troubleshooting

### Common Issues

**"No Cleaner class found"**
- Make sure your class is named `Cleaner` or ends with `Cleaner`
- Check for syntax errors in your cleaner file

**"Test failed: Missing required columns"**
- Verify your cleaned data includes all columns specified in project requirements
- Check column naming (case sensitivity, underscores vs spaces)

**Memory errors**
- Implement `download_to_path()` and `clean_from_path()` for disk-based processing
- Use `--disk` flag when running

**"Missing dependencies"**
- Add required packages to `requirements.txt`
- Run `pip install -r requirements.txt`

### Getting Help

1. **Check the example**: `python data_cleaning.py --cleaner-file example_cleaner`
2. **Review test output**: Failed tests show specific issues
3. **Enable debug logging**: Add `-v` for verbose output (if implemented)
4. **Contact support**: Reach out to your project lead with error messages

## Best Practices

### Data Quality

- Always work on a copy: `df.copy()`
- Log important operations and row counts
- Validate assumptions about the data
- Handle edge cases gracefully

### Code Organization

- Keep cleaning steps logical and sequential
- Use descriptive variable names
- Comment complex transformations
- Separate concerns (download vs clean)

### Performance

- For large files, use chunked processing
- Minimize memory usage by dropping unnecessary columns early
- Use efficient pandas operations (vectorized over loops)

### Security

- Never commit credentials or API keys
- Use environment variables for sensitive data
- Validate external data sources
- Be cautious with dynamic code execution

## Architecture Overview

The pipeline follows a simple, modular design:

1. **Single Cleaner**: One cleaner per project keeps things focused
2. **Clear Interface**: Three required methods make implementation straightforward
3. **Automatic Testing**: Validation runs without extra configuration
4. **Flexible Processing**: Support for both in-memory and disk-based workflows

This design prioritizes:
- **Simplicity**: Minimal learning curve for new users
- **Flexibility**: Handles diverse data sources and sizes
- **Reliability**: Automatic validation catches common issues
- **Maintainability**: Clear structure makes debugging easier
