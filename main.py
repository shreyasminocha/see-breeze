import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.title('This Blows')

DATE_COLUMN = 'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
            'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

@st.cache
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

data_load_state = st.text('Loading data...')
data = load_data(10000)
data_load_state.text("Done! (using st.cache)")

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)

st.subheader('Number of pickups by hour')
hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
st.bar_chart(hist_values)

fig = go.Figure(data=
    go.Scatterpolar(
        r = [0.5, 1, 2, 2.5, 3, 4],
        theta = [35, 70, 120, 155, 205, 240],
        mode = 'markers',
    ))

fig.update_layout(showlegend=False)

st.plotly_chart(fig, use_container_width=True)
