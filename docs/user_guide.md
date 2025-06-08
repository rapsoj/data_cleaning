# User Guide: Data Cleaning Pipeline

## 📖 Introduction

The Data Cleaning Pipeline is an automated framework for standardizing data preparation in machine learning projects. It provides a consistent interface for data cleaning tasks, automatic validation, and seamless integration with downstream ML pipelines, eliminating the bottleneck of manual data preparation and ensuring reproducible, high-quality datasets.

## 🔧 Usage

### Running from Command Line

The pipeline can be executed directly from the command line with various options:

```bash
python data_cleaning.py [OPTIONS]
```

### Running from IDE (PyCharm, VS Code, etc.)

1. Open `data_cleaning.py` in your IDE
2. Configure run parameters in your IDE's run configuration
3. Run the script directly

### Command Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--cleaner NAME` | Run a specific cleaner | `--cleaner weather_data` |
| `--list` | List all available cleaners | `--list` |
| `--list-all` | List all cleaners including those with missing dependencies | `--list-all` |
| `--info NAME` | Get detailed information about a specific cleaner | `--info weather_data` |
| `--test` | Run in test mode (validates data without saving) | `--cleaner weather_data --test` |
| `--disk` | Use disk-based processing for large datasets | `--cleaner large_dataset --disk` |
| `--parallel` | Run multiple cleaners in parallel (default: True) | `--parallel` |
| `--output-dir PATH` | Specify custom output directory | `--output-dir /custom/path` |
| `--install-deps NAME` | Install dependencies for a specific cleaner | `--install-deps weather_data` |

### Examples

```bash
# List available cleaners
python data_cleaning.py --list

# Run a specific cleaner
python data_cleaning.py --cleaner weather_data

# Test a cleaner without saving output
python data_cleaning.py --cleaner weather_data --test

# Run cleaner with disk-based processing
python data_cleaning.py --cleaner large_dataset --disk

# Install missing dependencies
python data_cleaning.py --install-deps weather_data

# Run all cleaners
python data_cleaning.py
```

### Data Flow and File Structure

```
data/
├── raw/                    # Downloaded raw data
│   └── weather_data/       # Raw data for each cleaner
│       └── data.csv
├── cleaned/                # Cleaned output data
│   └── weather_data_cleaned.csv   # Standardized output
└── temp/                   # Temporary processing files
```

**Output Location**: All cleaned data is automatically saved to `data/cleaned/{cleaner_name}_cleaned.csv`

## 🧪 Testing

### How Testing Works

The testing framework automatically discovers and runs tests to ensure data quality:

1. **Standard Tests**: Run automatically on all cleaners
2. **Custom Tests**: Defined in test specifications for specific cleaners

### Test Discovery

Tests are dynamically discovered from all Python files in `tests/test_definitions/`. Any function starting with `test_` is automatically registered:

```python
# tests/test_definitions/my_custom_tests.py
def test_my_validation(df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
    """Custom validation test"""
    # Your test logic
    return {
        'passed': True/False,
        'message': 'Description of result',
        'details': {...}
    }
```

### Adding New Tests

1. **Create a test function** in any file under `tests/test_definitions/`:
   ```python
   def test_date_format(df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
       column = params.get('column')
       try:
           pd.to_datetime(df[column])
           return {'passed': True, 'message': 'Date format valid'}
       except:
           return {'passed': False, 'message': f'Invalid date format in {column}'}
   ```

2. **Use in test specifications**:
   ```yaml
   # tests/test_specs/weather_data.yaml
   tests:
     date_validation:
       type: date_format
       params:
         column: date
       severity: error
   ```

### Default Tests

All cleaners automatically undergo these standard tests:

| Test | Purpose | Severity |
|------|---------|----------|
| `not_empty` | Ensures DataFrame has data | Error |
| `no_null_columns` | Detects completely empty columns | Error |
| `duplicate_rows` | Warns about excessive duplicates (>10%) | Warning |
| `data_types` | Detects suspicious type mismatches | Warning |
| `memory_usage` | Alerts if data uses >2GB memory | Warning |

### Test Specifications

Custom test specifications are YAML files in `tests/test_specs/` that define additional validations:

```yaml
# tests/test_specs/weather_data.yaml
tests:
  # Ensure critical fields have no nulls
  required_fields:
    type: no_nulls
    params:
      columns: [date, temperature, location]
    severity: error
  
  # Validate temperature range
  temp_range:
    type: value_range
    params:
      column: temperature
      min: -50
      max: 60
    severity: warning
  
  # Custom business logic
  data_freshness:
    type: expression
    params:
      expression: |
        (pd.Timestamp.now() - df['date'].max()).days < 7
      failure_message: "Data is more than 7 days old"
    severity: warning
```

