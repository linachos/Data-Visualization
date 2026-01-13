import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

@st.cache_data
def load_data():
    try:
        flights = pd.read_excel('data/flight_data.xlsx', sheet_name='flights')
        airports = pd.read_excel('data/flight_data.xlsx', sheet_name='airports')
        airlines = pd.read_excel('data/flight_data.xlsx', sheet_name='airlines')
        aircrafts = pd.read_excel('data/flight_data.xlsx', sheet_name='aircrafts')
        return flights, airports, airlines, aircrafts
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None
    
# Load data
flights, airports, airlines, aircrafts = load_data()

ny_nj_airports = ['EWR', 'JFK', 'LGA', 'SWF']
    
# Departure dataset
departures = flights[flights['origin'].isin(ny_nj_airports)].copy()

# Merge data
departures = departures.merge(airlines, on='airline_id', how='left')
departures = departures.merge(aircrafts, on='aircraft_id', how='left')
# Merge with origin airport data & rename
departures = departures.merge(airports, left_on='origin', right_on='airport_code', how='left')
departures = departures.rename(columns={'name': 'origin_airport_name', 
                                        'latitude': 'origin_lat',
                                        'longitude': 'origin_lon'})
# Merge again with destination airport data & rename
departures = departures.merge(airports, left_on='destination', right_on='airport_code', how='left')
departures = departures.rename(columns={'name': 'destination_airport_name', 
                                        'latitude': 'destination_lat',
                                        'longitude': 'destination_lon'})


# Arrival dataset
arrivals = flights[flights['destination'].isin(ny_nj_airports)].copy()

# Merge data
arrivals = arrivals.merge(airlines, on='airline_id', how='left')
arrivals = arrivals.merge(aircrafts, on='aircraft_id', how='left')
# Merge with origin airport data & rename
arrivals = arrivals.merge(airports, left_on='origin', right_on='airport_code', how='left')
arrivals = arrivals.rename(columns={'name': 'origin_airport_name',
                                    'latitude': 'origin_lat',
                                    'longitude': 'origin_lon'})
# Merge again with destination airport data & rename
arrivals = arrivals.merge(airports, left_on='destination', right_on='airport_code', how='left')
arrivals = arrivals.rename(columns={'name': 'destination_airport_name',
                                    'latitude': 'destination_lat',
                                    'longitude': 'destination_lon'})


# Add time based features
for df in [departures, arrivals]:
    # Convert dates
    df['scheduled_departure'] = pd.to_datetime(df['scheduled_departure'])
    df['departure'] = pd.to_datetime(df['departure'])
    df['scheduled_arrival'] = pd.to_datetime(df['scheduled_arrival'])
    df['arrival'] = pd.to_datetime(df['arrival'])

    # Add time-based features
    df['month_dep'] = df['scheduled_departure'].dt.month
    df['month_name_dep'] = df['scheduled_departure'].dt.strftime('%B')
    df['day_of_week_dep'] = df['scheduled_departure'].dt.day_name()
    df['hour_dep'] = df['scheduled_departure'].dt.hour
    df['date_dep'] = df['scheduled_departure'].dt.date
    
    df['month_arr'] = df['scheduled_arrival'].dt.month
    df['month_name_arr'] = df['scheduled_arrival'].dt.strftime('%B')
    df['day_of_week_arr'] = df['scheduled_arrival'].dt.day_name()
    df['hour_arr'] = df['scheduled_arrival'].dt.hour
    df['date_arr'] = df['scheduled_arrival'].dt.date
    
    # Add delay categories for departures
    df['departure_delay_category'] = pd.cut(
        df['departure_delay'], 
        bins=[-np.inf, 0, 15, 60, np.inf],
        labels=['On Time/Early', 'Minor (1-15 min)', 'Moderate (16-60 min)', 'Major (>60 min)']
    )
    
    # Add delay categories for arrivals
    df['arrival_delay_category'] = pd.cut(
        df['arrival_delay'], 
        bins=[-np.inf, 0, 15, 60, np.inf],
        labels=['On Time/Early', 'Minor (1-15 min)', 'Moderate (16-60 min)', 'Major (>60 min)']
    )
    
    # Add boolean flags
    df['departure_is_delayed'] = df['departure_delay'] > 0
    df['departure_on_time'] = df['departure_delay'] <= 0
    df['arrival_is_delayed'] = df['arrival_delay'] > 0
    df['arrival_on_time'] = df['arrival_delay'] <= 0
        
        
st.sidebar.header("Filters")
    
# Delay type selector
delay_type = st.sidebar.radio(
    "Delay Type",
    options=["Departure Delays", "Arrival Delays"],
    index=0,
    help="Choose whether to analyze departure or arrival delays"
)

# Set the delay column based on selection
working_df = departures if delay_type == "Departure Delays" else arrivals
working_label = "Departure" if delay_type == "Departure Delays" else "Arrival"

st.sidebar.markdown("---")


col1, col2 = st.columns(2)
with col1:
    avg_delay = working_df['departure_delay'].mean() if delay_type == "Departure Delays" else working_df['arrival_delay'].mean()
    st.markdown(f"""
            <div>
                <div class="kpi-value">{avg_delay:.1f} min</div>
                <div class="kpi-label">Average {working_label} Delay</div>
            </div>
        """, unsafe_allow_html=True)