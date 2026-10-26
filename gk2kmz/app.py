import streamlit as st

from coordinates import DATUMS, get_epsg
from views.coordinate_input import render_coordinate_input
from views.output_options import render_output_options
from views.results import render_results

st.set_page_config(
    page_title="Gauss-Krüger → KMZ",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("Gauss-Krüger → KMZ")

col1, col2 = st.columns(2)
datum = col1.selectbox("Datum", list(DATUMS.keys()))
faja = col2.selectbox("Faja", list(DATUMS[datum].keys()))
epsg = get_epsg(datum, faja)

input_mode, df_csv = render_coordinate_input(epsg)
options = render_output_options()
render_results(input_mode, df_csv, epsg, options)