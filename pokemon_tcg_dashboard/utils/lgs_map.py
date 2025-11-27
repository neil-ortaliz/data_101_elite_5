# Task 3 - Store Location Map

import pandas as pd
from typing import Union, Tuple
import logging

logger = logging.getLogger(__name__)


def _detect_lat_lon_columns(df: pd.DataFrame) -> Tuple[str, str]:
    """Detect lat/lon column names from common alternatives, or raise ValueError."""
    lat_candidates = ["lat", "latitude", "y", "LAT", "Latitude"]
    lon_candidates = ["lon", "lng", "longitude", "x", "LON", "Longitude"]

    lat_col = next((c for c in lat_candidates if c in df.columns), None)
    lon_col = next((c for c in lon_candidates if c in df.columns), None)

    if lat_col is None or lon_col is None:
        raise ValueError(f"Could not detect latitude/longitude columns. Found columns: {list(df.columns)}")

    return lat_col, lon_col


def _metro_manila_demo_df() -> pd.DataFrame:
    """Built-in Metro Manila demo dataset for quick demos."""
    data = {
        "store_name": [
            "Neutral Grounds - Glorietta",
            "Titan Hobby Shop",
            "Quantum TCG",
            "Neutral Grounds - Trinoma",
            "Gamehaven",
            "The Legends Hobby Shop",
            "Regran Collectibles",
            "NG Galleria"
        ],
        "lat": [14.5547, 14.5995, 14.5512, 14.6570, 14.5500, 14.6000, 14.6100, 14.6200],
        "lon": [121.0244, 120.9842, 121.0512, 121.0302, 121.0280, 121.0700, 121.0400, 121.0560],
        "type": ['LGS', 'LGS', 'Pokemon Center', 'LGS', 'LGS', 'LGS', 'Retailer', 'LGS'],
        "address": [
            "Glorietta 2, Makati City",
            "123 Shaw Blvd, Mandaluyong",
            "Uptown BGC, Taguig",
            "Trinoma Mall, Quezon City",
            "456 Makati Ave, Makati",
            "Ortigas Center, Pasig",
            "Commonwealth Ave, QC",
            "Robinsons Galleria, Ortigas"
        ],
        "phone": [
            "+63 2 1234 5678",
            "+63 2 2345 6789",
            "+63 2 3456 7890",
            "+63 2 4567 8901",
            "+63 2 5678 9012",
            "+63 2 6789 0123",
            "+63 2 7890 1234",
            "+63 2 8901 2345"
        ],
        "website": [
            "https://neutralgrounds.example/glorietta",
            "https://titan.example",
            "https://quantum.example",
            "https://neutralgrounds.example/trinoma",
            "https://gamehaven.example",
            "https://legends.example",
            "https://regran.example",
            "https://nggalleria.example",
        ],
        "hours": [
            "10AM - 9PM Daily",
            "11AM - 10PM Daily",
            "10AM - 8PM Daily",
            "10AM - 9PM Daily",
            "12PM - 10PM Daily",
            "11AM - 9PM Daily",
            "10AM - 8PM Daily",
            "10AM - 9PM Daily"
        ],
        "tournaments": [
            "Fridays 6PM, Sundays 2PM",
            "Saturdays 3PM",
            "Wednesdays 7PM",
            "Saturdays 4PM, Sundays 2PM",
            "Thursdays 6PM",
            "Fridays 7PM",
            "No regular schedule",
            "Sundays 3PM"
        ]
    }
    df = pd.DataFrame(data)
    df = df.reset_index(drop=True)
    df["store_id"] = "demo_" + df.index.astype(str)
    cols = ["store_id", "store_name", "address", "lat", "lon", "phone", "website", "type", "hours", "tournaments"]
    df = df[cols]
    return df


