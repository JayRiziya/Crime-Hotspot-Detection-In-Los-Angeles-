import sklearn
import streamlit as st
import pandas as pd
import joblib
from datetime import datetime

# Load the trained model, scaler, and encoder
model = joblib.load('crime_LA.joblib')
scaler = joblib.load('scaler.joblib')
encoder = joblib.load('encoder.joblib')
df = pd.read_csv('G:/LA_Crime_Data_from_2020_to_2024.csv')

# Function to predict crime hotspot
def predict_crime_hotspot(date_rptd, date_occ, time_occ, area_name, lat, lon):
    # Parse dates
    date_rptd = pd.to_datetime(date_rptd)
    date_occ = pd.to_datetime(date_occ)
    occ_year = date_occ.year
    occ_month = date_occ.month
    occ_day = date_occ.day

    # Prepare input data
    input_data = {
        'TIME OCC': time_occ,
        'LAT': lat,
        'LON': lon,
        'Rpt_Year': date_rptd.year,
        'Occ_Year': occ_year,
        'Occ_Month': occ_month,
        'Occ_Day': occ_day,
    }

    # Add dummy variables for area_name
    area_columns = [col for col in df.columns if col.startswith('AREA NAME_')]
    for area in area_columns:
        input_data[area] = 1 if f'AREA NAME_{area_name}' == area else 0

    # Add dummy variables for crime codes if necessary
    crime_columns = [col for col in df.columns if col.startswith('Crm Cd_')]
    for crime in crime_columns:
        input_data[crime] = 0  # Assuming no crime code info for prediction, set to 0

    # Create DataFrame
    input_df = pd.DataFrame([input_data])

    # Debug: Print columns to ensure consistency
    print("Input DataFrame columns:", input_df.columns)
    print("Scaler feature names:", scaler.feature_names_in_)

    # Align columns with those used for fitting
    missing_cols = set(scaler.feature_names_in_) - set(input_df.columns)
    for col in missing_cols:
        input_df[col] = 0
    input_df = input_df[scaler.feature_names_in_]

    # Apply scaling
    input_scaled = scaler.transform(input_df)

    # Make prediction
    prediction = model.predict(input_scaled)
    return prediction[0]

# Streamlit app design
st.title('Crime Hotspot Prediction')

date_rptd = st.date_input('Date Reported')
date_occ = st.date_input('Date Occurred')
time_occ = st.number_input('Time Occurred', min_value=0, max_value=2359, step=1)
area_name = st.selectbox('Area Name', ['Central', 'Southwest', 'Van Nuys', 'Wilshire', 'Hollywood', 'Southeast', 'Mission', 'Rampart', 'Hollenbeck'])
lat = st.number_input('Latitude')
lon = st.number_input('Longitude')

if st.button('Predict Hotspot'):
    result = predict_crime_hotspot(date_rptd, date_occ, time_occ, area_name, lat, lon)
    st.write(f'Predicted Reporting District: {result}')
