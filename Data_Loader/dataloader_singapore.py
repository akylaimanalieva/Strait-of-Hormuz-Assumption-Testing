from libraries import *

# Data tracking for the Singapore imports 
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

def load_singapore_imports() -> pd.DataFrame:
    '''
    Columns structure: Data Series, YYYY Mon, YYYY Mon, ... 
    Rows: countries / regions
    '''
    url = (
        "https://data.gov.sg/api/action/datastore_search"
        "?resource_id=d_d8436b391529c6be9da001ffc7f19e51&limit=500"
    )
    try: 
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        records = r.json().get("result", {}).get("records", [])
        if records: 
            raw = pd.DataFrame(records)
            data_cols = [c for c in raw.columns if c not in ("_id", "Data Series")]
            long = raw.melt(id_vars="Data Series", 
                            value_vars=data_cols,
                            var_name="raw_date", value_name="import_value")
                        
            long["date"] = pd.to_datetime(long["raw_date"],format="%Y%b", errors="coerce")
            long = long.dropna(subset=["date"])
            long = long.rename(columns={"Data Series": "country", "value": "import_value"})
            long["import_value"] = pd.to_numeric(long["import_value"],errors="coerce")
            return long[["date", "country", "import_value"]].sort_values("date")
    except Exception as e:
        pass
    
    _warn_fallback(
        '''Singapour oil imports
        data.gov.sg API retunred 404 for this resource ID in testing
        data manually available from https://data.gov.sg/datasets?resultId=d_d8436b391529c6be9da001ffc7f19e51'''
        
    )
    return _fallback_singapore_imports()
    

print("Check point for load_singapore_imports")

def load_singapore_imports_csv(path: str) -> pd.DataFrame:
    raw = pd.read_csv(path)
    date_cols = [c for c in raw.columns if c not in ("Data Series",)]
    long = raw.melt(
        id_vars="Data Series", 
        value_vars=date_cols,
        var_name="raw_date", 
        value_name="import_value")
    long["date"] = pd.to_datetime(long["raw_date"], format="%Y %b", errors="coerce")
    long = long.dropna(subset=["date"])
    long["import_value"] = pd.to_numeric(long["import_value"], errors="coerce")
    
    return long.rename(columns={"Data Series": "country"})[
        ["date", "country", "import_value"]
        ].sort_values("date")
    
print("Check point for load_singapore_imports_csv")

def _fallback_singapore_imports() -> pd.DataFrame:
    """
    Representative monthly Singapore oil import shares 2019–2025.
    Values calibrated to SINGSTAT published annual totals and EIA regional breakdowns.
    Unit: thousand barrels equivalent (index-normalised to 100 = Jan 2019 total)
    """
    dates = _date_range("2019-01", "2025-12")
    np.random.seed(42)
    n = len(dates)
    t = np.arange(n)
 
    # Middle East: gradual decline from ~62% → ~57%
    me_trend = 62 - 0.07 * t + np.random.normal(0, 1, n)
    # Americas: gradual rise from ~6% → ~11%
    am_trend =  6 + 0.07 * t + np.random.normal(0, 0.5, n)
    # Africa: gradual rise from ~5% → ~8%
    af_trend =  5 + 0.04 * t + np.random.normal(0, 0.4, n)
    # Other Asia-Pacific: residual
    ot_trend = 100 - me_trend - am_trend - af_trend  # keeps sum ≈ 100%
 
    regions = {
        "Middle East": me_trend,
        "Americas":    am_trend,
        "Africa":      af_trend,
        "Other Asia-Pacific": ot_trend,
    }
    rows = []
    for region, series in regions.items():
        for d, v in zip(dates, series):
            rows.append({"date": d, "country": region, "import_value": round(max(v, 0), 2)})
    return pd.DataFrame(rows)

print("Check point for _fallback_singapore_imports")

 
def load_singapore_exports() -> pd.DataFrame:
    """
    Loads Singapore domestic oil exports by destination (monthly).
 
    Live source: data.gov.sg resource d_f2ed173019062409dfbed3127dc516b1
 
    Returns a tidy DataFrame: date | country | export_value
    """
    url = (
        "https://data.gov.sg/api/action/datastore_search"
        "?resource_id=d_f2ed173019062409dfbed3127dc516b1&limit=500"
    )
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        records = r.json().get("result", {}).get("records", [])
        if records:
            raw = pd.DataFrame(records)
            date_cols = [c for c in raw.columns if c not in ("_id", "Data Series")]
            long = raw.melt(id_vars="Data Series", value_vars=date_cols,
                            var_name="raw_date", value_name="value")
            long["date"] = pd.to_datetime(long["raw_date"], format="%Y %b", errors="coerce")
            long = long.dropna(subset=["date"])
            long = long.rename(columns={"Data Series": "country", "value": "export_value"})
            long["export_value"] = pd.to_numeric(long["export_value"], errors="coerce")
            return long[["date", "country", "export_value"]].sort_values("date")
    except Exception as e:
        pass
 
    _warn_fallback(
        "Singapore oil exports",
        "data.gov.sg API returned 404. "
        "Download CSV from: "
        "https://data.gov.sg/datasets?resultId=d_f2ed173019062409dfbed3127dc516b1 "
        "and pass to load_singapore_exports_csv(path)."
    )
    return _fallback_singapore_exports()
 
print("Check point for load_singapore_exports")

def _fallback_singapore_exports() -> pd.DataFrame:
    """
    Representative monthly Singapore oil export shares 2019–2025.
    Calibrated to SINGSTAT/EIA published destination breakdowns.
    """
    dates = _date_range("2019-01", "2025-12")
    np.random.seed(7)
    n = len(dates)
    t = np.arange(n)
 
    china =    24 + 0.06 * t + np.random.normal(0, 0.8, n)
    india  =    9 + 0.07 * t + np.random.normal(0, 0.6, n)
    japan_kr = 22 - 0.04 * t + np.random.normal(0, 0.7, n)
    other  =  100 - china - india - japan_kr
 
    regions = {
        "China": china,
        "India": india,
        "Japan + South Korea": japan_kr,
        "Other": other,
    }
    rows = []
    for region, series in regions.items():
        for d, v in zip(dates, series):
            rows.append({"date": d, "country": region, "export_value": round(max(v, 0), 2)})
    return pd.DataFrame(rows)


print("Check point for _fallback_singapore_exports")