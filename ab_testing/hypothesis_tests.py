"""
hypothesis_tests.py
Implements Two-Proportion Z-test and Independent T-tests for A/B analysis.
"""
from dataclasses import dataclass
from typing import Tuple

import numpy as np
import pandas as pd
from scipy import stats

try:
    from statsmodels.stats.proportion import proportions_ztest
except ImportError:
    # Fallback if statsmodels not installed
    def proportions_ztest(count, nobs, alternative="two-sided"):
        p1 = count[0] / nobs[0]
        p2 = count[1] / nobs[1]
        p_pool = (count[0] + count[1]) / (nobs[0] + nobs[1])
        se = np.sqrt(p_pool * (1 - p_pool) * (1 / nobs[0] + 1 / nobs[1]))
        z = (p1 - p2) / se if se > 0 else 0.0
        p = 2 * (1 - stats.norm.cdf(abs(z)))
        return z, p


@dataclass
class TestResult:
    """Holds the result of a single hypothesis test."""
    metric: str
    test_type: str
    statistic: float
    p_value: float
    significant: bool
    alpha: float = 0.05
    interpretation: str = ""


def two_proportion_ztest(
    df: pd.DataFrame,
    alpha: float = 0.05,
) -> TestResult:
    """
    Two-proportion Z-test for conversion rate difference.

    H0: p_control == p_variant
    H1: p_control != p_variant (two-tailed)
    """
    control = df[df["group"] == "control"]
    variant = df[df["group"] == "variant"]

    n_c = len(control)
    n_v = len(variant)
    conv_c = control["converted"].sum()
    conv_v = variant["converted"].sum()

    count = np.array([conv_v, conv_c])
    nobs = np.array([n_v, n_c])

    z_stat, p_val = proportions_ztest(count, nobs, alternative="two-sided")

    significant = p_val < alpha
    rate_c = conv_c / n_c
    rate_v = conv_v / n_v
    uplift = ((rate_v - rate_c) / rate_c) * 100

    interpretation = (
        f"Conversion rate: Control={rate_c:.4f} ({rate_c*100:.2f}%), "
        f"Variant={rate_v:.4f} ({rate_v*100:.2f}%). "
        f"Uplift={uplift:.2f}%. "
        + ("Statistically significant difference detected." if significant
           else "No statistically significant difference detected.")
    )

    return TestResult(
        metric="conversion_rate",
        test_type="Two-Proportion Z-Test",
        statistic=round(z_stat, 4),
        p_value=round(p_val, 6),
        significant=significant,
        alpha=alpha,
        interpretation=interpretation,
    )


def independent_ttest(
    df: pd.DataFrame,
    metric: str,
    alpha: float = 0.05,
) -> TestResult:
    """
    Independent samples T-test for a continuous metric.

    H0: mean_control == mean_variant
    H1: mean_control != mean_variant (two-tailed)
    """
    control_vals = df[df["group"] == "control"][metric].dropna()
    variant_vals = df[df["group"] == "variant"][metric].dropna()

    t_stat, p_val = stats.ttest_ind(control_vals, variant_vals, equal_var=False)

    significant = p_val < alpha
    mean_c = control_vals.mean()
    mean_v = variant_vals.mean()
    diff = mean_v - mean_c

    interpretation = (
        f"{metric}: Control mean={mean_c:.4f}, Variant mean={mean_v:.4f}. "
        f"Difference={diff:.4f}. "
        + ("Statistically significant difference detected." if significant
           else "No statistically significant difference detected.")
    )

    return TestResult(
        metric=metric,
        test_type="Independent T-Test (Welch)",
        statistic=round(t_stat, 4),
        p_value=round(p_val, 6),
        significant=significant,
        alpha=alpha,
        interpretation=interpretation,
    )


def run_all_tests(df: pd.DataFrame, alpha: float = 0.05) -> dict:
    """Run full hypothesis testing suite and return results as dict."""
    conv_result = two_proportion_ztest(df, alpha)
    time_result = independent_ttest(df, "time_spent", alpha)
    clicks_result = independent_ttest(df, "clicks", alpha)

    return {
        "conversion_rate": vars(conv_result),
        "time_spent": vars(time_result),
        "clicks": vars(clicks_result),
    }
