# Student Guide: Contributing to the Data Cleaning Pipeline

## 🎯 Introduction

Welcome to the Data Cleaning Pipeline project! This guide will help you contribute your own data cleaners to our automated pipeline system. Whether you're cleaning weather data, financial records, or any other dataset, this framework provides a standardized way to ensure your work integrates seamlessly with the larger ML pipeline.

Your data cleaners will be automatically discovered, validated, and tested by our system, making it easy to contribute high-quality, reusable code that helps advance our machine learning projects.

## 🚀 Quickstart

### Option 1: Contributing Directly to This Repository

1. **Create your cleaner directory** under `cleaners/`:
   ```bash
   mkdir cleaners/your_cleaner_name
   ```

2. **Create the required file** `data_cleaner.py`:
   ```python
   from core.base_cleaner import DataCleaner
   import pandas as pd
   from typing import Dict, Any
   
   class Cleaner(DataCleaner):
       """Your cleaner description here"""
       
       def download_to_df(self) -> pd.DataFrame:
           # Download and return data as DataFrame
           pass
       
       def clean_from_df(self, df: pd.DataFrame) -> pd.DataFrame:
           # Clean and return the DataFrame
           pass
       
       def get_metadata(self) -> Dict[str, Any]:
           return {
               'source_name': 'Your Data Source',
               'variables': ['col1', 'col2', 'col3'],
               'temporal_resolution': 'daily',
               'spatial_resolution': 'county'
           }
   ```

3. **Test your cleaner**:
   ```bash
   python data_cleaning.py --cleaner your_cleaner_name --test
   ```

### Option 2: Working in Your Own Repository

1. **Create your own repository** with this structure:
   ```
   your-repo/
   ├── data_cleaner.py      # Required: Must contain a class named 'Cleaner'
   ├── requirements.txt     # Optional: Your dependencies
   └── any_other_files.py   # Your supporting code
   ```

2. **Implement the DataCleaner interface** in `data_cleaner.py`:
   ```python
   # Since you're in your own repo, you'll need to define the base class
   # or we'll handle the interface checking when we import your code
   
   class Cleaner:
       """Your cleaner implementation"""
       # Same methods as Option 1
   ```

3. **We'll clone and run your cleaner**:
   ```bash
   git clone https://github.com/yourusername/your-cleaner.git external_cleaners/your_cleaner_name
   python data_cleaning.py --cleaner your_cleaner_name
   ```

## 📋 Implementation Requirements

### Required File: `data_cleaner.py`

Your cleaner **must** be implemented in a file called `data_cleaner.py` at the top level of your cleaner directory. This file must contain a class named `Cleaner` that inherits from `DataCleaner`.

### Method Implementation Options

You have two options for implementing your cleaner:

#### Option A: In-Memory Processing (Recommended for datasets < 1GB)
```python
def download_to_df(self) -> pd.DataFrame:
    """Download data and return as a pandas DataFrame"""
    # Example: return pd.read_csv("https://data-source.com/data.csv")
    
def clean_from_df(self, df: pd.DataFrame) -> pd.DataFrame:
    """Clean the DataFrame and return cleaned version"""
    # Your cleaning logic here
```

#### Option B: File-Based Processing (For large datasets)
```python
def download_to_path(self, output_path: Path) -> Path:
    """Download data to disk and return the file path"""
    # Example: Download large file to output_path / "data.csv"
    
def clean_from_path(self, input_path: Path) -> pd.DataFrame:
    """Load and clean data from file path"""
    # Process file in chunks if needed
```

### Using the Data Directory

You have access to organized data storage:
- `data/raw/` - Store downloaded raw data
- `data/cleaned/` - Output cleaned data (handled automatically)
- `data/temp/` - Temporary processing files

Example usage:
```python
def download_to_path(self, output_path: Path) -> Path:
    # output_path will be something like data/raw/your_cleaner_name/
    file_path = output_path / "raw_data.csv"
    # Download to file_path
    return file_path
```

### Output Requirements

**Important**: Both cleaning methods (`clean_from_df` and `clean_from_path`) must return a pandas DataFrame. The pipeline will automatically save this cleaned data to `data/cleaned/your_cleaner_name_cleaned.csv`.

