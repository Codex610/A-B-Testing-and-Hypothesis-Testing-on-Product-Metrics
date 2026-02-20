"""
data_generator.py
Generates synthetic A/B test dataset with realistic distributions.
"""
import numpy as np
import pandas as pd
from pathlib import Path


def generate_ab_test_data(n_users: int = 20000, seed: int = 42) -> pd.DataFrame:
    """
    Generate a synthetic A/B test dataset.

    Args:
        n_users: Total number of users to generate.
        seed: Random seed for reproducibility.

    Returns:
        DataFrame with columns: user_id, group, converted, time_spent, clicks, session_count, date
    """
    np.random.seed(seed)

    # Split users equally
    n_control = n_users // 2
    n_variant = n_users - n_control

    # ── Control group ──────────────────────────────────────────────────────────
    control_converted = np.random.binomial(1, 0.12, n_control)          # 12% CVR
    control_time = np.random.gamma(shape=2.5, scale=3.0, size=n_control)  # ~7.5 min
    control_clicks = np.random.poisson(lam=3.2, size=n_control)
    control_sessions = np.random.poisson(lam=2.1, size=n_control) + 1

    # ── Variant group ──────────────────────────────────────────────────────────
    variant_converted = np.random.binomial(1, 0.148, n_variant)          # 14.8% CVR
    variant_time = np.random.gamma(shape=2.7, scale=3.3, size=n_variant)  # ~8.9 min
    variant_clicks = np.random.poisson(lam=3.9, size=n_variant)
    variant_sessions = np.random.poisson(lam=2.4, size=n_variant) + 1

    # ── Dates (last 30 days) ────────────────────────────────────────────────
    dates = pd.date_range(end="2024-12-31", periods=30).date
    control_dates = np.random.choice(dates, size=n_control)
    variant_dates = np.random.choice(dates, size=n_variant)

    # ── Assemble DataFrames ────────────────────────────────────────────────
    control_df = pd.DataFrame({
        "user_id": range(1, n_control + 1),
        "group": "control",
        "converted": control_converted,
        "time_spent": np.round(control_time, 2),
        "clicks": control_clicks,
        "session_count": control_sessions,
        "date": control_dates,
    })

    variant_df = pd.DataFrame({
        "user_id": range(n_control + 1, n_users + 1),
        "group": "variant",
        "converted": variant_converted,
        "time_spent": np.round(variant_time, 2),
        "clicks": variant_clicks,
        "session_count": variant_sessions,
        "date": variant_dates,
    })

    df = pd.concat([control_df, variant_df], ignore_index=True)
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    df["user_id"] = range(1, len(df) + 1)
    return df


def save_dataset(df: pd.DataFrame, path: str) -> None:
    """Save DataFrame to CSV."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
