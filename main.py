import streamlit as st
import altair as alt
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.figure_factory as ff
import numpy as np

STATIONS = ['KIKT', 'KBQX', 'KMIS']

st.title('See Breeze')

@st.cache
def load_data():
    data = pd.read_csv(
        DATA_URL,
        delim_whitespace=True,
        parse_dates=[[0, 1, 2]],
        index_col='#YY_MM_DD',
        skiprows=[1]
    )
    data = data.replace('MM', np.nan)
    return data

st.subheader('A Visualization of Wind Speed')

selected_station = st.sidebar.selectbox(label='Station', index=0, options=STATIONS)
DATA_URL = f'https://www.ndbc.noaa.gov/data/realtime2/{selected_station}.txt'

data_load_state = st.text('Loading data...')
data = load_data()
data_load_state.text('Done! (using st.cache)')

#plot
st.subheader('Wind Speed for the Past 45 days')
chart_data = pd.DataFrame(np.random.randn(20, 3))

st.line_chart(chart_data)


min_date, max_date = data.index.min(), data.index.max()

date = st.sidebar.date_input(
    label='Day',
    min_value=min_date,
    max_value=max_date,
    value=max_date,
).strftime('%Y %m %d')
rows_for_day = data.loc[date]

mean_wind_speed = rows_for_day['WSPD'].astype(float).mean()
mean_wind_direction = rows_for_day['WDIR'].astype(float).mean()

#polar plot
fig = go.Figure(data=
    go.Scatterpolar(
        r=[0, mean_wind_speed],
        theta=[0, mean_wind_direction],
        mode='lines+markers',
    ))

fig.update_layout(
    showlegend=False,
    polar={
        'radialaxis': {
            'range': [0, max(15, 1.5 * mean_wind_speed)],
            'dtick': 5,
        },
    },
    margin={
        't': 0, 'r': 0, 'b': 0, 'l': 0,
        'pad': 1,
    }
)

st.sidebar.plotly_chart(fig, use_container_width=True)

#line chart

np.random.seed(42)
source = pd.DataFrame(np.cumsum(np.random.randn(100, 3), 0).round(2),
                    columns=['KMIS', 'KAPT', 'KIKT'], index=pd.RangeIndex(100, name='Time'))

source = source.reset_index().melt('Time', var_name='Station', value_name='Wind Direction (in m/s)')

# Create a selection that chooses the nearest point & selects based on x-value
nearest = alt.selection(type='single', nearest=True, on='mouseover',
                        fields=['Time'], empty='none')

# The basic line
line = alt.Chart(source).mark_line(interpolate='basis').encode(
    x='Time:Q',
    y='Wind Direction (in m/s):Q',
    color='Station:N'
)

# Transparent selectors across the chart. This is what tells us
# the x-value of the cursor
selectors = alt.Chart(source).mark_point().encode(
    x='Time:Q',
    opacity=alt.value(0),
).add_selection(
    nearest
).properties(
    title='Wind Direction for the Past 45 Days'
)
selectors.configure_title(
    fontSize=40,
    font='Courier',
    anchor='start',
    color='gray'
)
# Draw points on the line, and highlight based on selection
points = line.mark_point().encode(
    opacity=alt.condition(nearest, alt.value(1), alt.value(0))
)

# Draw text labels near the points, and highlight based on selection
text = line.mark_text(align='left', dx=5, dy=-5).encode(
    text=alt.condition(nearest, 'Wind Direction (in m/s):Q', alt.value(' '))
)


# Draw a rule at the location of the selection
rules = alt.Chart(source).mark_rule(color='gray').encode(
    x='Time:Q',
).transform_filter(
    nearest
)

# Put the five layers into a chart and bind the data
base = alt.layer(
    line, selectors, points, rules, text
).properties(
    width=600, height=300
)
base
