import numpy as np
import pandas as pd
from pyproj import CRS, Transformer

# Datum + zone -> EPSG code
DATUMS = {
    "POSGAR 94":       {i: f"EPSG:{22180 + i}" for i in range(1, 8)},
    "POSGAR 2007":     {i: f"EPSG:{5342 + i}" for i in range(1, 8)},
    "Campo Inchauspe": {i: f"EPSG:{22190 + i}" for i in range(1, 8)},
}


def get_epsg(datum: str, faja: int) -> str:
    return DATUMS[datum][faja]


def central_meridian(epsg: str) -> float:
    """Read the central meridian (degrees) from the projection definition."""
    crs = CRS.from_user_input(epsg)
    for param in crs.coordinate_operation.params:
        name = param.name.lower()
        if "longitude of natural origin" in name or "central meridian" in name:
            return float(param.value)
    return float("nan")


def to_dms(values):
    """Decimal degrees -> (degrees, minutes, seconds). Sign stays on degrees."""
    values = np.asarray(values, dtype=float)
    sign = np.where(values < 0, -1, 1)
    absolute = np.abs(values)

    degrees = np.floor(absolute)
    minutes_full = (absolute - degrees) * 60
    minutes = np.floor(minutes_full)
    seconds = np.round((minutes_full - minutes) * 60, 5)

    # Avoid results like 60 seconds or 60 minutes.
    carry = seconds >= 60
    seconds = np.where(carry, 0.0, seconds)
    minutes = minutes + carry
    carry = minutes >= 60
    minutes = np.where(carry, 0, minutes)
    degrees = degrees + carry

    return sign * degrees, minutes, seconds


def convert_df(df: pd.DataFrame, epsg: str) -> pd.DataFrame:
    """Add mc, lat/lon (decimal) and lat/lon (G M S) to a DataFrame."""
    missing = {"name", "este", "norte"} - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {', '.join(sorted(missing))}")

    transformer = Transformer.from_crs(epsg, "EPSG:4326", always_xy=True)
    lon, lat = transformer.transform(df["este"].values, df["norte"].values)

    out = df.copy()
    out["mc"] = central_meridian(epsg)
    out["lat"] = lat
    out["lon"] = lon
    out["lat G"], out["lat M"], out["lat S"] = to_dms(lat)
    out["lon G"], out["lon M"], out["lon S"] = to_dms(lon)

    first = [
        "name", "norte", "este", "mc", "lat", "lon",
        "lat G", "lat M", "lat S", "lon G", "lon M", "lon S",
    ]
    rest = [column for column in out.columns if column not in first]
    return out[first + rest]