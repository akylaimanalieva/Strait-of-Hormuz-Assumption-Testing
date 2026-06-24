from libraries import *

# Sourcing data from seperate files
from dataloader_singapore import *
from dataloader_oil import *
from dataloader_pipeline import *
from dataloader_malacca import *

#Main data processing fucntions
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

#Load of the entire code
def load_all() -> dict:
    """
    Convenience function: loads all datasets and returns them in a dict.
    """
    print("Loading all datasets...\n")
    return {
        "singapore_imports": load_singapore_imports(),
        "singapore_exports": load_singapore_exports(),
        "oil_prices":        load_oil_prices(),
        "pipelines":         load_pipeline_data(),
        "malacca_traffic":   load_malacca_traffic(),
    }
 
 
if __name__ == "__main__":
    data = load_all()
    for name, df in data.items():
        print(f"\n── {name} ──")
        print(f"  Shape : {df.shape}")
        print(f"  Cols  : {list(df.columns)}")
        print(df.head(3).to_string(index=False))
 