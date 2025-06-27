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

SIMPLE EXAMPLE:
    def test_has_price_column(df):
        passed = 'price' in df.columns
        return {
            'passed': passed,
            'message': 'Price column exists' if passed else 'Missing price column',
            'details': {'columns': list(df.columns)}
        }

COMPLEX EXAMPLE:
    def test_price_is_positive(df):
        if 'price' not in df.columns:
            return {
                'passed': False,
                'message': 'Cannot check prices - price column missing',
                'details': {}
            }

        negative_prices = (df['price'] < 0).sum()
        total_prices = len(df['price'].dropna())
        passed = negative_prices == 0

        return {
            'passed': passed,
            'message': f'Found {negative_prices} negative prices out of {total_prices}',
            'details': {
                'negative_count': int(negative_prices),
                'total_count': int(total_prices),
                'min_price': float(df['price'].min()) if total_prices > 0 else None,
                'max_price': float(df['price'].max()) if total_prices > 0 else None
            }
        }

TEST CATEGORIES TO CONSIDER:
1. **Required Columns**: Check if essential columns exist
2. **Data Types**: Verify columns have correct types (numeric, date, string)
3. **Value Ranges**: Ensure values fall within expected bounds
4. **Relationships**: Validate relationships between columns
5. **Business Rules**: Check domain-specific constraints
6. **Completeness**: Verify required fields are not null
7. **Consistency**: Ensure data follows expected patterns

BEST PRACTICES:
- Make test names descriptive: test_population_is_positive not test_pop
- Return helpful messages that explain what went wrong
- Include relevant details to help debugging
- Handle edge cases (empty df, missing columns)
- Convert numpy types to Python types in details (use int(), float(), etc.)
- Consider making some tests warnings (passed=True with warning in message)

TIPS:
- Access columns safely: use 'column' in df.columns before accessing
- Handle NaN values: use df['col'].dropna() when needed
- For numeric comparisons, consider using pandas methods like .any(), .all()
- Remember that df might be empty or have unexpected structure
- Use type hints for clarity (though not required)
"""
import pandas as pd
from typing import Dict, Any


# Add your custom test functions below this line
# Remember: All functions must start with 'test_' and accept only a DataFrame parameter