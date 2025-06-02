import pandas as pd
from typing import Dict, Any


def test_not_empty(df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
    """Test that DataFrame is not empty"""
    return {
        'passed': len(df) > 0,
        'message': "DataFrame is empty",
        'details': {'row_count': len(df)}
    }


def test_no_null_columns(df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
    """Test for completely null columns"""
    null_columns = [col for col in df.columns if df[col].isnull().all()]
    return {
        'passed': len(null_columns) == 0,
        'message': f"Columns are completely null: {null_columns}",
        'details': {'null_columns': null_columns}
    }


def test_duplicate_rows(df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
    """Test for duplicate rows"""
    threshold = params.get('threshold', 0)
    duplicate_count = df.duplicated().sum()
    duplicate_pct = (duplicate_count / len(df) * 100) if len(df) > 0 else 0

    return {
        'passed': duplicate_pct < threshold,
        'message': f"Found {duplicate_count} duplicate rows ({duplicate_pct:.1f}%)",
        'details': {
            'duplicate_count': int(duplicate_count),
            'duplicate_percentage': float(duplicate_pct)
        }
    }


def test_data_types(df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
    """Check for suspicious data types"""
    issues = []

    # Check for object columns that might be numeric
    for col in df.select_dtypes(include=['object']).columns:
        sample = df[col].dropna().head(100)
        if len(sample) > 0:
            numeric_count = pd.to_numeric(sample, errors='coerce').notna().sum()
            if numeric_count / len(sample) > 0.9:
                issues.append(f"{col} appears to be numeric but stored as object")

    return {
        'passed': len(issues) == 0,
        'message': f"Data type issues: {'; '.join(issues)}",
        'details': {'issues': issues}
    }


# Add the custom test types that are referenced in the YAML
def test_no_nulls(df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
    """Test that specified columns have no null values"""
    columns = params.get('columns', [])
    null_counts = df[columns].isnull().sum()
    has_nulls = null_counts.any()

    return {
        'passed': not has_nulls,
        'message': f"Null values found in: {null_counts[null_counts > 0].to_dict()}",
        'details': {'null_counts': null_counts.to_dict()}
    }


def test_unique_keys(df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
    """Test that column combinations are unique"""
    columns = params.get('columns', [])
    dup_count = df[columns].duplicated().sum()

    return {
        'passed': dup_count == 0,
        'message': f"Found {dup_count} duplicate key combinations in {columns}",
        'details': {
            'duplicate_count': int(dup_count),
            'columns': columns
        }
    }


def test_value_range(df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
    """Test that values fall within specified range"""
    column = params.get('column')
    min_val = params.get('min', -float('inf'))
    max_val = params.get('max', float('inf'))

    out_of_range = ~df[column].between(min_val, max_val)
    count = out_of_range.sum()

    return {
        'passed': count == 0,
        'message': f"{count} values in '{column}' outside range [{min_val}, {max_val}]",
        'details': {
            'out_of_range_count': int(count),
            'expected_range': [min_val, max_val],
            'actual_range': [float(df[column].min()), float(df[column].max())]
        }
    }


def test_allowed_values(df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
    """Test that categorical values are in allowed list"""
    column = params.get('column')
    allowed = set(params.get('values', []))
    actual = set(df[column].unique())
    invalid = actual - allowed

    return {
        'passed': len(invalid) == 0,
        'message': f"Invalid values in '{column}': {sorted(invalid)}",
        'details': {
            'invalid_values': sorted(list(invalid)),
            'allowed_values': sorted(list(allowed)),
            'actual_values': sorted(list(actual))
        }
    }


def test_date_continuity(df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
    """Test that date series has no gaps"""
    date_column = params.get('column', 'date')
    frequency = params.get('frequency', 'D')  # Daily by default

    dates = pd.to_datetime(df[date_column]).sort_values()
    expected_range = pd.date_range(dates.min(), dates.max(), freq=frequency)
    missing_dates = set(expected_range) - set(dates)

    return {
        'passed': len(missing_dates) == 0,
        'message': f"Found {len(missing_dates)} missing dates in '{date_column}'",
        'details': {
            'missing_count': len(missing_dates),
            'missing_dates': [str(d) for d in sorted(missing_dates)[:10]],  # First 10
            'total_expected': len(expected_range)
        }
    }