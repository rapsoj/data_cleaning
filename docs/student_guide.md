# Beginner's Guide: How to Add a Data Cleaner

Welcome! This guide will help you write a **data cleaner** that fits into our machine learning project. Don't worry if you're new — we'll walk through it step by step. 

**Important**: Throughout this process, refer to the `Data Sources` tab of the `project-tracking` file for your project. It contains specifications for your cleaned data and helps track cleaning progress.

---

## What's a Data Cleaner?

A **data cleaner** is Python code that:

1. **Downloads** raw data from a source
2. **Cleans it up** (fixes missing values, standardises formats, selects relevant columns)
3. **Returns clean data** ready for machine learning

Our system handles saving results and running tests — you just need to write the cleaning logic.

---

## Before You Start

### 1. Understand Your Dataset

This is the most important step! Better models come from better data, and better data starts with understanding it.

**Check your assignment**: Look in the `project-tracking` file to see which dataset you're responsible for.

**Explore in a notebook**:

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the data
df = pd.read_csv('your_data.csv')  # or however you access it

# Basic exploration
df.head()                    # First few rows
df.info()                    # Column names and types
df.describe()                # Statistical summary
df.isnull().sum()           # Missing values per column

# Visualize key variables
df['your_column'].hist()     # Distribution
df.plot(x='date', y='value') # Trends over time
```

**Document what you find**:
- Missing values that need handling
- Incorrect data types (dates stored as strings, etc.)
- Outliers or impossible values
- Inconsistent formats (e.g., "N/A" vs actual nulls)

You'll become your project's expert on this dataset, so understand what each column means and how they relate to your target variable.

### 2. Test Your Cleaning Logic

Before writing the cleaner, test your cleaning steps in a notebook:
- Figure out how to download/access the data
- Test each cleaning step individually
- Verify the output matches the format specified in `project-tracking`

---

## Getting Started

### Step 1: Clone the Repository

**Option A: Using GitHub Desktop** (Recommended for beginners)
1. Install [GitHub Desktop](https://desktop.github.com)
2. Click `File` → `Clone Repository`
3. Find your project repo
4. Choose a local folder (e.g., `Documents/your-project`)
5. Click `Clone`

**Option B: Using Terminal**
```bash
git clone https://github.com/your-org/your-project.git
cd your-project
```

### Step 2: Edit the Cleaner File

1. Open `cleaner.py` in your favourite editor (VS Code recommended)
2. You'll see a template with empty functions to fill in
3. Replace the TODO comments with your actual code

### Step 3: Fill in the Required Functions

#### `get_metadata()`
Provide information about your data source:

```python
def get_metadata(self) -> Dict[str, Any]:
    return {
        'source': 'World Bank Open Data',
        'description': 'Economic indicators by country and year',
        'update_frequency': 'annual',  # or 'daily', 'monthly', 'static'
        'url': 'https://data.worldbank.org'
    }
```

#### `download_data()`
Download your raw data:

```python
def download_data(self) -> pd.DataFrame:
    # For a CSV from URL:
    return pd.read_csv("https://example.com/data.csv")
    
    # For an API:
    response = requests.get("https://api.example.com/data")
    return pd.DataFrame(response.json())
    
    # For a local file (if static):
    return pd.read_csv("data/raw/my_data.csv")
```

#### `clean_data()`
Clean the raw data:

```python
def clean_from_df(self, df: pd.DataFrame) -> pd.DataFrame:
    # Always work on a copy
    cleaned = df.copy()
    
    # Common cleaning steps:
    
    # 1. Standardise column names
    cleaned.columns = cleaned.columns.str.lower().str.replace(' ', '_')
    
    # 2. Handle missing values
    cleaned['population'] = cleaned['population'].fillna(0)
    cleaned = cleaned.dropna(subset=['country_code'])  # Drop if key column missing
    
    # 3. Fix data types
    cleaned['date'] = pd.to_datetime(cleaned['date'])
    cleaned['gdp'] = pd.to_numeric(cleaned['gdp'], errors='coerce')
    
    # 4. Filter to relevant data
    cleaned = cleaned[cleaned['year'] >= 2000]
    
    # 5. Ensure join keys exist (check project-tracking!)
    # These columns must be present for merging with other datasets
    required_columns = ['country_code', 'year']  # Example
    assert all(col in cleaned.columns for col in required_columns)
    
    return cleaned
