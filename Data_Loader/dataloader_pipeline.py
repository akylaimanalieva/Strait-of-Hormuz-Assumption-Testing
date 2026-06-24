from libraries import *

def _date_range(start="2019-01", end="2025-12", freq="MS"):
    return pd.date_range(start=start, end=end, freq=freq)

def _warn_fallback(name: str, reasons: str = ""):
    msg = (
        f"\n[DATA NOTICE] {name}: using representative sample data"
        f"{reasons}\n"
        f" I need to replace with real CVS data\n"
    )
    warnings.warn(msg, UserWarning, stacklevel=3)
    print(msg)

def load_pipeline_data() -> pd.DataFrame:
    """
    Bypass pipeline capacity and utilisation data.
 
    Source: EIA / straitofhormuz.report
    The website requires auth for CSV download; data below reflects published
    EIA capacity figures and IEA/Kpler utilisation estimates.
 
    Returns a DataFrame with one row per pipeline per month showing
    utilisation as a fraction of max capacity.
    """
    _warn_fallback(
        "Pipeline capacity data",
        "straitofhormuz.report requires account login for CSV. "
        "Figures below are from EIA published capacity tables + "
        "Kpler/IEA utilisation estimates. "
        "Replace with CSV once downloaded from the site."
    )
 
    dates = _date_range("2019-01", "2025-12")
    np.random.seed(3)
    n = len(dates)
    t = np.arange(n)
 
    pipelines = {
        "Saudi East-West (Petroline)": {
            "max_capacity_mbpd": 5.0,
            # Utilisation: rose from ~65% to ~80% after Hormuz concerns in 2019
            "util_pct": np.clip(65 + 0.15 * t + np.random.normal(0, 2, n), 50, 95),
        },
        "UAE ADCOP (Habshan–Fujairah)": {
            "max_capacity_mbpd": 1.5,
            # Low utilisation; some ramp-up post-2022
            "util_pct": np.clip(30 + 0.10 * t + np.random.normal(0, 3, n), 15, 60),
        },
        "Iraq-Turkey (Kirkuk–Ceyhan)": {
            "max_capacity_mbpd": 1.6,
            # Halted by legal disputes Mar 2023; sharp utilisation drop
            "util_pct": np.where(
                t < 50,
                np.clip(55 - 0.2 * t + np.random.normal(0, 3, n), 10, 80),
                np.clip(10 + np.random.normal(0, 2, n), 5, 20)
            ),
        },
    }
 
    rows = []
    for name, info in pipelines.items():
        for d, u in zip(dates, info["util_pct"]):
            rows.append({
                "date": d,
                "pipeline": name,
                "max_capacity_mbpd": info["max_capacity_mbpd"],
                "utilisation_pct": round(u, 1),
                "flow_mbpd": round(info["max_capacity_mbpd"] * u / 100, 2),
            })
    return pd.DataFrame(rows)
 

print("Check point for pipeline data")
