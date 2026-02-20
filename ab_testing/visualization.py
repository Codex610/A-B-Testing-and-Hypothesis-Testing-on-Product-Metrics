"""
visualization.py
Generates and saves analysis plots for the A/B test.
"""
from pathlib import Path
from typing import List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

PLOT_DIR = Path("outputs/plots")
COLORS = {"control": "#4A90D9", "variant": "#E8533A"}


def _save(fig: plt.Figure, name: str) -> str:
    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    path = PLOT_DIR / name
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def plot_conversion_rates(df: pd.DataFrame) -> str:
    """Bar chart comparing conversion rates between groups."""
    groups = df.groupby("group")["converted"].mean()
    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(
        groups.index, groups.values * 100,
        color=[COLORS[g] for g in groups.index],
        width=0.5, edgecolor="white", linewidth=1.5,
    )
    for bar, val in zip(bars, groups.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f"{val*100:.2f}%", ha="center", va="bottom", fontweight="bold", fontsize=12)
    ax.set_title("Conversion Rate by Group", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Group", fontsize=12)
    ax.set_ylabel("Conversion Rate (%)", fontsize=12)
    ax.set_ylim(0, groups.max() * 100 * 1.25)
    ax.grid(axis="y", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return _save(fig, "conversion_rate_bar.png")


def plot_time_spent_distribution(df: pd.DataFrame) -> str:
    """KDE + histogram comparing time_spent distributions."""
    fig, ax = plt.subplots(figsize=(9, 5))
    for group, color in COLORS.items():
        vals = df[df["group"] == group]["time_spent"]
        ax.hist(vals, bins=50, alpha=0.4, color=color, density=True, label=group.capitalize())
        vals.plot.kde(ax=ax, color=color, linewidth=2)
    ax.set_title("Time Spent Distribution: Control vs Variant", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Time Spent (minutes)", fontsize=12)
    ax.set_ylabel("Density", fontsize=12)
    ax.legend(fontsize=11)
    ax.grid(alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return _save(fig, "time_spent_distribution.png")


def plot_clicks_distribution(df: pd.DataFrame) -> str:
    """Histogram comparing clicks distributions."""
    fig, ax = plt.subplots(figsize=(9, 5))
    for group, color in COLORS.items():
        vals = df[df["group"] == group]["clicks"]
        ax.hist(vals, bins=range(0, 20), alpha=0.5, color=color,
                label=group.capitalize(), density=True, rwidth=0.85)
    ax.set_title("Clicks Distribution: Control vs Variant", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Number of Clicks", fontsize=12)
    ax.set_ylabel("Density", fontsize=12)
    ax.legend(fontsize=11)
    ax.grid(alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return _save(fig, "clicks_distribution.png")


def plot_boxplots(df: pd.DataFrame) -> str:
    """Side-by-side boxplots for time_spent and clicks."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    metrics = ["time_spent", "clicks"]
    titles = ["Time Spent (min)", "Clicks"]

    for ax, metric, title in zip(axes, metrics, titles):
        data = [df[df["group"] == g][metric].values for g in ["control", "variant"]]
        bp = ax.boxplot(data, patch_artist=True, widths=0.4,
                        medianprops=dict(color="black", linewidth=2))
        for patch, color in zip(bp["boxes"], COLORS.values()):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        ax.set_xticklabels(["Control", "Variant"], fontsize=11)
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.grid(axis="y", alpha=0.3)
        ax.spines[["top", "right"]].set_visible(False)

    fig.suptitle("Boxplot Comparison: Control vs Variant", fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    return _save(fig, "boxplots.png")


def plot_metrics_comparison(df: pd.DataFrame) -> str:
    """Grouped bar chart comparing all key metrics."""
    metrics = ["time_spent", "clicks", "session_count"]
    labels = ["Avg Time Spent (min)", "Avg Clicks", "Avg Sessions"]

    control_means = [df[df["group"] == "control"][m].mean() for m in metrics]
    variant_means = [df[df["group"] == "variant"][m].mean() for m in metrics]

    x = np.arange(len(metrics))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - width / 2, control_means, width, label="Control",
                   color=COLORS["control"], alpha=0.85)
    bars2 = ax.bar(x + width / 2, variant_means, width, label="Variant",
                   color=COLORS["variant"], alpha=0.85)

    for bars in [bars1, bars2]:
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                    f"{bar.get_height():.2f}", ha="center", va="bottom", fontsize=9)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_title("Metrics Comparison: Control vs Variant", fontsize=14, fontweight="bold", pad=15)
    ax.set_ylabel("Mean Value", fontsize=12)
    ax.legend(fontsize=11)
    ax.grid(axis="y", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return _save(fig, "metrics_comparison.png")


def generate_all_plots(df: pd.DataFrame) -> List[str]:
    """Generate and save all plots, return list of filenames."""
    paths = [
        plot_conversion_rates(df),
        plot_time_spent_distribution(df),
        plot_clicks_distribution(df),
        plot_boxplots(df),
        plot_metrics_comparison(df),
    ]
    return [Path(p).name for p in paths]