def load_and_validate_lgs_data(
    filepath_or_df: Union[str, pd.DataFrame, None] = None,
    *,
    load_example: bool = False
) -> pd.DataFrame:
    """
    Load and validate LGS data.

    Parameters
    ----------
    filepath_or_df : str | pd.DataFrame | None
        Path to CSV, or already-loaded DataFrame, or None.
    load_example : bool
        If True, return built-in Metro Manila demo dataset.

    Returns
    -------
    pd.DataFrame with standardized columns:
        ['store_id','store_name','address','lat','lon','phone','website', ...]
    """
    # explicit demo request
    if load_example:
        logger.info("Loading built-in Metro Manila demo dataset.")
        return _metro_manila_demo_df()

    # If caller passed a DataFrame
    if isinstance(filepath_or_df, pd.DataFrame):
        df = filepath_or_df.copy()
    elif isinstance(filepath_or_df, str):
        # If marker string "example" or "demo"
        if filepath_or_df.lower() in ("example", "demo"):
            return _metro_manila_demo_df()
        # else load CSV from path
        df = pd.read_csv(filepath_or_df)
    else:
        # fallback: no path provided — return demo with warning (safe default)
        logger.warning("No filepath provided; returning demo dataset. Pass a filepath to load real data.")
        return _metro_manila_demo_df()

    # Normalize common column names
    col_map = {}
    for cand in ["store_name", "name", "store", "storeName"]:
        if cand in df.columns:
            col_map[cand] = "store_name"
            break
    for cand in ["address", "addr", "location"]:
        if cand in df.columns:
            col_map[cand] = "address"
            break
    for cand in ["phone", "contact", "phone_number"]:
        if cand in df.columns:
            col_map[cand] = "phone"
            break
    for cand in ["website", "site", "url"]:
        if cand in df.columns:
            col_map[cand] = "website"
            break
    if col_map:
        df = df.rename(columns=col_map)

    # Detect lat/lon columns (raises ValueError if not found)
    lat_col, lon_col = _detect_lat_lon_columns(df)

    # Rename to standard names
    df = df.rename(columns={lat_col: "lat", lon_col: "lon"})

    # Required columns check
    required = ["store_name", "lat", "lon"]
    if "address" in df.columns:
        required.append("address")
    missing_required = [c for c in required if c not in df.columns]
    if missing_required:
        raise ValueError(f"Missing required columns: {missing_required}")

    # Drop rows with missing coordinates
    df = df.dropna(subset=["lat", "lon"])

    # Coerce numeric & validate ranges
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    df = df.dropna(subset=["lat", "lon"])
    df = df[(df["lat"] >= -90) & (df["lat"] <= 90) & (df["lon"] >= -180) & (df["lon"] <= 180)].copy()

    # Optional columns fill
    df["phone"] = df.get("phone", pd.Series(["N/A"] * len(df))).fillna("N/A")
    df["website"] = df.get("website", pd.Series(["N/A"] * len(df))).fillna("N/A")

    # Ensure store_id exists
    if "store_id" not in df.columns:
        df = df.reset_index(drop=True)
        df["store_id"] = df.index.astype(str)

    # Friendly column order
    base_cols = ["store_id", "store_name", "address", "lat", "lon", "phone", "website"]
    rest = [c for c in df.columns if c not in base_cols]
    df = df[base_cols + rest]

    logger.info("Loaded %d store records", len(df))
    return df


# Task 4 - Store Data Processing

import pandas as pd
from typing import Union, Tuple
import logging

logger = logging.getLogger(__name__)

def _detect_lat_lon_columns(df: pd.DataFrame) -> Tuple[str, str]:
    """Detect lat/lon column names from common alternatives, or raise ValueError."""
    lat_candidates = ["lat", "latitude", "y", "LAT", "Latitude"]
    lon_candidates = ["lon", "lng", "longitude", "x", "LON", "Longitude"]

    lat_col = next((c for c in lat_candidates if c in df.columns), None)
    lon_col = next((c for c in lon_candidates if c in df.columns), None)

    if lat_col is None or lon_col is None:
        raise ValueError(f"Could not detect latitude/longitude columns. Found columns: {list(df.columns)}")

    return lat_col, lon_col


def _metro_manila_demo_df() -> pd.DataFrame:
    """Built-in Metro Manila demo dataset for quick demos."""
    data = {
        "store_name": [
            "Neutral Grounds - Glorietta",
            "Titan Hobby Shop",
            "Quantum TCG",
            "Neutral Grounds - Trinoma",
            "Gamehaven",
            "The Legends Hobby Shop",
            "Regran Collectibles",
            "NG Galleria"
        ],
        "lat": [14.5547, 14.5995, 14.5512, 14.6570, 14.5500, 14.6000, 14.6100, 14.6200],
        "lon": [121.0244, 120.9842, 121.0512, 121.0302, 121.0280, 121.0700, 121.0400, 121.0560],
        "type": ['LGS', 'LGS', 'Pokemon Center', 'LGS', 'LGS', 'LGS', 'Retailer', 'LGS'],
        "address": [
            "Glorietta 2, Makati City",
            "123 Shaw Blvd, Mandaluyong",
            "Uptown BGC, Taguig",
            "Trinoma Mall, Quezon City",
            "456 Makati Ave, Makati",
            "Ortigas Center, Pasig",
            "Commonwealth Ave, QC",
            "Robinsons Galleria, Ortigas"
        ],
        "phone": [
            "+63 2 1234 5678",
            "+63 2 2345 6789",
            "+63 2 3456 7890",
            "+63 2 4567 8901",
            "+63 2 5678 9012",
            "+63 2 6789 0123",
            "+63 2 7890 1234",
            "+63 2 8901 2345"
        ],
        "website": [
            "https://neutralgrounds.example/glorietta",
            "https://titan.example",
            "https://quantum.example",
            "https://neutralgrounds.example/trinoma",
            "https://gamehaven.example",
            "https://legends.example",
            "https://regran.example",
            "https://nggalleria.example",
        ],
        "hours": [
            "10AM - 9PM Daily",
            "11AM - 10PM Daily",
            "10AM - 8PM Daily",
            "10AM - 9PM Daily",
            "12PM - 10PM Daily",
            "11AM - 9PM Daily",
            "10AM - 8PM Daily",
            "10AM - 9PM Daily"
        ],
        "tournaments": [
            "Fridays 6PM, Sundays 2PM",
            "Saturdays 3PM",
            "Wednesdays 7PM",
            "Saturdays 4PM, Sundays 2PM",
            "Thursdays 6PM",
            "Fridays 7PM",
            "No regular schedule",
            "Sundays 3PM"
        ]
    }
    df = pd.DataFrame(data)
    df = df.reset_index(drop=True)
    df["store_id"] = "demo_" + df.index.astype(str)
    cols = ["store_id", "store_name", "address", "lat", "lon", "phone", "website", "type", "hours", "tournaments"]
    df = df[cols]
    return df