**Available Test Types**:
- `no_nulls`: Check for null values in specified columns
- `unique_keys`: Ensure column combinations are unique
- `value_range`: Validate numeric ranges
- `allowed_values`: Check categorical values
- `regex_match`: Validate string patterns
- `expression`: Custom Python expressions

## 👥 Student Usage

### General Workflow

Students interact with the pipeline by creating data cleaners that follow our standardized interface. For detailed instructions, see `STUDENT_GUIDE.md`.

### Common Student Questions

**Q: Where do I put my code?**
A: Either in `cleaners/your_cleaner_name/` in this repo, or in your own GitHub repository.

**Q: What if I need special Python packages?**
A: Add a `requirements.txt` file in your cleaner directory. The pipeline will detect and prompt for installation.

**Q: How do I test my cleaner?**
A: Run `python data_cleaning.py --cleaner your_cleaner_name --test`

**Q: My cleaner fails with "Missing dependencies" - what do I do?**
A: Run `python data_cleaning.py --install-deps your_cleaner_name` or manually install the packages listed in the error message.

**Q: Can I process large files that don't fit in memory?**
A: Yes! Implement `download_to_path()` and `clean_from_path()` methods instead of the in-memory versions.

**Q: Where does my cleaned data go?**
A: Automatically saved to `data/cleaned/your_cleaner_name_cleaned.csv`

**Q: What if my data source requires authentication?**
A: Store credentials in environment variables or config files (never commit secrets!). Access them in your cleaner's `__init__` method.

### Tips for Students

1. Start with the template in `cleaners/template/`
2. Test frequently during development
3. Use meaningful log messages with `self.logger.info()`
4. Handle errors gracefully with try-except blocks
5. Document your data sources and cleaning decisions

## 🏗️ Repository Structure

```
data-cleaning-pipeline/
├── data_cleaning.py         # Main orchestrator
├── requirements.txt         # Base dependencies
├── STUDENT_GUIDE.md        # Detailed guide for contributors
├── USER_GUIDE.md           # This file
│
├── core/                    # Core framework
│   ├── base_cleaner.py     # Abstract base class defining the interface
│   ├── validators.py       # Common validation functions
│   └── utils.py           # Shared utilities
│
├── cleaners/               # Built-in cleaners
│   ├── template/          # Starter template for students
│   └── example_cleaner/   # Example implementation
│
├── external_cleaners/      # External cleaner repositories
│   └── .gitignore
│
├── tests/                  # Testing framework
│   ├── test_framework.py   # Main test orchestrator
│   ├── test_registry.py    # Dynamic test discovery
│   ├── test_definitions/   # Test function implementations
│   │   ├── builtin_tests.py
│   │   └── statistical_tests.py
│   └── test_specs/        # YAML test configurations
│
└── data/                   # Data storage
    ├── raw/               # Downloaded raw data
    ├── cleaned/           # Processed output
    └── temp/              # Temporary files
```

### Design Decisions

**1. Plugin-Based Architecture**
- **Why**: Allows independent development without modifying core code
- **Benefit**: Students can work in isolation; easy to add/remove cleaners

**2. Dual Implementation Options (Memory/Disk)**
- **Why**: Different datasets have different size constraints
- **Benefit**: Flexibility for both small and large dataset processing

**3. Automatic Test Discovery**
- **Why**: Easy to extend testing without modifying framework
- **Benefit**: Anyone can add tests by simply creating functions

**4. Standardized Output Location**
- **Why**: Downstream processes need predictable data locations
- **Benefit**: Enables pipeline automation and data versioning

**5. Separate Test Definitions and Specifications**
- **Why**: Reusable test logic with configurable parameters
- **Benefit**: Same test function can be used with different thresholds

**6. External Cleaner Support**
- **Why**: Students may prefer their own repositories
- **Benefit**: Supports different workflows and version control preferences

**7. Dependency Isolation**
- **Why**: Different cleaners need different packages
- **Benefit**: Avoids dependency conflicts; only install what's needed

This architecture prioritizes:
- **Modularity**: Each component has a single responsibility
- **Extensibility**: Easy to add new cleaners, tests, or features
- **Usability**: Clear interfaces and helpful error messages
- **Reliability**: Comprehensive testing and validation