This standardized output location ensures:
- Other parts of the ML pipeline can reliably find your cleaned data
- Data is versioned and organized consistently
- Multiple cleaners can be chained together

You don't need to save the file yourself - just return the cleaned DataFrame and the pipeline handles the rest:

```python
def clean_from_df(self, df: pd.DataFrame) -> pd.DataFrame:
    # Your cleaning logic
    cleaned_df = df.dropna()
    # ... more cleaning ...
    
    # Just return the DataFrame - it will be saved to data/cleaned/ automatically
    return cleaned_df
```

When we run it, the saved file will be named: `data/cleaned/{your_cleaner_name}_cleaned.csv`

## 🔄 Git Usage

### Working with Branches

1. **Create a feature branch** for your cleaner:
   ```bash
   git checkout -b feature/add-weather-cleaner
   ```

2. **Make your changes** and commit regularly:
   ```bash
   git add cleaners/weather_cleaner/
   git commit -m "Add weather data cleaner with temperature normalization"
   ```

3. **Push your branch** and create a pull request:
   ```bash
   git push origin feature/add-weather-cleaner
   ```

### Working in Your Own Repository

If you prefer to work in your own repository:

1. **Create your repository** with the required structure
2. **Develop and test** your cleaner independently
3. **Share your repo URL** with us
4. We'll clone it into `external_cleaners/` and run it through our pipeline

Your repository should be structured so that `data_cleaner.py` is at the root level, making it easy for our system to find and import your `Cleaner` class.

## 📁 File Structure

### If Contributing to This Repository

Your cleaner should follow this structure:

```
cleaners/
└── your_cleaner_name/
    ├── data_cleaner.py      # Required: Contains your Cleaner class
    ├── requirements.txt     # Optional: Additional dependencies
    ├── utils.py            # Optional: Helper functions
    ├── config.json         # Optional: Configuration files
    └── README.md           # Recommended: Documentation for your cleaner
```

### Example Structure

```
cleaners/
└── weather_data/
    ├── data_cleaner.py     # Main cleaner implementation
    ├── requirements.txt    # Contains: requests>=2.28.0, beautifulsoup4>=4.11.0
    ├── weather_utils.py    # Helper functions for temperature conversion
    └── README.md           # Documentation explaining data source and methods
```

### Dependencies Management

If your cleaner needs additional packages beyond the base requirements:

1. **Create a `requirements.txt`** in your cleaner directory:
   ```
   requests>=2.28.0
   beautifulsoup4>=4.11.0
   geopandas>=0.12.0
   ```

2. **The pipeline will automatically**:
   - Detect missing dependencies
   - Prompt users to install them
   - Or auto-install with `--install-deps` flag

3. **Best practices**:
   - Only include packages not in the base `requirements.txt`
   - Specify minimum versions for compatibility
   - Keep dependencies minimal

## ✅ Validation and Testing

Your cleaner will automatically go through:

1. **Standard Tests** (automatic):
   - Data not empty
   - No completely null columns
   - Memory usage checks
   - Data type consistency

2. **Custom Tests** (optional):
   - Add `tests/test_specs/your_cleaner_name.yaml` for specific validations
   - See the Testing Guide for details

3. **Running Tests**:
   ```bash
   # Test your cleaner
   python data_cleaning.py --cleaner your_cleaner_name --test
   
   # Run and save output
   python data_cleaning.py --cleaner your_cleaner_name
   ```

## 💡 Tips for Success

1. **Start Simple**: Implement basic downloading and cleaning first, then add complexity
2. **Handle Errors Gracefully**: Use try-except blocks for network requests and file operations
3. **Log Progress**: Use `self.logger.info()` to provide feedback during processing
4. **Document Your Work**: Add docstrings and comments explaining your approach
5. **Test Incrementally**: Test download and clean methods separately before full integration

## 🆘 Getting Help

- Check existing cleaners in `cleaners/` for examples
- Review the base `DataCleaner` class in `core/base_cleaner.py`
- Look at test specifications in `tests/test_specs/`
- Ask questions in the project discussion forum

Happy cleaning! 🧹✨