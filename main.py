import streamlit as st
import altair as alt
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.figure_factory as ff
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

#plot
st.subheader('Wind Speed for the Past 45 days')
chart_data = pd.DataFrame(
     np.random.randn(20, 3),
     columns=['KIKT', 'KAPT', 'KMIS'])

st.line_chart(chart_data)


#plotly chart


stations = ['KIKT', 'KBQX', 'KMIS']
selected_station = st.sidebar.selectbox(label='Station', index=0, options=stations)

date = st.sidebar.date_input(label='Day')

#polar plot
fig = go.Figure(data=
    go.Scatterpolar(
        r = [0.5, 1, 2, 2.5, 3, 4],
        theta = [35, 70, 120, 155, 205, 240],
        mode = 'markers',
    ))

fig.update_layout(showlegend=False)

st.plotly_chart(fig, use_container_width=True)