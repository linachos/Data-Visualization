NY/NJ Flight Delays Dashboard
Interactive Streamlit dashboard for analyzing flight delays from New York and New Jersey airports.

📁 Project Structure
flight-delays-dashboard/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── data/
│   └── flights_data.xlsx # Excel file with flight data (4 sheets)
└── utils/                # Helper functions (optional)
    ├── __init__.py
    ├── data_loader.py
    └── visualizations.py
🚀 Setup Instructions
1. Install Dependencies
bash
pip install -r requirements.txt
2. Prepare Data
Place your flights_data.xlsx file in the data/ folder. The Excel file should contain 4 sheets:

flights: Flight records with delay information
airports: Airport details (codes, names, coordinates)
airlines: Airline information
aircrafts: Aircraft specifications
3. Run the Dashboard
bash
streamlit run app.py
The dashboard will open automatically in your browser at http://localhost:8501

📊 Features
Interactive Filters: Select airports, airlines, and date ranges
KPI Cards: Key metrics (avg delay, on-time %, total flights, severe delays)
Map Visualization: Geographic view of airports with delay indicators
Bar Charts: Compare delays across airports and airlines
Line Charts: Track delay trends over time
Additional Insights: Day-of-week patterns, airline rankings
🎨 Dashboard Components
Required Elements (Assignment)
✅ Map: Airport locations with delay metrics
✅ Bar Chart: Delays by airport
✅ Line Chart: Daily delay trends
✅ KPIs: 4 key performance indicators
✅ Interactivity: Multiple filters (airports, airlines, dates)
📦 Deployment (Optional)
Deploy to Streamlit Community Cloud
Push your code to GitHub
Go to share.streamlit.io
Connect your GitHub repository
Select app.py as the main file
Deploy!
🔧 Customization
Modify colors in app.py (search for color_continuous_scale)
Add new visualizations using Plotly in utils/visualizations.py
Adjust KPIs and metrics in the main dashboard
Change layout by modifying Streamlit columns
📝 Notes
Ensure Excel file has all 4 required sheets
Date columns must be in datetime format
Delay values should be in minutes
NY/NJ airports: EWR, JFK, LGA, SWF
🐛 Troubleshooting
Issue: "Error loading data"

Check that flights_data.xlsx is in the data/ folder
Verify all 4 sheets exist with correct names
Issue: Map not displaying

Ensure airport latitude/longitude values are valid
Check internet connection (map tiles require connection)
Issue: Filters not working

Verify column names match those in your Excel file
Check for null values in filter columns
📧 Contact
For questions or issues, contact your instructor or refer to the assignment documentation.

