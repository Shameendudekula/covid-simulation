from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch

OUTPUT_NAME = "a2-covid-simulation.png"
STATES = ["H", "I", "S", "M", "D"]
STATE_LABELS = {
    "H": "Healthy",
    "I": "Infected (without symptoms)",
    "S": "Infected (with symptoms)",
    "M": "Immune",
    "D": "Deceased",
}
STATE_COLORS = {
    "H": "green",
    "I": "darkorange",
    "S": "indianred",
    "M": "lightseagreen",
    "D": "slategray",
}


def get_filepath(filename):
    """Return a path relative to this module."""
    return Path(__file__).resolve().parent / filename


def save_plot(fig, filename):
    """Save a figure as a high-resolution PNG."""
    output_path = get_filepath(filename)
    fig.savefig(output_path, dpi=180, bbox_inches="tight", facecolor="white")
    print(f"Plot saved to: {output_path}")


def read_dataset(filename):
    """Load the country-level simulation summary."""
    path = get_filepath(filename)
    if not path.exists():
        raise FileNotFoundError(f"Summary CSV not found: {path}")
    return pd.read_csv(path)


def create_plot(summary_csv, countries):
    """Create one stacked-area chart per selected country."""
    df = read_dataset(summary_csv)
    required = {"country", "date", *STATES}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Summary CSV is missing columns: {sorted(missing)}")
    if not countries:
        raise ValueError("At least one country must be selected.")

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "country"] )
    for state in STATES:
        df[state] = pd.to_numeric(df[state], errors="coerce").fillna(0)

    fig, axes = plt.subplots(
        nrows=len(countries), ncols=1,
        figsize=(13, 4.2 * len(countries)), squeeze=False,
        constrained_layout=True,
    )
    try:
        for ax, country in zip(axes[:, 0], countries):
            country_df = (
                df[df["country"] == country]
                .groupby("date")[STATES].sum().sort_index()
            )
            ax.set_title(
                f"COVID-19 Health-State Distribution — {country}",
                loc="left", fontsize=12, fontweight="bold", pad=10,
            )
            if country_df.empty:
                ax.text(0.5, 0.5, "No simulation data available",
                        transform=ax.transAxes, ha="center", va="center")
                continue

            dates = country_df.index
            values = country_df[STATES].to_numpy(dtype=float)
            ax.stackplot(
                dates, values.T,
                colors=[STATE_COLORS[s] for s in STATES], alpha=0.85,
                linewidth=0,
            )
            ax.set_xlabel("Date")
            ax.set_ylabel("Simulated people")
            ax.set_xlim(dates.min(), dates.max())
            ax.set_ylim(bottom=0)
            ax.grid(axis="y", alpha=0.25, linestyle="--")
            ax.set_axisbelow(True)

            locator = mdates.MonthLocator(interval=2)
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
            ax.tick_params(axis="x", labelsize=8)
            ax.tick_params(axis="y", labelsize=8)
            plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

            handles = [Patch(facecolor=STATE_COLORS[s], label=STATE_LABELS[s]) for s in STATES]
            ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.01, 1),
                      fontsize=8, frameon=False)

        fig.suptitle("COVID-19 Simulation Results", fontsize=16, fontweight="bold")
        save_plot(fig, OUTPUT_NAME)
    finally:
        plt.close(fig)


if __name__ == "__main__":
    create_plot("a2-covid-summary-timeseries.csv", ["Sweden", "Japan", "Afghanistan"])
