#!/usr/bin/env python3
"""Generate linear regression plots for recent top-3 Ptotsy peaks per year."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


DATA = {
    2014: [660.118, 657.526, 655.701],
    2015: [697.533, 671.311, 668.553],
    2016: [714.926, 695.053, 693.241],
    2017: [705.758, 702.726, 690.851],
    2018: [711.028, 706.280, 702.622],
    2019: [745.177, 730.823, 712.230],
    2020: [662.056, 661.553, 659.860],
    2021: [700.802, 680.770, 678.708],
    2022: [761.653, 712.398, 688.306],
    2023: [694.894, 683.628, 679.428],
    2024: [716.878, 712.429, 701.378],
    2025: [736.110, 699.685, 698.890],
}

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "images" / "regression"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def build_plot(start_year: int, end_year: int, output_name: str, title: str) -> tuple[float, float, float]:
    years = []
    peaks = []
    for year in range(start_year, end_year + 1):
        for value in DATA[year]:
            years.append(year)
            peaks.append(value)

    x = np.array(years, dtype=float)
    y = np.array(peaks, dtype=float)

    coefficients = np.polyfit(x, y, 1)
    trend = np.poly1d(coefficients)
    line_x = np.linspace(x.min(), x.max(), 200)
    line_y = trend(line_x)

    r_squared = 1.0 - np.sum((y - trend(x)) ** 2) / np.sum((y - y.mean()) ** 2)

    fig, ax = plt.subplots(figsize=(11.5, 6))
    ax.scatter(x, y, color="#E2001A", alpha=0.8, s=38, label="Top-3-Peaks")
    ax.plot(
        line_x,
        line_y,
        color="#4D4D4D",
        linewidth=2.5,
        label=f"Lineare Regression (R²={r_squared:.3f})",
    )

    ax.set_title(title)
    ax.set_xlabel("Jahr")
    ax.set_ylabel("Ptotsywert [MW]")
    ax.grid(True, axis="both", linestyle="--", alpha=0.3)
    ax.legend(loc="best")
    ax.set_xticks(range(start_year, end_year + 1))
    ax.set_xlim(start_year - 0.5, end_year + 0.5)

    fig.tight_layout()
    output_path = OUTPUT_DIR / output_name
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved: {output_path}")
    print(f"Slope: {coefficients[0]:.6f} MW/year")
    print(f"Intercept: {coefficients[1]:.6f}")
    print(f"R^2: {r_squared:.6f}")
    return float(coefficients[0]), float(coefficients[1]), float(r_squared)


if __name__ == "__main__":
    build_plot(
        2020,
        2025,
        "LR_top3_peaks_2020_2025.png",
        "Lineare Regression der Top-3-Peaks pro Jahr (2020--2025)",
    )
    build_plot(
        2023,
        2025,
        "LR_top3_peaks_2023_2025.png",
        "Lineare Regression der Top-3-Peaks pro Jahr (2023--2025)",
    )
