import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="NY Flight Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FFFFFF;
        text-align: center;
        margin-bottom: 1rem;
    }
    .kpi-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        text-align: center;
        height: 131px;
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
        
        # Merge data
        df = flights.merge(airlines, on='airline_id', how='left')
        df = df.merge(airports, left_on='origin', right_on='airport_code', how='left')
        df = df.merge(aircrafts, on='aircraft_id', how='left')
        
        # Rename airport columns for clarity
        df = df.rename(columns={'name': 'origin_airport_name', 
                                'latitude': 'origin_lat', 
                                'longitude': 'origin_lon'})
        
        # Convert dates
        df['scheduled_departure'] = pd.to_datetime(df['scheduled_departure'])
        df['departure'] = pd.to_datetime(df['departure'])
        
        # Create additional columns
        df['month'] = df['scheduled_departure'].dt.month
        df['month_name'] = df['scheduled_departure'].dt.strftime('%B')
        df['day_of_week'] = df['scheduled_departure'].dt.day_name()
        df['hour'] = df['scheduled_departure'].dt.hour
        df['date'] = df['scheduled_departure'].dt.date
        
        # Delay categories
        df['delay_category'] = pd.cut(df['departure_delay'], 
                                        bins=[-np.inf, 0, 15, 60, np.inf],
                                        labels=['On Time/Early', 'Minor (1-15 min)', 
                                            'Moderate (16-60 min)', 'Major (>60 min)'])
        
        df['is_delayed'] = df['departure_delay'] > 0
        df['on_time'] = df['departure_delay'] <= 15
        
        return df, airports, airlines, aircrafts
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None

# Load data
df, airports, airlines, aircrafts = load_data()

