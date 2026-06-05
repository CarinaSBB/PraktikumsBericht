#!/usr/bin/env python3
"""Generate bar charts for selected harmonic k values."""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

TARGET_K = [8, 12, 24, 48, 96, 288, 1440]
TARGET_WEEKS = [4, 26]
RANGE_PERIODS = {
    "jan_feb": {
        "start": "01-06",
        "end": "02-28",
        "title": "Zeitraum Jan-Feb",
        "caption": "Zeitraum Jan-Feb",
        "output_suffix": "kwfrom_jan_feb",
        "color": "#e76f51",
    },
    "jun_aug": {
        "start": "06-20",
        "end": "08-20",
        "title": "Zeitraum Jun-Aug",
        "caption": "Zeitraum Juni bis August",
        "output_suffix": "kwfrom_jun_aug",
        "color": "#457b9d",
    },
}
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "harmonics"
WEEKLY_DATA_DIR = DATA_DIR / "weekly"
RANGE_DATA_DIR = DATA_DIR / "ranges"
OUTPUT_DIR = ROOT / "images" / "k_barplots_by_year"


def detect_delimiter(path: Path) -> str:
    sample = path.read_text(encoding="utf-8", errors="ignore")[:4096]
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;").delimiter
    except csv.Error:
        return ";" if sample.count(";") > sample.count(",") else ","


def extract_year(filename: str) -> int | None:
    match = re.search(r"kw(\d{4})", filename)
    return int(match.group(1)) if match else None


def extract_week(filename: str) -> int | None:
    match = re.search(r"kw\d{4}_kw(\d+)", filename)
    return int(match.group(1)) if match else None


def extract_year_from_range(filename: str) -> int | None:
    match = re.search(r"kwfrom(\d{4})-", filename)
    return int(match.group(1)) if match else None


def detect_range_period(filename: str) -> str | None:
    for period_name, config in RANGE_PERIODS.items():
        if config["start"] in filename and config["end"] in filename:
            return period_name
    return None


