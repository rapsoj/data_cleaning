"""
Custom tests specific to this cleaner

=== HOW TO ADD CUSTOM TESTS ===

This file is where you add validation tests specific to your cleaner's data.
The test runner will automatically discover and run any function that starts with 'test_'.

IMPORTANT: All test functions must accept exactly ONE parameter: the DataFrame (df)

TEST FUNCTION SIGNATURE:
    def test_your_test_name(df: pd.DataFrame) -> Dict[str, Any]:

RETURN FORMAT:
Each test must return a dictionary with these keys:
    {
        'passed': bool,          # Required: True if test passed, False if failed
        'message': str,          # Required: Human-readable result message
        'details': dict          # Optional: Additional information about the test
    }
"""
import pandas as pd
from typing import Dict, Any


def test_has_exactly_three_columns(df: pd.DataFrame) -> Dict[str, Any]:
    """Check that we have exactly the three expected columns"""
    expected_columns = ['date', 'value', 'category']
    actual_columns = list(df.columns)

    passed = len(actual_columns) == 3 and all(col in actual_columns for col in expected_columns)

    return {
        'passed': passed,
        'message': 'Has exactly 3 columns: date, value, category' if passed else f'Expected 3 specific columns, got {len(actual_columns)}',
        'details': {
            'expected_columns': expected_columns,
            'actual_columns': actual_columns
        }
    }


def test_categories_only_ABC(df: pd.DataFrame) -> Dict[str, Any]:
    """Check that categories are exactly A, B, and C (uppercase)"""
    if 'category' not in df.columns:
        return {
            'passed': False,
            'message': 'Category column missing',
            'details': {}
        }

    unique_categories = sorted(df['category'].unique())
    expected_categories = ['A', 'B', 'C']

    passed = unique_categories == expected_categories

    return {
        'passed': passed,
        'message': 'Categories are exactly A, B, C' if passed else f'Categories should be A, B, C but got {unique_categories}',
        'details': {
            'expected': expected_categories,
            'actual': unique_categories
        }
    }