```

### Step 4: Test Your Cleaner

```bash
# Run your cleaner
python data_cleaning.py

# Run with validation tests
python data_cleaning.py --test

# See what info your cleaner provides
python data_cleaning.py --info
```

If tests fail, read the error messages — they'll tell you what needs fixing.

### Step 5: Commit and Push Your Changes

**Using GitHub Desktop**:
1. You'll see your changes listed
2. Write a commit message (e.g., "Implement World Bank data cleaner")
3. Click `Commit to main`
4. Click `Push origin`

**Using Terminal**:
```bash
git add cleaner.py
git commit -m "Implement World Bank data cleaner"
git push origin main
```

---

## Tips for Success

### Common Cleaning Tasks

**Standardise column names**:
```python
# Remove spaces, make lowercase
df.columns = df.columns.str.lower().str.replace(' ', '_')
```

**Handle different types of missing values**:
```python
# Replace various null representations
df.replace(['N/A', 'NA', '-', ''], pd.NA, inplace=True)
```

**Parse dates consistently**:
```python
# Handle different date formats
df['date'] = pd.to_datetime(df['date'], errors='coerce')
```

**Remove duplicates intelligently**:
```python
# Keep the most recent record for each country
df.sort_values('date', ascending=False).drop_duplicates(['country'])
```

### Debugging Tips

1. **Use logging**: The cleaner has a built-in logger
   ```python
   self.logger.info(f"Downloaded {len(df)} records")
   self.logger.warning(f"Dropped {null_count} rows with missing data")
   ```

2. **Test incrementally**: Don't write all cleaning steps at once. Add one, test, repeat.

3. **Check the output**: Look at `data/cleaned/cleaned_data.csv` after running

4. **Run validation tests**: They catch common issues like empty data or missing columns

### Using Additional Packages

If you need extra libraries, add them to `requirements.txt`:
```
requests>=2.28.0
beautifulsoup4>=4.11.0
openpyxl>=3.0.0  # For Excel files
```

---

## Working with Different Data Sources

### CSV from URL
```python
def download_data(self):
    return pd.read_csv("https://data.example.com/file.csv")
```

### API with Authentication
```python
def download_data(self):
    headers = {'Authorization': 'Bearer YOUR_TOKEN'}
    response = requests.get("https://api.example.com/data", headers=headers)
    response.raise_for_status()  # Check for errors
    return pd.DataFrame(response.json()['results'])
```

### Excel Files
```python
def download_data(self):
    return pd.read_excel("https://example.com/data.xlsx", sheet_name="Data")
```

### Web Scraping
```python
def download_data(self):
    # Only if no API/direct download available!
    response = requests.get("https://example.com/table")
    soup = BeautifulSoup(response.content, 'html.parser')
    # ... scraping logic ...
    return pd.DataFrame(scraped_data)
```

---

## Quick Checklist

Before submitting:

- [ ] `get_metadata()` returns accurate information about your data source
- [ ] `download_data()` successfully downloads the data
- [ ] `clean_data()` handles all data quality issues you identified
- [ ] Required join keys from `project-tracking` are present in cleaned data
- [ ] `python data_cleaning.py --test` passes all tests
- [ ] Committed and pushed your changes to GitHub

---

## Getting Help

- **Look at the example**: Run `python data_cleaning.py --cleaner-file example_cleaner` to see a working cleaner
- **Check test details**: If tests fail, read the specific error messages
- **Ask questions**: Reach out to your team lead or post in the project chat

Remember: The goal is clean, consistent data that can be merged with other datasets in your ML pipeline. Take time to understand your data — it's worth it!
