import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_airport_map(df: pd.DataFrame) -> go.Figure:
    """
    Create an interactive map showing airports with delay information
    
    Parameters:
    -----------
    df : pd.DataFrame
        Filtered flights dataframe
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    airport_stats = df.groupby(['origin', 'origin_airport_name', 
                                'origin_lat', 'origin_lon']).agg({
        'departure_delay': 'mean',
        'flight': 'count'
    }).reset_index()
    
    airport_stats.columns = ['origin', 'airport_name', 'lat', 'lon', 
                            'avg_delay', 'num_flights']
    
    fig = px.scatter_mapbox(
        airport_stats,
        lat='lat',
        lon='lon',
        size='num_flights',
        color='avg_delay',
        hover_name='airport_name',
        hover_data={
            'lat': False,
            'lon': False,
            'avg_delay': ':.1f',
            'num_flights': ':,'
        },
        color_continuous_scale='RdYlGn_r',
        size_max=50,
        zoom=8,
        title='Airport Locations & Average Delays'
    )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        height=450
    )
    
    return fig


def create_delay_bar_chart(df: pd.DataFrame, by: str = 'origin') -> go.Figure:
    """
    Create a horizontal bar chart for delays
    
    Parameters:
    -----------
    df : pd.DataFrame
        Filtered flights dataframe
    by : str
        Column to group by ('origin', 'airline', etc.)
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    delays = df.groupby(by)['departure_delay'].mean().sort_values(ascending=True)
    
    fig = go.Figure(go.Bar(
        x=delays.values,
        y=delays.index,
        orientation='h',
        marker=dict(
            color=delays.values,
            colorscale='RdYlGn_r',
            showscale=False
        ),
        text=[f"{val:.1f} min" for val in delays.values],
        textposition='outside'
    ))
    
    fig.update_layout(
        xaxis_title="Average Delay (minutes)",
        yaxis_title=by.capitalize(),
        height=400,
        showlegend=False,
        title=f'Average Delays by {by.capitalize()}'
    )
    
    return fig


def create_time_series(df: pd.DataFrame, freq: str = 'D') -> go.Figure:
    """
    Create a time series line chart of delays
    
    Parameters:
    -----------
    df : pd.DataFrame
        Filtered flights dataframe
    freq : str
        Frequency for aggregation ('D' for daily, 'W' for weekly, 'M' for monthly)
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    if freq == 'D':
        time_data = df.groupby('date')['departure_delay'].mean().reset_index()
        x_col = 'date'
        title = 'Daily Average Departure Delays'
    elif freq == 'W':
        df['week_start'] = df['scheduled_departure'].dt.to_period('W').dt.start_time
        time_data = df.groupby('week_start')['departure_delay'].mean().reset_index()
        x_col = 'week_start'
        title = 'Weekly Average Departure Delays'
    else:  # Monthly
        time_data = df.groupby('month_name')['departure_delay'].mean().reset_index()
        x_col = 'month_name'
        title = 'Monthly Average Departure Delays'
    
    fig = px.line(
        time_data,
        x=x_col,
        y='departure_delay',
        title=title,
        labels={'departure_delay': 'Average Delay (minutes)', x_col: 'Date'}
    )
    
    # Add threshold line
    fig.add_hline(
        y=15,
        line_dash="dash",
        line_color="red",
        annotation_text="15 min threshold (On-Time)",
        annotation_position="right"
    )
    
    fig.update_layout(height=350)
    
    return fig


def create_delay_distribution(df: pd.DataFrame) -> go.Figure:
    """
    Create a histogram showing delay distribution
    
    Parameters:
    -----------
    df : pd.DataFrame
        Filtered flights dataframe
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    fig = px.histogram(
        df,
        x='departure_delay',
        nbins=50,
        title='Distribution of Departure Delays',
        labels={'departure_delay': 'Delay (minutes)', 'count': 'Number of Flights'},
        color_discrete_sequence=['#1f77b4']
    )
    
    fig.add_vline(
        x=0,
        line_dash="dash",
        line_color="green",
        annotation_text="On Time"
    )
    
    fig.add_vline(
        x=15,
        line_dash="dash",
        line_color="orange",
        annotation_text="15 min"
    )
    
    fig.update_layout(height=350)
    
    return fig


def create_heatmap(df: pd.DataFrame) -> go.Figure:
    """
    Create a heatmap of delays by day of week and hour
    
    Parameters:
    -----------
    df : pd.DataFrame
        Filtered flights dataframe
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    heatmap_data = df.groupby(['day_of_week', 'hour'])['departure_delay'].mean().reset_index()
    heatmap_pivot = heatmap_data.pivot(index='day_of_week', columns='hour', values='departure_delay')
    
    # Reorder days
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_pivot = heatmap_pivot.reindex(day_order)
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_pivot.values,
        x=heatmap_pivot.columns,
        y=heatmap_pivot.index,
        colorscale='RdYlGn_r',
        text=heatmap_pivot.values,
        texttemplate='%{text:.1f}',
        textfont={"size": 8},
        colorbar=dict(title="Avg Delay (min)")
    ))
    
    fig.update_layout(
        title='Average Delays by Day and Hour',
        xaxis_title='Hour of Day',
        yaxis_title='Day of Week',
        height=400
    )
    
    return fig