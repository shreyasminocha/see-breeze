import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.title('This Blows')

DATE_COLUMN = 'date/time'
DATA_URL = 'https://www.ndbc.noaa.gov/data/realtime2/KIKT.txt'

@st.cache
def load_data():
    data = pd.read_csv(DATA_URL, delim_whitespace=True)
    return data

data_load_state = st.text('Loading data...')
data = load_data()
data_load_state.text('Done! (using st.cache)')

st.subheader('Number of pickups by hour')

fig = go.Figure(data=
    go.Scatterpolar(
        r = [0.5, 1, 2, 2.5, 3, 4],
        theta = [35, 70, 120, 155, 205, 240],
        mode = 'markers',
    ))

fig.update_layout(showlegend=False)

st.plotly_chart(fig, use_container_width=True)
