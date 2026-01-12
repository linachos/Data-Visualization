import pandas as pd
import numpy as np
from typing import Tuple

def load_and_process_data(filepath: str = 'data/flight_data.xlsx') -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load and preprocess flight data from Excel file
    
    Parameters:
    -----------
    filepath : str
        Path to the Excel file containing flight data
        
    Returns:
    --------
    tuple
        (flights_df, airports_df, airlines_df, aircrafts_df)
    """
    
    # Load all sheets
    flights = pd.read_excel(filepath, sheet_name='flights')
    airports = pd.read_excel(filepath, sheet_name='airports')
    airlines = pd.read_excel(filepath, sheet_name='airlines')
    aircrafts = pd.read_excel(filepath, sheet_name='aircrafts')
    
    # Merge flights with related tables
    df = flights.copy()
    df = df.merge(airlines, on='airline_id', how='left')
    df = df.merge(airports, left_on='origin', right_on='airport_code', how='left')
    df = df.merge(aircrafts, on='aircraft_id', how='left')
    
    # Rename columns to avoid confusion
    df = df.rename(columns={
        'name': 'origin_airport_name',
        'latitude': 'origin_lat',
        'longitude': 'origin_lon'
    })
    
    # Convert datetime columns
    df['scheduled_departure'] = pd.to_datetime(df['scheduled_departure'])
    df['departure'] = pd.to_datetime(df['departure'])
    df['scheduled_arrival'] = pd.to_datetime(df['scheduled_arrival'])
    df['arrival'] = pd.to_datetime(df['arrival'])
    
    # Add time-based features
    df['month'] = df['scheduled_departure'].dt.month
    df['month_name'] = df['scheduled_departure'].dt.strftime('%B')
    df['day_of_week'] = df['scheduled_departure'].dt.day_name()
    df['hour'] = df['scheduled_departure'].dt.hour
    df['date'] = df['scheduled_departure'].dt.date
    df['week'] = df['scheduled_departure'].dt.isocalendar().week
    
    # Add delay categories
    df['delay_category'] = pd.cut(
        df['departure_delay'],
        bins=[-np.inf, 0, 15, 60, np.inf],
        labels=['On Time/Early', 'Minor (1-15 min)', 'Moderate (16-60 min)', 'Major (>60 min)']
    )
    
    # Add boolean flags
    df['is_delayed'] = df['departure_delay'] > 0
    df['on_time'] = df['departure_delay'] <= 15
    df['severely_delayed'] = df['departure_delay'] > 60
    
    # Add time of day categories
    df['time_of_day'] = pd.cut(
        df['hour'],
        bins=[-1, 6, 12, 18, 24],
        labels=['Night (12am-6am)', 'Morning (6am-12pm)', 
                'Afternoon (12pm-6pm)', 'Evening (6pm-12am)']
    )
    
    return df, airports, airlines, aircrafts


def filter_data(df: pd.DataFrame, 
                airports: list = None,
                airlines: list = None,
                date_range: tuple = None) -> pd.DataFrame:
    """
    Filter dataframe based on user selections
    
    Parameters:
    -----------
    df : pd.DataFrame
        The main flights dataframe
    airports : list
        List of airport codes to filter
    airlines : list
        List of airlines to filter
    date_range : tuple
        (start_date, end_date) for filtering
        
    Returns:
    --------
    pd.DataFrame
        Filtered dataframe
    """
    filtered = df.copy()
    
    if airports:
        filtered = filtered[filtered['origin'].isin(airports)]
    
    if airlines:
        filtered = filtered[filtered['airline'].isin(airlines)]
    
    if date_range and len(date_range) == 2:
        filtered = filtered[
            (filtered['date'] >= date_range[0]) & 
            (filtered['date'] <= date_range[1])
        ]
    
    return filtered


def calculate_kpis(df: pd.DataFrame) -> dict:
    """
    Calculate key performance indicators
    
    Parameters:
    -----------
    df : pd.DataFrame
        Filtered flights dataframe
        
    Returns:
    --------
    dict
        Dictionary containing KPI values
    """
    return {
        'total_flights': len(df),
        'avg_delay': df['departure_delay'].mean(),
        'median_delay': df['departure_delay'].median(),
        'on_time_pct': (df['on_time'].sum() / len(df) * 100) if len(df) > 0 else 0,
        'delayed_pct': (df['is_delayed'].sum() / len(df) * 100) if len(df) > 0 else 0,
        'severe_delay_pct': (df['severely_delayed'].sum() / len(df) * 100) if len(df) > 0 else 0,
        'total_delay_minutes': df[df['is_delayed']]['departure_delay'].sum(),
        'max_delay': df['departure_delay'].max()
    }