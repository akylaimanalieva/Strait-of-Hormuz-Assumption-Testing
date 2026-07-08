"""
Tests for the notebooks in Visualisation_of_Data/.

This test checks the two things that most often break a notebook before a single plot renders:

  1. Notebook source itself. Static checks over the .ipynb JSON that catch
     copy-paste bugs like the ones already found in this repo:
       - Cost-Burden_Analysis2 imports `from Data_loaders import dataloader_oil`,
         but the real package is `Data_Loader` (capital L, singular).
       - Hormuz_flow_visualization and Impacts_on_Global_Oil_Trade hardcoded a
         specific contributor's local file path (e.g. /Users/riritorti/...),
         which only works on that one machine.

  2. Data_raw files. Every notebook loads a CSV/parquet from Data_raw/. These
     tests confirm each file exists, has the columns the notebook expects, and
     holds sane values (no negative prices, no unparseable dates, no missing
     date ranges the notebook specifically filters on).

Run with:
    python -m unittest Visualisation_of_Data/test.py -v

"""

import json
import re
import unittest
from pathlib import Path

import pandas as pd

VIZ_DIR = Path(__file__).resolve().parent
REPO_ROOT = VIZ_DIR.parent
DATA_RAW = REPO_ROOT / "Data_raw"

NOTEBOOKS = sorted(VIZ_DIR.glob("*.ipynb"))


def load_notebook_source(nb_path: Path) -> str:
    """Return the concatenated source of every code cell in a notebook."""
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    return "\n".join(
        "".join(cell.get("source", []))
        for cell in nb.get("cells", [])
        if cell.get("cell_type") == "code"
    )


class TestNotebooksAreWellFormed(unittest.TestCase):
    """Structural checks that don't require executing any notebook."""

    def test_notebooks_exist(self):
        self.assertTrue(NOTEBOOKS, f"No .ipynb files found in {VIZ_DIR}")

    def test_notebooks_are_valid_json(self):
        for nb_path in NOTEBOOKS:
            with self.subTest(notebook=nb_path.name):
                try:
                    json.loads(nb_path.read_text(encoding="utf-8"))
                except json.JSONDecodeError as e:
                    self.fail(f"{nb_path.name} is not valid notebook JSON: {e}")

    def test_no_hardcoded_personal_paths(self):
        """
        Regression test: Hormuz_flow_visualization and Impacts_on_Global_Oil_Trade
        previously (or currently) hardcode a specific contributor's local path,
        e.g. /Users/riritorti/... or /Users/veronica/.... That only runs on the
        author's own machine. Flag any /Users/<name>/ style path left in
        committed notebook source.
        """
        personal_path_pattern = re.compile(r"/Users/[^/\"'\s]+/")
        offenders = {}
        for nb_path in NOTEBOOKS:
            matches = personal_path_pattern.findall(load_notebook_source(nb_path))
            if matches:
                offenders[nb_path.name] = sorted(set(matches))
        self.assertFalse(
            offenders,
            f"Hardcoded personal file paths found: {offenders}. "
            "Use a relative path, or the Path.cwd()-based project-root "
            "detection already used in Impacts_on_Global_Oil_Trade.ipynb.",
        )

    def test_data_loader_import_path_is_correct(self):
        """
        Regression test: Cost-Burden_Analysis2 imports
        `from Data_loaders import dataloader_oil`, but the real module on
        disk is `Data_Loader` (capital L, singular, no 's'). Fail loudly if
        this typo is present, since it silently breaks the only notebook
        that uses the shared Data_Loader module.
        """
        bad_import = re.compile(r"from\s+Data_loaders\s+import")
        offenders = [
            nb_path.name
            for nb_path in NOTEBOOKS
            if bad_import.search(load_notebook_source(nb_path))
        ]
        self.assertFalse(
            offenders,
            f"Found `from Data_loaders import ...` (wrong package name) in: "
            f"{offenders}. The real module is `Data_Loader` (capital L, "
            "singular), and it needs an __init__.py to be importable.",
        )


class TestDataRawFilesExist(unittest.TestCase):
    """Every parquet/CSV a notebook loads must actually be present in Data_raw/."""

    def test_data_raw_folder_exists(self):
        self.assertTrue(DATA_RAW.exists(), f"{DATA_RAW} does not exist")

    def _assert_exists(self, filename: str) -> Path:
        path = DATA_RAW / filename
        self.assertTrue(path.exists(), f"Expected data file missing: {path}")
        return path

    def test_voy_intake_index_csv_exists(self):
        # Loaded directly by Hormuz_flow_visualization.ipynb
        self._assert_exists("crude_oil_export_voy_intake_index.csv")

    def test_singapore_imports_parquet_exists(self):
        # Loaded directly by Impacts_on_Global_Oil_Trade.ipynb
        self._assert_exists("singapore_imports_20260603_112515.parquet")

    def test_oil_prices_parquet_exists(self):
        # Loaded by dataloader_oil.load_oil_prices(), used by Cost-Burden_Analysis2
        self._assert_exists("oil_prices_20260603_112515.parquet")

    def test_yanbu_volume_candidates_csv_exists(self):
        # Referenced by yanbu_oil_flow_analysis.ipynb's data pipeline
        self._assert_exists("yanbu_volume_candidates.csv")


