import numpy as np
import pandas as pd
from pyproj import Transformer

from coordinates import central_meridian, to_dms

TABLE_COLS = [
    "name", "norte", "este", "mc", "lat", "lon",
    "lat G", "lat M", "lat S", "lon G", "lon M", "lon S",
]

GROUPS = {
    "gk": ["norte", "este"],
    "dec": ["lat", "lon"],
    "dms": ["lat G", "lat M", "lat S", "lon G", "lon M", "lon S"],
}


def empty_table() -> pd.DataFrame:
    return pd.DataFrame({
        column: pd.Series(dtype="object")
        for column in TABLE_COLS
    })


def num(value):
    """Cell text -> float. Accepts decimal comma or dot. Empty -> None."""
    if value is None:
        return None
    if isinstance(value, (int, float, np.floating)):
        return None if np.isnan(value) else float(value)

    text = str(value).strip()
    for char in "°'\"′″º \u00a0":
        text = text.replace(char, "")
    text = text.replace("\u2212", "-")

    if text in ("", "-", "+"):
        return None

    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    else:
        text = text.replace(",", ".")

    return float(text)


def _blank(value) -> bool:
    return (
        value is None
        or (isinstance(value, float) and np.isnan(value))
        or not str(value).strip()
    )


def _dms_to_dd(degrees, minutes, seconds):
    sign = -1.0 if np.signbit(degrees) else 1.0
    return sign * (
        abs(degrees)
        + (minutes or 0) / 60
        + (seconds or 0) / 3600
    )


def _dms_text(value):
    degrees, minutes, seconds = (float(part) for part in to_dms(value))
    return [
        ("-" if value < 0 else "") + str(int(abs(degrees))),
        str(int(minutes)),
        f"{seconds:.5f}",
    ]


def fill_row(df, i, source, epsg) -> bool:
    """Recalculate row i from the group the user edited."""
    values = {column: num(df.at[i, column]) for column in GROUPS[source]}
    to_ll = Transformer.from_crs(epsg, "EPSG:4326", always_xy=True)
    to_gk = Transformer.from_crs("EPSG:4326", epsg, always_xy=True)

    if source == "gk":
        if values["norte"] is None or values["este"] is None:
            return False
        lon, lat = to_ll.transform(values["este"], values["norte"])
    elif source == "dec":
        if values["lat"] is None or values["lon"] is None:
            return False
        lat, lon = values["lat"], values["lon"]
    else:
        if values["lat G"] is None or values["lon G"] is None:
            return False
        lat = _dms_to_dd(
            values["lat G"], values["lat M"], values["lat S"]
        )
        lon = _dms_to_dd(
            values["lon G"], values["lon M"], values["lon S"]
        )

    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("coordinates out of range (check the faja/datum)")

    df.at[i, "mc"] = f"{central_meridian(epsg):g}"

    if source != "gk":
        este, norte = to_gk.transform(lon, lat)
        df.at[i, "norte"] = f"{norte:.3f}"
        df.at[i, "este"] = f"{este:.3f}"

    if source != "dec":
        df.at[i, "lat"] = f"{lat:.8f}"
        df.at[i, "lon"] = f"{lon:.8f}"

    if source != "dms":
        for column, value in zip(
            ["lat G", "lat M", "lat S"],
            _dms_text(lat),
        ):
            df.at[i, column] = value
        for column, value in zip(
            ["lon G", "lon M", "lon S"],
            _dms_text(lon),
        ):
            df.at[i, column] = value

    return True


def _try_fill(df, i, source, epsg, errors) -> bool:
    try:
        ok = fill_row(df, i, source, epsg)
    except ValueError as error:
        errors.append(f"Row {i + 1}: {error}")
        return True

    if ok and _blank(df.at[i, "name"]):
        df.at[i, "name"] = f"Point {i + 1}"

    return ok


def detect_source(columns):
    for source, group_columns in GROUPS.items():
        if any(column in group_columns for column in columns):
            return source
    return None


def apply_changes(table, changes, epsg):
    """Apply Streamlit's data_editor changes and auto-fill rows."""
    df = table.copy().reset_index(drop=True)
    errors = []

    for i, change in changes.get("edited_rows", {}).items():
        i = int(i)
        for column, value in change.items():
            df.at[i, column] = value

        source = detect_source(change.keys())
        if source:
            _try_fill(df, i, source, epsg, errors)

    deleted = [int(index) for index in changes.get("deleted_rows", [])]
    if deleted:
        df = df.drop(index=deleted).reset_index(drop=True)

    for row in changes.get("added_rows", []):
        df.loc[len(df)] = [row.get(column) for column in TABLE_COLS]
        source = detect_source(row.keys())
        if source:
            _try_fill(df, len(df) - 1, source, epsg, errors)

    return df, errors


def recalc_all(table, epsg):
    """Keep typed coordinates and recalculate the rest for the new projection."""
    df = table.copy().reset_index(drop=True)
    errors = []

    for i in df.index:
        for source in ("gk", "dec", "dms"):
            if _try_fill(df, i, source, epsg, errors):
                break

    return df, errors


def table_to_numeric(table) -> pd.DataFrame:
    """Convert the text table to numeric rows with valid latitude/longitude."""
    def safe(value):
        try:
            number = num(value)
            return np.nan if number is None else number
        except ValueError:
            return np.nan

    out = pd.DataFrame({
        "name": [
            "" if _blank(value) else str(value)
            for value in table["name"]
        ]
    })

    for column in TABLE_COLS[1:]:
        out[column] = [safe(value) for value in table[column]]

    return out.dropna(subset=["lat", "lon"]).reset_index(drop=True)