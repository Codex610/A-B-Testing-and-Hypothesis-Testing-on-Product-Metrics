"""
confidence_intervals.py
Computes confidence intervals for differences in metrics between groups.
"""
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.proportion import proportion_confint


def ci_difference_proportions(
    df: pd.DataFrame,
    confidence: float = 0.95,
) -> dict:
    """
    Confidence interval for the difference in conversion rates (p_variant - p_control).
    Uses the normal approximation method.
    """
    control = df[df["group"] == "control"]
    variant = df[df["group"] == "variant"]

    n_c, n_v = len(control), len(variant)
    p_c = control["converted"].mean()
    p_v = variant["converted"].mean()
    diff = p_v - p_c

    se = np.sqrt(p_c * (1 - p_c) / n_c + p_v * (1 - p_v) / n_v)
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    lower = diff - z * se
    upper = diff + z * se

    return {
        "metric": "conversion_rate_difference",
        "lower": round(lower, 6),
        "upper": round(upper, 6),
        "point_estimate": round(diff, 6),
        "confidence_level": confidence,
    }


def ci_difference_means(
    df: pd.DataFrame,
    metric: str,
    confidence: float = 0.95,
) -> dict:
    """
    Confidence interval for the difference in means (variant - control)
    using Welch's formula.
    """
    control_vals = df[df["group"] == "control"][metric].dropna()
    variant_vals = df[df["group"] == "variant"][metric].dropna()

    mean_c, mean_v = control_vals.mean(), variant_vals.mean()
    diff = mean_v - mean_c
    n_c, n_v = len(control_vals), len(variant_vals)
    var_c, var_v = control_vals.var(ddof=1), variant_vals.var(ddof=1)

    se = np.sqrt(var_c / n_c + var_v / n_v)

    # Welch–Satterthwaite degrees of freedom
    df_welch = (var_c / n_c + var_v / n_v) ** 2 / (
        (var_c / n_c) ** 2 / (n_c - 1) + (var_v / n_v) ** 2 / (n_v - 1)
    )

    t_crit = stats.t.ppf(1 - (1 - confidence) / 2, df=df_welch)
    lower = diff - t_crit * se
    upper = diff + t_crit * se

    return {
        "metric": f"{metric}_difference",
        "lower": round(lower, 4),
        "upper": round(upper, 4),
        "point_estimate": round(diff, 4),
        "confidence_level": confidence,
    }


def compute_all_cis(df: pd.DataFrame, confidence: float = 0.95) -> dict:
    """Compute confidence intervals for all metrics."""
    return {
        "conversion_rate": ci_difference_proportions(df, confidence),
        "time_spent": ci_difference_means(df, "time_spent", confidence),
        "clicks": ci_difference_means(df, "clicks", confidence),
    }
