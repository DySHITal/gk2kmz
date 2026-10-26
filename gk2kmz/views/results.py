import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from coordinates import convert_df
from coordinate_table import table_to_numeric
from kmz import df_to_kmz_points, df_to_kmz_polygon
from views.coordinate_input import InputMode
from views.output_options import (
    OutputOptions,
    PointOutputOptions,
    PolygonOutputOptions,
)

RESULT_CONFIG = {
    "norte": st.column_config.NumberColumn(format="%.3f"),
    "este": st.column_config.NumberColumn(format="%.3f"),
    "mc": st.column_config.NumberColumn(format="%d"),
    "lat": st.column_config.NumberColumn(format="%.8f"),
    "lon": st.column_config.NumberColumn(format="%.8f"),
    "lat G": st.column_config.NumberColumn(format="%d"),
    "lat M": st.column_config.NumberColumn(format="%d"),
    "lat S": st.column_config.NumberColumn(format="%.5f"),
    "lon G": st.column_config.NumberColumn(format="%d"),
    "lon M": st.column_config.NumberColumn(format="%d"),
    "lon S": st.column_config.NumberColumn(format="%.5f"),
}


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(subset=["este", "norte"]).reset_index(drop=True)
    df["name"] = df["name"].fillna("").astype(str).str.strip()

    for i in df.index:
        if df.at[i, "name"] == "":
            df.at[i, "name"] = f"Point {i + 1}"

    return df


def make_kmz(df: pd.DataFrame, options: OutputOptions) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out_path = str(Path(tmp) / "output.kmz")

        if isinstance(options, PointOutputOptions):
            df_to_kmz_points(
                df,
                out_path,
                options.icon,
                options.color,
                options.scale,
            )
        else:
            df_to_kmz_polygon(
                df,
                out_path,
                options.color,
                options.fill_opacity,
                options.line_width,
                options.name,
                options.show_vertices,
            )

        data = Path(out_path).read_bytes()

    st.download_button(
        "Download KMZ",
        data,
        "output.kmz",
        "application/vnd.google-earth.kmz",
    )


def render_results(
    input_mode: InputMode,
    df_csv: pd.DataFrame | None,
    epsg: str,
    options: OutputOptions,
) -> None:
    try:
        if input_mode == "Type coordinates":
            df = table_to_numeric(st.session_state.table)
            if len(df) > 0:
                make_kmz(df, options)
        elif df_csv is not None:
            df = convert_df(clean(df_csv), epsg)
            if len(df) > 0:
                st.dataframe(df, column_config=RESULT_CONFIG)
                make_kmz(df, options)
    except Exception as error:
        st.error(f"Error: {error}")