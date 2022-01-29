from select import select
import streamlit as st
import altair as alt
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.figure_factory as ff
import numpy as np
import pydeck as pdk


STATIONS = ['KIKT', 'KATP', 'KMIS']

def station_data_url(station):
    return f'https://www.ndbc.noaa.gov/data/realtime2/{station}.txt'

st.set_page_config(
    page_title='See Breeze',
    page_icon='🌪️',
    initial_sidebar_state='expanded',
)


st.title('See Breeze')
st.markdown('_Interactive tool for monitoring and predicting data at NOAA weather stations_')

# image = Image.open('/Users/michaelwong/Desktop/468px-NOAA_logo.svg.png')
# st.image(image, width = 100, caption='(Not affiliated)')

@st.cache
def load_data(station):
    data = pd.read_csv(
        station_data_url(station),
        delim_whitespace=True,
        parse_dates=[[0, 1, 2]],
        index_col='#YY_MM_DD',
        skiprows=[1]
    )
    data = data.replace('MM', np.nan)
    data['WSPD'] = data['WSPD'].astype(float)
    data['WDIR'] = data['WDIR'].astype(float)

    return data


selected_station = st.sidebar.selectbox(label='Station', index=0, options=STATIONS)

# data_load_state = st.text('Loading data...')
data = load_data(selected_station)
# data_load_state.text(f'Loaded data for {selected_station}!')

#line chart
st.subheader(f'Wind Speed at {selected_station}')

source = data

# Create a selection that chooses the nearest point & selects based on x-value
nearest = alt.selection(type='single', nearest=True, on='mouseover',
                        fields=['#YY_MM_DD'], empty='none')

source = source.groupby('#YY_MM_DD').agg({ 'WSPD': 'mean' })

# The basic line
line = alt.Chart(source.reset_index()).mark_line().encode(
    x='#YY_MM_DD:T',
    y='WSPD:Q',
)

# Transparent selectors across the chart. This is what tells us
# the x-value of the cursor
selectors = alt.Chart(source).mark_point().encode(
    x='#YY_MM_DD:T',
    opacity=alt.value(0),
).add_selection(
    nearest
).properties(
    title='Wind Speed for the Past 45 Days'
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
    text=alt.condition(nearest, 'WSPD:Q', alt.value(' '))
)


# Draw a rule at the location of the selection
rules = alt.Chart(source).mark_rule(color='gray').encode(
    x='#YY_MM_DD:T',
).transform_filter(
    nearest
)

# Put the five layers into a chart and bind the data
base = alt.layer(
    line, selectors, points, rules, text
).properties(
    width=600, height=300
)

st.altair_chart(base, use_container_width=True)

st.markdown('\n---\n')

#MAP BEGINS
st.subheader('Station Map')

d1 = {'lat': [28.521, 29.296, 27.195], 'lon': [-88.289, -88.842, -90.027], 'name':['KIKT', 'KMIS','KATP'], 'cWind':[100,300,500], 'cDirection':[0,120,90]}

df = pd.DataFrame(data=d1)

tooltip = {
    "html":
        "<b>Station Name:</b> {name} <br/>"
        "<b>Current Wind Speed:</b> {cWind} m/s<br/>"
        "<b>Current Wind Direction:</b> {cDirection} degrees<br/>",
    "style": {
        "backgroundColor": "steelblue",
        "color": "white ",
    }
}

colorLayer = pdk.Layer(
            'ScatterplotLayer',
            data=df,
            get_position='[lon, lat]',
            get_color='[50, 59, 200, 160]',
            get_radius=15000,
            pickable=True,
            onClick=True,
            filled=True,
            line_width_min_pixels=10,
            opacity=2,
        )

textLayer = pdk.Layer(
            type='TextLayer',
            id='text-layer',
            data=df,
            pickable=False,
            get_position=['lon', 'lat'],
            get_text='name',
            get_color='[255,255,255]',
            billboard=False,
            get_size=10,
            get_angle=0,
            # Note that string constants in pydeck are explicitly passed as strings
            # This distinguishes them from columns in a data set
            get_text_anchor='"middle"',
            get_alignment_baseline='"center"'
)

st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=28.5,
        longitude=-90,
        zoom=6,
        pitch=0,
    ),
    layers=[colorLayer, textLayer,
    ],
    tooltip=tooltip
))

#MAP ENDS

min_date, max_date = data.index.min(), data.index.max()

date = st.sidebar.date_input(
    label='Day',
    min_value=min_date,
    max_value=max_date,
    value=max_date,
).strftime('%Y %m %d')
rows_for_day = data.loc[date]

mean_wind_speed = rows_for_day['WSPD'].mean()
mean_wind_direction = rows_for_day['WDIR'].mean()

#polar plot
fig = go.Figure(
    data=go.Scatterpolar(
        r=[0, mean_wind_speed],
        theta=[0, mean_wind_direction],
        mode='lines+markers',
    ),
)

fig.update_layout(
    title=f'Mean wind (m/s) on {date}',
    title_x=0.5,
    title_y=0,
    showlegend=False,
    polar={
        'radialaxis': {
            'range': [0, max(15, 1.5 * mean_wind_speed)],
            'dtick': 5,
        },
    },
    width=315,
    margin={
        't': 0, 'r': 25, 'b': 10, 'l': 25,
        'pad': 0,
    },
)

st.sidebar.plotly_chart(fig, config={ 'staticPlot': True })
