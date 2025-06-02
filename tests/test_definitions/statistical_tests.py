import pandas as pd
import numpy as np
from typing import Dict, Any
from scipy import stats


def test_distribution_normal(df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
    """Test if a column follows normal distribution"""
    column = params.get('column')
    alpha = params.get('alpha', 0.05)

    # Use Shapiro-Wilk test for normality
    data = df[column].dropna()
    sample_size = min(5000, len(data))  # Shapiro-Wilk has sample size limits

    if len(data) < 3:
        return {
            'passed': False,
            'message': f"Not enough data in '{column}' for normality test",
            'details': {'sample_size': len(data)}
        }

    statistic, p_value = stats.shapiro(data.sample(sample_size))

    return {
        'passed': p_value > alpha,
        'message': f"Column '{column}' {'appears' if p_value > alpha else 'does not appear'} normally distributed (p={p_value:.4f})",
        'details': {
            'p_value': float(p_value),
            'statistic': float(statistic),
            'alpha': alpha,
            'sample_size': sample_size
        }
    }


def test_outliers_zscore(df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
    """Test for outliers using z-score method"""
    column = params.get('column')
    threshold = params.get('threshold', 3)
    max_outlier_pct = params.get('max_percentage', 5)

    data = df[column].dropna()
    mean = data.mean()
    std = data.std()

    if std == 0:
        return {
            'passed': True,
            'message': f"Column '{column}' has no variation (std=0)",
            'details': {'std': 0}
        }

    z_scores = np.abs((data - mean) / std)
    outlier_count = (z_scores > threshold).sum()
    outlier_pct = (outlier_count / len(data)) * 100

    return {
        'passed': outlier_pct <= max_outlier_pct,
        'message': f"Column '{column}' has {outlier_count} outliers ({outlier_pct:.1f}% > {threshold} std devs)",
        'details': {
            'outlier_count': int(outlier_count),
            'outlier_percentage': float(outlier_pct),
            'threshold': threshold,
            'max_allowed_percentage': max_outlier_pct
        }
    }


def test_correlation(df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
    """Test correlation between two columns"""
    col1 = params.get('column1')
    col2 = params.get('column2')
    min_correlation = params.get('min_correlation', None)
    max_correlation = params.get('max_correlation', None)

    # Calculate correlation
    corr = df[[col1, col2]].corr().iloc[0, 1]

    passed = True
    messages = []

    if min_correlation is not None and corr < min_correlation:
        passed = False
        messages.append(f"correlation {corr:.3f} < minimum {min_correlation}")

    if max_correlation is not None and corr > max_correlation:
        passed = False
        messages.append(f"correlation {corr:.3f} > maximum {max_correlation}")

    message = f"Correlation between '{col1}' and '{col2}' is {corr:.3f}"
    if messages:
        message += f" ({'; '.join(messages)})"

    return {
        'passed': passed,
        'message': message,
        'details': {
            'correlation': float(corr),
            'min_correlation': min_correlation,
            'max_correlation': max_correlation
        }
    }