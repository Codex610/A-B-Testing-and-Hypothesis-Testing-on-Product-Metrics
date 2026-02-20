"""
business_insights.py
Derives business interpretations and final rollout recommendation.
"""
import pandas as pd


def compute_metrics_summary(df: pd.DataFrame) -> dict:
    """Compute summary metrics for both groups."""
    control = df[df["group"] == "control"]
    variant = df[df["group"] == "variant"]

    return {
        "control": {
            "n_users": len(control),
            "conversion_rate": round(control["converted"].mean(), 4),
            "avg_time_spent": round(control["time_spent"].mean(), 4),
            "avg_clicks": round(control["clicks"].mean(), 4),
            "avg_session_count": round(control["session_count"].mean(), 4),
            "total_conversions": int(control["converted"].sum()),
        },
        "variant": {
            "n_users": len(variant),
            "conversion_rate": round(variant["converted"].mean(), 4),
            "avg_time_spent": round(variant["time_spent"].mean(), 4),
            "avg_clicks": round(variant["clicks"].mean(), 4),
            "avg_session_count": round(variant["session_count"].mean(), 4),
            "total_conversions": int(variant["converted"].sum()),
        },
        "differences": {
            "conversion_rate_diff": round(variant["converted"].mean() - control["converted"].mean(), 4),
            "time_spent_diff": round(variant["time_spent"].mean() - control["time_spent"].mean(), 4),
            "clicks_diff": round(variant["clicks"].mean() - control["clicks"].mean(), 4),
        },
    }


def generate_business_insights(metrics: dict, test_results: dict, power: dict) -> dict:
    """
    Combine test results with business context to produce insights and recommendation.
    """
    conv_sig = test_results["conversion_rate"]["significant"]
    time_sig = test_results["time_spent"]["significant"]
    clicks_sig = test_results["clicks"]["significant"]

    uplift = power["conversion_uplift_pct"]
    diff = metrics["differences"]

    insights = []

    if conv_sig:
        insights.append(
            f"The variant group achieved a statistically significant lift of "
            f"{uplift:.2f}% in conversion rate "
            f"({metrics['control']['conversion_rate']*100:.2f}% → {metrics['variant']['conversion_rate']*100:.2f}%). "
            "This directly impacts revenue."
        )
    else:
        insights.append(
            "Conversion rate difference is not statistically significant. "
            "No reliable evidence the variant improves conversions."
        )

    if time_sig:
        insights.append(
            f"Users in the variant spent on average {diff['time_spent_diff']:.2f} more minutes per session, "
            "indicating improved engagement."
        )
    if clicks_sig:
        insights.append(
            f"Variant users averaged {diff['clicks_diff']:.2f} more clicks, "
            "suggesting better interaction with the product."
        )

    # Recommendation logic
    significant_count = sum([conv_sig, time_sig, clicks_sig])
    if significant_count >= 2 and conv_sig and uplift > 0:
        recommendation = "ROLLOUT"
        rationale = (
            "Multiple metrics show statistically significant improvement in the variant. "
            "A positive conversion uplift with increased engagement metrics strongly supports "
            "deploying the variant to all users."
        )
    elif conv_sig and uplift > 5:
        recommendation = "ROLLOUT"
        rationale = (
            f"Conversion rate uplift of {uplift:.2f}% is both statistically significant and "
            "practically meaningful. Recommend full rollout."
        )
    elif significant_count == 1 and not conv_sig:
        recommendation = "DO NOT ROLLOUT"
        rationale = (
            "No significant improvement in the primary metric (conversion rate). "
            "Engagement improvements alone do not justify a full rollout. "
            "Consider further experimentation."
        )
    else:
        recommendation = "MONITOR"
        rationale = (
            "Results are mixed. Some metrics show improvement but the primary metric "
            "does not meet significance thresholds. Recommend extending the experiment."
        )

    return {
        "insights": insights,
        "recommendation": recommendation,
        "rationale": rationale,
        "significant_metrics": significant_count,
        "total_metrics_tested": 3,
    }
