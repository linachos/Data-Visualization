import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

#######################
# Setup ###############
#######################

st.set_page_config(layout="wide")
st.title("Life Expectancy Explorer")

# Cache the data loading!
@st.cache_data
def load_data():
    dir = Path(__file__).parent.resolve()
    data_path = dir / "wdi.csv"
    return pd.read_csv(data_path)

df = load_data()

###########################
# Main User Interaction ###
###########################

st.sidebar.header("Settings")

# Input widgets
year = st.sidebar.select_slider(label="Year", options=df["year"].unique(), value=2020)
colorscale = st.sidebar.selectbox(label="Color Scale", options=["Viridis", "Inferno", "Magma"])

########################
# Main logic  ##########
########################

# Filter data for the selected year
plotdata = df[df["year"] == year].sort_values(by="life_expectancy", ascending=False)

# Create choropleth map
map = px.choropleth(plotdata, locations="iso3", color="life_expectancy", color_continuous_scale=colorscale, projection="natural earth")
map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=600)
map.update_geos(showframe=False)

########################
# Rendering   
########################

# ------ Metrics ------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Year", year)
col2.metric("Minimum Life Expectancy", f"{plotdata['life_expectancy'].min():.0f} years")
col3.metric("Average Life Expectancy", f"{plotdata['life_expectancy'].mean():.0f} years")
col4.metric("Maximum Life Expectancy", f"{plotdata['life_expectancy'].max():.0f} years")

# ------ Tabs ------
tab1, tab2 = st.tabs(["Map", "Data"]) 

# Tab 1: Map
selected_points = tab1.plotly_chart(map, on_select="rerun", selection_mode="points")

# Tab 1: Line Chart
if selected_points["selection"]["points"]:
    selected_countries = [point["location"] for point in selected_points["selection"]["points"]]
    linechart = px.line(df[df["iso3"].isin(selected_countries)], x="year", y="life_expectancy", color="country", markers=True)
    tab1.plotly_chart(linechart)
else:
    tab1.warning("Please select countries on the map. Use shift+click for multiple countries")

# Tab 2: Dataframe
selected_rows = tab2.dataframe(plotdata, 
                               column_config={"population": st.column_config.NumberColumn(format="compact"),
                                              "gdp": st.column_config.NumberColumn(format="compact"),
                                              "life_expectancy": st.column_config.NumberColumn(format="compact"),
                                              "fertility": st.column_config.NumberColumn(format="percent")})