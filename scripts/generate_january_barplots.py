#!/usr/bin/env python3
"""Generate bar charts for January Ptotsy statistics with years in ascending order."""

import matplotlib.pyplot as plt
from pathlib import Path

# Data from the user
data = {
    2014: {"mean": 293.4824, "variance": 8002.92, "p95": 442.32, "p99": 494.332},
    2015: {"mean": 309.5567, "variance": 9045.883, "p95": 465.01, "p99": 519.351},
    2016: {"mean": 307.8309, "variance": 10318.72, "p95": 474.317, "p99": 537.109},
    2017: {"mean": 328.3223, "variance": 10378.15, "p95": 491.835, "p99": 550.242},
    2018: {"mean": 292.8851, "variance": 8702.408, "p95": 442.815, "p99": 493.847},
    2019: {"mean": 311.2383, "variance": 10115.45, "p95": 474.971, "p99": 532.803},
    2020: {"mean": 294.8489, "variance": 9293.838, "p95": 453.354, "p99": 512.554},
    2021: {"mean": 296.043, "variance": 8990.277, "p95": 446.474, "p99": 500.603},
    2022: {"mean": 298.4309, "variance": 9641.617, "p95": 456.956, "p99": 515.358},
    2023: {"mean": 296.3372, "variance": 10104.64, "p95": 459.2628, "p99": 522.5864},
    2024: {"mean": 297.3638, "variance": 10189.78, "p95": 460.41, "p99": 522.681},
    2025: {"mean": 299.201, "variance": 10061.29, "p95": 459.883, "p99": 521.348},
    2026: {"mean": 307.2883, "variance": 10329.21, "p95": 471.635, "p99": 531.967},
}

# Sort years in ascending order
years = sorted(data.keys())
year_labels = [str(y) for y in years]

# Extract values
means = [data[y]["mean"] for y in years]
variances = [data[y]["variance"] for y in years]
p95s = [data[y]["p95"] for y in years]
p99s = [data[y]["p99"] for y in years]

# Output directory
ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "images" / "k_barplots_by_year"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Color scheme
color_sbbred = "#E2001A"

# Create separate bar charts
fig_config = [
    ("mean", means, "Mittelwert (MW)", "january_mean_by_year.png"),
    ("variance", variances, "Varianz (MW²)", "january_variance_by_year.png"),
    ("p95", p95s, "95%-Perzentil (MW)", "january_p95_by_year.png"),
    ("p99", p99s, "99%-Perzentil (MW)", "january_p99_by_year.png"),
]

for key, values, ylabel, filename in fig_config:
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Create bar chart
    bars = ax.bar(year_labels, values, color=color_sbbred, alpha=0.85, edgecolor="black", linewidth=0.5)
    
    # Formatting
    ax.set_xlabel("Jahr", fontsize=12, fontweight="bold")
    ax.set_ylabel(ylabel, fontsize=12, fontweight="bold")
    ax.set_title(f"Januar: {ylabel} (2014-2026)", fontsize=14, fontweight="bold")
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{height:.1f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    
    # Rotate x-axis labels
    ax.tick_params(axis="x", rotation=45)
    
    # Tight layout
    plt.tight_layout()
    
    # Save figure
    output_path = OUTPUT_DIR / filename
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved: {output_path}")
    
    plt.close(fig)

print("\nAll January bar charts created successfully!")