class TestVoyIntakeIndexData(unittest.TestCase):
    """Schema/sanity checks for the file Hormuz_flow_visualization.ipynb loads."""

    @classmethod
    def setUpClass(cls):
        path = DATA_RAW / "crude_oil_export_voy_intake_index.csv"
        if not path.exists():
            raise unittest.SkipTest(f"{path} not found")
        cls.df = pd.read_csv(path)

    def test_expected_columns_present(self):
        expected = {"date", "voy_intake_index"}
        missing = expected - set(self.df.columns)
        self.assertFalse(missing, f"Missing columns: {missing}")

    def test_dates_parse_with_no_nulls(self):
        dates = pd.to_datetime(self.df["date"], errors="coerce")
        self.assertFalse(dates.isna().any(), "Some 'date' values failed to parse")

    def test_index_values_are_numeric_and_non_negative(self):
        values = pd.to_numeric(self.df["voy_intake_index"], errors="coerce")
        self.assertFalse(values.isna().any(), "Non-numeric voy_intake_index values found")
        self.assertTrue((values >= 0).all(), "voy_intake_index has negative values")

    def test_has_data_for_2026(self):
        # The notebook does: df_2026 = df[df['date'].dt.year == 2026]
        dates = pd.to_datetime(self.df["date"])
        self.assertTrue(
            (dates.dt.year == 2026).any(),
            "No rows for year 2026 - the notebook's df_2026 filter would be empty",
        )

    def test_enough_rows_for_7day_rolling_average(self):
        # The notebook computes a 7-day rolling mean on the 2026 subset
        dates = pd.to_datetime(self.df["date"])
        n_2026 = (dates.dt.year == 2026).sum()
        self.assertGreaterEqual(
            n_2026, 7, "Fewer than 7 rows in 2026 - rolling(window=7) would be all NaN"
        )


class TestSingaporeImportsData(unittest.TestCase):
    """Schema/sanity checks for the file Impacts_on_Global_Oil_Trade.ipynb loads."""

    @classmethod
    def setUpClass(cls):
        path = DATA_RAW / "singapore_imports_20260603_112515.parquet"
        if not path.exists():
            raise unittest.SkipTest(f"{path} not found")
        cls.df = pd.read_parquet(path)

    def test_expected_columns_present(self):
        expected = {"date", "country", "import_value"}
        missing = expected - set(self.df.columns)
        self.assertFalse(missing, f"Missing columns: {missing}")

    def test_required_country_groups_present(self):
        # The notebook groups countries into "Middle East" vs "Americas + Africa"
        required = {"Middle East", "Americas", "Africa"}
        actual = set(self.df["country"].unique())
        missing = required - actual
        self.assertFalse(
            missing,
            f"Missing country group(s) needed for the Middle East vs "
            f"Alternative Supply comparison: {missing}",
        )

    def test_import_values_are_non_negative(self):
        values = pd.to_numeric(self.df["import_value"], errors="coerce")
        self.assertFalse(values.isna().any(), "Non-numeric import_value found")
        self.assertTrue((values >= 0).all(), "import_value has negative entries")

    def test_covers_ukraine_and_iran_event_windows(self):
        # Microanalysis 1 needs 2021-2022 data; Microanalysis 2 needs 2024+ data
        dates = pd.to_datetime(self.df["date"])
        self.assertTrue(
            (dates.dt.year <= 2022).any(), "No data on/before the 2022 Ukraine window"
        )
        self.assertTrue(
            (dates.dt.year >= 2024).any(), "No data on/after the 2024 Iran window"
        )


class TestOilPricesData(unittest.TestCase):
    """Schema/sanity checks for the parquet behind dataloader_oil.load_oil_prices()."""

    @classmethod
    def setUpClass(cls):
        path = DATA_RAW / "oil_prices_20260603_112515.parquet"
        if not path.exists():
            raise unittest.SkipTest(f"{path} not found")
        cls.df = pd.read_parquet(path)

    def test_expected_columns_present(self):
        expected = {"date", "region", "price_usd_bbl"}
        missing = expected - set(self.df.columns)
        self.assertFalse(missing, f"Missing columns: {missing}")

    def test_prices_are_positive(self):
        prices = pd.to_numeric(self.df["price_usd_bbl"], errors="coerce")
        self.assertFalse(prices.isna().any(), "Non-numeric price_usd_bbl found")
        self.assertTrue((prices > 0).all(), "Found zero or negative oil prices")

    def test_has_data_after_2021(self):
        # Cost-Burden_Analysis2 filters with df.query("date > 2021")
        dates = pd.to_datetime(self.df["date"])
        self.assertTrue((dates.dt.year > 2021).any(), "No rows after 2021")


if __name__ == "__main__":
    unittest.main()