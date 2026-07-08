"""
Strait of Malacca: Tanker Traffic Analysis
===========================================
 
Standalone script version of Change_in_Malacca_Traffic_Analysis.ipynb.
 
Data source: `dataloader_malacca.py` tries IMF PortWatch (https://portwatch.imf.org) --
a free, no-login ArcGIS API tracking real AIS-derived vessel transit counts for the
Strait of Malacca since 2019. If that request fails (no internet, service down, schema
change), the loader automatically falls back to representative/synthetic data so this
script never breaks outright. Check the printed `data_source` value below before
trusting the numbers.
 
marinetraffic.org was evaluated first but only offers a live ship-position map -- no
historical export, no free API -- so it isn't used here.

"""
 
import sys
from pathlib import Path
 
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # write straight to a file; no display server needed
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
 
 
def setup_import_path() -> Path:
    """
    Detect the project root whether this script is run from the repo root or
    from Visualisation_of_Data/ itself, so it works on any contributor's
    machine. Returns PROJECT_ROOT.
    """
    cwd = Path.cwd()
    if (cwd / "Data_Loader").exists():
        project_root = cwd
    elif (cwd.parent / "Data_Loader").exists():
        project_root = cwd.parent
    else:
        raise FileNotFoundError(
            "Could not find the Data_Loader/ folder. Run this script from the "
            "repository root or from Visualisation_of_Data/."
        )
 
    data_loader_dir = project_root / "Data_Loader"
 
    # Two entries are needed, not one: project_root so `from Data_Loader import
    # dataloader_malacca` resolves, and Data_Loader/ itself so that module's own
    # `from libraries import *` line (an implicit, non-relative import) resolves too.
    for p in (str(project_root), str(data_loader_dir)):
        if p not in sys.path:
            sys.path.insert(0, p)
 
    return project_root
 
 
PROJECT_ROOT = setup_import_path()
 
from Data_Loader import dataloader_malacca  # noqa: E402  (import must follow path setup)
 
 
KEY_EVENTS = {
    "2019-06-01": "Gulf of Oman tanker attacks",
    "2020-01-01": "Soleimani assassination",
    "2020-04-01": "COVID demand collapse",
    "2021-04-01": "JCPOA collapse / Iran tensions",
    "2022-02-01": "Ukraine war / compound shock",
    "2023-10-01": "Gaza conflict / Gulf tensions",
}
WINDOW_MONTHS = 6
 
 
def load_data() -> pd.DataFrame:
    df = dataloader_malacca.load_malacca_traffic()
    df["date"] = pd.to_datetime(df["date"])
    return df
 
 
def print_sanity_check(df: pd.DataFrame, data_source: str) -> None:
    print(f"Loaded {len(df)} rows. Data source: '{data_source}'.")
    print("Date range:", df["date"].min().date(), "to", df["date"].max().date())
    print(
        "Traffic index range:",
        df["traffic_index"].min(),
        "to",
        df["traffic_index"].max(),
    )
    print()
 
    if df["event"].notna().any():
        print("Labeled events (synthetic fallback only):")
        print(
            df.loc[df["event"].notna(), ["date", "traffic_index", "event"]]
            .to_string(index=False)
        )
    else:
        print(
            "No labeled events in this series (expected when data_source == 'live'; "
            "the real IMF PortWatch feed isn't pre-annotated with event labels)."
        )
    print()
 
 
