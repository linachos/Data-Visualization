import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


# decorator so that the data is not loaded again everytime
# we rerun the page eg. due to changing the year selection
@st.cache_data
def load_data():
    dir = Path(__file__).parent.resolve()
    data_path = dir / "wdi.csv"

    # we need to put the whole path here so that there
    # are no problems displaying the data in dashboard
    df = pd.read_csv(data_path)
    return df


df = load_data()

st.set_page_config(layout="wide")
st.title("Life Expectancy Explorer")
st.markdown("Hello")
st.subheader("Part 1")


# Inputs

color_selection = st.sidebar.selectbox(
    label="Variable of interest", options=["life_expectancy", "gdp_capita"], index=0
)

# year = st.select_slider("Select a year", options=range(2000, 2023))
year = st.sidebar.selectbox("Select a year", options=range(2000, 2023))
color_scale = st.sidebar.selectbox("Color Scale", options=["Reds", "Blues", "Magma"])
plotdata = df[df.year == year]

# Outputs

# Metric
st.metric("Mean Life Expectancy", plotdata.life_expectancy.mean())

tab1, tab2 = st.tabs(["Data", "Map"])

# Data
tab1.dataframe(plotdata)

# Plotly plot
fig = px.choropleth(
    plotdata,
    locations="iso3",
    color=color_selection,
    color_continuous_scale=color_scale,
)
plotly_selection = tab2.plotly_chart(fig, on_select="rerun")

# helper tool to understand selection
st.write(plotly_selection)

points = plotly_selection["selection"]["points"]
selected_countries = [point["location"] for point in points]
st.text(selected_countries)

plotdata2 = df[df.iso3.isin(selected_countries)]
lineplot = px.line(plotdata2, x="year", y="life_expectancy", color="country")
st.plotly_chart(lineplot)
