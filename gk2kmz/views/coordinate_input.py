from typing import Literal, Optional, Tuple

import pandas as pd
import streamlit as st

from coordinate_table import (
    apply_changes,
    empty_table,
    recalc_all,
)
from tooltip import CSV_HELP, CSV_TEMPLATE

InputMode = Literal["Type coordinates", "Upload CSV"]


def render_coordinate_input(epsg: str) -> Tuple[InputMode, Optional[pd.DataFrame]]:
    if "table" not in st.session_state:
        st.session_state.table = empty_table()
        st.session_state.ver = 0
        st.session_state.epsg = epsg
        st.session_state.errors = []

    # Recalculate the table when the selected datum or zone changes.
    if st.session_state.epsg != epsg:
        st.session_state.table, st.session_state.errors = recalc_all(
            st.session_state.table,
            epsg,
        )
        st.session_state.epsg = epsg
        st.session_state.ver += 1

    def on_table_edit():
        editor_key = f"editor_{st.session_state.ver}"
        changes = st.session_state[editor_key]
        table, errors = apply_changes(
            st.session_state.table,
            changes,
            st.session_state.epsg,
        )
        st.session_state.table = table
        st.session_state.errors = errors
        st.session_state.ver += 1

    input_mode: InputMode = st.radio(
        "Input",
        ["Type coordinates", "Upload CSV"],
        horizontal=True,
    )

    df_csv = None

    if input_mode == "Type coordinates":
        st.caption(
            "Fill **norte + este**, or **lat + lon**, or **G M S** "
            "(degrees required, empty minutes/seconds count as 0) and the "
            "other columns fill in automatically. Decimal comma or dot both "
            "work. Pasting from Excel works too."
        )
        st.data_editor(
            st.session_state.table,
            key=f"editor_{st.session_state.ver}",
            on_change=on_table_edit,
            num_rows="dynamic",
            use_container_width=True,
            disabled=["mc"],
            column_config={
                "name": st.column_config.TextColumn("name", width="medium"),
                "norte": st.column_config.TextColumn("norte", width="medium"),
                "este": st.column_config.TextColumn("este", width="medium"),
                "mc": st.column_config.TextColumn("mc", width="small"),
                "lat": st.column_config.TextColumn("lat", width="medium"),
                "lon": st.column_config.TextColumn("lon", width="medium"),
                "lat G": st.column_config.TextColumn("lat G", width="small"),
                "lat M": st.column_config.TextColumn("lat M", width="small"),
                "lat S": st.column_config.TextColumn("lat S", width="small"),
                "lon G": st.column_config.TextColumn("lon G", width="small"),
                "lon M": st.column_config.TextColumn("lon M", width="small"),
                "lon S": st.column_config.TextColumn("lon S", width="small"),
            },
        )

        for message in st.session_state.errors:
            st.warning(message)
    else:
        file = st.file_uploader("CSV file", type="csv", help=CSV_HELP)
        st.download_button("Download CSV template", CSV_TEMPLATE, "template.csv", "text/csv")
        if file is not None:
            df_csv = pd.read_csv(file)

    return input_mode, df_csv