if df is not None:
    # Header
    st.markdown('<div class="main-header">NY/NJ Airports Flight Delays</div>', 
                unsafe_allow_html=True)
    st.markdown("")
    st.markdown("### Port Authority of New York and New Jersey - 2024 Departures Delay Analysis")
    
    # Sidebar filters
    st.sidebar.header("Filters")
    st.sidebar.markdown("---")
    
    # Airport filter with select all/none buttons
    st.sidebar.subheader("Airports")
    ny_nj_airports = ['EWR', 'JFK', 'LGA', 'SWF']
    available_airports = sorted(df[df['origin'].isin(ny_nj_airports)]['origin'].unique())
    
    if 'airport_multiselect' not in st.session_state:
        st.session_state.airport_multiselect = available_airports
    
    col_a1, col_a2 = st.sidebar.columns(2)
    with col_a1:
        if st.button("✓ Select All", key="select_airports"):
            st.session_state.airport_multiselect = available_airports

    with col_a2:
        if st.button("✗ Clear All", key="deselect_airports"):
            st.session_state.airport_multiselect = []
    
    selected_airports = st.sidebar.multiselect(
        "Select Airport(s)",
        options=available_airports,
        key="airport_multiselect"
    )
    
    # Update session state
    #st.session_state.selected_airports = selected_airports
    
    # Airline filter with select all/none buttons
    st.sidebar.subheader("Airlines")
    airlines_list = sorted(df['airline'].dropna().unique())
    
    default_airlines = [
    'Delta Air Lines Inc.',
    'American Airlines Inc.',
    'United Air Lines Inc.',
    'Allegiant Air'
    ]

    if 'airline_multiselect' not in st.session_state:
        st.session_state.airline_multiselect = default_airlines

    col_b1, col_b2 = st.sidebar.columns(2)

    with col_b1:
        if st.button("✓ Select All", key="select_airlines"):
            st.session_state.airline_multiselect = airlines_list

    with col_b2:
        if st.button("✗ Clear All", key="deselect_airlines"):
            st.session_state.airline_multiselect = []

    selected_airlines = st.sidebar.multiselect(
        "Select Airline(s)",
        options=airlines_list,
        key="airline_multiselect"
    )
    
    # Date range filter
    st.sidebar.subheader("Date Range")
    min_date = df['date'].min()
    max_date = df['date'].max()
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Apply filters
    mask = (
        (df['origin'].isin(selected_airports)) &
        (df['airline'].isin(selected_airlines)) &
        (df['date'] >= date_range[0]) &
        (df['date'] <= date_range[1] if len(date_range) > 1 else date_range[0])
    )
    filtered_df = df[mask].copy()
    
    # Display filter summary
    st.sidebar.markdown("---")
    st.sidebar.metric("Filtered Flights", f"{len(filtered_df):,}")
    
    # KPIs
    col1, col2, col3 = st.columns([1,1,2])
    
    with col1:
        col1_top, col_sep, col1_bottom = st.container(), st.container(), st.container()
        with col1_top:
            total_flights = len(filtered_df)
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{total_flights:,}</div>
                    <div class="kpi-label">Total Flights</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col_sep:
            st.markdown("<br>", unsafe_allow_html=True)
        
        with col1_bottom:
            avg_delay = filtered_df['departure_delay'].mean()
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{avg_delay:.1f} min</div>
                    <div class="kpi-label">Average Delay</div>
                </div>
            """, unsafe_allow_html=True)
    
    with col2:
        col2_top, col_sep, col2_bottom = st.container(), st.container(), st.container()
        with col2_top:
            severely_delayed = (filtered_df['departure_delay'] > 60).sum()
            severe_pct = (severely_delayed / len(filtered_df) * 100)
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{severe_pct:.1f}%</div>
                    <div class="kpi-label">Severe Delays (>60 min)</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col_sep:
            st.markdown("<br>", unsafe_allow_html=True)
            
        with col2_bottom:
            on_time = (filtered_df['departure_delay'] <= 0).sum()
            on_time_pct = (on_time / len(filtered_df) * 100)
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{on_time_pct:.1f}%</div>
                    <div class="kpi-label">On-Time</div>
                </div>
            """, unsafe_allow_html=True)
    
    with col3:
        st.subheader("On-Time Performance")
        # Slider to choose delay threshold
        max_delay = 90 # Cap at 90 minutes for better UX
        delay_threshold = st.slider(
            "Delay threshold (minutes)",
            min_value=0,
            max_value=max_delay,
            value=15,
            step=5
        )

        # Compute KPI dynamically
        on_time_pct = (
            (filtered_df['departure_delay'] <= delay_threshold).sum()
            / len(filtered_df) * 100
        )

        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">{on_time_pct:.1f}%</div>
                <div class="kpi-label">
                    Flights with delay ≤ {delay_threshold} min
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Main visualizations
    col_left, col_sep, col_right = st.columns([0.9, 0.1, 0.9])
    
    with col_left:
        # Map
        st.subheader("Airport Locations & Delay Performance")
        
        airport_stats = filtered_df.groupby(['origin', 'origin_airport_name', 
                                            'origin_lat', 'origin_lon']).agg({
            'departure_delay': 'mean',
            'flight': 'count'
        }).reset_index()
        airport_stats.columns = ['origin', 'airport_name', 'lat', 'lon', 
                                'avg_delay', 'num_flights']
        
        fig_map = px.scatter_mapbox(
            airport_stats,
            lat='lat',
            lon='lon',
            #size='num_flights',
            color='avg_delay',
            hover_name='airport_name',
            hover_data={'lat': False, 'lon': False, 
                        'avg_delay': ':.1f', 'num_flights': ':,'},
            color_continuous_scale='RdYlGn_r',
            size_max=40,
            zoom=8,
            height=650,
            custom_data=['num_flights', 'avg_delay']
        )

        fig_map.update_traces(
            marker=dict(size=30, opacity=0.6),
            hovertemplate=(
                "<b>%{hovertext}</b><br><br>" +
                "Avg Delay: %{customdata[1]:.1f} min<br>" +
                "Total Flights: %{customdata[0]:,}<br>" +
                "<extra></extra>"
            )
        )
                
        fig_map.update_coloraxes(colorbar_title="Avg Delay", 
                                    colorbar_ticksuffix=" min", 
                                    colorbar_thickness=18,
                                    colorbar_len=0.9,
                                    colorbar_y=0.5,
                                    colorbar_yanchor="middle",
                                    colorbar_tickmode="linear",
                                    colorbar_tick0=0,
                                    colorbar_dtick=2)

        fig_map.update_layout(
            mapbox_style="open-street-map",
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            hoverlabel=dict(align="left")
        )
        
        st.plotly_chart(fig_map, use_container_width=True)
    
    with col_right:
        #top_right, bottom_right = st.container(), st.container()
        #with top_right:
            # Bar chart - Delays by Airport
            st.subheader("Average Delay by Airport")
            
            airport_delays = filtered_df.groupby('origin')['departure_delay'].mean().sort_values(ascending=True)
            
            fig_bar = go.Figure(go.Bar(
                x=airport_delays.index,
                y=airport_delays.values,
                orientation='v',
                marker=dict(
                    color=airport_delays.values,
                    colorscale='RdYlGn_r',
                    showscale=False
                ),
                text=[f"{val:.1f} min" for val in airport_delays.values],
                textposition='outside'
            ))
            
            max_delay = airport_delays.max()
            fig_bar.update_layout(
                #xaxis=dict(range=[0, max_delay*1.2]),
                yaxis_title="Average Delay (minutes)",
                xaxis_title="Airport",
                height=700,
                showlegend=False,
                margin=dict(l=100)
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
        
        #with bottom_right:
        #    pass
    
    # Line chart - Delays over time
    st.markdown("---")
    st.subheader("Delay Trends Over Time")
    
    time_series = filtered_df.groupby('date')['departure_delay'].mean().reset_index()
    
    fig_line = px.line(
        time_series,
        x='date',
        y='departure_delay',
        #title='Daily Average Departure Delays',
        labels={'departure_delay': 'Average Delay (minutes)', 'date': ''}
    )
    
    fig_line.update_layout(height=350)
    st.plotly_chart(fig_line, use_container_width=True)
    
    # Additional insights
    col_a, col_spacer, col_b = st.columns([1, 0.1, 1.5])
    
    with col_a:
        st.subheader("Top Airlines by Delay")
        st.markdown("")
        airline_delays = filtered_df.groupby('airline').agg({
            'departure_delay': 'mean',
            'flight': 'count',
            'origin': lambda x: ', '.join(sorted(x.unique()))
        }).sort_values('departure_delay', ascending=False).head(5)
        airline_delays.columns = ['Avg Delay (min)', 'Flights', 'Airports']
        airline_delays = airline_delays.reset_index()
        airline_delays = airline_delays.rename(columns={'airline': 'Airline'})
        st.dataframe(airline_delays.style.format({
            'Avg Delay (min)': '{:.1f}',
            'Flights': '{:,}'
        }), use_container_width=True, hide_index=True)
    
    with col_b:
        st.subheader("Delays by Day of Week")
        dow_delays = filtered_df.groupby('day_of_week')['departure_delay'].mean().reindex(
            ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        )
        dow_df = pd.DataFrame({
            'Day': dow_delays.index,
            'Average Delay': dow_delays.values
        })
        
        fig_dow = px.bar(
            dow_df,
            x='Day',
            y='Average Delay',
            color='Average Delay',
            color_continuous_scale='RdYlGn_r',
            custom_data=['Average Delay']
        )
        
        fig_dow.update_traces(
            hovertemplate=(
                "<b>%{x}</b><br>" +
                "Avg Delay: %{customdata[0]:.1f} min<br>" +
                "<extra></extra>"
            )
        )
        
        fig_dow.update_coloraxes(colorbar_title="Avg Delay", 
                                    colorbar_ticksuffix=" min", 
                                    colorbar_thickness=18,
                                    colorbar_len=0.9,
                                    colorbar_tickmode="linear",
                                    colorbar_tick0=0,
                                    colorbar_dtick=2)
        
        fig_dow.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig_dow, use_container_width=True)
        
        
    
    # Footer
    st.markdown("---")
    st.markdown("*Data source: Bureau of Transportation Statistics (BTS) 2024*")

else:
    st.error("Failed to load data. Please check that 'data/flight_data.xlsx' exists.")