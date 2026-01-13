import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="NY/NJ Flight Delays Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .kpi-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .kpi-label {
        font-size: 1rem;
        color: #666;
    }
    </style>
""", unsafe_allow_html=True)

# Load and cache data
@st.cache_data
def load_data():
    """Load all data from Excel file"""
    try:
        flights = pd.read_excel('data/flight_data.xlsx', sheet_name='flights')
        airports = pd.read_excel('data/flight_data.xlsx', sheet_name='airports')
        airlines = pd.read_excel('data/flight_data.xlsx', sheet_name='airlines')
        aircrafts = pd.read_excel('data/flight_data.xlsx', sheet_name='aircrafts')

        return flights, airports, airlines, aircrafts
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None

@st.cache_data
def prepare_datasets(flights, airports, airlines, aircrafts):
    """Prepare departure and arrival datasets for NY/NJ airports"""
    
    # Define NY/NJ airports
    NY_NJ_AIRPORTS = ['EWR', 'JFK', 'LGA', 'SWF']
    
    # === DEPARTURES DATASET ===
    # Filter for flights departing FROM NY/NJ airports
    departures = flights[flights['origin'].isin(NY_NJ_AIRPORTS)].copy()
    
    # Merge with airlines
    departures = departures.merge(airlines, on='airline_id', how='left')
    
    # Merge with airports for ORIGIN information
    departures = departures.merge(
        airports, 
        left_on='origin', 
        right_on='airport_code', 
        how='left'
    )
    departures = departures.rename(columns={
        'name': 'origin_airport_name',
        'latitude': 'origin_lat',
        'longitude': 'origin_lon'
    })
    
    # Merge with airports for DESTINATION information
    departures = departures.merge(
        airports[['airport_code', 'name', 'latitude', 'longitude']], 
        left_on='destination', 
        right_on='airport_code', 
        how='left',
        suffixes=('', '_dest')
    )
    departures = departures.rename(columns={
        'name': 'destination_airport_name',
        'latitude': 'destination_lat',
        'longitude': 'destination_lon'
    })
    
    # Merge with aircrafts
    departures = departures.merge(aircrafts, on='aircraft_id', how='left')
    
    # === ARRIVALS DATASET ===
    # Filter for flights arriving TO NY/NJ airports
    arrivals = flights[flights['destination'].isin(NY_NJ_AIRPORTS)].copy()
    
    # Merge with airlines
    arrivals = arrivals.merge(airlines, on='airline_id', how='left')
    
    # Merge with airports for ORIGIN information
    arrivals = arrivals.merge(
        airports, 
        left_on='origin', 
        right_on='airport_code', 
        how='left'
    )
    arrivals = arrivals.rename(columns={
        'name': 'origin_airport_name',
        'latitude': 'origin_lat',
        'longitude': 'origin_lon'
    })
    
    # Merge with airports for DESTINATION information
    arrivals = arrivals.merge(
        airports[['airport_code', 'name', 'latitude', 'longitude']], 
        left_on='destination', 
        right_on='airport_code', 
        how='left',
        suffixes=('', '_dest')
    )
    arrivals = arrivals.rename(columns={
        'name': 'destination_airport_name',
        'latitude': 'destination_lat',
        'longitude': 'destination_lon'
    })
    
    # Merge with aircrafts
    arrivals = arrivals.merge(aircrafts, on='aircraft_id', how='left')
    
    # === ADD TIME-BASED FEATURES TO BOTH ===
    for df_data in [departures, arrivals]:
        # Convert dates
        df_data['scheduled_departure'] = pd.to_datetime(df_data['scheduled_departure'])
        df_data['departure'] = pd.to_datetime(df_data['departure'])
        
        # Add time-based features
        df_data['month'] = df_data['scheduled_departure'].dt.month
        df_data['month_name'] = df_data['scheduled_departure'].dt.strftime('%B')
        df_data['day_of_week'] = df_data['scheduled_departure'].dt.day_name()
        df_data['hour'] = df_data['scheduled_departure'].dt.hour
        df_data['date'] = df_data['scheduled_departure'].dt.date
        
        # Add delay categories for departures
        df_data['departure_delay_category'] = pd.cut(
            df_data['departure_delay'], 
            bins=[-np.inf, 0, 15, 60, np.inf],
            labels=['On Time/Early', 'Minor (1-15 min)', 'Moderate (16-60 min)', 'Major (>60 min)']
        )
        
        # Add delay categories for arrivals
        df_data['arrival_delay_category'] = pd.cut(
            df_data['arrival_delay'], 
            bins=[-np.inf, 0, 15, 60, np.inf],
            labels=['On Time/Early', 'Minor (1-15 min)', 'Moderate (16-60 min)', 'Major (>60 min)']
        )
        
        # Add boolean flags
        df_data['departure_is_delayed'] = df_data['departure_delay'] > 0
        df_data['departure_on_time'] = df_data['departure_delay'] <= 15
        df_data['arrival_is_delayed'] = df_data['arrival_delay'] > 0
        df_data['arrival_on_time'] = df_data['arrival_delay'] <= 15
    
    return departures, arrivals, NY_NJ_AIRPORTS

# Load data
flights, airports, airlines, aircrafts = load_data()

if flights is not None:
    # Prepare both datasets
    departures_df, arrivals_df, NY_NJ_AIRPORTS = prepare_datasets(flights, airports, airlines, aircrafts)
    # Header
    st.markdown('<div class="main-header">✈️ NY/NJ Airports Flight Delays Dashboard</div>', 
                unsafe_allow_html=True)
    st.markdown("### Port Authority of New York and New Jersey - 2024 Flight Analysis")
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Delay type selector
    delay_type = st.sidebar.radio(
        "Delay Type",
        options=["Departure Delays", "Arrival Delays"],
        index=0,
        help="Choose whether to analyze departure or arrival delays"
    )
    
    # Set the working dataframe based on delay type
    if delay_type == "Departure Delays":
        working_df = departures_df
        airport_column = 'origin'
        airport_name_column = 'origin_airport_name'
        airport_lat_column = 'origin_lat'
        airport_lon_column = 'origin_lon'
    else:
        working_df = arrivals_df
        airport_column = 'destination'
        airport_name_column = 'destination_airport_name'
        airport_lat_column = 'destination_lat'
        airport_lon_column = 'destination_lon'
    
    # Set the delay column based on selection
    delay_column = 'departure_delay' if delay_type == "Departure Delays" else 'arrival_delay'
    delay_label = "Departure" if delay_type == "Departure Delays" else "Arrival"
    
    st.sidebar.markdown("---")
    
    # Airport filter with select all/none buttons
    st.sidebar.subheader("Airports")

    # Get available airports for current delay type
    available_airports = sorted(working_df[airport_column].unique())

    col_a1, col_a2 = st.sidebar.columns(2)
    with col_a1:
        select_all_airports = st.button("✓ Select All", key="select_airports")
    with col_a2:
        deselect_all_airports = st.button("✗ Clear All", key="deselect_airports")

    # Initialize or reset session state based on delay type
    session_key = f'selected_airports_{delay_type}'
    if session_key not in st.session_state:
        st.session_state[session_key] = available_airports

    # Handle button clicks for airports
    if select_all_airports:
        st.session_state[session_key] = available_airports
    if deselect_all_airports:
        st.session_state[session_key] = []

    # Filter session state to only include valid airports
    valid_selection = [a for a in st.session_state[session_key] if a in available_airports]

    selected_airports = st.sidebar.multiselect(
        "Select Airport(s)",
        options=available_airports,
        default=valid_selection,
        key=f"airport_multiselect_{delay_type}"
    )

    # Update session state
    st.session_state[session_key] = selected_airports
    
    # Airline filter with select all/none buttons
    st.sidebar.subheader("Airlines")
    airlines_list = sorted(working_df['airline'].dropna().unique())
    
    col_b1, col_b2 = st.sidebar.columns(2)
    with col_b1:
        select_all_airlines = st.button("✓ Select All", key="select_airlines")
    with col_b2:
        deselect_all_airlines = st.button("✗ Clear All", key="deselect_airlines")
    
    # Handle button clicks for airlines
    if select_all_airlines:
        st.session_state.selected_airlines = airlines_list
    if deselect_all_airlines:
        st.session_state.selected_airlines = []
    
    # Initialize session state for airlines if not exists
    if 'selected_airlines' not in st.session_state:
        st.session_state.selected_airlines = airlines_list
    
    selected_airlines = st.sidebar.multiselect(
        "Select Airline(s)",
        options=airlines_list,
        default=st.session_state.selected_airlines,
        key="airline_multiselect"
    )
    
    # Update session state
    st.session_state.selected_airlines = selected_airlines
    
    # Date range filter
    min_date = working_df['date'].min()
    max_date = working_df['date'].max()
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Apply filters
    mask = (
        (working_df[airport_column].isin(selected_airports)) &
        (working_df['airline'].isin(selected_airlines)) &
        (working_df['date'] >= date_range[0]) &
        (working_df['date'] <= date_range[1] if len(date_range) > 1 else date_range[0])
    )
    filtered_df = working_df[mask].copy()
    
    # Display filter summary
    st.sidebar.markdown("---")
    st.sidebar.metric("Filtered Flights", f"{len(filtered_df):,}")
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_delay = filtered_df[delay_column].mean()
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">{avg_delay:.1f} min</div>
                <div class="kpi-label">Average {delay_label} Delay</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        on_time_pct = (filtered_df[delay_column] <= 15).sum() / len(filtered_df) * 100
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">{on_time_pct:.1f}%</div>
                <div class="kpi-label">On-Time Performance</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_flights = len(filtered_df)
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">{total_flights:,}</div>
                <div class="kpi-label">Total Flights</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        severely_delayed = (filtered_df[delay_column] > 60).sum()
        severe_pct = (severely_delayed / len(filtered_df) * 100)
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">{severe_pct:.1f}%</div>
                <div class="kpi-label">Severe Delays (>60 min)</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Main visualizations
    col_left, col_right = st.columns([1.5, 1])
    
    with col_left:
        # Map
        st.subheader("📍 Airport Locations & Delay Performance")
        
        airport_stats = filtered_df.groupby([airport_column, airport_name_column, 
                                            airport_lat_column, airport_lon_column]).agg({
            delay_column: 'mean',
            'flight': 'count'
        }).reset_index()
        airport_stats.columns = ['airport_code', 'airport_name', 'lat', 'lon', 
                                'avg_delay', 'num_flights']
        
        fig_map = px.scatter_mapbox(
            airport_stats,
            lat='lat',
            lon='lon',
            size='num_flights',
            color='avg_delay',
            hover_name='airport_name',
            hover_data={'lat': False, 'lon': False, 
                       'avg_delay': ':.1f', 'num_flights': ':,'},
            color_continuous_scale='RdYlGn_r',
            size_max=40,
            zoom=8,
            height=400
        )
        
        fig_map.update_layout(
            mapbox_style="open-street-map",
            margin={"r": 0, "t": 0, "l": 0, "b": 0}
        )
        
        st.plotly_chart(fig_map, use_container_width=True)
    
    with col_right:
        # Bar chart - Delays by Airport
        st.subheader(f"📊 Average {delay_label} Delays by Airport")
        
        airport_delays = filtered_df.groupby(airport_column)[delay_column].mean().sort_values(ascending=True)
        
        fig_bar = go.Figure(go.Bar(
            x=airport_delays.values,
            y=airport_delays.index,
            orientation='h',
            marker=dict(
                color=airport_delays.values,
                colorscale='RdYlGn_r',
                showscale=False
            ),
            text=[f"{val:.1f} min" for val in airport_delays.values],
            textposition='outside'
        ))
        
        fig_bar.update_layout(
            xaxis_title="Average Delay (minutes)",
            yaxis_title="Airport",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Line chart - Delays over time
    st.subheader(f"📈 {delay_label} Delay Trends Over Time")
    
    time_series = filtered_df.groupby('date')[delay_column].mean().reset_index()
    
    fig_line = px.line(
        time_series,
        x='date',
        y=delay_column,
        title=f'Daily Average {delay_label} Delays',
        labels={delay_column: 'Average Delay (minutes)', 'date': 'Date'}
    )
    
    fig_line.add_hline(
        y=15, 
        line_dash="dash", 
        line_color="red",
        annotation_text="15 min threshold (On-Time)"
    )
    
    fig_line.update_layout(height=350)
    st.plotly_chart(fig_line, use_container_width=True)
    
    # Additional insights
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("🏢 Top Airlines by Delay")
        airline_delays = filtered_df.groupby('airline').agg({
            delay_column: 'mean',
            'flight': 'count'
        }).sort_values(delay_column, ascending=False).head(10)
        airline_delays.columns = ['Avg Delay (min)', 'Flights']
        st.dataframe(airline_delays.style.format({
            'Avg Delay (min)': '{:.1f}',
            'Flights': '{:,}'
        }), use_container_width=True)
    
    with col_b:
        st.subheader("📅 Delays by Day of Week")
        dow_delays = filtered_df.groupby('day_of_week')[delay_column].mean().reindex(
            ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        )
        fig_dow = px.bar(
            x=dow_delays.index,
            y=dow_delays.values,
            labels={'x': 'Day of Week', 'y': 'Average Delay (minutes)'},
            color=dow_delays.values,
            color_continuous_scale='RdYlGn_r'
        )
        fig_dow.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig_dow, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("*Data source: Bureau of Transportation Statistics (BTS) 2024*")

else:
    st.error("Failed to load data. Please check that 'data/flights_data.xlsx' exists.")