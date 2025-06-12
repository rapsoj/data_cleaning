"""
Standard tests that run on all cleaned datasets
Each test function should return either:
- bool: Simple pass/fail
- dict: {'passed': bool, 'message': str, 'details': dict}
"""
import pandas as pd
import numpy as np
from typing import Dict, Any


def test_not_empty(df: pd.DataFrame) -> Dict[str, Any]:
    """Check that the cleaned data is not empty"""
    passed = len(df) > 0
    return {
        'passed': passed,
        'message': f"DataFrame has {len(df)} rows",
        'details': {'row_count': len(df)}
    }


def test_has_columns(df: pd.DataFrame) -> Dict[str, Any]:
    """Check that the cleaned data has columns"""
    passed = len(df.columns) > 0
    return {
        'passed': passed,
        'message': f"DataFrame has {len(df.columns)} columns",
        'details': {'columns': list(df.columns)}
    }


def test_no_all_null_columns(df: pd.DataFrame) -> Dict[str, Any]:
    """Check for columns that are entirely null"""
    null_columns = df.columns[df.isnull().all()].tolist()
    passed = len(null_columns) == 0

    return {
        'passed': passed,
        'message': f"Found {len(null_columns)} all-null columns" if not passed else "No all-null columns",
        'details': {'null_columns': null_columns}
    }


def test_no_duplicate_rows(df: pd.DataFrame) -> Dict[str, Any]:
    """Check for duplicate rows"""
    duplicates = df.duplicated().sum()
    passed = duplicates == 0

    return {
        'passed': passed,
        'message': f"Found {duplicates} duplicate rows" if not passed else "No duplicate rows",
        'details': {
            'duplicate_count': int(duplicates),
            'duplicate_percentage': round(100 * duplicates / len(df), 2) if len(df) > 0 else 0
        }
    }


def test_reasonable_memory_usage(df: pd.DataFrame) -> Dict[str, Any]:
    """Check that the DataFrame isn't using excessive memory"""
    memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
    max_memory_mb = 1000  # 1GB threshold
    passed = memory_mb < max_memory_mb

    return {
        'passed': passed,
        'message': f"Memory usage: {memory_mb:.1f} MB",
        'details': {
            'memory_mb': round(memory_mb, 2),
            'threshold_mb': max_memory_mb
        }
    }


def test_column_names_valid(df: pd.DataFrame) -> Dict[str, Any]:
    """Check that column names are clean and valid"""
    issues = []

    for col in df.columns:
        # Check for spaces
        if ' ' in col:
            issues.append(f"Column '{col}' contains spaces")

        # Check for special characters (allow underscores and alphanumeric)
        if not col.replace('_', '').isalnum():
            issues.append(f"Column '{col}' contains special characters")

    passed = len(issues) == 0

    return {
        'passed': passed,
        'message': f"Found {len(issues)} column name issues" if not passed else "All column names valid",
        'details': {'issues': issues}
    }


def test_numeric_columns_valid(df: pd.DataFrame) -> Dict[str, Any]:
    """Check numeric columns for invalid values"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    issues = {}

    for col in numeric_cols:
        col_issues = []

        # Check for infinity
        if np.isinf(df[col]).any():
            col_issues.append("Contains infinity values")

        # Check if all values are the same
        if df[col].nunique() == 1:
            col_issues.append("All values are identical")

        if col_issues:
            issues[col] = col_issues

    passed = len(issues) == 0

    return {
        'passed': passed,
        'message': f"Found issues in {len(issues)} numeric columns" if not passed else "All numeric columns valid",
        'details': {'column_issues': issues}
    }


def test_date_columns_valid(df: pd.DataFrame) -> Dict[str, Any]:
    """Check date columns are properly formatted"""
    date_columns = df.select_dtypes(include=['datetime64']).columns.tolist()

    # Also check for columns that might be dates based on name
    potential_date_cols = [col for col in df.columns
                          if any(term in col.lower() for term in ['date', 'time', 'timestamp', 'year', 'month'])]

    issues = []

    for col in potential_date_cols:
        if col not in date_columns:
            # Check if it should be a date
            if df[col].dtype == 'object':
                try:
                    # See if it can be converted to date
                    sample = df[col].dropna().iloc[:10] if len(df[col].dropna()) > 0 else []
                    if len(sample) > 0:
                        pd.to_datetime(sample)
                        issues.append(f"Column '{col}' appears to be date but is type {df[col].dtype}")
                except:
                    pass

    # Check actual date columns
    for col in date_columns:
        # Check for unreasonable dates
        if pd.notnull(df[col]).any():
            min_date = df[col].min()
            max_date = df[col].max()

            if pd.notnull(min_date) and min_date.year < 1900:
                issues.append(f"Column '{col}' has dates before 1900")

            if pd.notnull(max_date) and max_date.year > 2100:
                issues.append(f"Column '{col}' has dates after 2100")

    passed = len(issues) == 0

    return {
        'passed': passed,
        'message': f"Found {len(issues)} date column issues" if not passed else "All date columns valid",
        'details': {
            'date_columns': date_columns,
            'issues': issues
        }
    }


def test_reasonable_null_percentage(df: pd.DataFrame) -> Dict[str, Any]:
    """Check if any columns have excessive null values"""
    null_threshold = 0.95  # Flag columns that are >95% null
    high_null_cols = {}

    for col in df.columns:
        null_pct = df[col].isnull().sum() / len(df)
        if null_pct > null_threshold:
            high_null_cols[col] = round(null_pct * 100, 2)

    passed = len(high_null_cols) == 0

    return {
        'passed': passed,
        'message': f"Found {len(high_null_cols)} columns with >95% null values" if not passed else "No excessive null columns",
        'details': {
            'high_null_columns': high_null_cols,
            'threshold_percent': null_threshold * 100
        }
    }


def test_string_columns_trimmed(df: pd.DataFrame) -> Dict[str, Any]:
    """Check that string columns don't have leading/trailing whitespace"""
    string_cols = df.select_dtypes(include=['object']).columns
    issues = []

    for col in string_cols:
        # Sample the column to check for whitespace issues
        sample = df[col].dropna().head(100)
        if len(sample) > 0:
            # Check if any values have leading/trailing whitespace
            trimmed = sample.str.strip()
            if not sample.equals(trimmed):
                issues.append(f"Column '{col}' has untrimmed values")

    passed = len(issues) == 0

    return {
        'passed': passed,
        'message': f"Found {len(issues)} columns with whitespace issues" if not passed else "All string columns properly trimmed",
        'details': {'columns_with_whitespace': issues}
    }