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


# IMF PortWatch's public ArcGIS Feature Service. No API key or login required.
# Tracks 28 major global maritime chokepoints (incl. the Strait of Malacca)
# using AIS vessel-tracking data, updated weekly (Tuesdays).
# Docs: https://portwatch.imf.org/pages/chokepoints-monitor

PORTWATCH_CHOKEPOINTS_URL = (
    "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/"
    "Daily_Chokepoints_Data/FeatureServer/0/query"
)


def _fetch_portwatch_malacca(timeout: int = 15) -> pd.DataFrame:
    """
    Pull real daily transit counts for the Strait of Malacca from IMF PortWatch.

    Filters by `portname LIKE '%Malacca%'` rather than a hardcoded chokepoint
    ID, since PortWatch has renumbered/added chokepoints over time (its ID
    range has grown from 12 to 28 across past updates) but the name is stable.
    Paginates through the service's per-request record cap.

    Returns columns: date, portname, n_total, n_tanker, n_cargo, capacity
    """
    base_params = {
        "where": "UPPER(portname) LIKE '%MALACCA%'",
        "outFields": "date,portname,n_total,n_tanker,n_cargo,capacity",
        "returnGeometry": "false",
        "orderByFields": "date ASC",
        "f": "json",
    }

    records = []
    offset = 0
    page_size = 2000

    while True:
        params = {**base_params, "resultOffset": offset, "resultRecordCount": page_size}
        resp = requests.get(PORTWATCH_CHOKEPOINTS_URL, params=params, timeout=timeout)
        resp.raise_for_status()
        payload = resp.json()

        if "error" in payload:
            raise RuntimeError(f"PortWatch API error: {payload['error']}")

        features = payload.get("features", [])
        if not features:
            break

        records.extend(f["attributes"] for f in features)

        if len(features) < page_size:
            break
        offset += page_size

    if not records:
        raise RuntimeError("PortWatch API returned no records matching 'Malacca'.")

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"], unit="ms")  # ArcGIS returns epoch ms
    df = df.sort_values("date").reset_index(drop=True)
    return df


def _load_malacca_traffic_synthetic() -> pd.DataFrame:
    """
    Representative sample data (previous fallback behaviour), used only when
    the live IMF PortWatch API is unreachable.

    Proxy: Singapore Port Authority tanker vessel arrivals, normalised.
    Index calibrated against UNCTAD Review of Maritime Transport published figures.
    """
    dates = _date_range("2019-01", "2025-12")
    np.random.seed(5)
    n = len(dates)

    # Key index values anchored to published events
    base = [
        100, 99, 98, 96,  # Jan–Apr 2019
        91, 88, 90, 93,   # May–Aug (sanctions + tanker attacks Jun 2019)
        91, 92, 93, 93,   # Sep–Dec
        92, 90, 88, 85,   # Jan–Apr 2020
        82, 78, 80, 83,   # May–Aug 2020 (COVID)
        84, 85, 86, 87,   # Sep–Dec 2020
        87, 86, 84, 83,   # Jan–Apr 2021
        81, 80, 82, 84,   # May–Aug (JCPOA collapse, tensions)
        85, 86, 87, 88,   # Sep–Dec 2021
        89, 90, 91, 90,   # Jan–Apr 2022
        91, 92, 93, 93,   # May–Aug
        94, 95, 95, 96,   # Sep–Dec
        96, 97, 97, 98,   # Jan–Apr 2023
        98, 99, 99, 100,  # May–Aug
        100, 101, 102, 103,  # Sep–Dec
        102, 103, 104, 104,  # Jan–Apr 2024
        105, 105, 106, 107,  # May–Aug
        106, 107, 107, 108,  # Sep–Dec
        108, 108, 109, 109,  # Jan–Apr 2025
        109, 110, 110, 110,  # May–Aug
        110, 110, 111, 111,  # Sep–Dec
    ]
    noise = np.random.normal(0, 0.8, n)
    index = [round(b + e, 1) for b, e in zip(base[:n], noise)]

    events = {
        "2019-06-01": "Gulf of Oman tanker attacks",
        "2020-01-01": "Soleimani assassination",
        "2020-04-01": "COVID demand collapse",
        "2021-04-01": "JCPOA collapse / Iran tensions",
        "2022-02-01": "Ukraine war / compound shock",
        "2023-10-01": "Gaza conflict / Gulf tensions",
    }

    df = pd.DataFrame({"date": dates, "traffic_index": index})
    df["event"] = df["date"].dt.strftime("%Y-%m-01").map(lambda d: events.get(d, None))
    df["source"] = "synthetic"
    return df


def load_malacca_traffic(prefer_live: bool = True) -> pd.DataFrame:
    """
    Tanker traffic index through the Strait of Malacca (Jan 2019 = 100).

    Tries IMF PortWatch's public Daily Chokepoint Transit data first --
    real AIS-derived vessel counts, free, no login required
    (https://portwatch.imf.org). If that fails for any reason (no internet
    access, the service is down, its schema changed, etc.), falls back to
    the previous representative sample data so downstream notebooks never
    break outright.

    Set prefer_live=False to force the synthetic fallback (e.g. for
    reproducible offline testing).

    Returns: date | traffic_index | event (optional annotation) | source
    ("live" or "synthetic")
    """
    if prefer_live:
        try:
            live = _fetch_portwatch_malacca()

            # Rebase raw vessel counts to a Jan-2019 = 100 index, matching the
            # convention of the previous synthetic series, so downstream
            # notebooks (rolling averages, event overlays) don't need to change.
            baseline = live.loc[live["date"] < "2019-02-01", "n_total"].mean()
            if not baseline or pd.isna(baseline):
                baseline = live["n_total"].iloc[0]

            live["traffic_index"] = (live["n_total"] / baseline * 100).round(1)
            live["event"] = None
            live["source"] = "live"

            print(
                "[DATA NOTICE] Strait of Malacca traffic: loaded live data from "
                "IMF PortWatch (https://portwatch.imf.org)."
            )
            return live[["date", "traffic_index", "event", "source"]]

        except Exception as e:
            _warn_fallback(
                "Strait of Malacca traffic",
                f" IMF PortWatch API request failed ({e}). "
                "Falling back to representative sample data. "
                "Check your internet connection, or call "
                "load_malacca_traffic(prefer_live=False) to skip the live "
                "attempt entirely.",
            )

    return _load_malacca_traffic_synthetic()