def plot_traffic(df: pd.DataFrame, data_source: str, output_path: Path) -> None:
    df = df.copy()
    df["ma_12m"] = df["traffic_index"].rolling(window=12, min_periods=1).mean()
 
    fig, ax = plt.subplots(figsize=(14, 6))
 
    ax.plot(df["date"], df["traffic_index"], alpha=0.5, label="Traffic index")
    ax.plot(df["date"], df["ma_12m"], linewidth=2, label="12-month rolling average")
 
    # Mark each labeled event with a vertical line and a rotated annotation.
    # Only present when running on the synthetic fallback series.
    events = df.loc[df["event"].notna()]
    for _, row in events.iterrows():
        ax.axvline(row["date"], color="grey", linestyle="--", alpha=0.6)
        ax.annotate(
            row["event"],
            xy=(row["date"], ax.get_ylim()[1]),
            xytext=(5, -10),
            textcoords="offset points",
            rotation=90,
            va="top",
            fontsize=8,
            color="dimgrey",
        )
 
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
 
    title_suffix = "IMF PortWatch, live" if data_source == "live" else "synthetic fallback"
    ax.set_title(f"Strait of Malacca Tanker Traffic Index ({title_suffix})")
    ax.set_xlabel("Date")
    ax.set_ylabel("Traffic index (baseline = 100)")
    ax.legend(loc="upper left")
    ax.grid(True, linestyle="--", alpha=0.4)
 
    plt.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Chart saved to: {output_path}")
    print()
 
 
def pre_post_change(df: pd.DataFrame, event_date: str, window_months: int = WINDOW_MONTHS) -> pd.Series:
    event_date = pd.Timestamp(event_date)
    pre_start = event_date - pd.DateOffset(months=window_months)
    post_end = event_date + pd.DateOffset(months=window_months)
 
    pre = df[(df["date"] >= pre_start) & (df["date"] < event_date)]
    post = df[(df["date"] >= event_date) & (df["date"] < post_end)]
 
    pre_mean = pre["traffic_index"].mean()
    post_mean = post["traffic_index"].mean()
    pct_change = (
        (post_mean - pre_mean) / pre_mean * 100
        if pd.notna(pre_mean) and pre_mean != 0
        else float("nan")
    )
 
    return pd.Series(
        {
            "pre_mean": round(pre_mean, 2) if pd.notna(pre_mean) else None,
            "post_mean": round(post_mean, 2) if pd.notna(post_mean) else None,
            "pct_change": round(pct_change, 2) if pd.notna(pct_change) else None,
        }
    )
 
 
def build_event_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compare traffic index in the WINDOW_MONTHS before vs. after each known
    geopolitical shock. Uses a fixed list of event dates (not the `event`
    column, which is only populated on the synthetic fallback) so it works
    regardless of which data source was loaded.
    """
    rows = []
    for date_str, label in KEY_EVENTS.items():
        if pd.Timestamp(date_str) < df["date"].min() or pd.Timestamp(date_str) > df["date"].max():
            continue  # event falls outside the loaded data's date range
        stats = pre_post_change(df, date_str)
        rows.append({"date": date_str, "event": label, **stats})
 
    return pd.DataFrame(rows)
 
 
def print_interpretation(data_source: str) -> None:
    print("Interpretation")
    print("--------------")
    print(
        "The 12-month rolling average smooths out month-to-month noise and shows the "
        "broad trend. The before/after table above quantifies each shock individually, "
        "so it's possible to compare, e.g., whether the Ukraine war (Feb 2022) or the "
        "Gaza conflict (Oct 2023) coincided with a larger shift in Malacca traffic than "
        "the earlier Gulf of Oman tanker attacks did.\n"
    )
    if data_source == "live":
        print(
            "data_source == 'live': this run pulled real AIS-derived transit counts "
            "from IMF PortWatch. The patterns above are empirical."
        )
    else:
        print(
            "data_source == 'synthetic': the live IMF PortWatch request failed and "
            "this run fell back to representative sample data. Treat the patterns "
            "above as a template for the analysis to re-run once connectivity to "
            "IMF PortWatch is available, not as a confirmed empirical finding."
        )
 
 
def main() -> None:
    df = load_data()
    data_source = df["source"].iloc[0]
 
    print_sanity_check(df, data_source)
 
    chart_path = Path(__file__).resolve().parent / "malacca_traffic_chart.png"
    plot_traffic(df, data_source, chart_path)
 
    summary = build_event_summary(df)
    print("Before/after comparison around key events")
    print("------------------------------------------")
    print(summary.to_string(index=False))
    print()
 
    print_interpretation(data_source)
 
 
if __name__ == "__main__":
    main()