def load_and_validate_lgs_data(
    filepath_or_df: Union[str, pd.DataFrame, None] = None,
    *,
    load_example: bool = False
) -> pd.DataFrame:
    """
    Load and validate LGS data. Defaults to built-in demo if load_example=True or filepath_or_df is None.

    Parameters
    ----------
    filepath_or_df : str | pd.DataFrame | None
        Path to CSV, or already-loaded DataFrame, or None.
    load_example : bool
        If True, return built-in Metro Manila demo dataset.

    Returns
    -------
    pd.DataFrame with standardized columns:
        ['store_id','store_name','address','lat','lon','phone','website', ...]
    """
    # If user explicitly asked for demo data
    if load_example:
        logger.info("Loading built-in Metro Manila demo dataset.")
        return _metro_manila_demo_df()

    # If caller passed a DataFrame
    if isinstance(filepath_or_df, pd.DataFrame):
        df = filepath_or_df.copy()
    elif isinstance(filepath_or_df, str):
        # If caller passed special token "example" or "demo"
        if filepath_or_df.lower() in ("example", "demo"):
            return _metro_manila_demo_df()
        # otherwise load CSV from given path
        df = pd.read_csv(filepath_or_df)
    else:
        # fallback: no path provided — return demo with warning (safe default)
        logger.warning("No filepath provided; returning demo dataset. Pass a filepath to load real data.")
        return _metro_manila_demo_df()

    # Normalize common column names
    col_map = {}
    for cand in ["store_name", "name", "store", "storeName"]:
        if cand in df.columns:
            col_map[cand] = "store_name"
            break
    for cand in ["address", "addr", "location"]:
        if cand in df.columns:
            col_map[cand] = "address"
            break
    for cand in ["phone", "contact", "phone_number"]:
        if cand in df.columns:
            col_map[cand] = "phone"
            break
    for cand in ["website", "site", "url"]:
        if cand in df.columns:
            col_map[cand] = "website"
            break
    if col_map:
        df = df.rename(columns=col_map)

    # Detect lat/lon columns (raises ValueError if not found)
    lat_col, lon_col = _detect_lat_lon_columns(df)

    # Rename to standard names
    df = df.rename(columns={lat_col: "lat", lon_col: "lon"})

    # Required columns check
    required = ["store_name", "lat", "lon"]
    if "address" in df.columns:
        required.append("address")
    missing_required = [c for c in required if c not in df.columns]
    if missing_required:
        raise ValueError(f"Missing required columns: {missing_required}")

    # Drop rows with missing coordinates
    df = df.dropna(subset=["lat", "lon"])

    # Coerce numeric & validate ranges
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    df = df.dropna(subset=["lat", "lon"])
    df = df[(df["lat"] >= -90) & (df["lat"] <= 90) & (df["lon"] >= -180) & (df["lon"] <= 180)].copy()

    # Optional columns fill
    df["phone"] = df.get("phone", pd.Series(["N/A"] * len(df))).fillna("N/A")
    df["website"] = df.get("website", pd.Series(["N/A"] * len(df))).fillna("N/A")

    # Ensure store_id exists
    if "store_id" not in df.columns:
        df = df.reset_index(drop=True)
        df["store_id"] = df.index.astype(str)

    # Friendly column order
    base_cols = ["store_id", "store_name", "address", "lat", "lon", "phone", "website"]
    rest = [c for c in df.columns if c not in base_cols]
    df = df[base_cols + rest]

    logger.info("Loaded %d store records", len(df))
    return df
