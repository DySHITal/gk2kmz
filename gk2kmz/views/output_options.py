from dataclasses import dataclass
from typing import Union

import streamlit as st

from kmz import ICONS


@dataclass(frozen=True)
class PointOutputOptions:
    icon: str
    color: str
    scale: float


@dataclass(frozen=True)
class PolygonOutputOptions:
    name: str
    color: str
    fill_opacity: float
    line_width: int
    show_vertices: bool


OutputOptions = Union[PointOutputOptions, PolygonOutputOptions]


def render_output_options() -> OutputOptions:
    mode = st.radio(
        "Output type",
        ["Single points", "Polygon"],
        horizontal=True,
    )

    if mode == "Single points":
        col1, col2, col3 = st.columns(3)
        return PointOutputOptions(
            icon=col1.selectbox("Symbol", list(ICONS.keys())),
            color=col2.color_picker("Symbol color", "#FFFFFF"),
            scale=col3.slider("Symbol size", 0.5, 2.0, 1.0, 0.1),
        )

    col1, col2 = st.columns(2)
    name = col1.text_input("Polygon name", "Polygon")
    color = col2.color_picker("Polygon color", "#FF0000")

    col3, col4, col5 = st.columns(3)
    return PolygonOutputOptions(
        name=name,
        color=color,
        fill_opacity=col3.slider("Fill opacity", 0.0, 1.0, 0.4, 0.05),
        line_width=col4.slider("Outline width", 1, 8, 2),
        show_vertices=col5.checkbox("Also show vertices as points"),
    )