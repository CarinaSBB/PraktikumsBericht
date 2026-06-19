#!/usr/bin/env python3
"""Generate a linear regression plot for the top-3 Ptotsy peaks per year from 2014 to 2019."""

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
}

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "images" / "regression"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = OUTPUT_DIR / "LR_top3_peaks_2014_2019.png"

years = []
peaks = []
for year, values in DATA.items():
    for value in values:
        years.append(year)
        peaks.append(value)

x = np.array(years, dtype=float)
y = np.array(peaks, dtype=float)

coefficients = np.polyfit(x, y, 1)
trend = np.poly1d(coefficients)
line_x = np.linspace(x.min(), x.max(), 200)
line_y = trend(line_x)

r_squared = 1.0 - np.sum((y - trend(x)) ** 2) / np.sum((y - y.mean()) ** 2)

plt.style.use("default")
fig, ax = plt.subplots(figsize=(11, 6))

ax.scatter(x, y, color="#E2001A", alpha=0.8, s=40, label="Top-3-Peaks")
ax.plot(line_x, line_y, color="#4D4D4D", linewidth=2.5, label=f"Lineare Regression (R²={r_squared:.3f})")

ax.set_title("Lineare Regression der Top-3-Peaks pro Jahr (2014--2019)")
ax.set_xlabel("Jahr")
ax.set_ylabel("Ptotsywert [MW]")
ax.grid(True, axis="both", linestyle="--", alpha=0.3)
ax.legend(loc="best")
ax.set_xticks(range(2014, 2020))
ax.set_xlim(2013.5, 2019.5)

fig.tight_layout()
fig.savefig(OUTPUT_PATH, dpi=300, bbox_inches="tight")
plt.close(fig)

print(f"Saved: {OUTPUT_PATH}")
print(f"Slope: {coefficients[0]:.6f} MW/year")
print(f"Intercept: {coefficients[1]:.6f}")
print(f"R^2: {r_squared:.6f}")