def read_rows(path: Path) -> list[dict[str, str]]:
    delimiter = detect_delimiter(path)
    with path.open("r", encoding="utf-8", errors="ignore", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        return [row for row in reader if row]


def to_float(value: str | None) -> float | None:
    if value is None:
        return None
    value = value.strip().replace(",", ".")
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def mean_or_zero(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def create_grouped_plot(
    data_by_year: dict[int, dict[int, list[float]]],
    output_dir: Path,
    week: int,
) -> Path | None:
    years = sorted(data_by_year)
    if not years:
        return None

    x_positions = list(range(len(TARGET_K)))
    fig, ax = plt.subplots(figsize=(12, 6))

    total_width = 0.8
    bar_width = total_width / max(len(years), 1)

    for idx, year in enumerate(years):
        year_values = [mean_or_zero(data_by_year[year].get(k, [])) for k in TARGET_K]
        offsets = [x - total_width / 2 + (idx + 0.5) * bar_width for x in x_positions]
        ax.bar(offsets, year_values, width=bar_width, label=str(year), alpha=0.9)

    ax.set_title(f"Balkendiagramm KW{week}: Jahre nebeneinander pro k")
    ax.set_xlabel("k")
    ax.set_ylabel("Amplitude")
    ax.set_xticks(x_positions)
    ax.set_xticklabels([str(k) for k in TARGET_K])
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.legend(title="Jahr")

    fig.tight_layout()
    output_file = output_dir / f"k_barplot_grouped_years_kw{week}.png"
    fig.savefig(output_file, dpi=220)
    plt.close(fig)
    return output_file


def create_year_week_comparison_plots(
    data_by_week: dict[int, dict[int, dict[int, list[float]]]],
    output_dir: Path,
) -> list[Path]:
    created: list[Path] = []
    for year in sorted({y for week in data_by_week.values() for y in week}):
        fig, ax = plt.subplots(figsize=(12, 6))
        x_positions = list(range(len(TARGET_K)))
        total_width = 0.8
        bar_width = total_width / max(len(TARGET_WEEKS), 1)

        for idx, week in enumerate(TARGET_WEEKS):
            year_data = data_by_week.get(week, {}).get(year, {})
            week_values = [mean_or_zero(year_data.get(k, [])) for k in TARGET_K]
            offsets = [x - total_width / 2 + (idx + 0.5) * bar_width for x in x_positions]
            ax.bar(offsets, week_values, width=bar_width, label=f"KW{week}", alpha=0.9)

        ax.set_title(f"Balkendiagramm {year}: KW4 vs KW26 pro k")
        ax.set_xlabel("k")
        ax.set_ylabel("Amplitude")
        ax.set_xticks(x_positions)
        ax.set_xticklabels([str(k) for k in TARGET_K])
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        ax.legend(title="Kalenderwoche")

        fig.tight_layout()
        output_file = output_dir / f"k_barplot_{year}_kw4_vs_kw26.png"
        fig.savefig(output_file, dpi=220)
        plt.close(fig)
        created.append(output_file)

    return created


def create_range_plots(output_dir: Path) -> list[Path]:
    csv_files = sorted(RANGE_DATA_DIR.glob("ptotsys_kwfrom*_harmonics_summary*.csv"))
    data_by_period: dict[str, dict[int, dict[int, list[float]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )

    for csv_file in csv_files:
        year = extract_year_from_range(csv_file.name)
        period = detect_range_period(csv_file.name)
        if year is None or period is None:
            continue

        rows = read_rows(csv_file)
        for row in rows:
            k_val = to_float(row.get("k"))
            amp_val = to_float(row.get("amplitude"))
            if k_val is None or amp_val is None:
                continue

            k_int = int(round(k_val))
            if k_int in TARGET_K:
                data_by_period[period][year][k_int].append(amp_val)

    created: list[Path] = []
    for period_name, config in RANGE_PERIODS.items():
        data_by_year = data_by_period.get(period_name, {})
        if not data_by_year:
            continue

        years = sorted(data_by_year)
        x_positions = list(range(len(TARGET_K)))
        fig, ax = plt.subplots(figsize=(12, 6))

        total_width = 0.8
        bar_width = total_width / max(len(years), 1)

        for idx, year in enumerate(years):
            year_values = [mean_or_zero(data_by_year[year].get(k, [])) for k in TARGET_K]
            offsets = [x - total_width / 2 + (idx + 0.5) * bar_width for x in x_positions]
            ax.bar(offsets, year_values, width=bar_width, label=str(year), alpha=0.9)

        ax.set_title(f"Balkendiagramm {config['title']}: Jahre nebeneinander pro k")
        ax.set_xlabel("k")
        ax.set_ylabel("Amplitude")
        ax.set_xticks(x_positions)
        ax.set_xticklabels([str(k) for k in TARGET_K])
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        ax.legend(title="Jahr")

        fig.tight_layout()
        grouped_name = "k_barplot_grouped_years_kwfrom.png"
        if period_name != "jan_feb":
            grouped_name = f"k_barplot_grouped_years_{config['output_suffix']}.png"
        grouped_output = output_dir / grouped_name
        fig.savefig(grouped_output, dpi=220)
        plt.close(fig)
        created.append(grouped_output)

        for year in years:
            values = [mean_or_zero(data_by_year[year].get(k, [])) for k in TARGET_K]

            fig, ax = plt.subplots(figsize=(10, 5))
            bars = ax.bar([str(k) for k in TARGET_K], values, color=config["color"])

            ax.set_title(f"Balkendiagramm der Amplituden ({year}, {config['title']})")
            ax.set_xlabel("k")
            ax.set_ylabel("Amplitude")
            ax.grid(axis="y", linestyle="--", alpha=0.4)

            for bar, val in zip(bars, values):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height(),
                    f"{val:.1f}",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                )

            fig.tight_layout()
            output_file = output_dir / f"k_barplot_{year}_{config['output_suffix']}.png"
            fig.savefig(output_file, dpi=200)
            plt.close(fig)
            created.append(output_file)

    return created


def create_plots() -> list[Path]:
    csv_files = sorted(WEEKLY_DATA_DIR.glob("ptotsys_kw*_harmonics_summary.csv"))
    data_by_week: dict[int, dict[int, dict[int, list[float]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )

    for csv_file in csv_files:
        year = extract_year(csv_file.name)
        week = extract_week(csv_file.name)
        if year is None or week not in TARGET_WEEKS:
            continue

        rows = read_rows(csv_file)
        for row in rows:
            k_val = to_float(row.get("k"))
            amp_val = to_float(row.get("amplitude"))
            if k_val is None or amp_val is None:
                continue

            k_int = int(round(k_val))
            if k_int in TARGET_K:
                data_by_week[week][year][k_int].append(amp_val)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []

    for week in TARGET_WEEKS:
        grouped_plot = create_grouped_plot(data_by_week.get(week, {}), OUTPUT_DIR, week)
        if grouped_plot is not None:
            created.append(grouped_plot)

    created.extend(create_year_week_comparison_plots(data_by_week, OUTPUT_DIR))

    for week in TARGET_WEEKS:
        for year in sorted(data_by_week.get(week, {})):
            values = []
            for k in TARGET_K:
                amp_samples = data_by_week[week][year].get(k, [])
                values.append(mean_or_zero(amp_samples))

            fig, ax = plt.subplots(figsize=(10, 5))
            bars = ax.bar([str(k) for k in TARGET_K], values, color="#2a9d8f")

            ax.set_title(f"Balkendiagramm der Amplituden ({year}, KW{week})")
            ax.set_xlabel("k")
            ax.set_ylabel("Amplitude")
            ax.grid(axis="y", linestyle="--", alpha=0.4)

            for bar, val in zip(bars, values):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height(),
                    f"{val:.1f}",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                )

            fig.tight_layout()
            output_file = OUTPUT_DIR / f"k_barplot_{year}_kw{week}.png"
            fig.savefig(output_file, dpi=200)
            plt.close(fig)
            created.append(output_file)

    created.extend(create_range_plots(OUTPUT_DIR))

    return created


def main() -> None:
    created_files = create_plots()
    if not created_files:
        print("Keine Diagramme erzeugt (keine passenden Daten gefunden).")
        return

    print("Erzeugte Diagramme:")
    for path in created_files:
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
