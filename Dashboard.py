import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
from scipy import stats

st.title("Incidents of crime in the City of LA")
st.markdown("An application to explore crime incidents in Los Angeles using Streamlit 🚗💥")

# Load data
DATA_URL = 'G:/LA_Crime_Data_from_2020_to_2024.csv'

@st.cache_data(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=['Date Rptd'])
    data = data.dropna(subset=['LAT', 'LON'])
    lowercase = lambda x: str(x).lower().replace(' ', '_')
    data = data.rename(lowercase, axis='columns')
    data = data.sort_values(by='date_rptd', ascending=False)
    
    # Remove outliers based on z-score for 'lat' and 'lon'
    data = data[(np.abs(stats.zscore(data['lat'])) < 3)]
    data = data[(np.abs(stats.zscore(data['lon'])) < 3)]
    
    return data

data = load_data(100000)

st.header("Where is the most place for crime in LA?")
crime = st.slider("Number of crime in LA", 0, 20)
st.map(data.query("crm_cd >= @crime")[['lat', 'lon']].dropna(how='any'))

st.header("What is the number of victims by age?")
age_range = st.slider("Victims by age to look at", 0, 100, (0, 100))
data = data[(data['vict_age'] >= age_range[0]) & (data['vict_age'] <= age_range[1])]

st.markdown(f"The victims' ages range from {age_range[0]} to {age_range[1]}")
st.markdown(f"There are a total of {len(data)} victims")
midpoint = (np.average(data['lat']), np.average(data['lon']))

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=data[['vict_age', 'lat', 'lon']],
            get_position=['lon', 'lat'],
            radius=100,
            extruded=True,
            pickable=True,
            elevation_scale=4,
            elevation_range=[0, 1000],
        ),
    ],
))

st.subheader("The number of victims by descent and sex")
chart_data = pd.DataFrame({
    'crm_cd': data['crm_cd'],
    'type': data['crm_cd_desc'],
    'descent': data['vict_descent'],
    'sex': data['vict_sex'],
})
chart_data = chart_data.groupby(by=['descent', 'sex']).size().reset_index(name='counts')
fig = px.bar(chart_data, x='descent', y='counts', color='sex', barmode='group', height=800)
st.write(fig)

st.header("Top 5 types of crimes")
select = st.selectbox('The types of crimes & area', 
    ['Vehicle - Stolen', 'Battery - Simple assault', 'Theft of identity', 'Burglary from vehicle', 'Vandalism - Felony']
)

if select == 'Vehicle - Stolen':
    st.write(data.query("crm_cd_desc == 'VEHICLE - STOLEN'")[["crm_cd_desc", "area_name", "premis_desc"]].sort_values(by=["crm_cd_desc"], ascending=False).dropna(how='any'))

elif select == 'Battery - Simple assault':
    st.write(data.query("crm_cd_desc == 'BATTERY - SIMPLE ASSAULT'")[["crm_cd_desc", "area_name", "premis_desc"]].sort_values(by=["crm_cd_desc"], ascending=False).dropna(how='any'))

elif select == 'Theft of identity':
    st.write(data.query("crm_cd_desc == 'THEFT OF IDENTITY'")[["crm_cd_desc", "area_name", "premis_desc"]].sort_values(by=["crm_cd_desc"], ascending=False).dropna(how='any'))

elif select == 'Burglary from vehicle':
    st.write(data.query("crm_cd_desc == 'BURGLARY FROM VEHICLE'")[["crm_cd_desc", "area_name", "premis_desc"]].sort_values(by=["crm_cd_desc"], ascending=False).dropna(how='any'))

elif select == 'Vandalism - Felony':
    st.write(data.query("crm_cd_desc == 'VANDALISM - FELONY ($400 & OVER, ALL CHURCH VANDALISMS)'")[["crm_cd_desc", "area_name", "premis_desc"]].sort_values(by=["crm_cd_desc"], ascending=False).dropna(how='any'))

if st.checkbox("Show Raw Data", False):
    st.subheader('Raw Data')
    st.write(data)
