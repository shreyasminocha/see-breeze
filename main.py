import streamlit as st
import altair as alt
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.figure_factory as ff
import numpy as np

STATIONS = ['KIKT', 'KBQX', 'KMIS']

st.title('This Blows')

@st.cache
def load_data():
    data = pd.read_csv(DATA_URL, delim_whitespace=True, parse_dates=[[0, 1, 2]], index_col='#YY_MM_DD')
    data = data.replace('MM', np.nan)
    return data

st.subheader('Number of pickups by hour')

selected_station = st.sidebar.selectbox(label='Station', index=0, options=STATIONS)
DATA_URL = f'https://www.ndbc.noaa.gov/data/realtime2/{selected_station}.txt'

data_load_state = st.text('Loading data...')
data = load_data()
data_load_state.text('Done! (using st.cache)')

#plot
st.subheader('Wind Speed for the Past 45 days')
chart_data = pd.DataFrame(np.random.randn(20, 3))

st.line_chart(chart_data)

#plotly chart
date = st.sidebar.date_input(label='Day').strftime('%Y %m %d')
rows_for_day = data.loc[date]

#polar plot
fig = go.Figure(data=
    go.Scatterpolar(
        r = [rows_for_day['WSPD'].astype(float).mean()],
        theta = [rows_for_day['WDIR'].astype(float).mean()],
        mode = 'markers',
    ))

fig.update_layout(showlegend=False)

st.plotly_chart(fig, use_container_width=True)
