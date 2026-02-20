"""
power_analysis.py
Performs statistical power analysis and minimum sample size calculation.
"""
import numpy as np
from scipy import stats

try:
    from statsmodels.stats.power import NormalIndPower, TTestIndPower
except ImportError:
    # Fallback implementations
    class NormalIndPower:
        def solve_power(self, effect_size, alpha, power, alternative="two-sided"):
            z_alpha = stats.norm.ppf(1 - alpha / 2)
            z_beta  = stats.norm.ppf(power)
            return ((z_alpha + z_beta) / effect_size) ** 2 if effect_size > 0 else float("inf")

    class TTestIndPower:
        def solve_power(self, effect_size, alpha, power, alternative="two-sided"):
            z_alpha = stats.norm.ppf(1 - alpha / 2)
            z_beta  = stats.norm.ppf(power)
            return 2 * ((z_alpha + z_beta) / effect_size) ** 2 if effect_size > 0 else float("inf")


def cohens_d(mean1: float, mean2: float, std1: float, std2: float) -> float:
    """Compute Cohen's d effect size for two independent groups."""
    pooled_std = np.sqrt((std1 ** 2 + std2 ** 2) / 2)
    return abs(mean2 - mean1) / pooled_std if pooled_std > 0 else 0.0


def conversion_uplift(p_control: float, p_variant: float) -> float:
    """Compute relative uplift in conversion rate."""
    return ((p_variant - p_control) / p_control) * 100 if p_control > 0 else 0.0


def effect_size_proportions(p1: float, p2: float) -> float:
    """Effect size h for two proportions (Cohen's h)."""
    return abs(2 * np.arcsin(np.sqrt(p2)) - 2 * np.arcsin(np.sqrt(p1)))


def power_analysis_conversion(
    p_control: float,
    p_variant: float,
    alpha: float = 0.05,
    power: float = 0.80,
) -> dict:
    """
    Minimum sample size per group for conversion rate test (two-proportion z-test).
    """
    effect_h = effect_size_proportions(p_control, p_variant)
    analysis = NormalIndPower()
    required_n = analysis.solve_power(effect_size=effect_h, alpha=alpha, power=power, alternative="two-sided")
    return {
        "test": "Two-Proportion Z-Test",
        "effect_size_h": round(effect_h, 4),
        "required_sample_size_per_group": int(np.ceil(required_n)),
        "alpha": alpha,
        "power": power,
    }


def power_analysis_ttest(
    mean1: float,
    mean2: float,
    std1: float,
    std2: float,
    metric: str,
    alpha: float = 0.05,
    power: float = 0.80,
) -> dict:
    """
    Minimum sample size per group for independent t-test.
    """
    d = cohens_d(mean1, mean2, std1, std2)
    analysis = TTestIndPower()
    required_n = analysis.solve_power(effect_size=d, alpha=alpha, power=power, alternative="two-sided")
    return {
        "test": f"Independent T-Test ({metric})",
        "cohens_d": round(d, 4),
        "required_sample_size_per_group": int(np.ceil(required_n)),
        "alpha": alpha,
        "power": power,
    }


def run_power_analysis(df, alpha: float = 0.05) -> dict:
    """Run full power analysis across all metrics."""
    import pandas as pd

    control = df[df["group"] == "control"]
    variant = df[df["group"] == "variant"]

    p_c = control["converted"].mean()
    p_v = variant["converted"].mean()

    conv_power = power_analysis_conversion(p_c, p_v, alpha)

    time_power = power_analysis_ttest(
        control["time_spent"].mean(), variant["time_spent"].mean(),
        control["time_spent"].std(), variant["time_spent"].std(),
        "time_spent", alpha,
    )

    clicks_power = power_analysis_ttest(
        control["clicks"].mean(), variant["clicks"].mean(),
        control["clicks"].std(), variant["clicks"].std(),
        "clicks", alpha,
    )

    uplift = conversion_uplift(p_c, p_v)

    return {
        "conversion_rate": conv_power,
        "time_spent": time_power,
        "clicks": clicks_power,
        "conversion_uplift_pct": round(uplift, 2),
        "actual_sample_size_per_group": len(control),
    }
